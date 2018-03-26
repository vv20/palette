fifo = open("palette.pipe", mode = "rt")
while True:
    print(fifo.readline())
