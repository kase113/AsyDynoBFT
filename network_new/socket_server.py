from gevent import monkey; monkey.patch_all(thread=False)

from gevent.server import StreamServer
import pickle
from typing import Callable
import os
import logging
import traceback
from multiprocessing import Value as mpValue, Process

 

# Network node class: deal with socket communications
class NetworkServer (Process):
 
    SEP = '\r\nSEP\r\nSEP\r\nSEP\r\n'.encode('utf-8')

    def __init__(self, port: int, my_ip: str, id: int, R: int, shard: int, addresses_list: list, server_to_bft: Callable, server_ready: mpValue, stop: mpValue):
 
        self.server_to_bft = server_to_bft
        self.ready = server_ready 
        self.stop = stop
        self.addresses_list = addresses_list
        self.N = len(self.addresses_list)
        self.ip = my_ip 
        self.port = port  
        # self.id = id % self.N
        self.id = id
        self.startpoint = int(R * shard)
        self.end = int((R+1) * shard)

        self.is_in_sock_connected = [False] * self.N
        self.socks = [None for _ in self.addresses_list]
        super().__init__()

    def _listen_and_recv_forever(self):
        pid = os.getpid()
        self.logger.info('node %d\'s socket server starts to listen ingoing connections on process id %d' % (self.id, pid))
        print("my IP is " + self.ip)
 
        def _handler(sock, address):
            #jid = self._address_to_id(address)
            jid = self._address_to_id_new(address)
            self.logger.info('hava recv jid %s' % (str(jid)))
            buf = b''
            try:
                while not self.stop.value:
                    buf += sock.recv(2_000_000)
                    self.logger.info('hava running recv')
                    tmp = buf.split(self.SEP, 1)
                    while len(tmp) == 2:
                        buf = tmp[1]
                        data = tmp[0] 
                        if data != '' and data:
                            (j, o) = (jid, pickle.loads(data))
                            # assert j in range(self.N)
                            self.server_to_bft((j, o))
                            self.logger.info('recv' + str((j, o)))
                            # print('server recv' + str((j, o)))
                        else:
                            self.logger.error('syntax error messages')
                            raise ValueError
                        tmp = buf.split(self.SEP, 1)
                    #gevent.sleep(0)
            except Exception as e:
                self.logger.error(str((e, traceback.print_exc())))

        self.streamServer = StreamServer((self.ip, self.port), _handler)
        self.streamServer.serve_forever()


    def run(self):
        pid = os.getpid()
        self.logger = self._set_server_logger(self.id)
        self.logger.info('node id %d is running on pid %d' % (self.id, pid))
        print(self.id, pid)
        with self.ready.get_lock():
            self.ready.value = True
        self._listen_and_recv_forever()

    def _address_to_id(self, address: tuple):
        for i in range(self.N):
            if address[0] != '127.0.0.1' and address[0] == self.addresses_list[i][0]:
                return i
        # return int((address[1] - 10000) / 200)
        return int((address[1] - 10000) / 500)
    def _address_to_id_new(self, address: tuple):
        return int((address[1] - 20000) / 500)

    def _set_server_logger(self, id: int):
        logger = logging.getLogger("node-" + str(id))
        logger.setLevel(logging.DEBUG)
        # logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s %(filename)s [line:%(lineno)d] %(funcName)s %(levelname)s %(message)s ')
        if 'log' not in os.listdir(os.getcwd()):
            os.mkdir(os.getcwd() + '/log')
        full_path = os.path.realpath(os.getcwd()) + '/log/' + "node-net-server-" + str(id) + ".log"
        file_handler = logging.FileHandler(full_path)
        file_handler.setFormatter(formatter) 
        logger.addHandler(file_handler)
        return logger
