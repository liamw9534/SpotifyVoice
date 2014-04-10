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

from __future__ import print_function
import sys, re, subprocess

def Debug(*objs):
  print("BluezAudio:", *objs, file=sys.stderr)

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
    #Debug("Cmd:", cmd, "Got output:", out)
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
  def __DeviceCreate(addr):
    cmd = ['sudo', 'bluez-test-device', 'create', addr]
    return BluezAudio.__ShellCmd(cmd)

  @staticmethod
  def __DeviceRemove(addr):
    cmd = ['sudo', 'bluez-test-device', 'remove', addr]
    return BluezAudio.__ShellCmd(cmd)

  @staticmethod
  def __DeviceList():
    cmd = ['sudo', 'bluez-test-device', 'list']
    return BluezAudio.__ShellCmd(cmd)

  @staticmethod
  def __ParseScanList(buf):
    """Parse info from 'hcitool scan'"""
    lines = buf.split('\n')
    devices = []
    for line in lines:
      line = line.strip()
      r = re.findall('(\w+:\w+:\w+:\w+:\w+:\w+)', line) # xx:xx:xx:xx:xx:xx
      if (r):
        devices.append(r[0])
    return devices

  def ScanNewDevices(self):
    """Scan for new devices"""
    out = BluezAudio.__Scan()
    return BluezAudio.__ParseScanList(out)

  def GetRegisteredDevices(self):
    """Retrieve list of all registered devices"""
    out = BluezAudio.__DeviceList()
    return BluezAudio.__ParseScanList(out)

  def ConnectDevices(self, candidates):
    """Connect devices"""
    already = self.GetConnectedDevices()
    connected = []
    for i in candidates:
      if (i not in already):
        BluezAudio.__DeviceCreate(i)
        if (BluezAudio.__ConnectDevice(i) == "" and
            BluezAudio.__AuthDevice(i) == "" and
            BluezAudio.__AudioConnect(i) == ""):
          connected.append(i)
        #else:
        #  BluezAudio.__DeviceRemove(i)
    return connected

  def GetConnectedDevices(self):
    out = BluezAudio.__GetConnectedDevices()
    return list(set(BluezAudio.__ParseScanList(out)))

  def DisconnectDevice(self, addr):
    op = BluezAudio.__AudioDisconnect(addr)
    #op += BluezAudio.__DeviceRemove(addr)
    if (op != ""):
      raise BluezAudioDeviceCommsError
    return addr

