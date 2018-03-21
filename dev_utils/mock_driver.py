'''
A simple script to open the pipe file to test palette without the keyboard
'''
fifo = open("palette.pipe", mode="w")
print("someone is reading yay")
input()
fifo.close()
