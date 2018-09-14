from botflow import *
from botflow.function import SpeedLimit
from botflow.config import config
import logging
logger=logging.getLogger("botflow.queue")
logger.setLevel(logging.DEBUG)
sum=0

def sum_up(i):

    global sum
    sum+=i
    return i


def test_sum():
    target=config.default_queue_max_size*3
    Bot.reset()
    Pipe(
        range(target),
        sum_up,
    )


    Bot.run()
    print(sum)

    Bot.debug_print()
    to_sum=(0+target-1)*target/2
    assert sum == to_sum


def test_speed():
    limited_speed=20

    import datetime
    start=datetime.datetime.now()
    count=0
    speed_record=[]
    def speed_rate(i):
        nonlocal count,speed_record,start
        count+=1
        if count>=limited_speed:
            end=datetime.datetime.now()
            s=(end-start).total_seconds()
            speed_record.append(count/s)
            count=0
            start=datetime.datetime.now()


    Bot.reset()
    Pipe(
        range(limited_speed*11),
        SpeedLimit(limited_speed),
        speed_rate

    )

    Bot.run()
    ok_count=0
    for s in speed_record:
        up=limited_speed*1.1
        low=limited_speed *0.9
        if s>low and s<up:
            ok_count+=1
    assert ok_count>=7

        # assert s < up
        # assert s > low