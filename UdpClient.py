"""
UdpClient

UDP client.

Copyright (c) 2014 All Right Reserved, Liam Wickins

Please see the LICENSE file for more information.

THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY 
KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
PARTICULAR PURPOSE.
"""

import socket

class UdpClient():

  def __init__(self, dest="127.0.0.1", port=5005):
    self.sock = socket.socket(socket.AF_INET,    # Internet
                              socket.SOCK_DGRAM) # UDP
    self.dest = dest
    self.port = port

  def SendMessage(self, msg):
    self.sock.sendto(msg, (self.dest, self.port))

  def RecvMessage(self, maxLen=2048):
    data, addr = self.sock.recvfrom(maxLen)
    return data, addr

