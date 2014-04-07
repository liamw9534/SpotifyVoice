"""
BluezAudio

Python wrapper around bluetooth audio command-line tools 'hcitool' and
'bluez-utils'.

Copyright (c) 2014 All Right Reserved, Liam Wickins

Please see the LICENSE file for more information.

THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY
KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
PARTICULAR PURPOSE.
"""

import sys, re, subprocess

class BluezAudioDeviceCommsError:
  """Exception raised when a device comms error occurs"""
  pass

class BluezAudio:
  """BluezAudio wrapper around command-line utilities"""

  def __init__(self):
    """Initialize object, we just get pulse audio information dictionary"""
    pass

  @staticmethod
  def __ShellCmd(cmd):
    """Shell command helper function"""
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = p.stdout.read()
    out += p.stderr.read()
    p.wait()
    #print "Cmd:", cmd, "Got output:", out
    return out

  @staticmethod
  def __Scan():
    cmd = ['sudo', 'hcitool', 'scan', '--refresh']
    return BluezAudio.__ShellCmd(cmd)

  @staticmethod
  def __GetConnectedDevices():
    cmd = ['sudo', 'hcitool', 'con']
    return BluezAudio.__ShellCmd(cmd)

  @staticmethod
  def __GetDeviceInfo(addr):
    cmd = ['sudo', 'hcitool', 'info', addr]
    return BluezAudio.__ShellCmd(cmd)

  @staticmethod
  def __ConnectDevice(addr):
    cmd = ['sudo', 'hcitool', 'cc', addr]
    return BluezAudio.__ShellCmd(cmd)

  @staticmethod
  def __AuthDevice(addr):
    cmd = ['sudo', 'hcitool', 'auth', addr]
    return BluezAudio.__ShellCmd(cmd)

  @staticmethod
  def __AudioConnect(addr):
    cmd = ['sudo', 'bluez-test-audio', 'connect', addr]
    return BluezAudio.__ShellCmd(cmd)

  @staticmethod
  def __AudioDisconnect(addr):
    cmd = ['sudo', 'bluez-test-audio', 'disconnect', addr]
    return BluezAudio.__ShellCmd(cmd)

  @staticmethod
  def __Sanitize(text):
    """Strip and remove quotes"""
    text = text.replace('"', '')
    return text.strip()

  @staticmethod
  def __ParseScanList(buf):
    """Parse info from 'hcitool scan'"""
    lines = buf.split('\n')
    devices = []
    for line in lines:
      line = line.strip()
      r = re.findall('(\w+:\w+:\w+:\w+:\w+:\w+)', line)   # E.g., Default Sink: ...
      if (r):
        devices.append(r[0])
    return devices

  def ConnectNewDevices(self):
    """Update scan list """
    out = BluezAudio.__Scan()
    candidates = BluezAudio.__ParseScanList(out)
    #print "Candidates:", candidates
    connected = []
    for i in candidates:
      if (BluezAudio.__ConnectDevice(i) == "" and
          BluezAudio.__AuthDevice(i) == "" and
          BluezAudio.__AudioConnect(i) == ""):
        connected.append(i)
    return connected

  def GetConnectedDevices(self):
    out = BluezAudio.__GetConnectedDevices()
    return BluezAudio.__ParseScanList(out)

  def DisconnectDevice(self, addr):
    if (BluezAudio.__AudioDisconnect(addr) != ""):
      raise BluezAudioDeviceCommsError
    return addr

