from ast import parse
from curses import meta
from gevent import monkey; monkey.patch_all(thread=False)
 
import time
import random
import traceback
from typing import List, Callable
from gevent import Greenlet
from myexperiements.sockettest.dumbo_node import DumboBFTNode
from myexperiements.sockettest.bdt_node import BdtBFTNode
from myexperiements.sockettest.rbcbdt_node import RbcBdtBFTNode
from myexperiements.sockettest.hbbft_node import HoneyBadgerBFTNode
from myexperiements.sockettest.rotatinghotstuff_node import RotatingHotstuffBFTNode
from myexperiements.sockettest.hbbft_node_shard import HoneyBadgerBFTNode_shard
from myexperiements.sockettest.ng_k_s_node import NGSNode
from myexperiements.sockettest.dl_bmr_sockets_node import DL2Node
from myexperiements.sockettest.hbbft_node_shard_new import HoneyBadgerBFTNode_shard_new
from network_new.socket_server import NetworkServer
from network_new.socket_client import NetworkClient
from multiprocessing import Value as mpValue, Queue as mpQueue
from ctypes import c_bool
 
 
def instantiate_bft_node(sid, i, B, N, f, per, K, R, MR, BP, S, T, bft_from_server: Callable, bft_to_client: Callable, ready: mpValue,
                         stop: mpValue, protocol="hbbft_shard_new", mute=False, F=100, debug=False, omitfast=False, bft_running: mpValue=mpValue(c_bool, False), countpoint=0):
    bft = None
    if protocol == 'dumbo':
        bft = DumboBFTNode(sid, i, B, N, f, bft_from_server, bft_to_client, ready, stop, K, mute=mute, debug=debug, bft_running=bft_running)
    elif protocol == "bdt":
        bft = BdtBFTNode(sid, i, S, T, B, F, N, f, bft_from_server, bft_to_client, ready, stop, K, mute=mute, omitfast=omitfast, bft_running=bft_running)
    elif protocol == "hotstuff":
        bft = RotatingHotstuffBFTNode(sid, i, S, T, B, F, N, f, bft_from_server, bft_to_client, ready, stop, K, mute=mute, omitfast=omitfast, bft_running=bft_running)
    elif protocol == "rbc-bdt":
        bft = RbcBdtBFTNode(sid, i, S, T, B, F, N, f, bft_from_server, bft_to_client, ready, stop, K, mute=mute, omitfast=omitfast, network=bft_running)
    elif protocol == "hbbft":
        bft = HoneyBadgerBFTNode(sid, i, B, N, f, bft_from_server, bft_to_client, ready, stop, K, mute=mute, debug=debug, bft_running=bft_running)
    # elif protocol == "hbbft_shard":
    #     bft = HoneyBadgerBFTNode_shard(sid, i, B, N, f, bft_from_server, bft_to_client, ready, stop, K, R, MR, mute=mute, debug=debug, bft_running=bft_running)
    elif protocol == "hbbft_shard_new":
        bft = HoneyBadgerBFTNode_shard_new(sid, i, B, N, f, per, bft_from_server, bft_to_client, ready, stop, K, R, MR, BP, mute=mute, debug=debug, bft_running=bft_running)
    elif protocol == "dumbong":
        bft = NGSNode(sid, i, S, B, F, N, f, bft_from_server, bft_to_client, ready, stop, mute=mute, countpoint=countpoint)
    else:
        print("Only support dumbo or mule or stable-hs or rotating-hs")
    return bft


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
    parser.add_argument('--R', metavar='R', required=False,
                        help='amount of shard', type=int, default=1)
    parser.add_argument('--MR', metavar='MR', required=False,
                        help='amount of shard', type=int, default=1)
    parser.add_argument('--per', metavar='per', type=float,required=False,
                        help='the per of across trand,from 0 to 1',default=0.1)
    parser.add_argument('--S', metavar='S', required=False,
                        help='slots to execute', type=int, default=50)
    parser.add_argument('--T', metavar='T', required=False,
                        help='fast path timeout', type=float, default=1)
    parser.add_argument('--P', metavar='P', required=False,
                        help='protocol to execute', type=str, default="hbbft_shard_new")
    parser.add_argument('--M', metavar='M', required=False,
                        help='whether to mute a third of nodes', type=bool, default=False)
    parser.add_argument('--F', metavar='F', required=False,
                        help='batch size of fallback path', type=int, default=100)
    parser.add_argument('--D', metavar='D', required=False,
                        help='whether to debug mode', type=bool, default=False)
    parser.add_argument('--O', metavar='O', required=False,
                        help='whether to omit the fast path', type=bool, default=False)
    parser.add_argument('--BP', metavar='BP',required=False,
                        help='batch processing', type=bool, default=True)
    parser.add_argument('--L', metavar='L', required=False,
                        help='amount of all record logger', type=int, default=12)
    args = parser.parse_args()

    # Some parameters
    sid = args.sid
    i = args.id
    N = args.N 
    f = args.f
    B = args.B
    K = args.K
    R = args.R
    MR = args.MR
    S = args.S
    T = args.T
    P = args.P
    M = args.M
    F = args.F
    D = args.D
    O = args.O
    per = args.per
    BP = args.BP
    L = args.L

    shard = int(N/MR) # amount of each shard


    # Random generator
    rnd = random.Random(sid)

    # Nodes list
    # host_file = 'hosts-' + str(R) + '.config'
    addresses = [None] * N
    try:
        with open('hosts.config', 'r') as hosts:
            for line in hosts:
                params = line.split()
                pid = int(params[0])
                priv_ip = params[1]
                pub_ip = params[2]
                port = int(params[3])
                # print(pid, ip, port)
                if (pid) not in range(N):
                    continue
                if pid == i:
                    my_address = (priv_ip, port)
                addresses[pid] = (pub_ip, port)
        assert all([node is not None for node in addresses])
        print("my_addresses:", my_address)
        print("addresses:", addresses)
        print("hosts.config is correctly read")

        # bft_from_server, server_to_bft = mpPipe(duplex=True)
        # client_from_bft, bft_to_client = mpPipe(duplex=True)

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

        # net_server = NetworkServer(my_address[1], my_address[0], i, R, N, addresses, server_to_bft, server_ready, stop)
        # net_client = NetworkClient(my_address[1], my_address[0], i, R, N, addresses, client_from_bft, client_ready, stop, bft_running, dynamic=False)
        net_server = NetworkServer(my_address[1], my_address[0], i, R, shard, addresses, server_to_bft, server_ready, stop)
        net_client = NetworkClient(my_address[1], my_address[0], i, R, L, shard, addresses, client_from_bft, client_ready, stop, bft_running, dynamic=False)
        bft = instantiate_bft_node(sid, i, B, N, f, per, K, R, MR, BP, S, T, bft_from_server, bft_to_client, net_ready, stop, P, M, F, D, O, bft_running)
        #print(O) 
        net_server.start() 
        net_client.start()

        while not client_ready.value or not server_ready.value:
            time.sleep(1)
            print("waiting for network ready...")
            print("this is the client", client_ready.value, server_ready.value)
 
        with net_ready.get_lock():
            net_ready.value = True

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
