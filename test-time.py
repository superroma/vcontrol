import time

timeout = 2
t0 = time.clock()
time.sleep(timeout)
t = time.clock() - t0

sec = t/timeout

print "t=", t
print "sec=", sec
