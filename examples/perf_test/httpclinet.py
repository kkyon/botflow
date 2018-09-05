from databot import *
import datetime
import time

count=0
def check_and_count(i):
    global count
    count+=1


# docker run -p 80:80 kennethreitz/httpbin
Pipe(
    range(10000),
    "http://127.0.0.1:80/get",
    HttpLoader(),
    check_and_count


)

start = datetime.datetime.now()
BotFlow.run()

end = datetime.datetime.now()

print(end-start)
print("count %d",count)

time.sleep(100)