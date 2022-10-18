from asyncore import read
from collections import defaultdict, namedtuple
from enum import Enum

from gevent.queue import Queue
import gevent

from honeybadgerbft.exceptions import UnknownTagError


class BroadcastTag(Enum):
    CROSS_RBC = 'CROSS_RBC'

BroadcastReceiverQueues = namedtuple(
    'BroadcastReceiverQueues', ('CROSS_RBC'))

def broadcast_receiver(recv_func, recv_queues):
    sender, (tag, j, msg) = recv_func()
    if tag not in BroadcastTag.__members__:
        raise UnknownTagError('Unknown tag: {}! Must be one of {}.'.format(
            tag, BroadcastTag.__members__.keys()))
    recv_queue = recv_queues._asdict()[tag]

    if tag != BroadcastTag.TPKE.value:
        recv_queue = recv_queue[j]

    recv_queue.put_nowait((sender, msg))

def broadcast_receiver_loop(recv_func, recv_queues):
    while True:
        broadcast_receiver(recv_func, recv_queues)

class CRBC():
    def __init__(self, sid, pid, N, f, send, recv,input):
        self.sid = self
        self.pid = pid
        self.N = N
        self.f = f
        self._send = send
        self._recv = recv
        self.input = input

        self.round = 0
        self._per_round_recv = {}


    def run(self):
        def _recv():
            while True:
                (sender, (r, msg)) = self._recv()

                if r not in self._per_round_recv:
                    # Buffer this message
                    assert r >= self.round      # pragma: no cover
                    self._per_round_recv[r] = Queue()

                _recv = self._per_round_recv[r]
                if _recv is not None:
                    # Queue it
                    _recv.put((sender, msg))

        gevent.spawn(_recv) 

        while True:
            r = self.round
            if r not in self._per_round_recv:
                self._per_round_recv[r] = Queue()
            def _make_send(r):
                def _send(j, o):
                    self._send(j, (r, o))
                return _send
            send_r = _make_send(r)
            recv_r = self._per_round_recv[r].get
            new_cross_tx = self._run_round(r, input, send_r, recv_r)

            self.round +=1

    def _run_round(self, r, tx_to_send, send, recv):
        # sid = self.sid + ':' + str(r)
        sid = self.sid
        pid = self.pid
        N = self.N 
        f = self.f
        round = self.round

        def broadcast(o):
            for j in range(N):
                send(j, o)

        crbc_recvs = [None] * N
        crbc_outputs = [Queue(1) for _ in range(N)]
        my_crbc_input = Queue(1)

        def _setup(j):
            def crbc_send(k, o):
                send(k, ('CRBC', j, o))

            crbc_input = tx_to_send

            crbc_recvs[j] = Queue()
            return gevent.spawn(crossshardbroadcast, sid, pid, N, f, j,
                                crbc_input,crbc_recvs[j].get, crbc_send)
        
        for j in range(N):
            _setup(j)

        recv_queues = BroadcastReceiverQueues(
            CROSS_RBC=crbc_recvs
        )
        gevent.spawn(broadcast_receiver_loop, recv, recv_queues)

def crossshardbroadcast (self, sid, pid, N, f, input, receive, send):
    assert N >= 3*f +1
    assert f >=0
    assert 0 <= pid < N

    InputThreshold  = f + 1
    ReadyThreshold  = f + 1
    OutputThreshold = 2 * f + 1


    def broadcast(o):
        for i in range(N):
            send(i, o)

    def decide(transaction):
        print('decide:',transaction)

    transaction = input()


    valCounter = defaultdict(lambda: 0)
    valSenders = set()
    ready = set()
    readySend = False
    readySenders = set()

    while True:
        sender, msg = receive()
        if msg[0] == 'VAL':
            transaction = msg
            if sender in valSenders:
                print("Redundant CROSS_VAL")
                continue

            #Update
            valSenders.add(sender)
            valCounter[transaction] +=1

            if len(valCounter) >= InputThreshold and not readySend:
                readySend = True
                broadcast(('READY', transaction))

        if msg[0] == 'READY':
            transaction = msg
            # Validation
            if sender in ready[transaction] or sender in readySenders:
                print("Redundant READY")
                continue

            #Update
            ready[transaction].add(sender)
            readySenders.add(sender)

            #Amplify ready message
            if len(ready[transaction]) >= ReadyThreshold and not readySend:
                readySend = True
                broadcast(('READY', transaction))
            
            if len(ready[transaction]) >= OutputThreshold:
                return decide(transaction)

            
