import time


def test_me(func):
    t1 = time.time()
    acc = 0
    for i in xrange(1000000):
        acc = func()
    t2 = time.time()
    print t2-t1


def main():
    test_me(time.clock)
    test_me(time.time) # way faster on unix

if __name__ == "__main__":
    main()
