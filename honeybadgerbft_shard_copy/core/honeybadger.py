# from email.headerregistry import Group
from asyncio.log import logger
from gevent.pool import Group
import json
from select import select
from tokenize import group
import traceback, time
# from asyncio.timeouts import timeout
import gevent
import numpy as np 
from collections import defaultdict, namedtuple, deque
from enum import Enum
from gevent import Greenlet
from gevent.queue import Queue
import random 
from honeybadgerbft_shard_copy.core.commoncoin import shared_coin
from honeybadgerbft_shard_copy.core.binaryagreement import binaryagreement
from honeybadgerbft_shard_copy.core.reliablebroadcast import reliablebroadcast
from honeybadgerbft_shard_copy.core.commonsubset import commonsubset
from honeybadgerbft_shard_copy.core.honeybadger_block import honeybadger_block
from honeybadgerbft_shard_copy.core.acrossshardcast import crossshardbroadcast
from honeybadgerbft_shard_copy.exceptions import UnknownTagError

block = set()

class BroadcastTag(Enum):
    ACS_COIN = 'ACS_COIN'
    ACS_RBC = 'ACS_RBC'
    ACS_ABA = 'ACS_ABA'
    TPKE = 'TPKE'
    CROSS_RBC = 'CROSS_RBC'
    

class Across_BroadcastTag(Enum):
    CROSS_RBC = 'CROSS_RBC'

BroadcastReceiverQueues = namedtuple(
    'BroadcastReceiverQueues', ('ACS_COIN', 'ACS_ABA', 'ACS_RBC', 'TPKE','CROSS_RBC'))

ABroadcastReceiverQueues = namedtuple(
    'BroadcastReceiverQueues', ('CROSS_RBC'))


def broadcast_receiver(recv_func, recv_queues, shard):
    sender, (tag, j, msg) = recv_func()
    if tag not in BroadcastTag.__members__:
        # TODO Post python 3 port: Add exception chaining.
        # See https://www.python.org/dev/peps/pep-3134/
        raise UnknownTagError('Unknown tag: {}! Must be one of {}.'.format(
            tag, BroadcastTag.__members__.keys()))
    recv_queue = recv_queues._asdict()[tag] 
    # logger.info('sender %s tag %s and j %s' % (str(sender), str(tag), str(j)))

    if tag != BroadcastTag.TPKE.value:
        recv_queue = recv_queue[j%shard]
    


    recv_queue.put_nowait((sender, msg))



def broadcast_receiver_loop(recv_func, recv_queues, shard):
    while True:
        gevent.sleep(0)
        time.sleep(0)
        broadcast_receiver(recv_func, recv_queues, shard)
 

class HoneyBadgerBFT():
    r"""HoneyBadgerBFT object used to run the protocol. 

    :param str sid: The base name of the common coin that will be used to
        derive a nonce to uniquely identify the coin.
    :param int pid: Node id.
    :param int B: Batch size of transactions.
    :param int N: Number of nodes in the network.
    :param int f: Number of faulty nodes that can be tolerated.
    :param str sPK: Public key of the threshold signature
        (:math:`\mathsf{TSIG}`) scheme.
    :param str sSK: Signing key of the threshold signature
        (:math:`\mathsf{TSIG}`) scheme.
    :param str ePK: Public key of the threshold encryption
        (:math:`\mathsf{TPKE}`) scheme.
    :param str eSK: Signing key of the threshold encryption
        (:math:`\mathsf{TPKE}`) scheme.
    :param send:
    :param recv:
    :param K: a test parameter to specify break out after K rounds
    """ 

    def __init__(self, sid, pid, B, N, f, sPK, sSK, ePK, eSK, per, send, recv, shard, K, R, MR, bp, logger, mute=False):
        self.sid = sid
        self.id = pid 
        self.B = B
        self.N = N
        self.f = f
        self.sPK = sPK
        self.sSK = sSK
        self.ePK = ePK
        self.eSK = eSK
        self._send = send
        self._recv = recv
        self.logger = logger
        self.round = 0  # Current block number
        self.transaction_buffer = deque()
        self._per_round_recv = {}  # Buffer of incoming messages
        self.K = K
        self.R = R
        self.MR = MR #amount of shard
        self.shard = shard
        self.startpoint = int(R * shard)
        self.end = int((R+1) * shard)
        self.bp = bp
        self.per = per
        self.ac_batch = per * (self.shard * self.B)
        self.thread = 5
        # self.bp = True


        self.s_time = 0
        self.e_time = 0
        self.txcnt = 0

        self.mute = mute


    def submit_tx(self, tx):
        """Appends the given transaction to the transaction buffer.

        :param tx: Transaction to append to the buffer.
        """
        #print('backlog_tx', self.id, tx)
        #if self.logger != None: self.logger.info('Backlogged tx at Node %d:' % self.id + str(tx))
        self.transaction_buffer.append(tx)

    def run_bft(self):
        """Run the HoneyBadgerBFT protocol."""

        if self.mute:

            def send_blackhole(*args):
                pass

            def recv_blackhole(*args):
                while True:
                    gevent.sleep(1)
                    time.sleep(1)
                    pass

            seed = int.from_bytes(self.sid.encode('utf-8'), 'little')
            if self.id in np.random.RandomState(seed).permutation(self.N)[:int((self.N - 1) / 3)]:
                self._send = send_blackhole
                self._recv = recv_blackhole

        def _recv_loop():
            """Receive messages."""
            #print("start recv loop...")
            while True:
                #gevent.sleep(0)
                try:
                    (sender, (r, msg) ) = self._recv()
                    #self.logger.info('recv1' + str((sender, o)))
                    # self.logger.info('recv1 %s sender and %s msg' % (str(sender), str(msg)))
                    #print('recv1' + str((sender, o)))
                    # Maintain an *unbounded* recv queue for each epoch
                    if r not in self._per_round_recv:
                        self._per_round_recv[r] = Queue()
                    # Buffer this message
                    self._per_round_recv[r].put_nowait((sender, msg))
                except:
                    continue

        # self._recv_thread = gevent.spawn(_recv)

        self._recv_thread = Greenlet(_recv_loop)
        self._recv_thread.start()

        self.s_time = time.time()
        if self.logger != None: self.logger.info('Node %d starts to run at time:' % self.id + str(self.s_time))

        while True:
            # For each round...

            gevent.sleep(0)
            time.sleep(0)

            start = time.time()

            r = self.round
            if r not in self._per_round_recv:
                self._per_round_recv[r] = Queue()

            # Select B transactions (TODO: actual random selection)
            tx_to_send = []
            for _ in range(self.B):
                tx_to_send.append(self.transaction_buffer.popleft())

            
            # TODO: Wait a bit if transaction buffer is not full
 
            # Run the round
            def _make_send(r):
                def _send(j, o):
                    self._send(j, (r, o))
                return _send

            send_r = _make_send(r) 
            recv_r = self._per_round_recv[r].get
            # print('this is the recv_r', recv_r)
            new_tx = self._run_round(r, tx_to_send, send_r, recv_r, self.s_time)

            if self.logger != None:
                #self.logger.info('Node %d Delivers Block %d: ' % (self.id, self.round) + str(new_tx))
                tx_cnt = str(new_tx).count("Dummy TX")
                self.txcnt = tx_cnt
                self.logger.info(
                'Node %d Delivers ACS Block in Round %d with having %d TXs' % (self.id, r, tx_cnt))

            end = time.time()

            if self.logger != None:
                self.logger.info('ACS Block Delay at Round %d at Node %d: ' % (self.id, r) + str(end - start))

            # Remove output transactions from the backlog buffer
            for _tx in tx_to_send:
                if _tx not in new_tx:
                    self.transaction_buffer.appendleft(_tx)

            

            self.round += 1     # Increment the round
            if self.round >= self.K:
                break   # Only run one round for now

        if self.logger != None:
            self.e_time = time.time()
            # self.logger.info("node %d breaks in %f seconds with total delivered Txs %d" % (self.id, self.e_time-self.s_time, self.txcnt))
            self.logger.info("node %d of shard %d in %f seconds with total delivered Txs %d and throughput with %f" % (self.id, self.R, self.e_time-self.s_time, self.txcnt, (self.txcnt / (self.e_time-self.s_time))))
        else:
            print("node %d breaks" % self.id)


    def _run_round(self, r, tx_to_send, send, recv, s_time):
        """Run one protocol round.

        :param int r: round id
        :param tx_to_send: Transaction(s) to process.
        :param send:
        :param recv:
        """
        # Unique sid for each round
        sid = self.sid + ':' + str(r)
        pid = self.id
        N = self.N
        f = self.f
        bp = self.bp

        def broadcast(o):
            """Multicast the given input ``o``.

            :param o: Input to multicast.
            """
            # for j in range(N):
            for j in range(self.startpoint, self.end):
                send(j, o)

        coin_recvs = [None] * self.shard
        aba_recvs  = [None] * self.shard  # noqa: E221
        rbc_recvs  = [None] * self.shard  # noqa: E221

        aba_inputs  = [Queue(1) for _ in range(self.shard)]  # noqa: E221
        aba_outputs = [Queue(1) for _ in range(self.shard)]
        rbc_outputs = [Queue(1) for _ in range(self.shard)]
        arbc_outputs = [Queue(1) for _ in range(self.shard)]

        my_rbc_input = Queue(1)
        # if self.logger != None: self.logger.info('Commit tx at Node %d:' % self.id + str(tx_to_send))

        def _setup(j):
            shard_j = j % self.shard
            """Setup the sub protocols RBC, BA and common coin.

            :param int j: Node index for which the setup is being done.
            """
            def coin_bcast(o):
                """Common coin multicast operation.
                :param o: Value to multicast.
                """
                broadcast(('ACS_COIN', j, o))

            coin_recvs[shard_j] = Queue()
            coin = shared_coin(sid + 'COIN' + str(j), pid, self.shard, N, f,
                               self.sPK, self.sSK,
                               coin_bcast, coin_recvs[shard_j].get)

            def aba_send(k, o):
                """Binary Byzantine Agreement multicast operation.
                :param k: Node to send.
                :param o: Value to send.
                """
                send(k, ('ACS_ABA', j, o))
 

            aba_recvs[shard_j] = Queue()
            gevent.spawn(binaryagreement, sid+'ABA'+str(j), pid, self.shard, f, coin,
                         aba_inputs[shard_j].get, aba_outputs[shard_j].put_nowait,
                         aba_recvs[shard_j].get, aba_send, self.startpoint, self.end)

            def rbc_send(k, o):
                """Reliable send operation.
                :param k: Node to send.
                :param o: Value to send.
                """
                send(k, ('ACS_RBC', j, o))

            # Only leader gets input
            rbc_input = my_rbc_input.get if j == pid else None
            
            rbc_recvs[shard_j] = Queue()
            rbc = gevent.spawn(reliablebroadcast, sid+'RBC'+str(j), pid, self.shard, f, j,
                               rbc_input, rbc_recvs[shard_j].get, rbc_send, self.startpoint, self.end, N)
            rbc_outputs[shard_j] = rbc.get  # block for output from rbc

        # N instances of ABA, RBC
        # for j in range(N):
        for j in range(self.startpoint, self.end):
            _setup(j)

        # One instance of TPKE
        def tpke_bcast(o):
            """Threshold encryption broadcast."""
            broadcast(('TPKE', '', o))

        tpke_recv = Queue()

        # One instance of ACS
        acs = gevent.spawn(commonsubset, pid, self.shard, f, rbc_outputs,
                           [_.put_nowait for _ in aba_inputs],
                           [_.get for _ in aba_outputs], self.startpoint, self.end)


        crbc_recvs = [None] * self.shard
        for i in range(self.startpoint, self.end):
            crbc_recvs[i % self.shard] = Queue()

        recv_queues = BroadcastReceiverQueues(
            ACS_COIN=coin_recvs,
            ACS_ABA=aba_recvs,
            ACS_RBC=rbc_recvs,
            TPKE=tpke_recv,
            CROSS_RBC=crbc_recvs,
        )
        gevent.spawn(broadcast_receiver_loop, recv, recv_queues, self.shard)

        _input = Queue(1)
        _input.put(json.dumps(tx_to_send))

        _output = honeybadger_block(pid, self.shard, self.f, self.ePK, self.eSK,
                          _input.get,
                          acs_put_in=my_rbc_input.put_nowait, acs_get_out=acs.get,
                          tpke_bcast=tpke_bcast, tpke_recv=tpke_recv.get)
        
        for batch in _output:
            # decoded_batch = (batch.decode())
            decoded_batch = json.loads(batch.decode())
            for tx in decoded_batch:
                block.add(tx)

        tx = list(block)
        logger.info((str(tx)))
        tx_cnt = str(tx).count("Dummy TX")
        if self.logger != None:
            e_time = time.time()
            self.logger.info("node %d of shard %d in %f seconds with total delivered Txs %d in %d round and throughout with %f" % (self.id, self.R, e_time-self.s_time, tx_cnt, self.round, tx_cnt / (e_time-self.s_time)))
        
        
        # AcrossBroadcast start
        def crbc_send(k, o): 
                send(k, ('CROSS_RBC', j, o))
        

        # ac_rbc in send by send
        # if self.bp == False: # tx one by one send
        #     ac = len(tx)
        #     self.logger.info("node %d start one by one send acrossBroadcast" % self.id)
        #     for i in range(ac):
        #         target_shard = int(i%self.MR)
        #         if target_shard == self.R:
        #             continue
        #         else:
        #             arbc_input = tx[i]
        #             arbc = gevent.spawn(crossshardbroadcast, sid, pid, self.shard, f, target_shard, arbc_input, crbc_recvs[j%self.shard].get, crbc_send, self.R, self.MR, self.logger, self.round)
        #             arbc_outputs[j%self.shard] = arbc.get

        if bp == True:  #batch processing
            self.logger.info("node %d start batch processing send acrossBroadcast" % self.id)
            target_shard = int((self.R+1)%self.MR) # ac_tx send to next shard
            # if self.R == 0:
            #     target_shard = 1
            # else:
            #     target_shard = 0
            for i in range(int(self.shard)):
                arbc_in = str(i)+str(sid)
                arbc = gevent.spawn(crossshardbroadcast, sid, pid, self.shard, f, target_shard, arbc_in, crbc_recvs[i%self.shard].get, crbc_send, self.R, self.MR, self.logger, self.round, self.ac_batch, self.thread)
                arbc_outputs[i%self.shard] = arbc.get
            arbc_recv = gevent.spawn(broadcast_receiver_loop, recv, recv_queues, self.shard)
            arbc_recv.join(timeout=0)
        print('arbc has done in round of', r)
        return list(block)

    def get_tx(self):
        return list(block)