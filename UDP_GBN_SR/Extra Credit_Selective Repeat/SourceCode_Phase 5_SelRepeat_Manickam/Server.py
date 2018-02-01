from Globals import*                                                        #Common variables
import Send_Receive                                                         #To Send/Receive function
import Functions                                                            #Functions like checksum, filesize, bit error, etc.


sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)                      #Socket with IPV4, UDP
sock.bind(addr)                                                             #Binding the socket
print("Server Started")

#The Probability can be set here for packet corruption or dropping (0-99)
Error_Prob = 0
Packt_drop = 0

receiver = Send_Receive.GBN(sock,Error_Prob,Packt_drop)


Received_File_Size =receiver.ReceiveFile("Received_Image.jpg")         #writes/stores the received data to a file,File Received from Client at the end of Loop
sock.close()                                                                #closing the socket

end = time.time()                                                           #Finding the end-time
Elapsed_time = end -  start                                                 #Elapsed time
print ("Server: File Received\nReceived File size: {0}\nTime taken in Seconds: {1}s".format(Received_File_Size,Elapsed_time))



