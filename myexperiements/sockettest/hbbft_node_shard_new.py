import numbers
import random
from tkinter.tix import Tree
from typing import Callable
import gevent
import os
import pickle
import logging
import os 
import traceback
import random
from ctypes import c_bool

from gevent import time
from gevent.queue import Queue
from gevent import Greenlet
from gevent import socket, monkey


# from honeybadgerbft_shard.core.honeybadger import HoneyBadgerBFT
# from honeybadgerbft_shard.core.acrossshardcast import CRBC
# from myexperiements.sockettest.make_random_tx import tx_generator
# from multiprocessing import Value as mpValue, Queue as mpQueue, Process
# from network_arbc.socket_client import NetworkClient
# from network_arbc.socket_server import NetworkServer

from honeybadgerbft_shard_copy.core.honeybadger import HoneyBadgerBFT
from honeybadgerbft_shard_copy.core.honeybadger_block import honeybadger_block
from myexperiements.sockettest.make_random_tx import tx_generator
from honeybadgerbft_shard_copy.core.acrossshardcast import CRBC
from multiprocessing import Value as mpValue, Queue as mpQueue, Process
from network_othernode.socket_client import NetworkClient
from network_othernode.socket_server import NetworkServer


def set_consensus_log(id: int): 
    logger = logging.getLogger("consensus-node-"+str(id))
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s %(filename)s [line:%(lineno)d] %(funcName)s %(levelname)s %(message)s ')
    if 'log' not in os.listdir(os.getcwd()):
        os.mkdir(os.getcwd() + '/log')
    full_path = os.path.realpath(os.getcwd()) + '/log/' + "consensus-node-"+str(id) + ".log"
    file_handler = logging.FileHandler(full_path)
    file_handler.setFormatter(formatter)  # 可以通过setFormatter指定输出格式
    logger.addHandler(file_handler)
    return logger

def load_key(id):

    with open(os.getcwd() + '/keys/' + 'sPK.key', 'rb') as fp:
        sPK = pickle.load(fp)

    with open(os.getcwd() + '/keys/' + 'ePK.key', 'rb') as fp:
        ePK = pickle.load(fp)

    with open(os.getcwd() + '/keys/' + 'sSK-' + str(id) + '.key', 'rb') as fp:
        sSK = pickle.load(fp)

    with open(os.getcwd() + '/keys/' + 'eSK-' + str(id) + '.key', 'rb') as fp:
        eSK = pickle.load(fp)

    return sPK, ePK, sSK, eSK


def set_logger_of_node(id: int):
    logger = logging.getLogger("node-"+str(id))
    logger.setLevel(logging.DEBUG)
    # logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s %(filename)s [line:%(lineno)d] %(funcName)s %(levelname)s %(message)s ')
    if 'log' not in os.listdir(os.getcwd()):
        os.mkdir(os.getcwd() + '/log')
    full_path = os.path.realpath(os.getcwd()) + '/log/' + "node-"+str(id) + ".log"
    file_handler = logging.FileHandler(full_path)
    file_handler.setFormatter(formatter)  # 可以通过setFormatter指定输出格式
    logger.addHandler(file_handler)
    return logger

 
class HoneyBadgerBFTNode_shard_new (HoneyBadgerBFT):
 
    def __init__(self, sid, id, B, N, f, per, bft_from_server, bft_to_client,ready: mpValue, stop: mpValue, K=3, R=1, MR=1, BP=False, mode='debug', mute=False,debug=False, bft_running: mpValue=mpValue(c_bool, False), tx_buffer=None):
        self.R = R # 当前 shard id
        self.MR = MR # 最大 shard id
        self.shard = int(N / MR)
        # if self.R == 0:
        #     self.shard = int(N/(R+1))# shard 是每组的节点数
        # else:
        #     self.shard = int(N/R)
        # self.sPK, self.ePK, self.sSK, self.eSK = load_key(id, self.R, self.shard,N)
        self.sPK, self.ePK, self.sSK, self.eSK = load_key(id)

        self.bft_from_server = bft_from_server
        self.bft_to_client = bft_to_client
        self.send = lambda j, o: self.bft_to_client((j, o))
        self.recv = lambda: self.bft_from_server()
        self.ready = ready
        self.stop = stop
        self.mode = mode
        self.running = bft_running
        
        self.N = N
        self.K = K
        self.B = B
        self.bp = BP

        
        HoneyBadgerBFT.__init__(self, sid, id, B, N, f, self.sPK, self.sSK, self.ePK, self.eSK, per, send=self.send, recv=self.recv, shard=self.shard, K=K, R=R, MR=MR, bp=BP, logger=set_consensus_log(id), mute=mute)
        
        self._prepare_bootstrap()

    def _prepare_bootstrap(self):
        if self.mode == 'test' or 'debug':
            for r in range(self.K * self.B):
                tx = tx_generator(250) # Set each dummy TX to be 250 Byte
                HoneyBadgerBFT.submit_tx(self, tx)
        else:
            pass
            # TODO: submit transactions through tx_buffer

    def across_broadcast(self, trans):

        print('across_broadcast is running...')
        # 用来决定目标shard id
        number = []
        for i in range(0, self.R):
            number.append(i)
        for i in range(self.R, self.MR):
            number.append(i)
        target = random.choice(number) # target of sending across_tx
        test_tatget = 0 # test shadr id 0

        # address is the id of targett shard
        addresses = [None] * self.shard
        try:
            with open('arbc_hosts.config', 'r') as hosts:
                for line in hosts:
                    params = line.split()
                    pid = int(params[0])
                    priv_ip = params[1]
                    pub_ip = params[1]
                    port = int(params[2])
                    # print(pid, ip, port)
                    if pid not in range(self.shard):
                        continue
                    if pid == self.id:
                        my_address = (priv_ip, port)
                    for _ in range((test_tatget*self.shard), (test_tatget+1)*self.shard):
                        addresses[pid] = (pub_ip, port)
            assert all([node is not None for node in addresses])

            client_bft_mpq = mpQueue()
            #client_from_bft = client_bft_mpq.get
            client_from_bft = lambda: client_bft_mpq.get(timeout=0.00001)
            bft_to_client = client_bft_mpq.put_nowait

            server_bft_mpq = mpQueue()
            #bft_from_server = server_bft_mpq.get
            bft_from_server = lambda: server_bft_mpq.get(timeout=0.00001)
            server_to_bft = server_bft_mpq.put_nowait

            client_ready = mpValue(c_bool, False) 
            server_ready = mpValue(c_bool, False)
            net_ready = mpValue(c_bool, False)
            stop = mpValue(c_bool, False)
            bft_running = mpValue(c_bool, False)  # True = good network; False = bad network

            net_server = NetworkServer(my_address[1], my_address[0], i, addresses, server_to_bft, server_ready, stop)
            net_client = NetworkClient(my_address[1], my_address[0], i, addresses, client_from_bft, client_ready, stop, bft_running, dynamic=False)
            #print(O) 
            net_server.start()
            net_client.start()

            while not client_ready.value or not server_ready.value:
                time.sleep(1)
                print("waiting for network ready...")

            with net_ready.get_lock():
                net_ready.value = True

            bft = CRBC(self.sid, self.id, self.R, self.f, bft_from_server, server_to_bft, trans,self.logger)

            bft_thread = Greenlet(bft.run)
            bft_thread.start()
            bft_thread.join()

            with stop.get_lock():
                stop.value = True

            net_client.terminate()
            net_client.join()
            time.sleep(1)
            net_server.terminate()
            net_server.join()

        except FileNotFoundError or AssertionError as e:
            traceback.print_exc()

        print("across broadcast end")

    def run(self):

        pid = os.getpid()
        self.logger.info('shard %d\'s node %d\'s start to run consensus on process id %d' % (self.R, self.id, pid))
        
        # self._prepare_bootstrap()

        while not self.ready.value:
            time.sleep(1)

        self.running.value = True

        self.run_bft()


def main(sid, i, B, N, f, addresses, K):
    badger = HoneyBadgerBFT(sid, i, B, N, f, addresses, K)
    # badger.run_hbbft_instance()
    badger.run()


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--sid', metavar='sid', required=True,
                        help='identifier of node', type=str)
    parser.add_argument('--id', metavar='id', required=True,
                        help='identifier of node', type=int)
    parser.add_argument('--N', metavar='N', required=True,
                        help='number of parties', type=int)
    parser.add_argument('--f', metavar='f', required=True,
                        help='number of faulties', type=int)
    parser.add_argument('--B', metavar='B', required=True,
                        help='size of batch', type=int)
    parser.add_argument('--K', metavar='K', required=True,
                        help='rounds to execute', type=int)
    args = parser.parse_args()

    # Some parameters
    sid = args.sid
    i = args.id
    N = args.N 
    f = args.f
    B = args.B
    K = args.K

    # Random generator
    rnd = random.Random(sid)

    # Nodes list
    host = "127.0.0.1"
    port_base = int(rnd.random() * 5 + 1) * 10000
    addresses = [(host, port_base + 200 * i) for i in range(N)]
    print(addresses)

    main(sid, i, B, N, f, addresses, K)
