from Globals import *
import Functions
import time


'''This function is the basically the client's RDT function to send the file.'''

def RdtSendPkt(f,udp_sock,addr,seq_nmbr,data,E_Prob=0,P_Drop=0,window_size=0,base=0,loop=0,image_buffer=[],time_buffer=[]):

    if (seq_nmbr < (base+window_size)):                                                                #check for empty slots in the windows
        while ((seq_nmbr < base+window_size) and (seq_nmbr <= loop)):                                  #condition for GBN protocol (Sliding window)
            if (seq_nmbr > 0):                                                                         #Initially file size is sent through sequence number 0
                data = f.read(buffer_size-4)                                                           #print("File Read")
            packet = Functions.MakePkt(seq_nmbr,Functions.checksum(data),data)                         #Packet is created with the sequence number,checksum,data
            image_buffer[seq_nmbr % window_size] = packet                                              #Buffer size of window size is created and data is added to the buffer.
            udp_sock.sendto(packet,addr)                                                               #sends the data
            print ("Packet Number_Sliding Window: ",seq_nmbr)
            time_buffer[seq_nmbr % window_size] = time.time()                                          #Time Buffer stores the start time for each packet
            seq_nmbr+=1                                                                                #sequence numbe is updated by 1
        print ("Start_Timer")
    try:                                                                                               #This is used for timer. if timed-out, it comes out of try loop and goes to exception.
        udp_sock.settimeout(0.03)                                                                      #UDP Socket timer is added here, In this case 30 milliseconds is set as timer.If timed-out before operation, it goes to the timer exception.
        Ack_pkt,addr = udp_sock.recvfrom(buffer_size)                                                  #Client receiving the Acknowledgement packet
        udp_sock.settimeout(None)                                                                      #It is equivalent to sock.setblocking(0), timer is actived only for receive function which takes care of entire operation according to the FSM.

        if (Functions.Error_Condition(P_Drop)) and (seq_nmbr< loop-window_size):                       #If Data_bit_error is true, it starts to Drop packet intentionally ! Basically The received packet not utilised/used. Also, ack packet is not dropped for the last window.
            while(time.time() < (time_buffer[base % window_size] + 0.03)):                             #As per the FSM, We need to time-out. Here we are using while loop. If current-time is less than the timer-time, it runs infinite loop with no operations. After timer-time, condition fails and loop comes out
                pass
            print ("############################ ACKNOWLEDGEMENT PACKET DROPPED !!! ################################\n")
            #raise OSError                                                                             #raise OSError
        else:                                                                                          #If Data_bit_error is False,then it refers to No-packet dropping. It goes to else loop and utilises the received packet.
            pkt_seq_nmbr,sender_chksum,ack_data=Functions.ExtractData(Ack_pkt)                         #Extracts the sequence number, checksum value, data from a packet

            if (Functions.Error_Condition(E_Prob)) and (seq_nmbr< loop-window_size):                   #If Data_bit_error is true, it starts to corrupt data intentionally. Also last window packets are not corrupted.
                ack_data = Functions.Data_Corrupt(ack_data)                                            #Function to corrupt data
                print ("############################ ACK CORRUPTED ################################")

            Ack_checksum = Functions.checksum(ack_data)                                                #Finds the checksum for received acknowledgement
            ack_data = ack_data.decode("UTF-8")                                                        #Decodes from byte to integer for the comparison
            ack_data_int = int(ack_data[3:len(ack_data)])                                              #Gets the integer value alone from the ACK. for example, if string 'ACK500' is the input then the output will be integer of 500
            #print ("Ack from Server: ",ack_data_int)

            '''Comparing Acknowledgement'''
            if ( ack_data_int >= base) and (Ack_checksum == sender_chksum ):                           #if packet is not corrupted and has expected sequence number
                base=ack_data_int +1                                                                   #base value is the next value to the ack value
                print ("ACK OKAY: ",ack_data)
                print ("Updated Base: ",base)
                print ("Stop Timer\n")

            elif (Ack_checksum != sender_chksum ):                                                     #if packet is corrupted, it resends the packet
                print ("Ack NOT OKAY:{} \n".format(ack_data))                                          #Do Nothing

    except (socket.timeout,OSError):
        print ("############################ SOCKET TIMED OUT !!! ################################")
        print ("Base: ",base)
        for i in range (base,seq_nmbr):                                                                #Resends the entire packet
            time_buffer[i % window_size] = time.time()                                                 #Restarting the timer, updating start time for the packet
            udp_sock.sendto(image_buffer[i % window_size],addr)                                        #Sending the data
            print ("Sending the packet: ",i)
        print ("\n")
    return seq_nmbr,base                                                                                   #returns updated sequence number, base value



'''This function is the basically the Server's RDT function to receive the file.'''
def RdtReceivePkt (sock,buffer_size,Rx_seq_num,E_Prob=0,P_Drop=0,loop=0,Window_Size = 0):
    receive_successful = 0                                                                                 #Receive_sucessful is set to '0' initially

    while (not(receive_successful)):                                                                       #loop goes on until condition becomes 'false'

        data, address = sock.recvfrom(buffer_size)                                                         #Packet is received from client

        if (Functions.Error_Condition(P_Drop))and (Rx_seq_num< loop-Window_Size):                          #If Data_bit_error is true, it starts to Drop packet intentionally ! by coming out of while-loop. Basically The received packet not utilised/used.Also, packet is not dropped for the last window.
          print ("############################ DATA PACKET DROPPED ################################\n")
          receive_successful=0                                                                             #Comes out of current loop and starts again since condition will be while(1).

        else:                                                                                              #If Data_bit_error is False,then it refers to No-packet dropping. It goes to else loop and utilises the received packet.
            seq_num,checksum,Img_Pkt=Functions.ExtractData(data)                                           #Extracts the sequence number, checksum value, data from a packet

            if (Functions.Error_Condition(E_Prob)) and (Rx_seq_num< loop-Window_Size):                     #If Data_bit_error is true, it starts to corrupt packet intentionally.Also, ack packet is not corrupted for the last window.
                Img_Pkt = Functions.Data_Corrupt(Img_Pkt)                                                  #Function to corrupt data
                print ("############################ Data Corrupted ################################\n")


            Rx_checksum = Functions.checksum(Img_Pkt)                                                      #Receiver Checksum in integer

            if ((Rx_checksum == checksum) and (seq_num == Rx_seq_num)):                                    #if packet is not corrupted and has expected sequence number, sends Acknowledgement with sequence number  *updates sequence number for next loop
                    Ack = Rx_seq_num                                                                       #sends sequence number as ACK
                    Ack = b'ACK' + str(Ack).encode("UTF-8")                                                #Converting (Ack) from int to string and then encoding to bytes
                    Sender_Ack = Functions.MakePkt(seq_num+1,Functions.checksum(Ack),Ack)                  #Server sends Ack with expected Seq_num (Next Sequence Number), checksum, Ack
                    print("Sequence Number: {0},Receiver_sequence: {1}, Checksum from Client: {2}, Checksum for Received File: {3}\n".format(seq_num,Rx_seq_num,checksum,Rx_checksum))
                    Rx_seq_num = 1 + seq_num                                                               #update sequence number to the next expected seqNum
                    receive_successful = 1                                                                 #Comes out of while loop

            elif ((Rx_checksum != checksum) or (seq_num != Rx_seq_num)):                                   #if packet is corrupted or has unexpected sequence number, sends Acknowledgement with previous Ackowledged sequence number. Requests client to resend the data.
                    Ack = Rx_seq_num - 1                                                                   #last acked sequence numvber
                    Ack = b'ACK' + str(Ack).encode("UTF-8")                                                #Converting (Ack) from int to string and then encoding to bytes
                    Sender_Ack = Functions.MakePkt(Rx_seq_num,Functions.checksum(Ack),Ack)                 #Server sends Ack with Seq_num, checksum, Ack
                    #print("Sequence Number: {0},Receiver_sequence: {1}\n".format(seq_num,Rx_seq_num))
                    receive_successful = 0                                                                 #Loop continues until satisfies condition
            sock.sendto(Sender_Ack,address)                                                                #sending the Acknowledgement packet to the client

    return Img_Pkt,address,Rx_seq_num                                                                      #returns data,address,updated sequence number

