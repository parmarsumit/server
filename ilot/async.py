'''
Created on 22 sept. 2015

@author: biodigitals
'''
from ilot.core.models import Item, DataPath
from copy import deepcopy
#from multiprocessing import Pool, Lock
import multiprocessing, logging
#from multiprocessing.pool import ThreadPool
from threading import Thread
import time
import traceback
from ilot.core.models import Translation
try:
    from multiprocessing import Process
except:
    from multiprocessing.process import Process

#from multiprocessing.process import Process
# thinking about threading/multiprocessing ...
# http://stackoverflow.com/questions/8068945/django-long-running-asynchronous-tasks-with-threads-processing
logger = multiprocessing.log_to_stderr()
logger.setLevel(logging.INFO)


class AsyncDispatcher(Thread):

    # offset at start
    istart = 0

    # cycle expressed in seconds
    icycle = 1

    # second by second count ..
    iclock = 0


    pool_size = 4

    cron_settings = []
    cron_execution = {}

    results = []
    _instance = None
    __running__ = False

    spawned = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = AsyncDispatcher()
            cls._instance.start()
        return cls._instance

    def __init__(self, *args, **kwargs):
        """
        Init a pool of thread or process
        """
        super(AsyncDispatcher, self).__init__(*args, **kwargs)

    def spawn(self, uid, function, fargs=[], fkwargs={}):
        """
        Execute the function now in an asynchronous process/thread
        """
        logger.debug('Spawning execution of %s' % function)
        #print('SPAWN', uid, '-> ', function)
        p = Thread(target=function, args=fargs, kwargs=fkwargs)
        if not uid in self.spawned:
            self.spawned[uid] = []
        self.spawned[uid].append(p)
        p.start()
        return p

    def join(self, timeout=None):
        """
        Join and vanish the running thread
        """
        self.__running__ = False
        #self.pool.close()
        #self.pool.join()
        super(AsyncDispatcher, self).join(timeout=timeout)

    def terminate(self, uid):
        for p in self.spawned[uid]:
            try:
                p.terminate()
                print('TERMINATE', uid)
            except:
                traceback.print_exc()
