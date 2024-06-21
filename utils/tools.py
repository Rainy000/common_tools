import os
import time
from datetime import datetime



def sizeConvert(size):
    K, M, G = 1024, 1024**2, 1024**3
    if size >= G:
        return str(size / G) + 'G Bytes'
    elif size >= M:
        return str(size / M) + 'M Bytes'
    elif size >= K:
        return str(size / K) + 'K Bytes'
    else:
        return str(size) + 'Bytes'


def makedir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        # os.chmod(path, mode=0o777)


def get_current_time():
    # 获取当前世界时间
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def time_transfrom(input_time, mode=0):
    if mode == 0:
        assert isinstance(input_time, str), 'input_time must be string'
        # world-time convert to time-stamp
        temp_time = time.strptime(input_time, "%Y-%m-%d-%H-%M-%S")
        # second convert to millisecond
        time_stamp = int(time.mktime(temp_time)) * 1000
        # print('input_time = {}, time_stamp = {}'.format(input_time, time_stamp))
        return time_stamp
    elif mode == 1:
        # time-stamp convert to world-time
        if not isinstance(input_time, int):
            input_time = int(input_time)
        # millisecond convert to second
        time_array = time.localtime(input_time / 1000)
        world_time = time.strftime("%Y-%m-%d-%H-%M-%S", time_array)
        # print('input_time = {}, world_time = {}'.format(input_time, world_time))
        return world_time