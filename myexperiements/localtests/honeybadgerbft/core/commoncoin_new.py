from gevent import monkey; monkey.patch_all(thread=False) 

import logging
from crypto.threshsig.boldyreva import g12deserialize, g12serialize
from collections import defaultdict
from gevent import Greenlet
from gevent.queue import Queue
import hashlib


logger = logging.getLogger(__name__)


class CommonCoinFailureException(Exception):
    """Raised for common coin failures."""
    pass





def shared_coin(sid, pid, N, f, PK, SK, broadcast, receive, single_bit=True, logger=None):
    """A shared coin based on threshold signatures

    :param sid: a unique instance id
    :param pid: my id number
    :param N: number of parties
    :param f: fault tolerance, :math:`f+1` shares needed to get the coin
    :param PK: ``boldyreva.TBLSPublicKey``
    :param SK: ``boldyreva.TBLSPrivateKey``
    :param broadcast: broadcast channel
    :param receive: receive channel
    :param single_bit: is the output coin a single bit or not ?
    :return: a function ``getCoin()``, where ``getCoin(r)`` blocks
    """

    #greenletPacker(Greenlet(_recv), 'shared_coin', (pid, N, f, broadcast, receive)).start()

    def getCoin(round):
        """Gets a coin.

        :param round: the epoch/round.
        :returns: a coin.

        """
        import secrets
        random_bytes = secrets.token_hex(128 // 2 + 1)
        random_number = int(random_bytes,16)
        new_coin = random_number % 2
        
        return new_coin
        

    return getCoin
