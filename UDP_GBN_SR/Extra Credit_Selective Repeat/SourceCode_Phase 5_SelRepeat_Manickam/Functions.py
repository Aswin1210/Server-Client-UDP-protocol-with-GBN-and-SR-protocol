import math
import random
import struct
from Globals import *

'''This function is used to find the file size with the help of seek function.'''
def File_size(file):
    file.seek(0,2)                                                  # moves the file pointer to the EOF
    fileSize = file.tell()                                          #gets file size
    file.seek(0,0)                                                  # moves the file pointer the the beginning of the file
    return fileSize                                                 #returns the file size in integer


'''This function is used to find how many loops the program has to run to transfer the file.'''
def looptimes(fileSize, buffer_size):
    loopTimes = (fileSize / (buffer_size-3))                        #Filesize is divided by (buffersize (1024)-3) to find the loopTimes, because 3 bytes will be the headers for the packet
    loop = math.ceil(loopTimes)                                     #Changing loopTimes to next integer
    return (loop)                                                   #returns the loop value in integer


'''This function updates the sequence number'''
def Update_Seq_num(seq_num):
    return 1-seq_num                                                #returns 1-seq_num in integer


'''This function is used to find the Checksum for the data'''
def checksum(data):
    checksum_addition=0                                             #inital checksum value is zero
    for i in range(0,len(data),2):                                  #Loop starts from 0 to len(data)-1, iterated +2 times.
        first_2bits = data[i : (i+2)]                               #taking 16 bits (2 bytes) value from 1024 bytes
        if len(first_2bits) == 1:
            two_byte_integer = struct.unpack("!B",first_2bits)[0]   #If len(data)=1 it has to be unpacked with standard size 1
        elif len(first_2bits) == 2:
            two_byte_integer = struct.unpack("!H",first_2bits)[0]   #If len(data)=2 it has to be unpacked with standard size 2
        checksum_addition = checksum_addition + two_byte_integer    #checksum addition
        while (checksum_addition>>16)==1:                           #loop goes on until condition becomes 'false'
            checksum_addition = (checksum_addition & 0xffff) + (checksum_addition >>16)  #Wrapup function
    return checksum_addition                                        #returns checksum for the data in integer


'''This function is used to find the Bit_Error has to happen or not'''
def Error_Condition(E_Prob=0):
    Data_Bit_Error = False                                          #Data_Bit_Error has been initialised as 'False'
    Random_Num = random.random()                                    #This generates a random probability value (0.00 to 1.00)
    if (Random_Num < (E_Prob/100)):                                 #converting percentage(E_Prob) to probability [(0 to 100) into (0.00 to 1.00)] in order to compare with Random_Num
        Data_Bit_Error = True                                       #If condition is 'True' it corrupts data
    return Data_Bit_Error                                           #returns Data_Bit_Error as 'True' or 'False'


'''This Function is used to corrupt the data'''
def Data_Corrupt(data):
    return (b'XX'+ data[2:])                                        #Replacing the first two bytes of data with alphabet character 'X' in order to corrupt, returns in byte


'''This Function is used to Extract Data (Sequence number,checksum, data) from packet'''
def ExtractData(packet):                                            #Extracts the packet
    dataLen=len(packet)-struct.calcsize('HH')                       #this is used to find the length of the data, (length of the sequence number (2byte) and checksum(2bytes) are fixed)
    pktFrmt="!HH"+str(dataLen)+"s"                                  #This is the packet format. example if data length is 1020 bytes then it should be "!HH1020s".
    return struct.unpack(pktFrmt,packet)                            #returns the unpacked values of packet.


'''This Function is used to make packet (Sequence number + checksum + data -> together forms a packet)'''
def MakePkt(seqNums,chksums,data):
    pktFrmt="!HH"+str(len(data))+"s"                                #This is the packet format. example if data length is 1020 bytes then it should be "!HH1021s".
    packet=struct.pack(pktFrmt,seqNums,chksums,data)                #Packs sequence number, checksum,data and forms a packet
    return packet                                                   #returns packet in bytes



