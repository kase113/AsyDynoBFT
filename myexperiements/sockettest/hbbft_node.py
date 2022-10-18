import random
from typing import Callable
import gevent
import os
import pickle
import logging
import os 
import traceback
from ctypes import c_bool

from gevent import time
from gevent.queue import Queue
from gevent import Greenlet
from gevent import socket, monkey
from honeybadgerbft.core.honeybadger import HoneyBadgerBFT
from myexperiements.sockettest.make_random_tx import tx_generator
from multiprocessing import Value as mpValue, Queue as mpQueue, Process


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

# Network node class: deal with socket communications
class Node(Greenlet):

    SEP = '\r\nSEP\r\n'

    def __init__(self, port: int, ip: str, id: int, addresses_list: list, logger=None):
        self.queue = Queue()
        self.ip = ip
        self.port = port
        self.id = id
        self.addresses_list = addresses_list
        self.socks = [None for _ in self.addresses_list]
        if logger is None:
            self.logger = set_logger_of_node(self.id)
        else:
            self.logger = logger
        Greenlet.__init__(self)

    def _run(self):
        self.logger.info("node %d starts to run..." % self.id)
        self._serve_forever()

    def _handle_request(self, sock, address):

        def _finish(e: Exception):
            self.logger.error("node %d's server is closing..." % self.id)
            self.logger.error(str(e))
            print(e)
            print("node %d's server is closing..." % self.id)
            pass

        buf = b''
        try:
            while True:
                gevent.sleep(0)
                buf += sock.recv(4096)
                tmp = buf.split(self.SEP.encode('utf-8'), 1)
                while len(tmp) == 2:
                    buf = tmp[1]
                    data = tmp[0]
                    if data != '' and data:
                        if data == 'ping'.encode('utf-8'):
                            sock.sendall('pong'.encode('utf-8'))
                            self.logger.info("node {} is pinging node {}...".format(self._address_to_id(address), self.id))
                        else:
                            (j, o) = (self._address_to_id(address), pickle.loads(data))
                            assert j in range(len(self.addresses_list))
                            gevent.spawn(self.queue.put_nowait((j, o)))
                    else:
                        self.logger.error('syntax error messages')
                        raise ValueError
                    tmp = buf.split(self.SEP.encode('utf-8'), 1)
        except Exception as e:
            self.logger.error(str((e, traceback.print_exc())))
            _finish(e)

    def _serve_forever(self):
        self.server_sock = socket.socket()
        self.server_sock.bind((self.ip, self.port))
        self.server_sock.listen(5)
        while True:
            sock, address = self.server_sock.accept()
            gevent.spawn(self._handle_request, sock, address)
            self.logger.info('node id %d accepts a new socket from node %d' % (self.id, self._address_to_id(address)))
            gevent.sleep(0)

    def _watchdog_deamon(self):
        pass 

    def connect_all(self):
        self.logger.info("node %d is fully meshing the network" % self.id)
        is_sock_connected = [False] * len(self.addresses_list)
        while True:
            try:
                for j in range(len(self.addresses_list)):
                    if not is_sock_connected[j]:
                        is_sock_connected[j] = self._connect(j)
                if all(is_sock_connected):
                    break
                time.sleep(1)
            except Exception as e:
                self.logger.info(str((e, traceback.print_exc())))

    def _connect(self, j: int):
        sock = socket.socket()
        sock.bind((self.ip, self.port + j + 1))
        try:
            sock.connect(self.addresses_list[j])
            sock.sendall(('ping' + self.SEP).encode('utf-8'))
            pong = sock.recv(4096)
        except Exception as e1:
            return False
            #print(e1)
            #traceback.print_exc()
        if pong.decode('utf-8') == 'pong':
            self.logger.info("node {} is ponging node {}...".format(j, self.id))
            self.socks[j] = sock
            return True
        else:
            self.logger.info("fails to build connect from {} to {}".format(self.id, j))
            return False

    def _send(self, j: int, o: bytes):
        msg = b''.join([o, self.SEP.encode('utf-8')])
        try:
            self.socks[j].sendall(msg)
        except Exception as e1:
            self.logger.error("fail to send msg")
            #print("fail to send msg")
            try:
                self._connect(j)
                self.socks[j].connect(self.addresses_list[j])
                self.socks[j].sendall(msg)
            except Exception as e2:
                self.logger.error(str((e1, e2, traceback.print_exc())))

    def send(self, j: int, o: object):
        try:
            self._send(j, pickle.dumps(o))
        except Exception as e:
            self.logger.error(str(("problem objective when sending", o)))
            traceback.print_exc(e)

    def _recv(self):
        #time.sleep(0.001)
        #try:
        (i, o) = self.queue.get()
        #print("node %d is receving: " % self.id, (i, o))
        return (i, o)
        #except Exception as e:
        #   print(e)
        #   pass

    def recv(self):
        return self._recv()

    def _address_to_id(self, address: tuple):
        # print(address)
        # print(self.addresses_list)
        # assert address in self.addresses_list
        for i in range(len(self.addresses_list)):
            if address[0] != '127.0.0.1' and address[0] == self.addresses_list[i][0]:
                return i
        return int((address[1] - 10007) / 200)

 
class HoneyBadgerBFTNode (HoneyBadgerBFT):
 
    def __init__(self, sid, id, B, N, f, bft_from_server, bft_to_client,ready: mpValue, stop: mpValue, K=3, mode='debug', mute=False,debug=False, bft_running: mpValue=mpValue(c_bool, False), tx_buffer=None):
        self.sPK, self.ePK, self.sSK, self.eSK = load_key(id)

        self.bft_from_server = bft_from_server
        self.bft_to_client = bft_to_client
        self.send = lambda j, o: self.bft_to_client((j, o))
        self.recv = lambda: self.bft_from_server()
        self.ready = ready
        self.stop = stop
        self.mode = mode
        self.running = bft_running

        # HoneyBadgerBFT.__init__(self, sid, id, B, N, f, self.sPK, self.sSK, self.ePK, self.eSK, send=None, recv=None, K=K, logger=set_consensus_log(id), mute=mute)
        HoneyBadgerBFT.__init__(self, sid, id, B, N, f, self.sPK, self.sSK, self.ePK, self.eSK, send=self.send, recv=self.recv, K=K, logger=set_consensus_log(id), mute=mute)

        # self.server = Node(id=id, ip=addresses_list[id][0], port=addresses_list[id][1], addresses_list=addresses_list, logger=self.logger)
        self.N = N
        self._prepare_bootstrap()
        def hosts_config(self):
            addresses = [None] * self.N
            try:
                with open('hosts.config', 'r') as hosts:
                    for line in hosts:
                        params = line.split()
                        pid = eval(params[0])
                        ip = params[1]
                        port = eval(params[3])
                        # print(pid, ip, port)
                        if pid not in range(N):
                            continue
                        addresses[pid] = [ip, port]
                # print(addresses)
                assert all([node is not None for node in addresses])
                print("hosts.config is correctly read")
                print('addresses:',addresses)
            except FileNotFoundError or AssertionError as e:
                traceback.print_exc()
            return addresses
        addresses_list = hosts_config(self)
        print(addresses_list)
        self.server = Node(id=id, ip=addresses_list[id][0], port=addresses_list[id][1], addresses_list=addresses_list, logger=self.logger)

    def _prepare_bootstrap(self):
        if self.mode == 'test' or 'debug':
            for r in range(self.K * self.B):
                tx = tx_generator(250) # Set each dummy TX to be 250 Byte
                HoneyBadgerBFT.submit_tx(self, tx)
        else:
            pass
            # TODO: submit transactions through tx_buffer

    def start_socket_server(self):
        pid = os.getpid()
        #print('pid: ', pid)
        self.logger.info('node id %d is running on pid %d' % (self.id, pid))
        self.server.start()

    def connect_socket_servers(self):
        # self.server.connect_and_send_forever()
        self.server._serve_forever
        self._send = self.server.send
        self._recv = self.server.recv

    def run_hbbft_instance(self):
        self.start_socket_server()
        time.sleep(3)
        gevent.sleep(3)
        self.connect_socket_servers()
        time.sleep(3)
        gevent.sleep(3)
        self.run()
        time.sleep(3)
        gevent.sleep(3)
        self.server.stop_service()

    def run(self):

        pid = os.getpid()
        self.logger.info('node %d\'s starts to run consensus on process id %d' % (self.id, pid))

        # self._prepare_bootstrap()

        while not self.ready.value:
            time.sleep(1)

        self.running.value = True

        self.run_bft()
        self.stop.value = True



def main(sid, i, B, N, f, addresses, K):
    badger = HoneyBadgerBFTNode(sid, i, B, N, f, addresses, K)
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
