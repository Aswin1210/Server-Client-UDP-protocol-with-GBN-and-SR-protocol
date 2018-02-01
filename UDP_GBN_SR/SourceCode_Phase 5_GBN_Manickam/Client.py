from Globals import *                                               #Common variables
import Functions                                                    #Functions like checksum, filesize, bit error, etc.
import Send_Receive                                                 #To Send/Receive function

'''To corrupt data packet, Set value from 0 - 99 in E_prob'''
E_Prob = 0                                                          #E_prob is the error probability and can be set from 0-99
P_Drop = 0                                                          #P_Drop is the packet dropping probability and can be set from 0-99


Time_buffer=[None]*Window_Size                                      #Time_Buffer stores the start time for the packets
print ("window_Size: ",Window_Size)                                 #prints the window size
image_buffer=[None]*Window_Size                                     #Stores the data in the buffer
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)              #Socket with IPV4, UDP
f = open('Lion.jpg','rb')                                           #opening a new file, this file will be transferred to the server

fileSize = Functions.File_size(f)                                   #File size is calculated

loop = Functions.looptimes(fileSize,buffer_size)                    #finding the loop value
loop_bytes = struct.pack("!I", loop)                                #change loop from integer to byte inorder to send data from client to server
print("File has been Extracted \nFile size: {0} \nNo. of Loops to send the entire file: {1}".format(fileSize,loop))
seq_nmbr = 0                                                        #Sequence Number is set to 0 initially
base=0                                                              #Here base is set to 0
print('Client File Transfer Starts...')

while (base <= loop):                                               #Loop runs until sequence number is equal to loop value. Sequence number starts from 1.
    seq_nmbr,base = Send_Receive.RdtSendPkt(f,sock,addr,seq_nmbr,loop_bytes,E_Prob,P_Drop,Window_Size,base,loop,image_buffer,Time_buffer) #calls the function rdt_send to send the packet

f.close()                                                           #File closed
sock.close()                                                        #Socket Closed

end = time.time()                                                   #Gets the End time
Elapsed_time = end - start                                          #Gets the elapsed time
print ("Client: File Sent\nFile size sent to server: {0}\nTime taken in Seconds:{1}s\n".format(fileSize,Elapsed_time))


