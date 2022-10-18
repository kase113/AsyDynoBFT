import random
import time
import logging
from tkinter.messagebox import NO
import gevent
from gevent import monkey
from gevent.queue import Queue
from honeybadgerbft_shard.core.acrossshardcast import CRBC
 

monkey.patch_all(thread=False)

def simple_router(N, maxdelay=0.01, seed=None):
    """Builds a set of connected channels, with random delay

    :return: (receives, sends)
    """
    rnd = random.Random(seed)

    queues = [Queue() for _ in range(N)] 
    _threads = []

    def makeSend(i):
        def _send(j, o):
            delay = rnd.random() * maxdelay
            if not i % 3:
                delay *= 0
            gevent.spawn_later(delay, queues[j].put_nowait, (i,o))
        return _send

    def makeRecv(j):
        def _recv():
            (i,o) = queues[j].get()
            # print(j, (i,o))
            #print 'RECV %8s [%2d -> %2d]' % (o[0], i, j)
            return (i,o)
        return _recv

    return ([makeSend(i) for i in range(N)],
            [makeRecv(j) for j in range(N)])

### Test asynchronous across shard broadcast
def _test_across(N=4, f=1, seed=None):
    sid = 'sidA'
    # Generate threshold sig keys

    # Generate threshold enc keys

    rnd = random.Random(seed)
    #print 'SEED:', seed
    router_seed = rnd.random()
    sends, recvs = simple_router(N, seed=router_seed)

    badgers = [None] * N
    threads = [None] * N
    
    # This is an experiment parameter to specify the maximum round number 
    B = 256

    logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    

    for i in range(N):
        trans = '<[HBBFT Input %d]>' % (i+10)
        badgers[i] = CRBC(sid, i, N, f, sends[i], recvs[i], trans, logger)
        #print(sPK, sSKs[i], ePK, eSKs[i])

    for i in range(N):
        threads[i] = gevent.spawn(badgers[i].run)



    print('start the test...')
    time_start = time.time()

    #gevent.killall(threads[N-f:])
    #gevent.sleep(3)
    #for i in range(N-f, N):
    #    inputs[i].put(0)
    try:
        outs = [threads[i].get() for i in range(N)]
        print(outs)
        # Consistency check
        assert len(set(outs)) == 1
    except KeyboardInterrupt:
        gevent.killall(threads)
        raise

    time_end = time.time()
    print('complete the test...')
    print('time cost: ', time_end-time_start, 's')


def test_acrossbroad():
    _test_across()

if __name__ == '__main__':
    # test_honeybadger()
    test_acrossbroad()
