#List = [0,0,2,3,0,5,6,7,8,0,0,0]

'''
base_copy = self.base
pointer = self.base

while (pointer < (base_copy + self.window_size)):
    print ("sequence: ",self.sequence_number)
    self.base = self.sequence_number  + 1
    file.write(self.image_buffer[self.sequence_number % self.window_size])
    pointer +=1
    '''




'''base= 1
while base in List:
    base = base +1
    print (base)'''


'''if List[0] == List[1]:
    print ("True")
else:
    print ("False")'''


import signal
from Globals import*
from threading import Timer


sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind(addr)
print("Hey Hey Started")



try:
  Timer(1).start()
  sock.recv(1024)


except OSError:
  print ("Timed Out")



