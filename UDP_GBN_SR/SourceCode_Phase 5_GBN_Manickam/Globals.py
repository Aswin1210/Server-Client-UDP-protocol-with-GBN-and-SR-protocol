import socket
import struct
import time

start = time.time()                    #This is used to find the start time of the program, elapsed time can be found by end time - start time

'''Importing IP address, port number, Buffersize'''
UDP_IP = "localhost"                   #Localhost is the IP address of this machine
UDP_PORT = 5005                        #Port Number is assigned to 5005
buffer_size = 1024                     #Buffer_size is set to 1024. packet size is 1024 with sequence number 1 byte, checksum 2 bytes, data 1021 bytes.
addr = (UDP_IP,UDP_PORT)

'''For the GBN Sliding window, set the Window Size value'''
Window_Size = 5                        #Set the window size for the Go-Back-N protocol. This window size is only for the client program for the sliding window. Server side window size is always 1. client window size also included in server program ONLY to avoid intentional packet corrupt/drop for the last window.
