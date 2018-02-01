from Globals import *
import Functions


class GBN:

    def __init__(self,sockets,E_Prb=0,P_Drp=0):
        self.window_size = 5                                                                                            #Window Size for the selective repeat
        self.udp_sock= sockets                                                                                          #UDP Socket
        self.sequence_number=0                                                                                          #Sequence number for sender and receiver
        self.base = 0                                                                                                   #Base for sender and reciver
        self.image_buffer = [None]*Window_Size                                                                          #Image buffer is used to store the date in the buffer
        self.E_Prob = E_Prb                                                                                             #Error Probability
        self.P_Drop = P_Drp                                                                                             #Packet Dropping Probabiity
        self.ack_buffer = [0]*Window_Size                                                                               #Ack Buffer is used in the client program to store the acks in the buffer.
        self.time_buffer = [0]*Window_Size
    '''This function is the basically the client's RDT function to send the file.'''

    def RdtSendPkt(self,f,addr,data,loop=0):
        while (self.base <= loop):

            if (self.sequence_number < (self.base+self.window_size)):                                                   #check for empty slots in the windows
                while ((self.sequence_number < self.base+self.window_size) and (self.sequence_number <= loop)):         #condition for GBN protocol (Sliding window)
                    if (self.sequence_number > 0):                                                                      #Initially file size is sent through sequence number 0
                        data = f.read(buffer_size-4)                                                                    #print("File Read")

                    packet = Functions.MakePkt(self.sequence_number,Functions.checksum(data),data)                      #Packet is created with the sequence number,checksum,data
                    self.image_buffer[self.sequence_number % self.window_size] = packet                                 #Buffer size of window size is created and data is added to the buffer.
                    self.time_buffer[self.sequence_number % self.window_size]=time.time()
                    self.udp_sock.sendto(packet,addr)                                                                   #sends the data
                    print ("Packet Number_Sliding Window: ",self.sequence_number)
                    self.sequence_number+=1                                                                             #sequence numbe is updated by 1
                    next_sequence= self.sequence_number + 1                                                             #Updates the next sequence number
            print ("Start_Timer")

            try:                                                                                                        #This is used for timer. if timed-out, it comes out of try loop and goes to exception.
                #if (time.time() < (self.time_buffer[self.base % self.window_size]+0.03)):
                self.udp_sock.settimeout(0.03)                                                                          #UDP Socket timer is added here, In this case 30 milliseconds is set as timer.If timed-out before operation, it goes to the timer exception.
                Ack_pkt,addr = self.udp_sock.recvfrom(buffer_size)                                                      #Client receiving the Acknowledgement packet
                self.udp_sock.settimeout(None)                                                                          #It is equivalent to sock.setblocking(0), timer is actived only for receive function which takes care of entire operation according to the FSM.
                if (Functions.Error_Condition(self.P_Drop)) and (self.sequence_number< loop-self.window_size):          #If Data_bit_error is true, it starts to Drop packet intentionally ! Basically The received packet not utilised/used. Also, ack packet is not dropped for the last window.
                    while (time.time() < (self.time_buffer[self.base % self.window_size]+0.03)):
                            pass
                    print ("############################ ACKNOWLEDGEMENT PACKET DROPPED !!! ################################\n")
                    raise OSError
                else:                                                                                                   #If Data_bit_error is False,then it refers to No-packet dropping. It goes to else loop and utilises the received packet.
                    pkt_seq_nmbr,sender_chksum,ack_data=Functions.ExtractData(Ack_pkt)                                  #Extracts the sequence number, checksum value, data from a packet

                    if (Functions.Error_Condition(self.E_Prob)) and (self.sequence_number< loop-self.window_size):      #If Data_bit_error is true, it starts to corrupt data intentionally. Also last window packets are not corrupted.
                        ack_data = Functions.Data_Corrupt(ack_data)                                                     #Function to corrupt data
                        print ("############################ ACK CORRUPTED ################################")

                    Ack_checksum = Functions.checksum(ack_data)                                                         #Finds the checksum for received acknowledgement
                    ack_data = ack_data.decode("UTF-8")                                                                 #Decodes from byte to integer for the comparison
                    ack_data_int = int(ack_data[3:len(ack_data)])                                                       #Gets the integer value alone from the ACK. for example, if string 'ACK500' is the input then the output will be integer of 500

                    '''Comparing the Acknowledgement'''

                    if ( ack_data_int >= self.base) and (Ack_checksum == sender_chksum ):                               #if packet is not corrupted and has expected sequence number
                        if ack_data_int == self.base:
                            self.base=ack_data_int +1                                                                   #self.base value is the next value to the ack value
                            print ("ACK OKAY: ",ack_data)
                            print ("BASE UPDATED: ",self.base)
                        else:
                            self.ack_buffer [pkt_seq_nmbr % self.window_size]=ack_data_int                              #Stores the value in the buffer
                            print ("Ack_Buffer: ",self.ack_buffer)

                        while self.base in self.ack_buffer:                                                             #Condition to check whether any acks are stored in the buffer.
                            self.base +=1                                                                               #updates the base
                            print("BASE UPDATED: ",self.base)
                        print ("Stop_Timer\n")

                    elif (Ack_checksum != sender_chksum ):                                                              #if packet is corrupted, it resends the packet
                        print ("Ack NOT OKAY: ",ack_data)
                        raise OSError                                                                                   #After time out it goes to exception and resends the data.
                #else:
                    #raise OSError

            except (socket.timeout,OSError):
                    print ("############################ TIMED OUT !!! ################################")
                    print ("Base: ",self.base)
                    self.time_buffer[self.base % self.window_size]=time.time()
                    self.udp_sock.sendto(self.image_buffer[self.base % self.window_size],addr)                          #Resending the corresponding packet.
                    print ("Sending the packet:{0}\n ".format(self.base))



    '''This function is the basically the Server's RDT function to receive the file.'''
    def RdtReceivePkt (self,file,loop=0):

            print ("Base: ",self.base)
            data, address = self.udp_sock.recvfrom(buffer_size)                                                         #Packet is received from client

            if (Functions.Error_Condition(self.P_Drop))and (self.sequence_number< loop-Window_Size):                    #If Data_bit_error is true, it starts to Drop packet intentionally ! by coming out of while-loop. Basically The received packet not utilised/used.Also, packet is not dropped for the last window.
              Img_Pkt = 0
              print ("############################ DATA PACKET DROPPED ################################\n")

            else:                                                                                                       #If Data_bit_error is False,then it refers to No-packet dropping. It goes to else loop and utilises the received packet.
                seq_num,checksum,Img_Pkt=Functions.ExtractData(data)                                                    #Extracts the sequence number, checksum value, data from a packet

                if (Functions.Error_Condition(self.E_Prob)) and (self.sequence_number< loop-Window_Size):               #If Data_bit_error is true, it starts to corrupt packet intentionally.Also, ack packet is not corrupted for the last window.
                    Img_Pkt = Functions.Data_Corrupt(Img_Pkt)                                                           #Function to corrupt data
                    print ("############################ Data Corrupted ################################\n")

                Rx_checksum = Functions.checksum(Img_Pkt)                                                               #Receiver Checksum in integer

                if ((Rx_checksum == checksum) and (self.sequence_number < (self.base + self.window_size))):             #if packet is not corrupted and has expected sequence number, sends Acknowledgement with sequence number  *updates sequence number for next loop
                        self.image_buffer[seq_num % self.window_size]=Img_Pkt
                        Ack = seq_num                                                                                   #sends sequence number as ACK
                        Ack = b'ACK' + str(Ack).encode("UTF-8")                                                         #Converting (Ack) from int to string and then encoding to bytes
                        Sender_Ack = Functions.MakePkt(seq_num+1,Functions.checksum(Ack),Ack)                           #Server sends Ack with expected Seq_num (Next Sequence Number), checksum, Ack
                        self.udp_sock.sendto(Sender_Ack,address)                                                        #sending the Acknowledgement packet to the client
                        print("Sequence Number: {0},Receiver_sequence: {1}, Checksum from Client: {2}, Checksum for Received File: {3}\n".format(seq_num,self.sequence_number,checksum,Rx_checksum))

                        if (seq_num == self.base):                                                                      #If inorder packet arrives, write and update the base
                            self.base = self.sequence_number  + 1
                            if (self.sequence_number) > 0:                                                              #Initial sequence number 0, used only to get the file size from the client for the loop purpose.
                                file.write(Img_Pkt)                                                                     #delivers the packet from buffer
                            self.image_buffer[self.sequence_number % self.window_size] = None
                            self.sequence_number += 1                                                                   #update sequence number to the next expected seqNum

                            while (self.image_buffer[(self.sequence_number) % self.window_size] != None):               #checks whether next packet is in the buffer,If present, writes the date and updates the base
                                print ("PACKET DELIVERED: ",self.sequence_number)
                                self.base = (self.sequence_number)+1
                                print ("BASE UPDATED    : ",self.base)
                                file.write(self.image_buffer[self.sequence_number % self.window_size])
                                self.image_buffer[self.sequence_number % self.window_size] = None
                                self.sequence_number +=1                                                                #updates the receiver sequence number.
                                print("\n")

                elif ((Rx_checksum != checksum) or (seq_num != self.sequence_number)):                                  #if packet is corrupted or has unexpected sequence number, sends Acknowledgement with previous Ackowledged sequence number. Requests client to resend the data.
                        pass                                                                                            #Do nothing
                if seq_num == 0:
                    return Img_Pkt,address                                                                              #returns data,address only for sequence number 0.

    def ReceiveFile(self,recvImgName):
        p = open(recvImgName, 'wb')                                                                                     #opening a new file to copy the transferred image

        loopTimes,address = self.RdtReceivePkt(0,0)                                                                     #Receiving the file size from client
        loop= struct.unpack("!I", loopTimes)[0]                                                                         #changing loop from byte to integer
        print ("No. of Loops to send the entire file: ", loop)
        print("write/Receiving process starting soon")                                                                  #Receiving File from Client

        while self.sequence_number <= loop:
            self.RdtReceivePkt(p,loop)                                                                                  #Calls the function RdtReceivePkt to receive the packet
        Received_File_Size = Functions.File_size(p)                                                                     #Calculating Received Image file size
        p.close()                                                                                                       #closing the file
        return Received_File_Size
