from asyncio.log import logger
from asyncore import read
from collections import defaultdict, namedtuple
from concurrent.futures import thread
from enum import Enum
import logging
from re import I
import time

from gevent.queue import Queue
import gevent
from gevent import Greenlet

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
    
    logger.info ('this is the sender',sender)
    if tag == BroadcastTag.CROSS_RBC.value:
        recv_queue = recv_queue[j]

    recv_queue.put_nowait((sender, msg))

def broadcast_receiver_loop(recv_func, recv_queues):
    while True:
        broadcast_receiver(recv_func, recv_queues)

class CRBC():
    def __init__(self, sid, pid, N, f, send, recv, input, logger):
        self.sid = sid
        self.pid = pid
        self.N = N
        self.f = f
        self._send = send
        self._recv = recv
        self.input = input
        self.logger = logger

        self.round = 0
        self._per_round_recv = {}


    def run(self):

        def _recv_loop():
            """Receive messages."""
            #print("start recv loop...")
            while True:
                #gevent.sleep(0)
                try:
                    (sender, (r, msg) ) = self._recv()
                    
                    #self.logger.info('recv1' + str((sender, o)))
                    #print('recv1' + str((sender, o)))
                    # Maintain an *unbounded* recv queue for each epoch
                    if r not in self._per_round_recv:
                        self._per_round_recv[r] = Queue()
                    # Buffer this message
                    self._per_round_recv[r].put_nowait((sender, msg))
                except:
                    continue

        # gevent.spawn(_recv)
        self._recv_thread = Greenlet(_recv_loop)
        self._recv_thread.start()
        self.s_time = time.time()

        if self.logger != None: self.logger.info('Node %d starts to run across broadcast at time:' % self.pid + str(self.s_time))

        while True:
            # gevent.sleep(0)
            # time.sleep(0)

            r = self.round
            if r not in self._per_round_recv:
                self._per_round_recv[r] = Queue()

            def _make_send(r):
                def _send(j, o):
                    self._send(j, (r, o))
                return _send
            
            send_r = _make_send(r)
            recv_r = self._per_round_recv[r].get
            if self.logger != None: self.logger.info('run it1')
            new_cross_tx = self._run_round(r, input, send_r, recv_r)
            if self.logger != None: self.logger.info('run it5 and new_cross_tx',new_cross_tx)
            # print('newcross', new_cross_tx)

            e_time = time.time()
            if self.logger != None:
                self.logger.info('Node %d Delivers ACS Block in Round %d with having across TXs' % (self.pid, r) + str(e_time - self.s_time))

            self.round +=1
            if self.round >= 1:
                break

            self.logger.info('node break')

    def _run_round(self, r, tx_to_send, send, recv):
        # sid = self.sid + ':' + str(r)
        sid = self.sid
        pid = self.pid
        N = self.N 
        f = self.f


        crbc_recvs = [None] * N
        crbc_outputs = [Queue(1) for _ in range(N)]
        # my_crbc_input = Queue(1)

        recv_queues = BroadcastReceiverQueues(
            CROSS_RBC=crbc_recvs
        )

        gevent.spawn(broadcast_receiver_loop, recv, recv_queues)

        for j in range(N):
            if self.logger != None: self.logger.info('run it2')
            def crbc_send(k, o):
                send(k, ('CROSS_RBC', j, o))

            crbc_input = tx_to_send
            task_list = []
            output_list = []

            crbc_recvs[j] = Queue()
            if self.logger != None: self.logger.info('run it3')
            task = gevent.spawn(crossshardbroadcast, sid, pid, N, f, j, crbc_input, crbc_recvs[j].get, crbc_send, self.logger)
            task_list.append(task)
            output_list.append(task.get)

        try:
            gevent.joinall(task_list)
        except KeyboardInterrupt:
            gevent.killall(task_list)

def crossshardbroadcast (sid, pid, N, f, target, input, receive, send, R, MR, logger, round, batch, threads):

    # start_time = time.time()
    assert MR >= R
    assert N >= 3*f +1
    assert f >=0

    ReadyThreshold  = f + 1  
    OutputThreshold = f + 1
    readySent = False
    ready = defaultdict(set)

    for i in range(target*N, (target+1)*N):
        if i<= (R+1)*N and i >= R * N:
            continue
        else:
            for j in range(int(batch/N)):
                ac_input = input + str(j)
                send(i, ('ARBC', ac_input))
    
    # if target == 0:
    #     # for i in range(target * N, (target+1) * N):
    #     for i in range(0,4):
    #         print('arbc is running', f)
    #         for j in range(50):
    #             new_input = input + str(j)
    #         # if i<= (R+1)*N and i >= R * N:
    #         #     continue
    #         # logger.info('hava send ac_tx %s the pid %s and the target id with %s' % (str(input), str(pid), str(i)))
    #             send(i, ('ARBC', new_input))
    # elif target == 1:
    #     for i in range(4,8):
    #         print('arbc is running', f)
    #         for j in range(50):
    #             new_input = input + str(j)
    #             send(i, ('ARBC', new_input))
        
    def broadcast(o):
        for i in range(R*N, (R+1)*N):
            send(i, o)

    def decide(transaction, readySender, logger):
        end_time = time.time()
        logger.info('decide: %s with the ready_list %s in %f in round of %d' % (transaction, str(readySender[ac_tx]), end_time-s_time[ac_tx], round))


    readySenders = defaultdict(set)
    s_time = {}
    readyCounter = defaultdict(lambda: 0)


    while True:
        sender, msg = receive()
        if msg[0] == 'ARBC':
            ac_tx = msg
            # Validation Redundant``
            # tx_hash = hash(ac_tx)
            if sender in readySenders[ac_tx]:
                continue
            if len(readySenders[ac_tx]) >= ReadyThreshold:
                continue
            # Update start time
            if (ac_tx in s_time) == False:
                s_time[ac_tx] = time.time()

            readyCounter[ac_tx] += 1
            readySenders[ac_tx].add(sender)

            # logger.info('this is the greenlet current %s and len of readySenders %s' % (str(gevent.getcurrent()), str(len(readySenders))))
            # logger.info(' this is the elements of readySenders %s' % (str(readySenders)))
            
            # logger.info('have add on set %s and sender %s and member of readySenders %s and round value with %s' % (str(ac_tx), str(sender), str(readySenders[ac_tx]), str(round)))
            # logger.info('have add on Count %s' % (str(readyCounter[ac_tx])))

            if len(readySenders[ac_tx]) >= OutputThreshold :
                decide(ac_tx, readySenders,logger)
            
            
















            
            # if len(readySenders[tx_hash]) >= ReadyThreshold:
            #     return decide(ac_tx, readySenders,logger)
                # broadcast(('CRBC', ac_tx))
                
        # elif msg[0] == 'CRBC':
        #     (_, ac_tx) = msg

        #     if sender in ready[ac_tx]:
        #         continue
        #     if len(ready[ac_tx]) >= ReadyThreshold and not readySent:
        #         broadcast(('CRBC', ac_tx))
            
        #     if len(ready[ac_tx]) >= OutputThreshold:
        #         return decide(ac_tx, ready,logger)


            
