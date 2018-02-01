from Globals import *                                               #Common variables
import Functions                                                    #Functions like checksum, filesize, bit error, etc.
import Send_Receive                                                 #To Send/Receive function


sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)              #Socket with IPV4, UDP
f = open('Lion.jpg','rb')                                           #opening a new file, this file will be transferred to the server

#The Probability can be set here for packet corruption or dropping (0-99)
Error_Prob = 0
Packt_drop = 0

sender = Send_Receive.GBN(sock,Error_Prob,Packt_drop)

fileSize = Functions.File_size(f)                                   #File size is calculated
loop = Functions.looptimes(fileSize,buffer_size)                    #finding the loop value
loop_bytes = struct.pack("!I", loop)                                #change loop from integer to byte inorder to send data from client to server
print("File has been Extracted \nFile size: {0} \nNo. of Loops to send the entire file: {1}".format(fileSize,loop))
print('Client File Transfer Starts...')


sender.RdtSendPkt(f,addr,loop_bytes,loop) #calls the function rdt_send to send the packet

f.close()                                                           #File closed
sock.close()                                                        #Socket Closed

end = time.time()                                                   #Gets the End time
Elapsed_time = end - start                                          #Gets the elapsed time
print ("Client: File Sent\nFile size sent to server: {0}\nTime taken in Seconds:{1}s\n".format(fileSize,Elapsed_time))


