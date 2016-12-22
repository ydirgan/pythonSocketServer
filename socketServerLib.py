#https://www.python.org/dev/peps/pep-0263/
# coding: utf-8
################################################################################################################         
## PyMusicServer Library (originated from YADlib)                                                             ##         
## AUTHOR Alejandro Dirgan                                                                                    ##
## VERSION 1.0                                                                                                ##                     
## DATE Jan 2016                                                                                              ##
################################################################################################################         


try:
   from evdev import InputDevice
except: 
   pass
try:
   from select import select
except: 
   print 'select lib not found'
try:
   from subprocess import STDOUT, PIPE, Popen
except: 
   print 'subprocess lib not found'
try:
   from sys import exit
except: 
   print 'sys lib not found'
try:
   import signal
except: 
   print 'signal lib not found'
try:
   from time import sleep, strptime, strftime
except: 
   print 'time lib not found'
try:
   import picamera
except: 
   pass
   #print 'picamera lib not found'
try:
   import os
except: 
   print 'os lib not found'
try:
   from datetime import timedelta, datetime
except: 
   print 'datetime lib not found'
try:
   import socket
except: 
   print 'socket lib not found'
try:
   from threading import Thread, Lock
except: 
   print 'Thread lib not found'

try:
   from inspect import stack
except: 
   print 'inspect lib not found'
try:
   import imaplib
except: 
   print 'imaplib lib not found'
try:
   from email import email
except: 
   print 'email lib not found'
try:
   from email.parser import HeaderParser
except: 
   print 'HeaderParser lib not found'
try:
   import smtplib
except: 
   print 'smtplib lib not found'
try:
   from shutil import rmtree
except: 
   print 'shutil lib not found'
try:
   from glob import glob
except: 
   print 'glob lib not found'
try:
   import sqlite3
except: 
   print 'sqlite3 lib not found'
try:
   from urllib2 import urlopen
except: 
   print 'urllib2 lib not found'
try:
   from collections import OrderedDict
except: 
   print 'collections lib not found'
try:
	import thread
except: 
   print 'thread lib not found'
try:
	from random import randint, seed
except: 
   print 'random lib not found'   
try:
   import RPi.GPIO as GPIO
except: 
   print 'GPIO lib not found'   
try:
   import traceback
except: 
   print 'traceback lib not found'   
try:
   import urllib
except: 
   print 'urllib not found'   
try:
   import json
except: 
   print 'json not found'   

try:
   import unicodedata
except: 
   print 'unicodedata not found'   

#################################################
class ledHandle():
#################################################
#------------------------------------------------   
	def __init__(self, pin=23):
#------------------------------------------------   
		self.pin = pin
		self.stop = False
		self.sequence = 'no sequence'
		self.lock = Lock()
		self.init()

#------------------------------------------------   
	def init(self):
#------------------------------------------------   
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		GPIO.setup(self.pin, GPIO.OUT)
		self.led = GPIO.PWM(self.pin, 100)

#------------------------------------------------   
	def getSequence(self):
#------------------------------------------------   
		return self.sequence

#------------------------------------------------   
	def dimmed(self, delay=0.005):
#------------------------------------------------   
		self.lock.acquire()
		self.led.start(0)
		self.sequence = 'dimmed'
		while not self.stop:
			for i in range(0,100):
				if self.stop: break
				self.led.ChangeDutyCycle(i)
				sleep(delay)
			for i in range(100,-1,-1):
				if self.stop: break
				self.led.ChangeDutyCycle(i) 
				sleep(delay)
		self.led.stop()
		self.sequence = 'no sequence'
		self.lock.release()
		self.stop = False

#------------------------------------------------   
	def sequence2(self, delay1=0.5, delay2=0.7):
#------------------------------------------------   
		self.lock.acquire()
		delay = 0.5
		self.sequence = 'sequence2'
		while not self.stop:
			if self.stop: break
			GPIO.output(self.pin, 1) 
			sleep(delay1)
			if self.stop: break
			GPIO.output(self.pin, 0) 
			sleep(delay2)
			if self.stop: break
		self.sequence = 'no sequence'
		self.lock.release()
		self.stop = False

#------------------------------------------------   
	def spark(self, seq=((0.5,0.5)), final=1):
#------------------------------------------------   
		self.lock.acquire()
		self.sequence = 'spark'
		GPIO.output(self.pin, 0) 
		while not self.stop:
			if self.stop: break
			ledState = True

			for delay in seq:
				if self.stop: break
				GPIO.output(self.pin, 1 if ledState else 0) 
				sleep(delay)
				if self.stop: break
				ledState = not ledState

			if not self.stop:
				sleep(final-delay)
		self.sequence = 'no sequence'
		self.lock.release()
		self.stop = False

#------------------------------------------------   
	def isOn(self):
#------------------------------------------------   
		return self.lock.locked()

#------------------------------------------------   
	def cleanup(self):
#------------------------------------------------   
		GPIO.cleanup()

#------------------------------------------------   
	def finalize(self):
#------------------------------------------------   
		self.turnOff()
		self.cleanup()

#------------------------------------------------   
	def turnOff(self, timeout = 5):
#------------------------------------------------   
		ledTimeout = 0
		self.stop = True
		while self.isOn() and ledTimeout<=timeout: 
			sleep(.5)
			ledTimeout += .5
      
      
      
#################################################
class buildPlaylists():
#################################################
#------------------------------------------------   
	def __init__(self, musicdir='./', playlistdir='./'):
#------------------------------------------------   
		self.playlistdir=os.path.abspath(playlistdir)
		self.musicbase = os.path.abspath(musicdir)
		self.avoidCharsArray = ["'","(",")","[","]","{","}","<",">",",",".","?","^","%","$","#","@","!","|",":",";","~"," -"]
#------------------------------------------------   
	def removeChars(self, string, chars):
#------------------------------------------------   
		returnValue = string
		
		for i in chars: 
			returnValue=returnValue.replace(i,"")
		
		return returnValue   

#------------------------------------------------   
	def run(self, execute=False, loglevel=1, deletePlaylistsDir=False, prefix = None, verbose=False):
#------------------------------------------------   
		returnValue = []
		if deletePlaylistsDir and execute:
			shellCommand('rm %s/*'%self.playlistdir).run()
		
		for dir1 in sorted(os.listdir(self.musicbase)): 
			artistAll = []
			artist = self.removeChars(dir1.lower().strip().replace(' ','_'),self.avoidCharsArray)
         
			if prefix == None:
			   proceed = True
			else:
			   proceed = artist.lower().startswith(prefix.lower())
            
			if os.path.isdir(os.path.join(self.musicbase,dir1)) and proceed:
				if verbose and loglevel >= 1: returnValue.append('Artist: %s'%artist)
				for dir2 in sorted(os.listdir(os.path.join(self.musicbase,dir1))):
					printed = False
					album = self.removeChars(dir2.lower().strip().replace(' -','').replace(' ','_'),self.avoidCharsArray)
                                 
					filename = '%s-%s.m3u'%(artist,album)
					if os.path.isfile(os.path.join(self.playlistdir,filename)) and execute:
						try:
							os.remove(os.path.join(self.playlistdir,filename))
						except Exception as err:
							print err

					if os.path.isdir(os.path.join(self.musicbase,dir1,dir2)):
						for objeto in sorted(os.listdir(os.path.join(self.musicbase,dir1,dir2))):
							#filename = '%s-%s.m3u'%(artist,album)
							if not os.path.isdir(os.path.join(self.musicbase,dir1,dir2,objeto)):
								if not printed: 
									if verbose and loglevel >= 2: returnValue.append('filename:  %s'%filename)
									printed = True
								if '.mp3' in objeto.lower() or '.m4a' in objeto.lower() or '.flac' in objeto.lower():
									if os.path.isfile(os.path.join(self.musicbase,dir1,dir2,objeto)):
										if verbose and loglevel >= 3: returnValue.append(' song: %s'%objeto)
										if execute: 
											shellCommand('echo "%s" >> "%s"/"%s"'%(os.path.join(self.musicbase,dir1,dir2,objeto),self.playlistdir,filename)).run()
							else:
								filename = '%s-%s__%s.m3u'%(artist,album,self.removeChars(objeto.lower().strip().replace(' -','').replace(' ','_'),self.avoidCharsArray))

								if os.path.isfile(os.path.join(self.playlistdir,filename)) and execute:
									try:
										os.remove(os.path.join(self.playlistdir,filename))
									except Exception as err:
										print err

								if not printed: 
									if verbose and loglevel >= 2: returnValue.append('filename_: %s'%filename)
									for file1 in sorted(os.listdir(os.path.join(self.musicbase,dir1,dir2,objeto))): 
										if os.path.isfile(os.path.join(self.musicbase,dir1,dir2,objeto,file1)): 
											if '.mp3' in file1.lower() or '.m4a' in file1.lower() or '.flac' in file1.lower():
												if os.path.isfile(os.path.join(self.musicbase,dir1,dir2,objeto,file1)):
													if verbose and loglevel >= 3: returnValue.append(' song: %s'%file1)
													if execute: 
														shellCommand('echo "%s" >> "%s"/"%s"'%(os.path.join(self.musicbase,dir1,dir2,objeto,file1),self.playlistdir,filename)).run()
				
		return returnValue


################################################################################################################         
## procedure for humanize_duration                                                                            ##         
## source: http://stackoverflow.com/users/1759091/vvhitecode                                                  ##
## version unknown                                                                                            ##
################################################################################################################               
def humanize_duration(amount, units='s'):
   INTERVALS = [(lambda mlsec:divmod(mlsec, 1000), 'ms'),
             (lambda seconds:divmod(seconds, 60), 's'),
             (lambda minutes:divmod(minutes, 60), 'm'),
             (lambda hours:divmod(hours, 24), 'h'),
             (lambda days:divmod(days, 7), 'D'),
             (lambda weeks:divmod(weeks, 4), 'W'),
             (lambda years:divmod(years, 12), 'M'),
             (lambda decades:divmod(decades, 10), 'Y')]

   for index_start, (interval, unit) in enumerate(INTERVALS):
      if unit == units:
         break

   amount_abrev = []
   last_index = 0
   amount_temp = amount
   for index, (formula, abrev) in enumerate(INTERVALS[index_start: len(INTERVALS)]):
      divmod_result = formula(amount_temp)
      amount_temp = divmod_result[0]
      amount_abrev.append((divmod_result[1], abrev))
      if divmod_result[1] > 0:
         last_index = index

   amount_abrev_partial = amount_abrev[0: last_index + 1]
   amount_abrev_partial.reverse()

   final_string = ''
   for amount, abrev in amount_abrev_partial:
      final_string += str(amount) + abrev + ' '

   return final_string

################################################################################################################         
## procedure for empty a file                                                                                 ##         
## Alejandro Dirgan - 2014                                                                                    ##
## version 0.5                                                                                                ##
################################################################################################################               
def emptyFile(filename=''):
##################################################################################################################         
   returnValue = 1
   try:
      open(filename, 'w').close()
      returnValue = 0
   except Exception as err: 
      pass
   return returnValue

#########################################################     
def playSound(sound):
#########################################################     
   mediaSound = shellCommand('mpg123 '+sound)
   mediaSound.runBackground()     

################################################################################################################         
## procedure for cat a file into a list rturning a iteration                                                  ##         
## Alejandro Dirgan - 2014                                                                                    ##
## version 0.5                                                                                                ##
################################################################################################################               
def catFile(filename=''):
##################################################################################################################         
   lines = []
   try:
      content=open(filename, 'r')
      for line in (t.strip('\n') for t in content.readlines()):
         lines.append(line)
   except Exception as err: 
      pass

   return lines

################################################################################################################         
## procedure for writng a list of itmes into a file                                                           ##         
## Alejandro Dirgan - 2014                                                                                    ##
## version 0.5                                                                                                ##
################################################################################################################               
def writeItems2File(filename='', items=[], emptyFileFirst = False):
##################################################################################################################         
   returnValue=1

   if emptyFileFirst: emptyFile(filename)
   
   try: 
      f=open(filename, 'a')
      f.writelines(["%s\n" % item for item in items])
      returnValue = 0  
   except Exception as err: 
      pass

   return returnValue 

################################################################################################################         
## procedure for making a dir                                                                                 ##         
## Alejandro Dirgan - 2014                                                                                    ##
## version 0.5                                                                                                ##
################################################################################################################               
def mkdir(dirname=''):
##################################################################################################################         
   returnValue=1

   if not os.path.isdir(dirname):
      os.makedirs(dirname)
      returnValue = 0
      
   return returnValue      
   
   
################################################################################################################         
## procedure for getting number format hh:mm:ss from seconds                                                  ##         
## Alejandro Dirgan - 2014                                                                                    ##
## version 0.5                                                                                                ##
################################################################################################################               
def hhmmss(secs):
##################################################################################################################         
   a = timedelta(seconds=secs)
  
   return str(a)

################################################################################################################         
## procedure for getting number format hh:mm:ss from seconds                                                  ##         
## Alejandro Dirgan - 2014                                                                                    ##
## version 0.5                                                                                                ##
################################################################################################################               
def seconds(hhmmss):
##################################################################################################################         
   if hhmmss.count(':') == 0: 
      t='00:00:'+hhmmss
   elif hhmmss.count(':') == 1:   
      t='00:'+hhmmss
   elif hhmmss.count(':') == 2:   
      t=hhmmss
   
   return sum([a*b for a,b in zip([3600,60,1], map(int,t.split(':')))])  
      
################################################################################################################         
## procedure for getting filesystem utilization percentage - tested on Ubuntu, Raspbian                       ##         
## Alejandro Dirgan - 2014                                                                                    ##
## version 0.5                                                                                                ##
################################################################################################################               
def fsUtilization(fs):
##################################################################################################################         
   fs=shellCommand("df -k | grep %s | awk '{print $5'} | cut -d'%%' -f1" %fs)

   size = -1
   try:
      output=fs.run()
   
      if not fs.status(): 
         for i in fs.run():
            size=i
      else: 
        size=-1      
   except:
         size = -1
         
   return int(size)
   
##################################################################################################################         
#-------------------------------------------------------------------------------------------------------------------
def run_command(command):
#-------------------------------------------------------------------------------------------------------------------
   p = Popen(command, shell=True, stdout=PIPE, stderr=STDOUT)
   return iter(p.stdout.readline, b'')
   
################################################################################################################         
## class for running shell commands    - tested on Ubuntu, Raspbian                                           ##         
## Alejandro Dirgan - 2014                                                                                    ##
## version 0.5                                                                                                ##
################################################################################################################         
class shellCommand():
   
   RETURNCODE = 0
   OUTPUT = 1
   NOERROR = 0
   
#-------------------------------------------------------------------------------------------------------------------
   def __init__(self, command):
#-------------------------------------------------------------------------------------------------------------------
      self.returnCode = 0
      self.commandLine = command
      
#crear run para comandos de background      
#-------------------------------------------------------------------------------------------------------------------
   def run(self, sortedOutput=False):
#-------------------------------------------------------------------------------------------------------------------
      returnOutput=list()
      p = Popen(self.commandLine, shell=True, stdout=PIPE, stderr=STDOUT)
      for i in iter(p.stdout.readline, b''):
         returnOutput.append(i.replace('\n','').strip())
      self.returnCode = p.wait() 
      
      if sortedOutput:
         commandOutput = sorted(returnOutput)
      else:
         commandOutput = (returnOutput)

      return iter(commandOutput)

#-------------------------------------------------------------------------------------------------------------------
   def runBackground(self):
#-------------------------------------------------------------------------------------------------------------------
      p = Popen(self.commandLine, shell=True, stdout=PIPE, stderr=STDOUT)
      
      return p

#-------------------------------------------------------------------------------------------------------------------
   def replaceCommand(self, command):
#-------------------------------------------------------------------------------------------------------------------
      self.commandLine = command
      
      return self
           
#-------------------------------------------------------------------------------------------------------------------
   def status(self):
#-------------------------------------------------------------------------------------------------------------------
      return self.returnCode



################################################################################################################         
## class for top os command    - tested on Ubuntu, Raspbian                                                   ##         
## Alejandro Dirgan - 2014                                                                                    ##
## version 0.5                                                                                                ##
################################################################################################################         
class top():

   """ 
   us, user    : time running un-niced user processes
   sy, system  : time running kernel processes
   ni, nice    : time running niced user processes
   io, IO-wait : time waiting for I/O completion
   hi          : time spent servicing hardware interrupts
   si          : time spent servicing software interrupts
   st          : time stolen from this vm by the hypervisor
   """
   DEFAULTDELAY = 1
   
#-------------------------------------------------------------------------------------------------------------------
   def __init__(self):
#-------------------------------------------------------------------------------------------------------------------
      self.values = {
         'users':0,
         'load1':0,
         'load5':0,
         'load15':0,
         'us':0,
         'sy':0,
         'ni':0,
         'idle':0,
         'io':0,
         'hi':0,
         'si':0,
         'st':0,
         'memtotal':0,
         'memused':0,
         'memfree':0,
         'membuffers':0,
         'swaptotal':0,
         'swapused':0,
         'swapfree':0,
         'swapcached':0,         
         'tasks':0,        
         'running':0,        
         'sleepping':0,        
         'stopped':0,        
         'zombie':0        
      }
#      self.top = shellCommand('top -b -n 2 -d %f -p 1 '%self.DEFAULTDELAY)
      self.top = shellCommand('top -b -n 2 -d %f | egrep "top \-|Tasks|Cpu\(s\)|Mem:|Swap:" | tail -5'%self.DEFAULTDELAY)
      self.topValues = list()
      
      self.errorMessage = 'No Errors Found'
      self.errorCode = 0

#-------------------------------------------------------------------------------------------------------------------
   def test(self, delay=DEFAULTDELAY):
#-------------------------------------------------------------------------------------------------------------------
      if not self.errorCode:
         while True:
            self.updateValues(delay)
            print 'pyTop ---------------------------------------------------------------------------------'
            print '   uptime: %s'%self.topValues[0].split(',')[0].split('-')[1]
            print '    users: %9s       1m: %9s       5m: %9s          15m: %9s'%(self.values['users'], self.values['load1'], self.values['load5'], self.values['load15'])
            print '    tasks: %9s  running: %9s sleeping: %9s      stopped: %9s'%(self.values['tasks'], self.values['running'], self.values['sleeping'], self.values['stopped'])
            print '      usr: %8s%%      sys: %8s%%     nice: %8s%%         idle: %8s%%'%(self.values['us'], self.values['sy'], self.values['ni'], self.values['id'])
            print '       io: %8s%%       hi: %8s%%       si: %8s%%           st: %8s%%'%(self.values['io'], self.values['hi'], self.values['si'], self.values['st'])
            print 'mmemtotal: %9s  memused: %9s  memfree: %9s  membuffeers: %9s'%(self.values['memtotal'], self.values['memused'], self.values['memfree'], self.values['membuffers'])
            print 'swaptotal: %9s swapused: %9s swapfree: %9s   swapcached: %9s'%(self.values['swaptotal'], self.values['swapused'], self.values['swapfree'], self.values['swapcached'])
            print '---------------------------------------------------------------------------------------'
         sleep(.5)
         
#-------------------------------------------------------------------------------------------------------------------
   def update(self,delay=DEFAULTDELAY):
#-------------------------------------------------------------------------------------------------------------------
      self.topValues = list()
      temp = list()
      
      #revisar el head y el tail para ajustar entre raspbian y ubuntu
      output=self.top.run()
      self.errorCode  = self.top.status()   
 
      if not self.errorCode:
         for i in output:
            self.topValues.append(i)
      else: 
         self.errorMessage = 'Top command return error code: %s'%self.top.status() 

               
#-------------------------------------------------------------------------------------------------------------------
   def updateValues(self, delay=DEFAULTDELAY):
#-------------------------------------------------------------------------------------------------------------------
      self.update(delay) 
      self.values['users'] = self.topValues[0].split(',')[2].strip().split(' ')[0]
      if self.topValues[0].count(',')==5:
         self.values['load1'] = self.topValues[0].split(',')[3].split(':')[1].strip() 
         self.values['load5'] = self.topValues[0].split(',')[4].strip()
         self.values['load15'] = self.topValues[0].split(',')[5].strip()
      else:
         self.values['load1'] = self.topValues[0].split(',')[2].split(':')[1].strip() 
         self.values['load5'] = self.topValues[0].split(',')[3].strip()
         self.values['load15'] = self.topValues[0].split(',')[4].strip()

      self.values['tasks'] = self.topValues[1].split(',')[0].split(':')[1].strip().split(' ')[0]
      self.values['running'] = self.topValues[1].split(',')[1].strip().split(' ')[0]
      self.values['sleeping'] = self.topValues[1].split(',')[2].strip().split(' ')[0]
      self.values['stopped'] = self.topValues[1].split(',')[3].strip().split(' ')[0]
      self.values['zombie'] = self.topValues[1].split(',')[4].strip().split(' ')[0]

      self.values['us'] = self.topValues[2].split(',')[0].split(':')[1].strip().split(' ')[0]   
      self.values['sy'] = self.topValues[2].split(',')[1].strip().split(' ')[0]   
      self.values['ni'] = self.topValues[2].split(',')[2].strip().split(' ')[0]   
      self.values['id'] = self.topValues[2].split(',')[3].strip().split(' ')[0]   
      self.values['io'] = self.topValues[2].split(',')[4].strip().split(' ')[0]   
      self.values['hi'] = self.topValues[2].split(',')[5].strip().split(' ')[0]   
      self.values['si'] = self.topValues[2].split(',')[6].strip().split(' ')[0]   
      self.values['st'] = self.topValues[2].split(',')[7].strip().split(' ')[0]   

      self.values['memtotal'] = self.topValues[3].split(':')[1].split(',')[0].strip().split(' ')[0]
      self.values['memused'] = self.topValues[3].split(',')[1].strip().split(' ')[0]
      self.values['memfree'] = self.topValues[3].split(',')[2].strip().split(' ')[0]
      self.values['membuffers'] = self.topValues[3].split(',')[3].strip().split(' ')[0]

      self.values['swaptotal'] = self.topValues[4].split(':')[1].split(',')[0].strip().split(' ')[0]
      self.values['swapused'] = self.topValues[4].split(',')[1].strip().split(' ')[0]
      self.values['swapfree'] = self.topValues[4].split(',')[2].strip().split(' ')[0]
      self.values['swapcached'] = self.topValues[4].split(',')[3].strip().split(' ')[0]

#-------------------------------------------------------------------------------------------------------------------
   def errorCode(self):      
#-------------------------------------------------------------------------------------------------------------------
      return errorCode      

#-------------------------------------------------------------------------------------------------------------------
   def errorMessage(self):      
#-------------------------------------------------------------------------------------------------------------------
      return errorMessage

################################################################################################################         
## class for obtaining information of OS ifconfig - tested on Ubuntu, Raspbian                                ##         
## Alejandro Dirgan - 2014                                                                                    ##
## version 0.5                                                                                                ##
################################################################################################################         
class ifconfig():

   
#-------------------------------------------------------------------------------------------------------------------
   def __init__(self):
#-------------------------------------------------------------------------------------------------------------------
      self.ifaces = dict()
      self.errorCode = 0
      self.errorMessage = ''
      
      self.updateIfaces()
      
#-------------------------------------------------------------------------------------------------------------------
   def __repr__(self):
#-------------------------------------------------------------------------------------------------------------------
      returnValue=''
      for i in self.ifaces: 
         
         returnValue=returnValue+'-----------------------------------\n%s (%s)\n'%(i, self.ifaces[i]['status'])
         returnValue=returnValue+'         mtu: %s\n'%(self.ifaces[i]['mtu'] if self.ifaces[i]['mtu'] else 'not assigned' )
         returnValue=returnValue+'        addr: %s\n'%(self.ifaces[i]['addr'] if self.ifaces[i]['addr'] else 'not assigned' )
         returnValue=returnValue+'         mac: %s\n'%(self.ifaces[i]['mac'] if self.ifaces[i]['mac'] else 'not assigned' )
         returnValue=returnValue+'        mask: %s\n'%(self.ifaces[i]['mask'] if self.ifaces[i]['mask'] else 'not assigned' )
         returnValue=returnValue+'       bcast: %s\n'%(self.ifaces[i]['bcast'] if self.ifaces[i]['bcast'] else 'not assigned' )
         returnValue=returnValue+'          rx: %s\n'%(self.ifaces[i]['rx'] if self.ifaces[i]['rx'] else 'not assigned' )
         returnValue=returnValue+'          tx: %s\n'%(self.ifaces[i]['tx'] if self.ifaces[i]['rx'] else 'not assigned' )
         
      return returnValue
      
#-------------------------------------------------------------------------------------------------------------------
   def updateIfaces(self):
#-------------------------------------------------------------------------------------------------------------------
      iface = shellCommand('/sbin/ifconfig -s | grep -v face')
      
      output=iface.run()
 
      if not iface.status():
         for i in output:
            i=' '.join(i.split())
            self.ifaces[i.split(' ')[0]] = {'MTU':i.split(' ')[1]}
      else: 
         self.errorMessage='ifconfig error: %s'%iface.status()   
         self.errorCode=iface.status()
      
      if not self.errorCode: 
         for interface in self.ifaces: 
            HWaddr = ''  
            Bcast='' 
            Mask=''
            Addr=''
            RX=''
            TX=''
            STATUS=''
            MTU=''
            iface.replaceCommand('/sbin/ifconfig %s'%interface)
            output=iface.run()
            if not iface.status():
               for var in output: 
                  if var.find('HWaddr')>=0:
                     HWaddr = var.split('HWaddr')[1].strip()
                  elif var.find('Bcast')>=0:  
                     Bcast = var.split('Bcast:')[1].split(' ')[0] 
                     Mask = var.split('Mask:')[1].split(' ')[0] 
                     Addr = var.split('addr:')[1].split(' ')[0] 
                  elif var.find('RX bytes')>=0:  
                     RX = var.split('RX bytes:')[1].split(' ')[0]  
                     TX = var.split('TX bytes:')[1].split(' ')[0] 
                  elif var.find('Metric')>=0:  
                     STATUS = var.split(' ')[0]  
                     MTU = var.split('MTU:')[1].split(' ')[0]
                         
                     

               self.ifaces[interface]={'mac':HWaddr, 'bcast': Bcast, 'mask':Mask, 'addr':Addr, 'rx':RX, 'tx':TX, 'status':STATUS, 'mtu': MTU}
               

#-------------------------------------------------------------------------------------------------------------------
   def getAddr(self, interface='lo'): 
#-------------------------------------------------------------------------------------------------------------------
      try: 
         returnValue=self.ifaces[interface]['addr'] 
      except: 
         returnValue=''   

      return returnValue

#-------------------------------------------------------------------------------------------------------------------
   def getMac(self, interface='lo'): 
#-------------------------------------------------------------------------------------------------------------------
      try:
		 returnValue=self.ifaces[interface]['mac'] 
      except: 
         returnValue=''   

      return returnValue

#-------------------------------------------------------------------------------------------------------------------
   def getMask(self, interface='lo'): 
#-------------------------------------------------------------------------------------------------------------------
      try: 
         returnValue=self.ifaces[interface]['mask'] 
      except: 
         returnValue=''   

      return returnValue

#-------------------------------------------------------------------------------------------------------------------
   def getBcast(self, interface='lo'): 
#-------------------------------------------------------------------------------------------------------------------
      try: 
         returnValue= self.ifaces[interface]['bcast'] 
      except: 
         returnValue=''   

      return returnValue

#-------------------------------------------------------------------------------------------------------------------
   def getRx(self, interface='lo'): 
#-------------------------------------------------------------------------------------------------------------------
      self.updateIfaces()
      try: 
         returnValue= self.ifaces[interface]['rx'] 
      except: 
         returnValue=''   

      return returnValue

#-------------------------------------------------------------------------------------------------------------------
   def getTx(self, interface='lo'): 
#-------------------------------------------------------------------------------------------------------------------
      self.updateIfaces()
      try: 
         returnValue= self.ifaces[interface]['tx'] 
      except: 
         returnValue=''   

      return returnValue

#-------------------------------------------------------------------------------------------------------------------
   def interfaces(self):
#-------------------------------------------------------------------------------------------------------------------
      returnValues=list()
      for i in self.ifaces: returnValues.append(i)
      return (returnValues)


################################################################################################################         
## class for obtaining information from OS df command - tested on Ubuntu, Raspbian                            ##         
## Alejandro Dirgan - 2014                                                                                    ##
## version 0.5                                                                                                ##
################################################################################################################         
class df():
   
#-------------------------------------------------------------------------------------------------------------------
   def __init__(self):
#-------------------------------------------------------------------------------------------------------------------
      self.fs = dict()
      self.errorCode = 0
      self.errorMessage = ''
      
      self.updateFs()

#-------------------------------------------------------------------------------------------------------------------
   def updateFs(self, debug=False):
#-------------------------------------------------------------------------------------------------------------------      
      fs = shellCommand('/bin/df -k')
      
      output=fs.run()
 
      if not fs.status():
         for filesystem in output:
            FS = ''  
            SZ='' 
            US=''
            AV=''
            UP=''
            MO=''

            filesystem=' '.join(filesystem.split())
            if not filesystem.lower().find('use%')>=0:
               FS=filesystem.split()[0]
               SZ=filesystem.split()[1]
               US=filesystem.split()[2]
               AV=filesystem.split()[3]
               UP=filesystem.split()[4]
               MO=filesystem.split()[5]
               self.fs[MO]={'SIZE':SZ,'USED':US, 'AVAILABLE':AV, '% USED':UP, 'FILESYSTEM':FS}
               if debug: print self.fs[FS]
      
      self.errorMessage='df error: %s'%fs.status()   
      self.errorCode=fs.status()

#-------------------------------------------------------------------------------------------------------------------
   def __repr__(self):
#-------------------------------------------------------------------------------------------------------------------
      returnValue=''
      for filesystem in self.fs: 
         
         returnValue=returnValue+'-----------------------------------\n%s\n'%(filesystem)
         returnValue=returnValue+'         Size: %s\n'%(self.fs[filesystem]['SIZE'])
         returnValue=returnValue+'         Used: %s\n'%(self.fs[filesystem]['USED'])
         returnValue=returnValue+'    Available: %s\n'%(self.fs[filesystem]['AVAILABLE'])
         returnValue=returnValue+'        %%used: %s\n'%(self.fs[filesystem]['% USED'])
         returnValue=returnValue+'   FileSystem: %s\n'%(self.fs[filesystem]['FILESYSTEM'])
         
      return returnValue
      
#-------------------------------------------------------------------------------------------------------------------
   def getFilesystems(self):
#-------------------------------------------------------------------------------------------------------------------
      returnValues=list()
      for fs in self.fs: returnValues.append(fs)
      return (returnValues)

#-------------------------------------------------------------------------------------------------------------------
   def getFsSize(self, fs='/'):
#-------------------------------------------------------------------------------------------------------------------
      try:
         returnValue=self.fs[fs]['SIZE']
      except: 
         returnValue=''   
      return (int(returnValue))

#-------------------------------------------------------------------------------------------------------------------
   def getFsUsed(self, fs='/'):
#-------------------------------------------------------------------------------------------------------------------
      try:
         returnValue=self.fs[fs]['USED']
      except: 
         returnValue=''   
      return (int(returnValue))

#-------------------------------------------------------------------------------------------------------------------
   def getFsAvailable(self, fs='/'):
#-------------------------------------------------------------------------------------------------------------------
      try:
         returnValue=self.fs[fs]['AVAILABLE']
      except: 
         returnValue=''   
      return (int(returnValue))

#-------------------------------------------------------------------------------------------------------------------
   def getFsPused(self, fs='/'):
#-------------------------------------------------------------------------------------------------------------------
      try:
         returnValue=self.fs[fs]['% USED']
      except: 
         returnValue=''   
      return (returnValue)

#-------------------------------------------------------------------------------------------------------------------
   def getFsName(self, fs='/'):
#-------------------------------------------------------------------------------------------------------------------
      try:
         returnValue=self.fs[fs]['FILESYSTEM']
      except: 
         returnValue=''   
      return (returnValue)


################################################################################################################         
## class for ping a host - tested on Ubuntu, Raspbian                                                         ##         
## Alejandro Dirgan - 2014                                                                                    ##
## version 0.5                                                                                                ##
################################################################################################################         
class ping():

#-------------------------------------------------------------------------------------------------------------------
   def __init__(self, host='localhost'):
#-------------------------------------------------------------------------------------------------------------------   
      self.host = host
      self.exitCode = 0
      self.Message= ''
      self.pingHost = shellCommand('ping -c 1 -W 1 %s'%self.host)
   
#-------------------------------------------------------------------------------------------------------------------
   def run(self, host='', verbose=False):
#-------------------------------------------------------------------------------------------------------------------   
      
      if host:
         self.pingHost.replaceCommand('ping -c 1 -W 1 %s'%host)
         self.host=host
      else: 
         self.pingHost.replaceCommand('ping -c 1 -W 1 localhost')   

      output=self.pingHost.run()
      if not self.pingHost.status(): 
         if verbose: print '%s is alive'%self.host
         self.Message = '%s is alive'%self.host
      elif self.pingHost.status() == 2: 
         if verbose: print '%s is unknown'%self.host
         self.Message = '%s is unknown'%self.host
      elif self.pingHost.status() == 1: 
         if verbose: print '%s is not responding'%self.host
         self.Message = '%s is not responding'%self.host
         
      self.exitCode = self.pingHost.status() 

#-------------------------------------------------------------------------------------------------------------------
   def getExitCode(self): 
#-------------------------------------------------------------------------------------------------------------------   
      return self.exitCode

#-------------------------------------------------------------------------------------------------------------------
   def getMessage(self): 
#-------------------------------------------------------------------------------------------------------------------   
      return self.Message


################################################################################################################         
## class for load a /etc/host in a list - tested on Ubuntu, Raspbian                                          ##         
## Alejandro Dirgan - 2014                                                                                    ##
## version 0.5                                                                                                ##
################################################################################################################         
class hosts():

#-------------------------------------------------------------------------------------------------------------------
   def __init__(self):
#-------------------------------------------------------------------------------------------------------------------   
      self.hosts = dict()
      self.hostnames = list()
      self.exitCode = 0
      self.Message= ''

      self.getHosts()

#-------------------------------------------------------------------------------------------------------------------
   def __repr__(self):
#-------------------------------------------------------------------------------------------------------------------
      returnValue=''
      for host in self.hosts: 
         
         returnValue=returnValue+'host: %25s  IP: %s\n'%(host, self.hosts[host])
         
      return returnValue
      
#-------------------------------------------------------------------------------------------------------------------
   def getHosts(self):
#-------------------------------------------------------------------------------------------------------------------   
            
      for host in catFile('/etc/hosts'): 
         host=' '.join(host.split())
         if not host.startswith('#') and len(host)>0 and host.find('::')==-1:
            self.hosts[host.split()[1]]= host.split()[0]
            self.hostnames.append(host.split()[1])

#-------------------------------------------------------------------------------------------------------------------
   def getHostnames(self):
#-------------------------------------------------------------------------------------------------------------------   
      return (self.hostnames)


################################################################################################################         
## class for iwlist  - tested on Ubuntu, Raspbian                                                             ##         
## Alejandro Dirgan - 2014                                                                                    ##
## version 0.5                                                                                                ##
################################################################################################################         
class iwlist():

   
#-------------------------------------------------------------------------------------------------------------------
   def __init__(self, net):
#-------------------------------------------------------------------------------------------------------------------   
      self.interfaces = ifconfig()
      self.iwList = dict()

      self.addr = ''
      self.essi = ''
      self.prot = ''
      self.mode = ''
      self.freq = ''
      self.encr = ''
      self.bitr = ''
      self.qual = ''
      self.sign = ''
      
      self.refreshIw(net)
#-------------------------------------------------------------------------------------------------------------------
   def refreshIw(self, net):  
#-------------------------------------------------------------------------------------------------------------------   
      iwCommand=shellCommand('iwlist %s scan'%net)
       
      output = iwCommand.run()
      celString = ''
      init = True
      for line in output: 
         if line.strip().startswith('Cell'): 
            celString = '-'.join((line.strip().split('-')[0].strip()).split())+' '
            self.parse(celString, line.strip().split('-')[1].strip())
            if not init: 
               self.iwPack(celString)
            init = False   
            continue
         self.parse(celString, line.strip())
      self.iwPack(celString)
#-------------------------------------------------------------------------------------------------------------------
   def iwPack(self, celNum):
#-------------------------------------------------------------------------------------------------------------------
      self.iwList[self.essi]={'address':self.addr, 'protocol':self.prot, 'mode':self.mode, 'frequency':self.freq, 'encryption':self.encr, 'bitrate':self.bitr, 'quality':self.qual, 'signal':self.sign}
#-------------------------------------------------------------------------------------------------------------------
   def parse(self, celNum, line):
#-------------------------------------------------------------------------------------------------------------------
      if line.lower().find('address')>=0: 
         self.addr=line.lower().split('address:')[1].strip()
      elif line.lower().find('essid')>=0: 
         self.essi=line.lower().split('essid:')[1].strip()      
      elif line.lower().find('mode')>=0: 
         self.mode=line.lower().split('mode:')[1].strip()      
      elif line.lower().find('protocol')>=0: 
         self.prot=line.lower().split('protocol:')[1].strip()      
      elif line.lower().find('frequency')>=0: 
         self.freq=line.lower().split('frequency:')[1].strip()      
      elif line.lower().find('bit rate')>=0: 
         self.bitr=line.lower().split('bit rates:')[1].strip()      
      elif line.lower().find('encrypt')>=0: 
         self.encr=line.lower().split('encryption key:')[1].strip()      
      elif line.lower().find('quality')>=0: 
         self.qual=line.lower().split('quality=')[1].split()[0].strip()      

         self.sign=line.lower().split('signal level=')[1].strip()      

#-------------------------------------------------------------------------------------------------------------------
   def __repr__(self):
#-------------------------------------------------------------------------------------------------------------------
      returnValue=''
      for essid in self.iwList: 
         
         returnValue=returnValue+'-----------------------------------\nESSID: %s\n'%(essid)
         returnValue=returnValue+'       Address: %s\n'%self.iwList[essid]['address']
         returnValue=returnValue+'      Protocol: %s\n'%self.iwList[essid]['protocol']
         returnValue=returnValue+'          Mode: %s\n'%self.iwList[essid]['mode']
         returnValue=returnValue+'     Frequency: %s\n'%self.iwList[essid]['frequency']
         returnValue=returnValue+'     Bit Rates: %s\n'%self.iwList[essid]['bitrate']
         returnValue=returnValue+'    Encryption: %s\n'%self.iwList[essid]['encryption']
         returnValue=returnValue+'       Quality: %s\n'%self.iwList[essid]['quality']
         returnValue=returnValue+'        Signal: %s\n'%self.iwList[essid]['signal']
         
      return returnValue

#-------------------------------------------------------------------------------------------------------------------
   def nets(self):
#-------------------------------------------------------------------------------------------------------------------
      returnValues=list()
      for i in self.iwList: returnValues.append(i)
      return (returnValues) 

#-------------------------------------------------------------------------------------------------------------------
   def getAddress(self, net):
#-------------------------------------------------------------------------------------------------------------------
      try:
         returnValue=self.iwList[net]['address']
      except: 
         returnValue=''   
      return (returnValue)

#-------------------------------------------------------------------------------------------------------------------
   def getMode(self, net):
#-------------------------------------------------------------------------------------------------------------------
      try:
         returnValue=self.iwList[net]['mode']
      except: 
         returnValue=''   
      return (returnValue)      

#-------------------------------------------------------------------------------------------------------------------
   def getFrequency(self, net):
#-------------------------------------------------------------------------------------------------------------------
      try:
         returnValue=self.iwList[net]['frequency']
      except: 
         returnValue=''   
      return (returnValue)

#-------------------------------------------------------------------------------------------------------------------
   def getBitrate(self, net):
#-------------------------------------------------------------------------------------------------------------------
      try:
         returnValue=self.iwList[net]['bitrate']
      except: 
         returnValue=''   
      return (returnValue)
      
#-------------------------------------------------------------------------------------------------------------------
   def getEncryption(self, net):
#-------------------------------------------------------------------------------------------------------------------
      try:
         returnValue=self.iwList[net]['encryption']
      except: 
         returnValue=''   
      return (returnValue)      

#-------------------------------------------------------------------------------------------------------------------
   def getQuality(self, net=''):
#-------------------------------------------------------------------------------------------------------------------
      try: 
         if net:
            returnValue=self.iwList[net]['quality']
         else: 
            lines = [line.strip() for line in open('/proc/net/wireless')]
            returnValue=lines[2].split()[2].replace('.','') 
      except: 
         returnValue=''   
      return (returnValue)

#-------------------------------------------------------------------------------------------------------------------
   def getSignal(self, net=''):
#-------------------------------------------------------------------------------------------------------------------
      try:
         if net:
            returnValue=self.iwList[net]['signal']
         else: 
            lines = [line.strip() for line in open('/proc/net/wireless')]
            returnValue=lines[2].split()[3].replace('.','') 
      except: 
         returnValue=''   
      return (returnValue)

#lines = [line.strip() for line in open('/proc/net/wireless')]

###############################################################################################################
#-------------------------------------------------------------------------------------------------------------------
def wirelessQuality():
#-------------------------------------------------------------------------------------------------------------------
   try: 
      lines = [line.strip() for line in open('/proc/net/wireless')]
      returnValue=lines[2].split()[2].replace('.','') 
   except: 
      returnValue=''   

   return (returnValue)

#------------------------------------------------------------------------------------------------------------------
def wirelessSignal():
#-------------------------------------------------------------------------------------------------------------------
   try:
      lines = [line.strip() for line in open('/proc/net/wireless')]
      returnValue=lines[2].split()[3].replace('.','') 
   except: 
      returnValue=''   

   return (returnValue)



################################################################################################################         
## class for picamera  - Raspbian                                                                             ##         
## Alejandro Dirgan - 2014                                                                                    ##
## version 0.5                                                                                                ##
################################################################################################################         
class yadCamera():
   
#-------------------------------------------------------------------------------------------------------------------
   def __init__(self):
#-------------------------------------------------------------------------------------------------------------------   

      self.camera = picamera.PiCamera()
      self.stillMedia = '/media/usb0'
      self.stillPath = '/media/usb0/camera'
      self.stillNamePrefix = 'picam-'
      self.stillMaxDiskUsage = 95
      self.stillWidth = 1280
      self.stillHeight = 720      
      
      self.stillError = 0
      self.stillErrorMessage='no error'

      self.camera.start_preview()
      self.camera.resolution = (self.stillWidth, self.stillHeight)
      
      self.lastPicture = self.nextStillName()

#modificar
#-------------------------------------------------------------------------------------------------------------------
   def setParam(self, media='', path='', prefix='', maxDisk=0, defaultWidth = 0, defaultHeight = 0): 
#-------------------------------------------------------------------------------------------------------------------

      if path:
         path = os.path.abspath(path)
      
         returnValue = -1


         if not os.path.exists(path): 
            mkdir(path)
            os.chmod(path, 0777)
            self.stillPath=path
            self.lastPicture = self.nextStillName()
            returnValue=0
         else: 
            self.stillPath=path
            returnValue=0              

      if media: 
         self.stillMedia = media
         
      if prefix: 
         self.stillNamePrefix = prefix
         returnValue = 0

      if maxDisk > 0: 
         self.stillMaxDiskUsage = maxDisk
         returnValue = 0

      if defaultWidth > 0: 
         self.stillWidth = defaultWidth 
         returnValue = 0        

      if defaultHeight > 0: 
         self.stillHeight = defaultHeight 
         returnValue = 0        


      return returnValue
#-------------------------------------------------------------------------------------------------------------------
   def getPath(self): 
#-------------------------------------------------------------------------------------------------------------------     
      return self.stillPath   

#-------------------------------------------------------------------------------------------------------------------
   def getPrefix(self): 
#-------------------------------------------------------------------------------------------------------------------     
      return self.stillPrefix   

#-------------------------------------------------------------------------------------------------------------------
   def getMaxDisk(self): 
#-------------------------------------------------------------------------------------------------------------------     
      return self.stillMaxDiskUsage   

#-------------------------------------------------------------------------------------------------------------------
   def getResolution(self): 
#-------------------------------------------------------------------------------------------------------------------     
      return [self.stillWidth,  self.stillHeight]  

#-------------------------------------------------------------------------------------------------------------------
   def getLastPicture(self): 
#-------------------------------------------------------------------------------------------------------------------     
      return self.lastPicture 

#-------------------------------------------------------------------------------------------------------------------
   def getPicturesTaken(self): 
#-------------------------------------------------------------------------------------------------------------------     
      return numberOfFiles(self.stillPath+'/*.jpg')

#-------------------------------------------------------------------------------------------------------------------
   def getFreeSpace(self): 
#-------------------------------------------------------------------------------------------------------------------     
      return fsUtilization(self.stillMedia)
      
#-------------------------------------------------------------------------------------------------------------------
   def flashLed(self, repeat=4, pause=.1):
#-------------------------------------------------------------------------------------------------------------------
      self.camera.led = False
      for i in range(repeat):
         self.camera.led = True
         sleep(pause)
         self.camera.led = False
         sleep(pause)

#-------------------------------------------------------------------------------------------------------------------
   def close(self): 
#-------------------------------------------------------------------------------------------------------------------     
      self.camera.stop_preview()
      self.camera.close() 

#-------------------------------------------------------------------------------------------------------------------
   def getError(self): 
#-------------------------------------------------------------------------------------------------------------------     
      return self.stillError 

#-------------------------------------------------------------------------------------------------------------------
   def getErrorMessage(self): 
#-------------------------------------------------------------------------------------------------------------------     
      return self.stillErrorMessage

#-------------------------------------------------------------------------------------------------------------------
   def resetError(self): 
#-------------------------------------------------------------------------------------------------------------------     
      self.stillError=0
      self.stillErrorMessage=''

#-------------------------------------------------------------------------------------------------------------------
   def nextStillName(self, withPath=False):
#-------------------------------------------------------------------------------------------------------------------

      returnValue =''
      
      if mountPoint(self.stillMedia):
         if not os.path.exists(self.stillPath): 
            mkdir(self.stillPath)
      else:      
         self.stillError = -1
         self.stillErrorMessage = 'media !mounted'
         return returnValue

#      if not os.path.exists(self.stillPath): 
#         if mountPoint(self.stillPath)=='': 
#            self.stillError = -1
#            self.stillErrorMessage = 'media !mounted'
#            return returnValue
#         else:
#            os.mkdir(self.stillPath)
               
      fileList=shellCommand('ls '+self.stillPath+'/*.jpg 2>/dev/null')
         
      if not os.path.exists(self.stillPath): 
         mkdir(self.stillPath)
               
      output = fileList.run()
      
      lastName = ''
      for i in output: 
         lastName = i
  
      leadingPath=self.stillPath+'/' if withPath else '' 

      if not lastName: 
         returnValue = leadingPath+'picam-'+''.zfill(5)+'.jpg'
      else: 
         returnValue=leadingPath+'picam-'+str(int(lastName.split('-')[1].split('.')[0])+1).zfill(5)+'.jpg'      
   
      
      return returnValue

#-------------------------------------------------------------------------------------------------------------------
   def shoot(self, stillName = '', width=0, height=0, flash=True):
#-------------------------------------------------------------------------------------------------------------------

      if self.stillError==-1: 
         return '' 
         
      if stillName: 
         pictureName = stillName
         self.lastPicture = stillName
      else:   
         pictureName=self.nextStillName(withPath=True)
         self.lastPicture = self.nextStillName()
       
      changeResolution = True if width != 0 or height != 0 else False

      if changeResolution: 
         self.camera.resolution = [width, height]
      
      if flash: self.flashLed(repeat=6, pause=.05)

           
      sleep(.05)
      self.camera.capture(pictureName)
      
      if changeResolution: 
         self.camera.resolution = [self.stillWidth, self.stillHeight]
         
        
      return pictureName

##################################################################################################################         
def numberOfFiles(filename):
##################################################################################################################         
   wc=shellCommand('ls %s | wc -l 2>/dev/null'%filename)

   try:
      output=wc.run()
   
      if not wc.status(): 
         for i in wc.run():
            nfiles=i
      else: 
        nfiles=-1      
   except:
         nfiles = -1
         
   return int(nfiles)
 
##################################################################################################################         
def mountPoint(path):
##################################################################################################################         
    path = os.path.abspath(path)
    
    try:
       orig_dev = os.stat(path).st_dev

       while path != '/':
           dir = os.path.dirname(path)
           if os.stat(dir).st_dev != orig_dev:
               # we crossed the device border
               break
           path = dir
       return path 
    except:
       return ''

        
##################################################################################################################         
class dateTime():
    
    def __init__(self): 
       self.error = 0
       self.refresh()      
       self.start = datetime.now()
       self.stop  = self.start
       self.elapsed=0
       self.timerStarted = False
       
       self.refresh()

#-------------------------------------------------------------------------------------------------------------------
    def humanizeElapsed(self): 
#-------------------------------------------------------------------------------------------------------------------
       return humanize_duration(self.elapsed)
       
#-------------------------------------------------------------------------------------------------------------------
    def refresh(self): 
#-------------------------------------------------------------------------------------------------------------------
      dateTime = datetime.now()
      self.dateString = dateTime.strftime('%b %d,%Y')
      self.classicDate = dateTime.strftime('%d/%m/%y')
      self.classicStime = dateTime.strftime('%H:%M:%S')
      self.timeString = dateTime.strftime('%H:%M%P')
      
      return self
      
#-------------------------------------------------------------------------------------------------------------------
    def startTimer(self, timerId='timer1'): 
#-------------------------------------------------------------------------------------------------------------------
       self.error = 0
       self.elapsed=0
       self.timerStarted = True
       self.start = datetime.now()

       return self       

#-------------------------------------------------------------------------------------------------------------------
    def stopTimer(self, timerId='timer1'): 
#-------------------------------------------------------------------------------------------------------------------
       self.error = 0
       self.timerStarted = False
       self.stop = datetime.now()

       return self       

#-------------------------------------------------------------------------------------------------------------------
    def timeLapsed(self, p=6, timerId = 'timer1'): 
#-------------------------------------------------------------------------------------------------------------------
        self.error = 0
        
        if self.timerStarted: 
           self.elapsed = (datetime.now()-self.start).total_seconds()
        else: 
           self.elapsed = (self.stop - self.start).total_seconds()
        
        return float(self.elapsed)


##################################################################################################################         
class timer():
    
    def __init__(self): 
       self.error = 0
       self.timers = {}
       self.timers['timer1'] = { 'timerId': 'timer1', 
                                'timeout': 60,
                                'start': 0,
                                'stop': 0,
                                'started': False,
                                'diff': 0,
                                'seconds': 0,
                                'days': 0,
                                'microseconds': 0 }
                                
#-------------------------------------------------------------------------------------------------------------------
    def setTimer(self, timerId='timer1', timeoutinseconds=60, startNow=False): 
#-------------------------------------------------------------------------------------------------------------------
       self.error = 0
       try: 
          self.timers[timerId] = { 'timerId': timerId, 
                                   'timeout': timeoutinseconds,
                                   'start': 0,
                                   'stop': 0,
                                   'started': False,
                                   'diff': 0,
                                   'seconds': 0,
                                   'days': 0,
                                   'microseconds': 0 }
          returnValue = timerId                         
       except: 
          self.error = -1
          
       if startNow: self.startTimer(timerId=timerId)   

       return self 
#-------------------------------------------------------------------------------------------------------------------
    def setTimeout(self, timerId='timer1', timeoutinseconds=60): 
#-------------------------------------------------------------------------------------------------------------------
       self.error = 0     
       try: 
          self.timers[timerId]['timeout'] = timeoutinseconds
          returnValue = timeoutinseconds 
       except: 
          self.error = -1

       return self
       
#-------------------------------------------------------------------------------------------------------------------
    def trigger(self, timerId='timer1'): 
#-------------------------------------------------------------------------------------------------------------------
       self.error = 0
       returnValue = False
       try: 
          if self.timeLapsed(timerId=timerId) > self.timers[timerId]['timeout']: 
             returnValue = True
       except: 
          self.error = -1
       
       return returnValue
             
#-------------------------------------------------------------------------------------------------------------------
    def startTimer(self, timerId='timer1'): 
#-------------------------------------------------------------------------------------------------------------------
       self.error = 0
       try: 
          self.timers[timerId]['started'] = True
       except: 
          self.error = -1
       try: 
          self.timers[timerId]['start'] = datetime.now()
       except: 
          self.error = -1

       return self       

#-------------------------------------------------------------------------------------------------------------------
    def stopTimer(self, timerId='timer1'): 
#-------------------------------------------------------------------------------------------------------------------
       self.error = 0
       try: 
          self.timers[timerId]['started'] = False
       except: 
          self.error = -1
       try: 
          self.timers[timerId]['stop'] = datetime.now()
       except: 
          self.error = -1

       self.timeDifference(timerId=timerId)

       return self       

#-------------------------------------------------------------------------------------------------------------------
    def timeLapsed(self, p=6, timerId = 'timer1'): 
#-------------------------------------------------------------------------------------------------------------------
        self.error = 0
        precisionTimeElapsed = 0.0
        try: 
           if self.timers[timerId]['started']: 
              precisionTimeElapsed=(datetime.now() - self.timers[timerId]['start']).total_seconds()
           else: 
              precisionTimeElapsed=self.timers[timerId]['diff']
        except: 
           self.error = -1

        return precisionTimeElapsed

#-------------------------------------------------------------------------------------------------------------------
    def isStarted(self, timerId='timer1'): 
#-------------------------------------------------------------------------------------------------------------------
       return self.timers[timerId]['started']

#-------------------------------------------------------------------------------------------------------------------
    def timeDifference(self, p=6, timerId='timer1'): 
#-------------------------------------------------------------------------------------------------------------------
        self.error = 0
        try: 
           self.timers[timerId]['diff'] = (self.timers[timerId]['stop'] - self.timers[timerId]['start']).total_seconds()
           returnValue = self.timers[timerId]['diff']
           self.timers[timerId]['seconds'] = self.timers[timerId]['diff'].total_seconds()
           self.timers[timerId]['days'] = self.timers[timerId]['diff'].days
           self.timers[timerId]['microseconds'] = self.timers[timerId]['diff'].microseconds
        except: 
           self.error = -1
        
        return self

################################################################
class stringScroll():
################################################################
   WINDOW = 16
#---------------------------------------------------------------
   def __init__(self, string='', space=' '):
#---------------------------------------------------------------
      self.start=True
      self.end = False

      self.offset=0
      self.space= space
      self.setString(string)   
     
      self.movingForward = True
     
#---------------------------------------------------------------
   def isEnd(self):
#---------------------------------------------------------------
     return self.end
#---------------------------------------------------------------
   def setOffset(self, offset):
#---------------------------------------------------------------
      self.offset = offset
      self.pos1=self.offset
      self.pos2=self.pos1 + self.WINDOW
      self.maxIter = len(self.string) - self.WINDOW - self.offset + 1

#---------------------------------------------------------------
   def setWindow(self, window):
#---------------------------------------------------------------
      if window > 5:
         self.WINDOW = window
      self.pos1=self.offset
      self.pos2=self.pos1 + self.WINDOW
      self.string = self.space*self.WINDOW + self.originalString + self.space*self.WINDOW
      self.maxIter = len(self.string) - self.WINDOW - self.offset + 1
      self.start=True
      self.end = False

#---------------------------------------------------------------
   def getWindow(self):
#---------------------------------------------------------------
      return self.WINDOW
       
#---------------------------------------------------------------
   def setString(self, string='', spaces = True):
#---------------------------------------------------------------
      self.originalString = string
      if spaces:
         self.string = self.space*self.WINDOW + string + self.space*self.WINDOW
      else: 
         self.string = string
            
      self.pos1=self.offset
      self.pos2=self.pos1 + self.WINDOW
      self.maxIter = len(self.string) - self.WINDOW - self.offset + 1

#---------------------------------------------------------------
   def replaceString(self, _string, spaces=True):
#---------------------------------------------------------------
      len1=len(self.originalString)
      self.originalString = _string

      if spaces:
         self.string = self.space*self.WINDOW + _string[0:len1] + self.space*self.WINDOW
      else: 
         self.string = _string[0:len1]
     
#---------------------------------------------------------------
   def visibleString(self):
#---------------------------------------------------------------
      _string = self.string[self.pos1:self.pos2]
      #print '%s, %s:%s'%(self.string, self.pos1, self.pos2)
      return _string

#---------------------------------------------------------------
   def forward(self):
#---------------------------------------------------------------

      if self.pos1 == 0:
         self.start = True
      else:
         self.start = False

      if self.pos1 >= self.maxIter - 1:
         self.end = True
      else:
         self.end = False

      if self.pos1 < self.maxIter + self.offset - 1:
         self.pos1 += 1
         self.pos2 = self.pos1 + self.WINDOW
        

#---------------------------------------------------------------
   def backward(self):
#---------------------------------------------------------------

      if self.pos1 == 0:
         self.start = True
      else:
         self.start = False

      if self.pos1 >= self.maxIter - 1:
         self.end = True
      else:
         self.end = False
        
      if self.pos1 > 0 + self.offset:
         self.pos1 -= 1
         self.pos2 = self.pos1+self.WINDOW

#---------------------------------------------------------------
   def moveBackForth(self):
#---------------------------------------------------------------
      if self.movingForward:
         self.forward()
         if self.end: self.movingForward = False   
      else:
         self.backward()  
         if self.start: self.movingForward = True

#---------------------------------------------------------------
   def goBeginning(self, string=''):
#---------------------------------------------------------------
      self.pos1=self.offset
      self.pos2=self.pos1 + self.WINDOW

#---------------------------------------------------------------
   def goEnd(self, string=''):
#---------------------------------------------------------------
      self.pos1=self.offset + self.maxIter
      self.pos2=self.pos1 + self.WINDOW

#---------------------------------------------------------------
   def moveForward(self, steps=1, cycling=True):
#---------------------------------------------------------------
      for s in range(steps):
         if self.end and cycling:
            self.goBeginning()   
         self.forward()  

#---------------------------------------------------------------
   def moveBackward(self, steps=1, cycling=True):
#---------------------------------------------------------------
      for s in range(steps):
         if self.start and cycling:
            self.goEnd()   
         self.backward()  

################################################################
class YADthread():
################################################################

#---------------------------------------------------------------
   def __init__(self, _process, _args=()):
#---------------------------------------------------------------
      self.process = _process
      self.args = _args
      self.process = Thread(target=_process, args=_args)
      self.process.deamon = True
      self.lastError = ''
      self.finished = False
      
#---------------------------------------------------------------
   def start(self):
#---------------------------------------------------------------
      try:
         self.process.start()
      except:
         self.lastError = "Error: unable to start thread"
         print self.lastError
  
#---------------------------------------------------------------
   def isAlive(self):
#---------------------------------------------------------------
      return self.process.isAlive()

#---------------------------------------------------------------
   def join(self):
#---------------------------------------------------------------
      return self.process.join()
         
#---------------------------------------------------------------
   def stop(self):
#---------------------------------------------------------------
      try:
         self.process._Thread__stop()
         self.process.join()
         self.finished = True     
      except:
         self.lastError = str(self.getName()) + ' could not be terminated'
         print(self.lastError)


##################################################################################################################         
class keyboardPoller(Thread):
##################################################################################################################         
   def __init__(self, verbose=False): 
      Thread.__init__(self)
      
      self.logger = logFacility(module='keyboardPoller')
      self.verbose=verbose

      self.lastKeyStroke=''
      self.anyKey=False #olvidar con timer (hacer una clase para medir tiempo entre eventos
      self.keyPressed=False
      self.anyKeyPressed=False
      self.stopMain = False
      
      self.responseTime=.001
      
      self.KPRESS=2
      self.KDOWN=1
      self.KUP=0
      
      self.shift=0
      self.control=0
      self.alt=0
      
      self.keyDown = False
      
      try:
         self.device = map(InputDevice, ('/dev/input/event0', '/dev/input/event1'))
         self.device = {dev.fd : dev for dev in self.device}
         self.keyboardPresent = True
      except: 
         self.keyboardPresent = False
         print 'keyboardPoller: no devices where found!'
         
      self.readerProcess = YADthread(self.keyboardReader)
      self.keyboardReaderExit = False

      if self.verbose: 
         try:
            for dev in self.device.values(): print(dev)
         except: 
            pass   

      self.pshift=False
      self.pcontrol=False
      self.palt=False  
      
      self.keybAvailable = False  
      self.kBuffer=[]  
      self.maxBuffer=2
      
      self.defineKeybMap()

#--------------------------------------------------------      
   def 	defineKeybMap(self):
#--------------------------------------------------------      
      
      self.modifiers = [42,54,29,56,100]
      
      self.keyboard = {
         2:'1', 3:'2', 4:'3', 5:'4', 6:'5', 7:'6', 8:'7', 9:'8', 10:'9', 11:'0',   
         12:'-', 13:'=', 14: 'BACKSPACE',
         16:'q', 17:'w', 18:'e', 19:'r', 20:'t', 21:'y', 22:'u', 23:'i', 24:'o', 25:'p',   
         26:'[', 27:']',
         30:'a', 31:'s', 32:'d', 33:'f', 34:'g', 35:'h', 36:'j', 37:'k', 38:'l',   
         39:';', 40:"'''", 41:"'`'", 43:"'\'",   
         44:'z', 45:'x', 46:'c', 47:'v', 48:'b', 49:'n', 50:'m', 51:',', 52:'.',   
         53:'/', 
         28: 'ENTER', 01:'ESCAPE', 15:'TAB', 58:'CAPSLOCK', 42:'SHIFT', 29:'CONTROL', 100:'ALT',
         57: ' ', 59: 'F1', 60: 'F2', 61: 'F3', 62: 'F4', 63: 'F5', 64: 'F6', 65: 'F7', 66: 'F8',
         105: 'LEFT', 106: 'RIGHT', 103: 'UP', 108: 'DOWN',
         272: 'LEFTMOUSE', 273: 'RIGHTMOUSE',
      }

      self.keyMap = [
#000     #0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18
         '','ESCAPE','1','2','3','4','5','6','7','8','9','0','-', '=', 'BACKSPACE','TAB','q','w','e',
         #19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,
         'r','t','y','u','i','o','p','[',']','ENTER', 'CONTROL', 'a','s','d','f','g','h','j','k','l', 
         #39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58
         ';',"\'","`",'', '\\','z','x','c','v','b','n','m',',','.', '/','','','',' ','CAPSLOCKS',    
         #59, 60, 61, 62, 63, 64, 65, 66, 67, 68
         'F1','F2','F3','F4','F5','F6','F7','F8','','',  
         #69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88
         '','','','','','','','','','','','','','','','','','','','',
#100     #89,90,91,92,93,94,95,96,97,98,99,00,01,02,03,04,05,06,07,08
         '','','','','','','','','','','','','','','UP','','LEFT','RIGHT','','DOWN',
         #09,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28
         '','','','','','','','','','','','','','','','','','','','',
         #29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48
         '','','','','','','','','','','','','','','','','','','','',
         #59,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68
         '','','','','','','','','','','','','','','','','','','','',
         #69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88
         '','','','','','','','','','','','','','','','','','','','',
#200     #89,90,91,92,93,94,95,96,97,98,99,00,01,02,03,04,05,06,07,08
         '','','','','','','','','','','','','','','','','','','','',
         #09,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28
         '','','','','','','','','','','','','','','','','','','','',
         #29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48
         '','','','','','','','','','','','','','','','','','','','',
         #49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68
         '','','','','','','','','','','','','','','','','','','','',
         #69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88
         '','','','LEFTMOUSE','RIGHTMOUSE','','','','','','','','','','','','','','','',


#SHIFT
#300     #0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18
         '','SHIFT+ESCAPE','!','@','#','$','%','\^','&','*','(',')','_', '+', 'SHIFT+BACKSPACE','SHIFT+TAB','Q','W','E',
         #19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,
         'R','T','Y','U','I','O','P','{','}','SHIFT+ENTER', 'SHIFT+CONTROL', 'A','S','D','F','G','H','J','K','L', 
         #39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58
         ':',"\"","~",'', '|','Z','X','C','V','B','N','M','<','>', '?','','','','SHIFT+SPACE','CAPSLOCKS',    
         #59, 60, 61, 62, 63, 64, 65, 66, 67, 68
         'SHIFT+F1','SHIFT+F2','SHIFT+F3','SHIFT+F4','SHIFT+F5','SHIFT+F6','SHIFT+F7','SHIFT+F8','','',  
         #69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88
         '','','','','','','','','','','','','','','','','','','','',
#400     #89,90,91,92,93,94,95,96,97,98,99,00,01,02,03,04,05,06,07,08
         '','','','','','','','','','','','','','','SHIFT+UP','','SHIFT+LEFT','SHIFT+RIGHT','','SHIFT+DOWN',
         #09,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28
         '','','','','','','','','','','','','','','','','','','','',
         #29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48
         '','','','','','','','','','','','','','','','','','','','',
         #59,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68
         '','','','','','','','','','','','','','','','','','','','',
         #69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88
         '','','','','','','','','','','','','','','','','','','','',
#500     #89,90,91,92,93,94,95,96,97,98,99,00,01,02,03,04,05,06,07,08
         '','','','','','','','','','','','','','','','','','','','',
         #09,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28
         '','','','','','','','','','','','','','','','','','','','',
         #29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48
         '','','','','','','','','','','','','','','','','','','','',
         #49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68
         '','','','','','','','','','','','','','','','','','','','',
         #69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88
         '','','','SHIFT+LEFTMOUSE','SHIFT+RIGHTMOUSE','','','','','','','','','','','','','','','t',

#CONTROL
#600     #0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18
         '','CTRL+ESCAPE','CTRL+1','CTRL+2','CTRL+3','CTRL+4','CTRL+5','CTRL+6','CTRL+7','CTRL+8','CTRL+9','CTRL+0','CTRL+-', 'CTRL+=', 'CTRL+BACKSPACE','CTRL+TAB','CTRL+q','CTRL+w','CTRL+e',
         #19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,
         'CTRL+r','CTRL+t','CTRL+y','CTRL+u','CTRL+i','CTRL+o','CTRL+p','CTRL+[','CTRL+]','CTRL+ENTER', 'CTRL+CONTROL', 'CTRL+a','CTRL+s','CTRL+d','CTRL+f','CTRL+g','CTRL+h','CTRL+j','CTRL+k','CTRL+l', 
         #39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58
         'CTRL+;',"CTRL+'","CTRL+`",'', 'CTRL+\\','CTRL+z','CTRL+x','CTRL+c','CTRL+v','CTRL+b','CTRL+n','CTRL+m','CTRL+,','CTRL+.', 'CTRL+/','','','','CTRL+SPACE','CAPSLOCKS',    
         #59, 60, 61, 62, 63, 64, 65, 66, 67, 68
         'CTRL+F1','CTRL+F2','CTRL+F3','CTRL+F4','CTRL+F5','CTRL+F6','CTRL+F7','CTRL+F8','','',  
         #69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88
         '','','','','','','','','','','','','','','','','','','','',
#700     #89,90,91,92,93,94,95,96,97,98,99,00,01,02,03,04,05,06,07,08
         '','','','','','','','','','','','','','','CTRL+UP','','CTRL+LEFT','CTRL+RIGHT','','CTRL+DOWN',
         #09,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28
         '','','','','','','','','','','','','','','','','','','','',
         #29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48
         '','','','','','','','','','','','','','','','','','','','',
         #59,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68
         '','','','','','','','','','','','','','','','','','','','',
         #69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88
         '','','','','','','','','','','','','','','','','','','','',
#800     #89,90,91,92,93,94,95,96,97,98,99,00,01,02,03,04,05,06,07,08
         '','','','','','','','','','','','','','','','','','','','',
         #09,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28
         '','','','','','','','','','','','','','','','','','','','',
         #29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48
         '','','','','','','','','','','','','','','','','','','','',
         #49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68
         '','','','','','','','','','','','','','','','','','','','',
         #69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88
         '','','','CTRL+LEFTMOUSE','CTRL+RIGHTMOUSE','','','','','','','','','','','','','','','',

#ALT
#900     #0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18
         '','ALT+SCAPE','F9','F10','F11','F12','ALT+5','ALT+6','ALT+7','ALT+8','ALT+9','ALT+0','ALT+-', 'ALT+=', 'DEL','ALT+TAB','ALT+q','ALT+w','ALT+e',
         #19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,
         'ALT+r','ALT+t','ALT+y','ALT+u','ALT+i','ALT+o','ALT+p','ALT+[','ALT+]','CTRL+ALT+DEL', 'ALT+CONTROL', 'ALT+a','ALT+s','ALT+d','ALT+f','ALT+g','ALT+h','ALT+j','ALT+k','ALT+l', 
         #39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58
         'ALT+;',"ALT+'","ALT+`",'', 'ALT+\\','ALT+z','ALT+x','ALT+c','ALT+v','ALT+b','ALT+n','ALT+m','ALT+,','ALT+.', 'ALT+/','','','','ALT+SPACE','CAPSLOCKS',    
         #59, 60, 61, 62, 63, 64, 65, 66, 67, 68
         'RF','PRTSC','MUTE','VOL-','VOL+','BACKWARD','PLAY','FORWARD','','',  
         #69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88
         '','','','','','','','','','','','','','','','','','','','',
#1000    #89,90,91,92,93,94,95,96,97,98,99,00,01,02,03,04,05,06,07,08
         '','','','','','','','','','','','','','','PAGEUP','','ALT+LEFT','ALT+RIGHT','','PAGEDOWN',
         #09,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28
         '','','','','','','','','','','','','','','','','','','','',
         #29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48
         '','','','','','','','','','','','','','','','','','','','',
         #59,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68
         '','','','','','','','','','','','','','','','','','','','',
         #69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88
         '','','','','','','','','','','','','','','','','','','','',
#1100    #89,90,91,92,93,94,95,96,97,98,99,00,01,02,03,04,05,06,07,08
         '','','','','','','','','','','','','','','','','','','','',
         #09,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28
         '','','','','','','','','','','','','','','','','','','','',
         #29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48
         '','','','','','','','','','','','','','','','','','','','',
         #49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68
         '','','','','','','','','','','','','','','','','','','','',
         #69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88
         '','','','ALT+LEFTMOUSE','ALT+RIGHTMOUSE','','','','','','','','','','','','','','','',      
      
#SHIFT+ALT
#1200     #0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18
         '','SHIFT+ALT+SCAPE','SHIFT+ALT+1','SHIFT+ALT+2','SHIFT+ALT+3','SHIFT+ALT+4','SHIFT+ALT+5','SHIFT+ALT+6','SHIFT+ALT+7','SHIFT+ALT+8','SHIFT+ALT+9','SHIFT+ALT+0','SHIFT+ALT+_', 'SHIFT+ALT++', 'SHIFT+ALT+BACKSPACE','SHIFT+ALT+TAB','SHIFT+ALT+Q','SHIFT+ALT+W','SHIFT+ALT+E',
         #19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,
         'SHIFT+ALT+R','SHIFT+ALT+T','SHIFT+ALT+Y','SHIFT+ALT+U','SHIFT+ALT+I','SHIFT+ALT+O','SHIFT+ALT+P','SHIFT+ALT+{','SHIFT+ALT+}','CTRL+SHIFT+ENTER', 'SHIFT+ALT+CONTROL', 'SHIFT+ALT+A','SHIFT+ALT+S','SHIFT+ALT+D','SHIFT+ALT+F','SHIFT+ALT+G','SHIFT+ALT+H','SHIFT+ALT+J','SHIFT+ALT+K','SHIFT+ALT+L', 
         #39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58
         'SHIFT+ALT+:',"SHIFT+ALT+\"","SHIFT+ALT+~",'', 'SHIFT+ALT+|','SHIFT+ALT+Z','SHIFT+ALT+X','SHIFT+ALT+C','SHIFT+ALT+V','SHIFT+ALT+B','SHIFT+ALT+N','SHIFT+ALT+M','SHIFT+ALT+<','SHIFT+ALT+>', 'SHIFT+ALT+?','','','','SHIFT+ALT+SPACE','CAPSLOCKS',    
         #59, 60, 61, 62, 63, 64, 65, 66, 67, 68
         'SHIFT+ALT+F1','SHIFT+ALT+F2','SHIFT+ALT+F3','SHIFT+ALT+F4','SHIFT+ALT+F5','SHIFT+ALT+F6','SHIFT+ALT+F7','SHIFT+ALT+F8','','',  
         #69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88
         '','','','','','','','','','','','','','','','','','','','',
#1300    #89,90,91,92,93,94,95,96,97,98,99,00,01,02,03,04,05,06,07,08
         '','','','','','','','','','','','','','','SHIFT+ALT+UP','','SHIFT+ALT+LEFT','SHIFT+ALT+RIGHT','','SHIFT+ALT+DOWN',
         #09,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28
         '','','','','','','','','','','','','','','','','','','','',
         #29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48
         '','','','','','','','','','','','','','','','','','','','',
         #59,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68
         '','','','','','','','','','','','','','','','','','','','',
         #69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88
         '','','','','','','','','','','','','','','','','','','','',
#1400    #89,90,91,92,93,94,95,96,97,98,99,00,01,02,03,04,05,06,07,08
         '','','','','','','','','','','','','','','','','','','','',
         #09,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28
         '','','','','','','','','','','','','','','','','','','','',
         #29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48
         '','','','','','','','','','','','','','','','','','','','',
         #49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68
         '','','','','','','','','','','','','','','','','','','','',
         #69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88
         '','','','SHIFT+ALT+LEFTMOUSE','SHIFT+ALT+RIGHTMOUSE','','','','','','','','','','','','','','','',
         
#CRTL+ALT
#1500     #0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18
         '','CTRL+ALT+SCAPE','CTRL+ALT+1','CTRL+ALT+2','CTRL+ALT+3','CTRL+ALT+4','CTRL+ALT+5','CTRL+ALT+6','CTRL+ALT+7','CTRL+ALT+8','CTRL+ALT+9','CTRL+ALT+0','CTRL+ALT+-', 'CTRL+ALT+=', 'DEL','CTRL+ALT+TAB','CTRL+ALT+q','CTRL+ALT+w','CTRL+ALT+e',
         #19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,
         'CTRL+ALT+r','CTRL+ALT+t','CTRL+ALT+y','CTRL+ALT+u','CTRL+ALT+i','CTRL+ALT+o','CTRL+ALT+p','CTRL+ALT+[','CTRL+ALT+]','CTRL+CTRL+ALT+DEL', 'CTRL+ALT+CONTROL', 'CTRL+ALT+a','CTRL+ALT+s','CTRL+ALT+d','CTRL+ALT+f','CTRL+ALT+g','CTRL+ALT+h','CTRL+ALT+j','CTRL+ALT+k','CTRL+ALT+l', 
         #39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58
         'CTRL+ALT+;',"CTRL+ALT+'","CTRL+ALT+`",'', 'CTRL+ALT+\\','CTRL+ALT+z','CTRL+ALT+x','CTRL+ALT+c','CTRL+ALT+v','CTRL+ALT+b','CTRL+ALT+n','CTRL+ALT+m','CTRL+ALT+,','CTRL+ALT+.', 'CTRL+ALT+/','','','','CTRL+ALT+SPACE','CAPSLOCKS',    
         #59, 60, 61, 62, 63, 64, 65, 66, 67, 68
         'CTRL+ALT+F1','CTRL+ALT+F2','CTRL+ALT+F3','CTRL+ALT+F4','CTRL+ALT+F5','CTRL+ALT+F6','CTRL+ALT+F7','CTRL+ALT+F8','','',  
         #69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88
         '','','','','','','','','','','','','','','','','','','','',
#1600    #89,90,91,92,93,94,95,96,97,98,99,00,01,02,03,04,05,06,07,08
         '','','','','','','','','','','','','','','CTRL+ALT+UP','','CTRL+ALT+LEFT','CTRL+ALT+RIGHT','','CTRL+ALT+DOWN',
         #09,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28
         '','','','','','','','','','','','','','','','','','','','',
         #29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48
         '','','','','','','','','','','','','','','','','','','','',
         #59,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68
         '','','','','','','','','','','','','','','','','','','','',
         #69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88
         '','','','','','','','','','','','','','','','','','','','',
#1700    #89,90,91,92,93,94,95,96,97,98,99,00,01,02,03,04,05,06,07,08
         '','','','','','','','','','','','','','','','','','','','',
         #09,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28
         '','','','','','','','','','','','','','','','','','','','',
         #29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48
         '','','','','','','','','','','','','','','','','','','','',
         #49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68
         '','','','','','','','','','','','','','','','','','','','',
         #69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88
         '','','','CTRL+ALT+LEFTMOUSE','CTRL+ALT+RIGHTMOUSE','','','','','','','','','','','','','','','',   
         
#SHIFT+CTRL
#1200     #0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18
         '','SHIFT+CTRL+SCAPE','SHIFT+CTRL+1','SHIFT+CTRL+2','SHIFT+CTRL+3','SHIFT+CTRL+4','SHIFT+CTRL+5','SHIFT+CTRL+6','SHIFT+CTRL+7','SHIFT+CTRL+8','SHIFT+CTRL+9','SHIFT+CTRL+0','SHIFT+CTRL+_', 'SHIFT+CTRL++', 'SHIFT+CTRL+BACKSPACE','SHIFT+CTRL+TAB','SHIFT+CTRL+Q','SHIFT+CTRL+W','SHIFT+CTRL+E',
         #19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,
         'SHIFT+CTRL+R','SHIFT+CTRL+T','SHIFT+CTRL+Y','SHIFT+CTRL+U','SHIFT+CTRL+I','SHIFT+CTRL+O','SHIFT+CTRL+P','SHIFT+CTRL+{','SHIFT+CTRL+}','CTRL+SHIFT+ENTER', 'SHIFT+CTRL+CONTROL', 'SHIFT+CTRL+A','SHIFT+CTRL+S','SHIFT+CTRL+D','SHIFT+CTRL+F','SHIFT+CTRL+G','SHIFT+CTRL+H','SHIFT+CTRL+J','SHIFT+CTRL+K','SHIFT+CTRL+L', 
         #39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58
         'SHIFT+CTRL+:',"SHIFT+CTRL+\"","SHIFT+CTRL+~",'', 'SHIFT+CTRL+|','SHIFT+CTRL+Z','SHIFT+CTRL+X','SHIFT+CTRL+C','SHIFT+CTRL+V','SHIFT+CTRL+B','SHIFT+CTRL+N','SHIFT+CTRL+M','SHIFT+CTRL+<','SHIFT+CTRL+>', 'SHIFT+CTRL+?','','','','SHIFT+CTRL+SPACE','CAPSLOCKS',    
         #59, 60, 61, 62, 63, 64, 65, 66, 67, 68
         'SHIFT+CTRL+F1','SHIFT+CTRL+F2','SHIFT+CTRL+F3','SHIFT+CTRL+F4','SHIFT+CTRL+F5','SHIFT+CTRL+F6','SHIFT+CTRL+F7','SHIFT+CTRL+F8','','',  
         #69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88
         '','','','','','','','','','','','','','','','','','','','',
#1300    #89,90,91,92,93,94,95,96,97,98,99,00,01,02,03,04,05,06,07,08
         '','','','','','','','','','','','','','','SHIFT+CTRL+UP','','SHIFT+CTRL+LEFT','SHIFT+CTRL+RIGHT','','SHIFT+CTRL+DOWN',
         #09,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28
         '','','','','','','','','','','','','','','','','','','','',
         #29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48
         '','','','','','','','','','','','','','','','','','','','',
         #59,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68
         '','','','','','','','','','','','','','','','','','','','',
         #69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88
         '','','','','','','','','','','','','','','','','','','','',
#1400    #89,90,91,92,93,94,95,96,97,98,99,00,01,02,03,04,05,06,07,08
         '','','','','','','','','','','','','','','','','','','','',
         #09,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28
         '','','','','','','','','','','','','','','','','','','','',
         #29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48
         '','','','','','','','','','','','','','','','','','','','',
         #49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68
         '','','','','','','','','','','','','','','','','','','','',
         #69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88
         '','','','SHIFT+CTRL+LEFTMOUSE','SHIFT+CTRL+RIGHTMOUSE','','','','','','','','','','','','','','','',]
                  
#--------------------------------------------------------      
   def 	showSpecialKeys(self):
#--------------------------------------------------------      
      if self.shift and not self.pshift: 
         print 'shift down'
         self.pshift=True
      if not self.shift and self.pshift: 
         print 'shift up'
         self.pshift=False
      if self.control and not self.pcontrol: 
         print 'control down'
         self.pcontrol=True
      if not self.control and self.pcontrol: 
         print 'control up'
         self.pcontrol=False
      if self.alt and not self.palt: 
         print 'alt down'
         self.palt=True
      if not self.alt and self.palt: 
         print 'alt up'
         self.palt=False

#--------------------------------------------------------      
   def 	resetLastKey(self):
#--------------------------------------------------------      
      sleep(.05)
      self.lastKeyStroke = ''
      self.keybAvailable = False
      self.anyKeyPressed=False
      self.anyKey=False
#--------------------------------------------------------      
   def 	getLastKey(self):
#--------------------------------------------------------      
      returnValue = self.lastKeyStroke
      return returnValue   

#--------------------------------------------------------      
   def isAnyKeyPressed(self):
#--------------------------------------------------------      
      return self.anyKeyPressed   

#--------------------------------------------------------      
   def 	popLastKey(self):
#--------------------------------------------------------      
      if self.keybAvailable: 
         try:
            returnValue = self.kBuffer[0]
            self.kBuffer.pop(0)
            if len(self.kBuffer) == 0: self.keybAvailable = False 
         except: 
            returnValue=''   
         return returnValue
      else: 
         return ''   
           
#--------------------------------------------------------      
   def run(self):
#--------------------------------------------------------      

      self.readerProcess.start()

      while not self.stopMain: 
         if self.verbose: self.showSpecialKeys()            
         sleep(.1)

#--------------------------------------------------------      
   def keyboardReader(self):
#--------------------------------------------------------      
      while not self.keyboardReaderExit:
         
         #keyTime=dateTime()
         
         if self.keyboardPresent:
            r1,w1,x1 = select(self.device, [], [])
            for fd in r1:
               for event in self.device[fd].read():
                  self.keyPressed=False
                  self.offset=0
                  
                  if event.type==1: 
                         
                     if event.value==self.KDOWN or event.value==self.KPRESS: 
                     
                        self.keyDown = True
                        if event.code==42: self.shift=289
                        if event.code==29: self.control=289*2
                        if event.code==100: self.alt=289*3

                        if self.verbose: print 'type: %d shift %d, control %d, alt %d, code %d, value %d, sum %d, offset %d, char %s'%(event.type, self.shift, self.control, self.alt, event.code, event.value, self.shift+self.control+self.alt+event.code, self.offset ,self.keyMap[self.offset+self.shift+self.control+self.alt+event.code])
                        
                        if (event.code not in self.modifiers): 
                           #keyTime.startTimer()
                           try: 
                              self.anyKeyPressed=True
                              self.keybAvailable = True
                              self.lastKeyStroke = self.keyMap[self.shift+self.control+self.alt+event.code]
                           
                              if self.shift!=0 and self+control!=0 and self.alt==0: 
                                 self.offset = 227                           
                     
                              
                              if lastKeyStroke == '': 
                                 self.logger.logMessage(self.shift+self.control+self.alt+event.code, severity='WARNING')
                           except Exception as err: 
                              pass    
                                             
                     if event.value==self.KUP: 
                     
                        self.keyDown = False
                        #print 'keyup'
                        if event.code==42: self.shift=0
                        if event.code==29: self.control=0
                        if event.code==100: self.alt=0
                        #if (event.code not in self.modifiers): 
                           #keyTime.stopTimer()
                           #print keyTime.timeLapsed()
                        self.resetLastKey()
                        self.anyKeyPressed=False


         sleep(self.responseTime)



#--------------------------------------------------------      
   def stop(self):
#--------------------------------------------------------      
      self.logger.logMessage('Exiting from keyboard poller')
      self.keyboardReaderExit=True
      self.stopMain=True
      self.readerProcess.stop()
      
      
#############################################################
def signal_handler(signal, frame): 
   par.stop()
   print 'exiting...'   
   exit(0)
   
      
#################################################
class gmailBox():
#################################################

   IMAP_SERVER = 'imap.gmail.com'
   IMAP_PORT = '993'
   IMAP_USE_SSL = True

   SMTP_SERVER = 'smtp.gmail.com'
   SMTP_PORT = '587'

#------------------------------------------------   
   def __init__(self, user, password):
#------------------------------------------------   
      self.user = user
      self.password = password
     

      if self.IMAP_USE_SSL:
         self.imap = imaplib.IMAP4_SSL(self.IMAP_SERVER, self.IMAP_PORT)
      else:
         self.imap = imaplib.IMAP4(self.IMAP_SERVER, self.IMAP_PORT)

     
      self.resetError()
     
      self.verbose = True

      self.header = None
     
      self.connected = False
      
      self.validEmails = []
      self.secret = '00000'

#------------------------------------------------   
   def setSecret(self, secret):
#------------------------------------------------   
      self.secret = secret

#------------------------------------------------   
   def setVerbose(self, verbose = True):
#------------------------------------------------   
      self.verbose = verbose

#------------------------------------------------   
   def addValidEmail(self, email):
#------------------------------------------------   
      self.validEmails.append(email)
      
#------------------------------------------------   
   def isValidEmail(self, fromEmail, subject): 
#------------------------------------------------   
      returnValue=False
      for e in self.validEmails: 
         if e in fromEmail and self.secret in subject: returnValue=True
      return returnValue

#------------------------------------------------   
   def sendMail(self, to="", subject='dummy', message='dummy email'):
#------------------------------------------------   
      self.resetError()
     
      if not to: to = self.user
      try:
         smtpserver = smtplib.SMTP(self.SMTP_SERVER,self.SMTP_PORT)
      except Exception as err:
         if self.verbose:
            print "sendMail error: \n   %s"%err  
         self.errorMessage = err
         self.error = True 
         return False

      smtpserver.ehlo()
      smtpserver.starttls()
      smtpserver.ehlo
     
      try:
         smtpserver.login(self.user, self.password)
      except Exception as err:
         if self.verbose:
            print "sendMail (login) error: \n   %s"%err  
         self.errorMessage = err
         self.error = True 
         return  False  

      header = 'To:' + to + '\n' + 'From: ' + self.user + '\n' + 'Subject: %s \n'%subject
      msg = header + '\n%s\n\n'%message
      		
      if self.verbose:
         print msg

      try:
         smtpserver.sendmail(self.user, to, msg)
      except Exception as err:
         if self.verbose:
            print "sendMail (login) error: \n   %s"%err  
         self.errorMessage = err
         self.error = True 
         return False 

      if self.verbose:
         print 'message sent!'

      smtpserver.close()
      
      return True

#------------------------------------------------   
   def getError(self):
#------------------------------------------------   
      return (self.error,self.errorMessage)
      
#------------------------------------------------   
   def resetError(self):
#------------------------------------------------   
      self.errorMessage = ""
      self.error = False

#------------------------------------------------   
   def connect(self, mailbox='inbox'):
#------------------------------------------------   
      self.resetError()
      try:
         status,data = self.imap.login(self.user, self.password)
      except Exception as err:
         if self.verbose:
            print "connect (login) error: \n   %s"%err  
         self.errorMessage = err
         self.error = True 
         return False  


      self.resetError()
      try:
         status,data = self.imap.select(mailbox)
         if status == 'NO':
            self.errorMessage = data[0]
            self.error = True
            return False
             
      except Exception as err:
         if self.verbose:
            print "connect (select) error: \n   %s"%err  
         self.errorMessage = err
         self.error = True
         return False

      self.connected = True
      
      return True
 
#------------------------------------------------   
   def close(self):
#------------------------------------------------   
      self.imap.close()
      self.imap.logout()
 
#------------------------------------------------   
   def getCount(self, mtype = 'ALL', mailbox="inbox"):
#------------------------------------------------   
      self.resetError()
     
      if not self.connected:
         if not self.connect(mailbox):
				return False
        
      returnValue = -1     
      try:
         status, data = self.imap.search(None, mtype)
         returnValue = sum(1 for num in data[0].split())
      except Exception as err:
         if self.verbose:
            print "getCount error: \n   %s"%err  
         self.errorMessage = err
         self.error = True 
        
      return returnValue

#------------------------------------------------   
   def getEmailUIDs(self, mtype = 'ALL', last = 0):
#------------------------------------------------   
      self.resetError()

      if not self.connected:
         self.errorMessage = 'gmailBox is not connected'
         self.error = True 
         return iter([])

      data =[]
      returnValue = iter(data)     
      try:
         result, data = self.imap.uid('search', None, mtype)
         if last > 0:
            t = 0
            temp = []
            for i in reversed(data[0].split()):
               temp.append(i)
               t += 1
               if t > last-1: break
            returnValue = iter(temp)
         else:
            returnValue = iter(data[0].split())
           
      except Exception as err:
         if self.verbose:
            print "getEmailUIDs error: \n   %s"%err  
         self.errorMessage = err
         self.error = True 
        
      return returnValue

#------------------------------------------------   
   def getTo(self):
#------------------------------------------------   
     if self.header:
        return self.header['TO']
     else:
        return '' 

#------------------------------------------------   
   def getFrom(self):
#------------------------------------------------   
     if self.header:
        return self.header['FROM']
     else:
        return '' 

#------------------------------------------------   
   def getSubject(self):
#------------------------------------------------   
     if self.header:
        return self.header['SUBJECT']
     else:
        return '' 

#------------------------------------------------   
   def getDate(self):
#------------------------------------------------   
     if self.header:
        return self.header['DATE']
     else:
        return '' 

#------------------------------------------------   
   def fetchHeader(self, num):
#------------------------------------------------   
      self.resetError()     

      if not self.connected:
         self.errorMessage = 'gmailBox is not connected'
         self.error = True 
         return

      try:
         status, data = self.imap.uid('fetch', num, '(BODY.PEEK[HEADER])')
         self.header = email.message_from_string(data[0][1])
      except Exception as err:
         if self.verbose:
            print "fetchHeader error: \n   %s"%err  
         self.errorMessage = err
         self.error = True 
    
    
#------------------------------------------------   
   def fetchMessage(self, num):
#------------------------------------------------   
      self.resetError()     

      if not self.connected:
         self.errorMessage = 'gmailBox is not connected'
         self.error = True 
         return

      try:
         status, data = self.imap.uid('fetch', num, '(RFC822)')
         email_msg = email.message_from_string(data[0][1])
         
         return email_msg
      except Exception as err:
         if self.verbose:
            print "fetchMessage error: \n   %s"%err  
         self.errorMessage = err
         self.error = True 
         return ""
 
#------------------------------------------------   
   def delete_message(self, num):
#------------------------------------------------   
      self.resetError()     

      if not self.connected:
         self.errorMessage = 'gmailBox is not connected'
         self.error = True 
         return

      try:
         self.imap.store(num, '+FLAGS', r'\Deleted')
         self.imap.expunge()
      except Exception as err:
         if self.verbose:
            print "fetchMessage error: \n   %s"%err  
         self.errorMessage = err
         self.error = True 
 
#         status, data = self.imap.search(None, 'TO', email_address)
#         data = [d for d in data if d is not None]
#         if status == 'OK' and data:
#            for num in reversed(data[0].split()):
#               status, data = self.imap.fetch(num, '(RFC822)')
#               email_msg = email.message_from_string(data[0][1])#
#               return email_msg

############################### 
class sound(): 
###############################

#------------------------------------------------   
   def __init__(self):
#------------------------------------------------   
      from pygame import mixer
      self.error = 0
      self.errorMessage = ''
      
      self.soundFiles = {}
      
      mixer.init()

#------------------------------------------------   
   def addSound(self, soundName, soundFile):
#------------------------------------------------   
      self.error=0
      self.errorMessage=''
      if os.path.isfile(soundFile): 
         try:
             self.soundFiles[soundName]=mixer.Sound(soundFile)
         except Exception as err: 
            self.errorMessage = err
            self.error  = -1
      else: 
         self.error = -2
         self.errorMessage = 'sound class: %s no such sound file'%soundFile

#------------------------------------------------   
   def getLength(self, soundName='', soundFile=''):
#------------------------------------------------   
      returnValue = 0
      if soundName!='': 
         returnValue = self.soundFiles[soundName].get_length()

      if soundFile !='':   
         returnValue = mixer.Sound(soundFile).get_length()
         
      return returnValue
         
#------------------------------------------------   
   def play(self, soundName=''):
#------------------------------------------------   
      if self.error==0:
         try: 
            self.soundFiles[soundName].play()
         except: 
            pass
      return self.error
              
#------------------------------------------------   
   def playFile(self, soundFile):
#------------------------------------------------   
      self.error=0
      self.errorMessage=''
      if os.path.isfile(soundFile): 
         try:
             mixer.Sound(soundFile).play()
         except Exception as err: 
            self.errorMessage = err
            self.error  = -1
      else: 
         self.error = -2
         self.errorMessage = 'sound class: %s no such sound file'%soundFile


#------------------------------------------------   
   def getError(self):
#------------------------------------------------   
      return self.error
      
############################### 
def importPlaylists(path, extension='m3u'):
############################### 
   tree=treeList()
   
   path = os.path.abspath(path)
   
   if not os.path.isdir(path): 
      return tree
      
   directory = sorted(glob(os.path.abspath(path)+'/*-*.'+extension))

   importedArtist = ''
   for file in directory: 
      filename = file.split('-')
      artist = filename[0].split('/')[-1]
      fullPathArtist = filename[0]
      
      if importedArtist != artist:
         importedArtist =  artist    
         tree.addItem(importedArtist, parentName=tree.ROOT, filename=file)
      if not 'all.'+extension in filename[1]: 
         tree.addItem(filename[1].split('.')[0],parentName=importedArtist, filename=file)

   return tree

############################### 
def importPlaylistsFromList(listOfFiles, extension='m3u'):
############################### 
   tree=treeList()
         
   importedArtist = ''
   for file in listOfFiles: 
      filename = file.split('-')
      artist = filename[0]
      
      if importedArtist != artist:
         importedArtist =  artist    
         tree.addItem(importedArtist, parentName=tree.ROOT)
      if not 'all' in filename: 
         tree.addItem(filename[1].split('.')[0],parentName=importedArtist)
    
   return tree

############################### 
class iSpeedTest(): 
###############################

#------------------------------------------------   
   def __init__(self, home='/home/ydirgan/', appName='speedTest'):
#------------------------------------------------   
      self.logFile = os.path.abspath(home) + '/%s.log'%appName      

      self.log = logFacility(module=appName, logFile=self.logFile)
      
      self.command = '/usr/local/bin/speedtest-cli'
      
      self.error = False
      
      if not os.path.isfile(self.command):
         self.error = True
         
      self.speedTest = shellCommand(self.command+' --simple') 
            
#------------------------------------------------   
   def test(self):
#------------------------------------------------   
      if self.error:
         return ('-1','-1','-1')
      else:   
         returnValue = ['-1 ms','-1 Mbits/s','-1 Mbits/s']
         for line in self.speedTest.run():
            try:
               if 'Ping' in line: returnValue[0] = line.split(': ')[1].split(' ms')[0]
               if 'Download' in line: returnValue[1] = line.split(': ')[1].split(' Mbit/s')[0]
               if 'Upload' in line: returnValue[2] = line.split(': ')[1].split(' Mbit/s')[0]
            except:
               pass   
         
         self.log.logMessage(',%s,%s,%s'%(returnValue[0],returnValue[1],returnValue[2]))
         
         return returnValue

   
############################### 
class fifo(): 
###############################

#------------------------------------------------   
   def __init__(self):
#------------------------------------------------   
      self.listOfItems = treeList()
      
#------------------------------------------------   
   def push(self, element):
#------------------------------------------------   
      self.listOfItems.addItem(element, parentName = self.listOfItems.ROOT)
      return self

#------------------------------------------------   
   def hasItems(self):
#------------------------------------------------   
      if self.listOfItems.numberOfItems() > 0:
         return True
      else:
         return False
         
#------------------------------------------------   
   def pop(self):
#------------------------------------------------   
      returnValue = ''
      if self.listOfItems.numberOfItems() > 0:
         returnValue = self.listOfItems.goFirst().activeLabel()
         self.listOfItems.deleteActiveItem()
      
      return returnValue
         
   
############################### 
class logFacility(): 
###############################

   SEVERITY = { 'NOSET'   :  (0, 'NOSET'),
                'DEBUG'   : (10, 'DEBUG'),
                'INFO'    : (20, 'INFO'),
                'WARNING' : (30, 'WARNING'),
                'ERROR'   : (40, 'ERROR'),
                'CRITICAL': (50, 'CRITIAL'),
   } 
#------------------------------------------------   
   def __init__(self, module = 'not assigned', logFile = None, print2console = True):
#------------------------------------------------   
      self._module = module
      self._severity = self.SEVERITY['INFO'][1]
      self._file = logFile
      if logFile == None:
         self._write2disk = False
      else: 
         self._write2disk = True  
      
      self.print2console = print2console
      'format = _module:_severity [_date _time] _message'
      self._format = '%s:%s [%s %s] %s'
      
      self._dateTime = dateTime()
      
      self.log = shellCommand('echo')
      
#------------------------------------------------   
   def logMessage(self, message='no message', severity = 'INFO'):
#------------------------------------------------   

      self._dateTime.refresh()
         
      try: 
         _severity = self.SEVERITY[severity][1]
      except: 
         _severity = '(SEVERITY NOT FOUND)'
        
      _msg = self._format%(self._module, _severity, self._dateTime.classicDate, self._dateTime.classicStime, message)
               
      if self.print2console: print _msg
               
      if self._write2disk: self.log.replaceCommand('echo "%s" >> %s'%(_msg,self._file)).runBackground()   


############################### 
class speech(): 
###############################

#------------------------------------------------   
   def __init__(self, path = './', language='EN'):
#------------------------------------------------   
      self.log = logFacility(module = 'speech in yadlib')
      self.speechPath = os.path.abspath(path)
      
      if language == 'EN':
         self.speechBin = self.speechPath+'/speech_en.sh'
      elif language == 'ES': 
         self.speechBin = self.speechPath+'/speech_es.sh'
      else:   
         self.speechBin = self.speechPath+'/speech_en.sh'
         
      self.error=0
      
      
      #create it if not found as a file
      #speech_es.sh
      #!/bin/bash
      #say() { local IFS=+;/usr/bin/mplayer -ao alsa -really-quiet -noconsolecontrols "http://translate.google.com/translate_tts?tl=en&q=$*"; }
      #say $*

      #speech_es.sh
      #!/bin/bash
      #say() { local IFS=+;/usr/bin/mplayer -ao alsa -really-quiet -noconsolecontrols "http://translate.google.com/translate_tts?tl=es&q=$*"; }
      #say $*
      
      
      if not os.path.isfile(self.speechBin): 
         self.log.logMessage(message='speech excutable not found at %s'%self.speechPath, severity='ERROR')
         self.error = 1
      
      self.sayText = shellCommand('%s speech test'%self.speechBin)
      

#------------------------------------------------   
   def say(self, text, runInBackground = True):
#------------------------------------------------   
      if self.error == 0:
         self.sayText.replaceCommand('%s %s'%(self.speechBin, text))
         if runInBackground:
            self.sayText.runBackground()
         else: 
            self.sayText.run()
                
      elif self.error==1:    
         self.log.logMessage(message='speech excutable not found at %s'%self.speechPath, severity='ERROR')

#------------------------------------------------   
   def repeatLast(self):
#------------------------------------------------   
      if self.error == 0:
         self.sayText.runBackground()
      elif self.error==1:    
         self.log.logMessage(message='speech excutable not found at %s'%self.speechPath, severity='ERROR')


############################### 
class nfc(): 
###############################

#------------------------------------------------   
   def __init__(self, verbose = True):
#------------------------------------------------         
      self.verbose = verbose
      self.log = logFacility(module = 'nfc in yadlib')
      self.resetError()
      
      self.uid = None
      
      self.db = {}
      
      self.nfc = shellCommand('nfc-list')

#------------------------------------------------   
   def resetError(self):
#------------------------------------------------         
      self.error = 0
      self.errorMessage = ''
      
#------------------------------------------------   
   def poll(self):
#------------------------------------------------         
      self.resetError()
      self.uid = None
      for line in self.nfc.run(): 
         if 'UID' in line: 
            uid=line.split()
            try: 
               self.uid = '%s-%s-%s-%s'%(uid[2],uid[3],uid[4],uid[5])
            except: 
               pass   
         elif 'ERROR' in line: 
            self.error=1
            if self.verbose:
               self.log.logMessage(message='%s'%line, severity='ERROR')
            self.errorMessage = line
      
      if self.nfc.status(): 
         self.error = 2
         if self.verbose:
            self.log.logMessage(message='nfc-list binary not found!', severity='ERROR')
         self.errorMessage = 'nfc-list binary not found!'

      return self.uid

#------------------------------------------------   
   def getUid(self):
#------------------------------------------------         
      return self.uid

#------------------------------------------------   
   def addUid(self, name, uid):
#------------------------------------------------         
      self.db[uid] = name

#------------------------------------------------   
   def printUid(self):
#------------------------------------------------         
      self.resetError()
      try: 
         print self.db[self.uid]
         sleep(.5)
      except: 
         print '%s not found'%self.uid   
         self.error = 3
         self.errorMessage = '%s not found'%self.uid 

#------------------------------------------------   
   def getError(self):
#------------------------------------------------         
      return (self.error, self.errorMessage)

###############################
def internet_on():
###############################
    returnValue = True
    try:
       response=urlopen('http://www.google.com',None, 1)
    except: 
       returnValue = False
    
    return returnValue 
    

###############################
def socketClient(host='localhost', port=6600, command='', timeout=10):
###############################
    RECV_SIZE = (2**20)*10 #10 megabytes
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    
    returnData = []

    try:
       s.connect((host, int(port)))
       if command: s.send(command+'\n')
       s.shutdown(socket.SHUT_WR)

       tempData = ''
 
       while True:
           data = s.recv(RECV_SIZE)
           if data: tempData += data
           if not data:
               break
       s.close()    

       returnData = ''.join(tempData).splitlines() 

    except Exception, e: 
       returnData.append(str(e)) 
           

    return returnData

##################################################################################################################         
class mpdClient():
##################################################################################################################         
    DEFAULTPLAYLISTDIR = '/home/pi/scripts/piMusicMedia/playlists/list1'
    MP3='mp3'
    RADIO='radio'

    def __init__(self, playListDir = DEFAULTPLAYLISTDIR, host='localhost', port=6600, logFile=None, verbose=False):
       
       self.log = logFacility(module='mpdClient', logFile = logFile )
       self.lastError = 'no error'
       self.status = {}
       self.currentSong = {}
       
       self.verbose = verbose
       
       if self.verbose:
          self.log.logMessage('(init mpdClient) is in verbose mode')  

       self.playListDir = playListDir
       
       self.host = host
       self.port = port
       
       if self.checkMpd() != 'service mpd OK': 
          self.log.logMessage('(init mpdClient) service mpd not available! [%s]'%self.lastError)  

       self.getStatus()
       
       try: 
          if self.lastError == 'no error':
             self.lastVolume = int(self.status['volume'])
          else:   
             self.lastVolume = 0
       except Exception as err:
          pass          
          
#-------------------------------------------------------------------------------------------------------------------
    def checkMpd(self): 
#-------------------------------------------------------------------------------------------------------------------
       
       try:
          status=socketClient(host=self.host, port=self.port, command='')
          
          returnValue = ''
          
          tError = ['Errno' in item for item in status]
          if True in tError: 
             self.lastError = status[tError.index(True)].split(']')[1].strip()
             returnValue = self.lastError
          else:   
             self.lastError='no error'
             returnValue = 'service mpd OK'
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             

       return returnValue   
           
#-------------------------------------------------------------------------------------------------------------------
    def getStatus(self): 
#-------------------------------------------------------------------------------------------------------------------
       self.lastError = 'no error'

       try:       
          status=socketClient(host=self.host, port=self.port, command='status')

          tError = ['Errno' in item for item in status]
          if True in tError: 
             self.lastError = status[tError.index(True)].split(']')[1].strip()
          else:   
             for item in status: 
                if ':' in item: 
                   field = item.split(':',1)
                   self.status[field[0]] = field[1].strip()
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             
       
       return self.status
       
#-------------------------------------------------------------------------------------------------------------------
    def getCurrentSong(self): 
#-------------------------------------------------------------------------------------------------------------------
       self.lastError = 'no error'
        
       try:        
          self.currentSong = {}
          
          currentSong=socketClient(host=self.host, port=self.port, command='currentsong')
          tError = ['Errno' in item for item in currentSong]
          if True in tError: 
             self.lastError = currentSong[tError.index(True)].split(']')[1].strip()
          else:   
             for item in currentSong: 
                if ':' in item: 
                   field = item.split(':',1)
                   self.currentSong[field[0]] = field[1].strip()
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             
       
       return self.currentSong 
#-------------------------------------------------------------------------------------------------------------------
    def setPlaylistPath(self, path): 
#-------------------------------------------------------------------------------------------------------------------
       self.lastError = 'no error'
       
       try:
          path = os.path.abspath(path)
          
          if not os.path.isdir(path): 
             self.lastError = 'playlist path is not valid'
             self.state = 'playlist path not found'
             return

       except Exception as err:
          if self.verbose: print(traceback.format_exc())             
          
       self.playListDir = path 

#-------------------------------------------------------------------------------------------------------------------
    def getError(self): 
#-------------------------------------------------------------------------------------------------------------------
       return self.lastError

#-------------------------------------------------------------------------------------------------------------------
    def mute(self, dimm=0, refresh=True): 
#-------------------------------------------------------------------------------------------------------------------
       try:
          if refresh:
             self.getStatus()
          
          if self.lastError != 'no error': return

          self.volume = int(self.status['volume'])

          if self.volume == dimm: 
             socketClient(host=self.host, port=self.port, command='setvol %d'%self.lastVolume)
             self.lastVolume = dimm            
          else:
             socketClient(host=self.host, port=self.port, command='setvol %d'%dimm)
             self.lastVolume = self.volume
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             

#-------------------------------------------------------------------------------------------------------------------
    def increaseVolume(self, increment = 5, refresh=True): 
#-------------------------------------------------------------------------------------------------------------------
       try:   
          if refresh:
             self.getStatus()
          
          if self.lastError != 'no error': return

          self.volume = int(self.status['volume'])

          if self.volume < 100: 
             self.volume += increment

          if self.volume >= 100:
             self.volume = 100

          socketClient(host=self.host, port=self.port, command='setvol %d'%self.volume)
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             
              
       return self.volume   

#-------------------------------------------------------------------------------------------------------------------
    def decreaseVolume(self, decrement = 5, refresh=True): 
#-------------------------------------------------------------------------------------------------------------------   
       try:
          if refresh:
             self.getStatus()
          
          if self.lastError != 'no error': return

          self.volume = int(self.status['volume'])

          if self.volume > 0: 
             self.volume -= decrement

          if self.volume < 0:
             self.volume = 0   

          socketClient(host=self.host, port=self.port, command='setvol %d'%self.volume)
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             
       
       return self.volume

#-------------------------------------------------------------------------------------------------------------------
    def setVolume(self, volume=50, refresh=False): 
#-------------------------------------------------------------------------------------------------------------------   
       #print 'setVolume: called by %s'%stack()[1][3]
       try:
          if volume > 100: volume = 100 
          if volume < 0: volume = 0   

          socketClient(host=self.host, port=self.port, command='setvol %d'%volume)
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             

       return volume

#-------------------------------------------------------------------------------------------------------------------
    def getVolume(self, refresh=True): 
#-------------------------------------------------------------------------------------------------------------------
       try:   
          if refresh:
             self.getStatus()
          
          if self.lastError != 'no error': return

          self.volume = int(self.status['volume'])
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             
       
       return self.volume       

#-------------------------------------------------------------------------------------------------------------------
    def play(self, number=None, refresh=False): 
#-------------------------------------------------------------------------------------------------------------------
       #print 'play command: called by %s'%stack()[1][3]
       try:
          if number == None: 
             socketClient(host=self.host, port=self.port, command='play')
          else:    
             socketClient(host=self.host, port=self.port, command='play %s'%(int(number) -1))
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             
                

#-------------------------------------------------------------------------------------------------------------------
    def add(self, song='', listOfSongs=[], refresh=False): 
#-------------------------------------------------------------------------------------------------------------------
       try:
          if song:
             socketClient(host=self.host, port=self.port, command='add "%s"'%song)

          if listOfSongs: 
             for song in listOfSongs:
                socketClient(host=self.host, port=self.port, command='add "%s"'%song)
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             
  
#-------------------------------------------------------------------------------------------------------------------
    def toggle(self, refresh=True): 
#-------------------------------------------------------------------------------------------------------------------
       #print 'toggle command: called by %s'%stack()[1][3]
       try:
          if refresh:
             self.getStatus()
          
          if self.lastError != 'no error': return

          state = self.status['state']

          if state != 'play': 
             socketClient(host=self.host, port=self.port, command='play')
          else: 
             socketClient(host=self.host, port=self.port, command='pause')
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             
        
#-------------------------------------------------------------------------------------------------------------------
    def pause(self, refresh=False): 
#-------------------------------------------------------------------------------------------------------------------
       #print 'pause command: called by %s'%stack()[1][3]
       try:
          socketClient(host=self.host, port=self.port, command='pause')
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             
          
#-------------------------------------------------------------------------------------------------------------------
    def stop(self, refresh=False): 
#-------------------------------------------------------------------------------------------------------------------
       try:
          socketClient(host=self.host, port=self.port, command='stop')
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             

#-------------------------------------------------------------------------------------------------------------------
    def next(self, refresh=False): 
#-------------------------------------------------------------------------------------------------------------------
       try:
          socketClient(host=self.host, port=self.port, command='next')
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             
 
#-------------------------------------------------------------------------------------------------------------------
    def previous(self, refresh=False): 
#-------------------------------------------------------------------------------------------------------------------
       try:
          socketClient(host=self.host, port=self.port, command='previous')
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             
 
#-------------------------------------------------------------------------------------------------------------------
    def shuffle(self, refresh=False): 
#-------------------------------------------------------------------------------------------------------------------
       try:
          socketClient(host=self.host, port=self.port, command='shuffle')
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             

#-------------------------------------------------------------------------------------------------------------------
    def toggleRepeat(self, refresh=True): 
#-------------------------------------------------------------------------------------------------------------------
       try:
          if refresh:
             self.getStatus()
          
          if self.lastError != 'no error': return

          state = self.status['repeat']

          if state == '0': 
             socketClient(host=self.host, port=self.port, command='repeat 1')
          else:    
             socketClient(host=self.host, port=self.port, command='repeat 0')
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             

#-------------------------------------------------------------------------------------------------------------------
    def setRepeatOn(self): 
#-------------------------------------------------------------------------------------------------------------------
       try:
          if self.lastError != 'no error': return

          socketClient(host=self.host, port=self.port, command='repeat 1')
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             

#-------------------------------------------------------------------------------------------------------------------
    def setRepeatOff(self): 
#-------------------------------------------------------------------------------------------------------------------
       try:
          if self.lastError != 'no error': return

          socketClient(host=self.host, port=self.port, command='repeat 0')
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             

#-------------------------------------------------------------------------------------------------------------------
    def toggleRandom(self, refresh=True): 
#-------------------------------------------------------------------------------------------------------------------
       try:
          if refresh:
             self.getStatus()
          
          if self.lastError != 'no error': return

          state = self.status['random']

          if state == '0': 
             socketClient(host=self.host, port=self.port, command='random 1')
          else:    
             socketClient(host=self.host, port=self.port, command='random 0')
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             

#-------------------------------------------------------------------------------------------------------------------
    def setRandomOn(self): 
#-------------------------------------------------------------------------------------------------------------------
       try:
          if self.lastError != 'no error': return

          socketClient(host=self.host, port=self.port, command='random 1')
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             

#-------------------------------------------------------------------------------------------------------------------
    def setRandomOff(self): 
#-------------------------------------------------------------------------------------------------------------------
       try:
          if self.lastError != 'no error': return

          socketClient(host=self.host, port=self.port, command='random 0')
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             

#-------------------------------------------------------------------------------------------------------------------
    def toggleSingle(self, refresh=True): 
#-------------------------------------------------------------------------------------------------------------------
       try:
          if refresh:
             self.getStatus()
          
          if self.lastError != 'no error': return

          state = self.status['single']

          if state == '0': 
             socketClient(host=self.host, port=self.port, command='single 1')
          else:    
             socketClient(host=self.host, port=self.port, command='single 0')
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             

#-------------------------------------------------------------------------------------------------------------------
    def setSingleOn(self): 
#-------------------------------------------------------------------------------------------------------------------
       try:
          if self.lastError != 'no error': return

          socketClient(host=self.host, port=self.port, command='single 1')
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             

#-------------------------------------------------------------------------------------------------------------------
    def setSingleOff(self): 
#-------------------------------------------------------------------------------------------------------------------
       try:
          if self.lastError != 'no error': return

          socketClient(host=self.host, port=self.port, command='single 0')
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             

#-------------------------------------------------------------------------------------------------------------------
    def toggleConsume(self, refresh=True): 
#-------------------------------------------------------------------------------------------------------------------
       try:
          if refresh:
             self.getStatus()
          
          if self.lastError != 'no error': return

          state = self.status['consume']

          if state == '0': 
             socketClient(host=self.host, port=self.port, command='consume 1')
          else:    
             socketClient(host=self.host, port=self.port, command='consume 0')
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             

#-------------------------------------------------------------------------------------------------------------------
    def setConsumeOn(self): 
#-------------------------------------------------------------------------------------------------------------------
       try:
          if self.lastError != 'no error': return

          socketClient(host=self.host, port=self.port, command='consume 1')
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             

#-------------------------------------------------------------------------------------------------------------------
    def setConsumeOff(self): 
#-------------------------------------------------------------------------------------------------------------------
       try:
          if self.lastError != 'no error': return

          socketClient(host=self.host, port=self.port, command='consume 0')
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             

#-------------------------------------------------------------------------------------------------------------------
    def clear(self, refresh=False): 
#-------------------------------------------------------------------------------------------------------------------
       try:
          socketClient(host=self.host, port=self.port, command='clear')
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             

#-------------------------------------------------------------------------------------------------------------------
    def load(self, playList): 
#-------------------------------------------------------------------------------------------------------------------
       try:
          if playList: 
             for pl in playList: 
              socketClient(host=self.host, port=self.port, command='load %s'%pl)
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             

#-------------------------------------------------------------------------------------------------------------------
    def listPlayLists(self, artist=None, refresh=False, avoid=None, avoidStartWith='%'): 
#-------------------------------------------------------------------------------------------------------------------

       returnData = []
       
       try:
          for pl in socketClient(host=self.host, port=self.port, command='listplaylists', timeout=30): 
             if 'playlist:' in pl: 
                playlist = pl.split(':')[1].strip()
                if artist == None:
                   if avoid != None:
                      if not avoid in playlist:
                         if not playlist.startswith(avoidStartWith):
                            returnData.append(playlist)
                   else:
                      if not playlist.startswith(avoidStartWith):
                         returnData.append(playlist)
                      
                else:
                   if artist+'-' in playlist:
                      if avoid != None:
                         if not avoid in playlist:
                            if not playlist.startswith(avoidStartWith):
                               returnData.append(playlist)
                      else:
                         if not playlist.startswith(avoidStartWith):
                            returnData.append(playlist)

       except Exception as err:
          if self.verbose: print(traceback.format_exc())             

                 
       return iter(sorted(returnData))                   	

#-------------------------------------------------------------------------------------------------------------------
    def loadRadioLists(self, ext='pls', refresh=False): 
#-------------------------------------------------------------------------------------------------------------------      

       playLists = []

       try:
          playListDir = shellCommand('ls %s'%self.playListDir)
          try: 
             for i in playlistDir.run(): 
                if i.find(ext)>=0:
                   playLists.append(i.split('.%s'%ext)[0])       
          except Exception as err: 
             if self.verbose: print(traceback.format_exc())             
             self.lastError = str(err) 

       except Exception as err:
          if self.verbose: print(traceback.format_exc())             
       
       return iter(sorted(playLists))  
                                   
#-------------------------------------------------------------------------------------------------------------------
    def loadPlayLists(self, ext='m3u', refresh=False): 
#-------------------------------------------------------------------------------------------------------------------      

       playLists = []
       try:
          playListDir = shellCommand('ls %s'%self.playListDir)
          try: 
             for i in playListDir.run(): 
                if i.find(ext)>=0:
                   playLists.append(i.split('.%s'%ext)[0])       
          except Exception as err: 
             if self.verbose: print(traceback.format_exc())             
             self.lastError = str(err) 

       except Exception as err:
          if self.verbose: print(traceback.format_exc())             
       
       return iter(sorted(playLists))  

#-------------------------------------------------------------------------------------------------------------------
    def getGenre(self, refresh=True): 
#-------------------------------------------------------------------------------------------------------------------

       returnValue = 'no album' 
       try:
          if refresh:
             self.getCurrentSong()
          
          if self.lastError != 'no error': return
         
          if 'Genre' in self.currentSong.keys(): 
             try: 
                returnValue = self.currentSong['Genre']
             except Exception as err: 
                if self.verbose: print(traceback.format_exc())             
             self.lastError = 'error getting Album Genre'

       except Exception as err:
          if self.verbose: print(traceback.format_exc())             
       
       return returnValue

#-------------------------------------------------------------------------------------------------------------------
    def getAlbumDate(self, refresh=True): 
#-------------------------------------------------------------------------------------------------------------------
       returnValue = 'no album' 

       try:
          if refresh:
             self.getCurrentSong()
          
          if self.lastError != 'no error': return
          
          if 'Date' in self.currentSong.keys(): 
             try: 
                returnValue = self.currentSong['Date']
             except: 
                if self.verbose: print(traceback.format_exc())             
                self.lastError = 'error getting Album Date'
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             
       
       return returnValue

#-------------------------------------------------------------------------------------------------------------------
    def getAlbum(self, refresh=True): 
#-------------------------------------------------------------------------------------------------------------------
       returnValue = 'no album' 

       try:
          if refresh:
             self.getCurrentSong()
          
          if self.lastError != 'no error': return
          
          if 'Album' in self.currentSong.keys(): 
             try: 
                returnValue = self.currentSong['Album']
             except: 
                if self.verbose: print(traceback.format_exc())             
                self.lastError = 'error getting Album'

       except Exception as err:
          if self.verbose: print(traceback.format_exc())             
       
       return returnValue
       
#-------------------------------------------------------------------------------------------------------------------
    def getTitle(self, refresh=True): 
#-------------------------------------------------------------------------------------------------------------------

       returnValue = 'no title' 

       try:
          if refresh:
             self.getCurrentSong()
          
          if self.lastError != 'no error': return
          
          if 'Title' in self.currentSong.keys(): 
             try: 
                returnValue = self.currentSong['Title']
             except: 
                self.lastError = 'error getting Title'
          elif 'file' in self.currentSong.keys() : 
             try: 
                returnValue = self.currentSong['file'].split('/')[-1].split('.mp3')[0]
             except: 
                if self.verbose: print(traceback.format_exc())             
                self.lastError = 'error getting Title'

       except Exception as err:
          if self.verbose: print(traceback.format_exc())             
       
       return returnValue
       
#-------------------------------------------------------------------------------------------------------------------
    def getArtist(self, refresh=True): 
#-------------------------------------------------------------------------------------------------------------------

       returnValue = 'no artist' 

       try:
          if refresh:
             self.getCurrentSong()
          
          if self.lastError != 'no error': return
          
          if self.getMediaType() == 'mp3':
             if 'Artist' in self.currentSong.keys(): 
                try: 
                   returnValue = self.currentSong['Artist']
                except: 
                   self.lastError = 'error getting Atist'
             elif 'file' in self.currentSong.keys() : 
                try: 
                   returnValue = self.currentSong['file'].split('/')[0]
                except: 
                   if self.verbose: print(traceback.format_exc())             
                   self.lastError = 'error getting Atist'
          elif self.getMediaType() == 'radio':
               returnValue = self.getRadioStation()

       except Exception as err:
          if self.verbose: print(traceback.format_exc())             
            
       return returnValue

#-------------------------------------------------------------------------------------------------------------------
    def cpPlayLists(self, playlist, destination, ext='m3u', refresh=False): 
#-------------------------------------------------------------------------------------------------------------------      
       self.resetError()
       plist = self.playListDir + '/' + playlist + '.' + ext
       
       command='cp %s %s/.'%(plist, os.path.abspath(destination))       
       
       cp = shellCommand(command)

       try: 
          cp.run()
       except Exception as err: 
          if self.verbose: print(traceback.format_exc())             
          self.lastError = str(err) 
          self.status = str(err)
       
       return 
             
#-------------------------------------------------------------------------------------------------------------------
    #position as %percent
    def goPercent(self, position, refresh=True): 
#-------------------------------------------------------------------------------------------------------------------      
       self.lastError = 'no error'

       try:
          if refresh:
             self.getCurrentSong()

          if self.lastError == 'no error': 
             try: 
                status=socketClient(host=self.host, port=self.port, command='seek %s %s'%(int(self.currentSong['Pos']), int(float(self.currentSong['Time'])*float(position)/100)))
                tError = ['Errno' in item for item in status]
                if True in tError: 
                   try: 
                      self.lastError = status[tError.index(True)].split(']')[1].strip()
                   except Exception as err:
                      if self.verbose: print(traceback.format_exc())             
                      self.lastError = 'error going to especific percentage of the song'
             except Exception as err:
                if self.verbose: print(traceback.format_exc())             
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             

#-------------------------------------------------------------------------------------------------------------------
    #delta in seconds
    def seek(self, position = None, offset=0, relative=False, refresh=False): 
#-------------------------------------------------------------------------------------------------------------------      
       try:
			 self.offset(position=position, delta=offset, relative=relative)
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             
       
#-------------------------------------------------------------------------------------------------------------------
    #delta in seconds
    def offset(self, position = None, delta=0, relative=True, refresh=True): 
#-------------------------------------------------------------------------------------------------------------------      
       self.lastError = 'no error'

       if refresh:
          self.getStatus()
          self.getCurrentSong()
       
       if position == None: 
          songPos = int(self.currentSong['Pos'])
       else: 
          try: 
             songPos = position - 1
          except Exception as err:
             if self.verbose: print(traceback.format_exc())             
             songPos = 0      
       
       if self.lastError == 'no error': 
          if relative: 
             try:
                time=self.status['time']
                elapsed = int(time.split(':')[0])
                total= int(time.split(':')[1])
                if (elapsed+delta) < total or (elapsed+delta) > 0 : 
                   status=socketClient(host=self.host, port=self.port, command='seek %s %s'%(songPos, elapsed+delta))
                   tError = ['Errno' in item for item in status]
                   if True in tError: 
                      try:
                         self.lastError = status[tError.index(True)].split(']')[1].strip()
                      except Exception as err:
                        if self.verbose: print(traceback.format_exc())             
                        self.lastError = 'error setting offset'
             except Exception as err:
                if self.verbose: print(traceback.format_exc())             
                self.lastError = 'error setting offset'
          else: 
             try:
                status=socketClient(host=self.host, port=self.port, command='seek %s %s'%(songPos, abs(delta)))
             except Exception as err:
                if self.verbose: print(traceback.format_exc())             
          

#-------------------------------------------------------------------------------------------------------------------
    def setVerboseOn(self): 
#-------------------------------------------------------------------------------------------------------------------
       self.verbose = True
       
#-------------------------------------------------------------------------------------------------------------------
    def setVerboseOff(self): 
#-------------------------------------------------------------------------------------------------------------------
       self.verbose = False        

#-------------------------------------------------------------------------------------------------------------------
    def updateInfo(self): 
#-------------------------------------------------------------------------------------------------------------------
       self.getStatus()
       self.getCurrentSong()
       
#-------------------------------------------------------------------------------------------------------------------
    def updateMpcDb(self, refresh=False): 
#-------------------------------------------------------------------------------------------------------------------
 
       returnValue = '(OK) updating'
       status=socketClient(host=self.host, port=self.port, command='update')
       tError = ['Errno' in item for item in status]
       updating = ['updating' in item for item in status]
       if True in tError and not True in updating:
          returnValue = '(ERROR) mpc cant update the database' 
          try:  
             self.lastError = status[tError.index(True)].split(']')[1].strip()
          except Exception as err:
             if self.verbose: print(traceback.format_exc())             
             self.lastError = 'error updating mpd database'
 
       return returnValue      
#-------------------------------------------------------------------------------------------------------------------
    def getPlayState(self, refresh=True): 
#-------------------------------------------------------------------------------------------------------------------
       if refresh:
          self.getStatus()
       
       try: 
          returnValue = self.status['state']
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             
          returnValue = 'stop'

       return returnValue

#-------------------------------------------------------------------------------------------------------------------
    def getSong(self, refresh=False): 
#-------------------------------------------------------------------------------------------------------------------
       return self.getTitle() 

#-------------------------------------------------------------------------------------------------------------------
    def getCurrentSongList(self): 
#-------------------------------------------------------------------------------------------------------------------
       status=socketClient(host=self.host, port=self.port, command='playlist')

       returnValue = []

       tError = ['Errno' in item for item in status]
       if True in tError: 
          try:
             self.lastError = status[tError.index(True)].split(']')[1].strip()
          except Exception as err:
             if self.verbose: print(traceback.format_exc())             
             self.lastError = 'error getting current song list'
       else:   
          for i in status: 
            line = i.split('file:')
            try:  
               returnValue.append(line[1].strip())
            except Exception as err:
               #ignore lines that are not files
               pass             

       return returnValue 
              
#-------------------------------------------------------------------------------------------------------------------
    def getSongFilename(self, refresh=True): 
#-------------------------------------------------------------------------------------------------------------------
       if refresh:
          self.getCurrentSong()
       
       returnValue = 'no song filename'
       if self.lastError == 'no error':
          try: 
             returnValue = self.currentSong['file']
          except Exception as err:
             if self.verbose: print(traceback.format_exc())             
 
       return returnValue 

#-------------------------------------------------------------------------------------------------------------------
    def getSongPos(self, refresh=True): 
#-------------------------------------------------------------------------------------------------------------------
       if refresh:
          self.getCurrentSong()
       returnValue = 0
       if self.lastError == 'no error':
          try: 
             returnValue = int(self.currentSong['Pos'])+1
          except Exception as err:
             if self.verbose: print(traceback.format_exc())             
       
       return returnValue 

#-------------------------------------------------------------------------------------------------------------------
    def countSongs(self, refresh=True): 
#-------------------------------------------------------------------------------------------------------------------
       if refresh:
          self.getCurrentSong()

       returnValue = 0
       if self.lastError == 'no error':
          try: 
             returnValue = len(self.getCurrentSongList())
          except Exception as err:
             if self.verbose: print(traceback.format_exc())             

       return returnValue 

#-------------------------------------------------------------------------------------------------------------------
    def getSongTimeLapsed(self, refresh=False): 
#-------------------------------------------------------------------------------------------------------------------

       try:
         returnValue = int(self.getSongTimeLapsed_float())  
       except Exception as err:
          if self.verbose: print(traceback.format_exc())             

       return returnValue
       
#-------------------------------------------------------------------------------------------------------------------
    def getSongTimeLapsed_float(self, refresh=True): 
#-------------------------------------------------------------------------------------------------------------------
       if refresh:
          self.getStatus()
       
       returnValue = 0
       if self.lastError == 'no error':
          try: 
             returnValue = float(self.status['elapsed'])
          except Exception as err:
             if self.verbose: print(traceback.format_exc())             
       
       return returnValue 

#-------------------------------------------------------------------------------------------------------------------
    def getFloatSongPercent(self, decimals=2, refresh=True): 
#-------------------------------------------------------------------------------------------------------------------
       if refresh:
          self.getStatus()
       
       returnValue = 0
       if self.lastError == 'no error':
          try: 
             elapsed = int(self.status['time'].split(':')[0])
             total = int(self.status['time'].split(':')[1])
             returnValue = float("{0:.2f}".format((float(elapsed)/float(total)*100)))
          except Exception as err:
             if self.verbose: print(traceback.format_exc())             
       
       return returnValue 

#-------------------------------------------------------------------------------------------------------------------
    def getSongPercent(self, refresh=True): 
#-------------------------------------------------------------------------------------------------------------------
       if refresh:
          self.getStatus()
       
       returnValue = 0
       if self.lastError == 'no error':
          try: 
             elapsed = int(self.status['time'].split(':')[0])
             total = int(self.status['time'].split(':')[1])
             returnValue = int(float(elapsed)/float(total)*100)
          except Exception as err:
             if self.verbose: print(traceback.format_exc())             
       
       return returnValue 

#-------------------------------------------------------------------------------------------------------------------
    def getRandom(self, refresh=True): 
#-------------------------------------------------------------------------------------------------------------------
       if refresh:
          self.getStatus()
       
       returnValue = 0
       if self.lastError == 'no error':
          try: 
             if self.status['random'] == '1': 
                returnValue = True
             else: 
                returnValue = False   
          except Exception as err:
             if self.verbose: print(traceback.format_exc())             
       
       return returnValue 

#-------------------------------------------------------------------------------------------------------------------
    def getRadioStation(self, refresh=True): 
#-------------------------------------------------------------------------------------------------------------------
       if refresh:
          self.getCurrentSong()
       
       returnValue = 'no radio station'
       if self.lastError == 'no error' and self.getMediaType() == 'radio':
          try:
             returnValue = self.currentSong['Name']
          except Exception as err:
             if self.verbose: print(traceback.format_exc())             
             try:
                returnValue = self.currentSong['Title']
             except Exception as err:
                if self.verbose: print(traceback.format_exc())             
                returnValue = self.currentSong['file'] 
                       
       return returnValue 

#-------------------------------------------------------------------------------------------------------------------
    def getMediaType(self, refresh=True): 
#-------------------------------------------------------------------------------------------------------------------
       if refresh:
          self.getCurrentSong()
       
       returnValue = 'unknown'
       if self.lastError == 'no error':
          try: 
             if 'http://' in self.currentSong['file']: 
                returnValue = 'radio'
             else: 
                returnValue = 'mp3'   
          except Exception as err:
             if self.verbose: print(traceback.format_exc())             
       
       return returnValue 


############################### 
############################### 
############################### 
############################### 
############################### 
############################### 
class userMusicContext(): 
###############################
   
   USERMUSICCONTEXT_VERSION = '0.6.7'

   #HISTORY OF CHANGES
   # 0.6.7
   # remove all tables and useless procedures
   # add stattion type to addStation and listStations functions

   LISTLABEL='listsholder'
   DEFAULTUSER = 'newuser'
   DEFAULTLIST = 'general'
   PLACEHOLDER = 'placeholder'
   MPDUSER = 'mpduser'
   PRESETUSER = 'presetstation'
   DEFAULTPLAYLISTDIR = '/home/ydirgan/playlists'
   MUSICPATH = '/home/ydirgan/Music'
   

   USERS = { 'USERNAME': 0,
             'NAME': 1,
             'EMAIL': 2,
             'MOBILLE': 3,
             'PASSWD': 4,
             'NFCID': 5,
             'ACTIVE': 6,
             'VOLUME': 7,
              }
#------------------------------------------------   
   def __init__(self, userPath='./', playlistsPath = DEFAULTPLAYLISTDIR, musicPath = MUSICPATH, dbName = 'userMusicContext.db', create = False, logFile = None, verbose=True):
#------------------------------------------------          
      self.init = False
      self.verbose = verbose
      self.printError = False
      self.log = logFacility(module = 'userMusicContext class', logFile = logFile)
      self.resetError()
      
      self.firstUserPlaylistChar = '%'
      
      self.defaultVolume = 50
      self.defaultRandom = 0
      self.defaultASC = 0
      self.defaultT2CR = 20
      self.defaultSoundActivated = 1
      self.defaultVervose = 0
      self.defaultPlaylistPath = os.path.abspath(playlistsPath)
      self.musicPath = os.path.abspath(musicPath)

      self.setPath(userPath)
      self.dbName =  dbName
      self.dbPath = self.home+'/'+dbName
      
      self.playlistsPath = playlistsPath
      
      self.activeUser = None
      self.activeId = None

      self.db = None
      
      self.usersFields = []
      self.stationsFields = []
      self.playlistsFields = []
      
      self.jumpToSong = pickList()

      self.specialUsers = [self.MPDUSER, self.PRESETUSER]
      
      self.dbConnect(create)
      
      if self.verbose: self.log.logMessage(message='(init userMusicContext) is is verbose mode')
      
      self.mp3 = mpdClient(playListDir = playlistsPath, logFile=logFile, verbose=self.verbose) 

      #self.voice = speech(path=userPath,language = 'ES')    
      
      #self.internetTest()
      
      self.activeUser = self.getActiveUser()
      
#------------------------------------------------   
   def getMusicPath(self):
#------------------------------------------------  
      return self.musicPath

#------------------------------------------------   
   def setMusicPath(self, musicPath):
#------------------------------------------------  
      self.musicPath=musicPath

#------------------------------------------------   
   def internetTest(self):
#------------------------------------------------  
      self.internetOn = YADthread(internet_on).start()
               
#------------------------------------------------   
   def welcomeUser(self, backg=False):
#------------------------------------------------  
      if not self.internetOn: return
      #cambiar a nombre cuando podamos colocarlo desde la aplicacion
      dt=dateTime()
      
      hour = int(dt.classicStime.split(':')[0])
      #if hour > 0 and hour <=12:
      #   self.voice.say('Buenos Dias '+self.getActiveUserDetails()[0]['username'], runInBackground=False)
      #elif hour > 12 and hour <=18:   
      #   self.voice.say('Buenas Tardes '+self.getActiveUserDetails()[0]['username'], runInBackground=False)
      #elif hour >18:   
      #   self.voice.say('Buenas Noches '+self.getActiveUserDetails()[0]['username'], runInBackground=False)

#------------------------------------------------   
   def saySentence(self, sentence, backg=False):
#------------------------------------------------  
      if self.internetOn: pass #self.voice.say(sentence, runInBackground=backg)

#------------------------------------------------   
   def setVerboseOn(self):
#------------------------------------------------         
      self.verbose = True

#------------------------------------------------   
   def setVerboseOff(self):
#------------------------------------------------         
      self.verbose = False

#------------------------------------------------   
   def resetError(self):
#------------------------------------------------         
      self.error = 0
      self.errorMessage = ''

#--------------------------------------------------------      
   def setPath(self, home): 
#--------------------------------------------------------      
      self.resetError()
      
      _home = os.path.abspath(home)
      
      if not os.path.isdir(_home): 
         mkdir(_home)

      self.home = _home

#------------------------------------------------   
   def loadFields(self):
#------------------------------------------------         
      cursor = self.db.cursor()
      error = False
      try:
         cursor.execute('SELECT * FROM USERS')
         self.usersFields = [f[0] for f in cursor.description]               
      except Exception as err: 
         if self.verbose: print(traceback.format_exc())
         if self.verbose: self.log.logMessage(message='(loadFields) %s'%err, severity='FATAL')
         if self.verbose: self.log.logMessage(message='(loadFields) USERS table not found!', severity='FATAL')
         error = True 
      try:
         cursor.execute('SELECT * FROM STATIONS')
         self.stationsFields = [f[0] for f in cursor.description]               
      except Exception as err: 
         if self.verbose: print(traceback.format_exc())
         if self.verbose: self.log.logMessage(message='(loadFields) %s'%err, severity='FATAL') 
         if self.verbose: self.log.logMessage(message='(loadFields) STATIONS table not found!', severity='FATAL')
         error = True 
      try:
         cursor.execute('SELECT * FROM STATIONPLAYLISTS')
         self.stationPlaylistsFields = [f[0] for f in cursor.description]               
      except Exception as err: 
         if self.verbose: print(traceback.format_exc())
         if self.verbose: self.log.logMessage(message='(loadFields) %s'%err, severity='FATAL') 
         if self.verbose: self.log.logMessage(message='(loadFields) STATIONPLAYLISTS table not found!', severity='FATAL')
         error = True 
      if error: 
         exit(1)

 
#------------------------------------------------   
   def recreateDB(self):
#------------------------------------------------         
      self.createDbLayout()

#------------------------------------------------   
   def dbConnect(self, recreate = False):
#------------------------------------------------         
      self.resetError()
      
      if recreate or not os.path.isfile(self.dbPath): 
         self.createDbLayout()
      else: 
         try: 
            self.db = sqlite3.connect(self.dbPath, check_same_thread=False)
            self.db.text_factory = str
         except Exception as err:
            if self.verbose: print(traceback.format_exc())
            self.error = 1
            self.errorMessage = err
            self.log.logMessage(message=err, severity='ERROR')   
            
      cursor=self.db.cursor()
      cursor.execute('''SELECT * FROM USERS WHERE active=1''') 
     
      user=cursor.fetchone()
      if user != None: 
         self.activeUser = user[0]
         self.activeId = user[5]
         
      self.loadFields()   
            
#------------------------------------------------   
   def printDataStruct(self):
#------------------------------------------------         
      self.resetError()
      cursor = self.db.cursor()
      print '-'*40
      print 'Database: '+self.dbName
      print '-'*40
      for table in cursor.execute('''SELECT * FROM sqlite_master WHERE type="table"'''): 
         print table[2] + '(TABLE)'
         field = self.db.cursor()
         field.execute('SELECT * FROM %s'%table[2])
         field.fetchall()
         fieldnames=[f[0] for f in field.description]
            
         for i in fieldnames: 
            print '  --> '+i         

#------------------------------------------------   
   def dbFileExists(self):
#------------------------------------------------         
      dbExists = False
      if os.path.isfile(self.dbPath):
         dbExists = True      
      return dbExists   

#------------------------------------------------   
   def createDbLayout(self):
#------------------------------------------------         
      self.resetError()

      emptyFile(self.dbPath)
      
      if self.verbose: self.log.logMessage(message='(createDbLayout) recreating DB %s!'%self.dbPath, severity='INFO')

      try: 
         self.db = sqlite3.connect(self.dbPath, check_same_thread=False)
         self.db.text_factory = str

         cursor = self.db.cursor()
      
         #USERS TABLE
         cursor.execute('''
                       CREATE TABLE USERS(username TEXT PRIMARY KEY, name TEXT, email TEXT, type TEXT, enabled INTEGER, genre TEXT,
                       mobile TEXT, passwd TEXT, nfcid TEXT, active INTEGER, volume TEXT, loginsound TEXT, admin INTEGER,
                       gvar1 INTEGER, gvar2 INTEGER, gvar3 INTEGER, gvar4 INTEGER, gvar5 INTEGER, 
                       gvar6 INTEGER, gvar7 INTEGER, gvar8 INTEGER, gvar9 INTEGER, gvar10 INTEGER,
                       bio TEXT, url TEXT, similarartists TEXT)
                     ''')
         cursor.execute('''INSERT INTO USERS(username, name, email, mobile, passwd, nfcid, active, volume, loginsound, admin, type, enabled)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''', (self.MPDUSER,'','','','','',0,'50','',1,'SPECIAL', 1))
         cursor.execute('''INSERT INTO USERS(username, name, email, mobile, passwd, nfcid, active, volume, loginsound, admin, type, enabled)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''', (self.PRESETUSER,'','','','','',0,'50','',1,'SPECIAL', 1))
                                             
         #STATIONS TABLE
         cursor.execute('''
                       CREATE TABLE STATIONS(username TEXT, station TEXT, activestation INTEGER,                        
                                             activemediatype INTEGER, genre TEXT, mediatype INTEGER,
                                             songname TEXT, artistname TEXT, songpos TEXT, timelapsed TEXT, 
                                             state TEXT, favorite INTEGER, enabled INTEGER, type TEXT)
                     ''')

         #STATIONPLAYLISTS TABLE
         cursor.execute('''
                       CREATE TABLE STATIONPLAYLISTS(username TEXT, station TEXT, playlist TEXT, mediatype INTEGER)
                     ''')

         #SONGS TABLE
         cursor.execute('''
                       CREATE TABLE SONGS(username TEXT, station TEXT, playlist TEXT, song TEXT, number INTEGER, enabled INTEGER, count INTEGER, likeit INTEGER)
                     ''')

         #GENRES
         cursor.execute('''
                       CREATE TABLE GENRES(genrename TEXT)
                     ''')

         #PERSONAL PLAYLISTS TABLE for "grouping" stations
         cursor.execute('''
                       CREATE TABLE GROUPS(username TEXT, groupName TEXT, station TEXT, number INTEGER, enabled INTEGER, count INTEGER, likeit INTEGER)
                     ''')

         self.createIndexes()

         self.db.commit()      

      except Exception as err:
         if self.verbose: print(traceback.format_exc())
         self.error = 1
         self.errorMessage = err
         self.log.logMessage(message=err, severity='ERROR')   
      

#------------------------------------------------   
   def createIndexes(self):
#------------------------------------------------         
      self.resetError()
      returnValue = True
      if self.verbose: self.log.logMessage(message='(createIndexes) recreating Indexes %s!'%self.dbPath, severity='INFO')

      try: 
         self.db = sqlite3.connect(self.dbPath, check_same_thread=False)
         self.db.text_factory = str

         cursor = self.db.cursor()
      
         #USERS TABLE
         cursor.execute('''
                       CREATE INDEX IF NOT EXISTS userTable_username ON USERS (username)
                     ''')
         #STATIONS TABLE
         cursor.execute('''
                       CREATE INDEX IF NOT EXISTS stationTable_username ON STATIONS (username)
                     ''')
         cursor.execute('''
                       CREATE INDEX IF NOT EXISTS stationTable_station ON STATIONS (station)
                     ''')
         cursor.execute('''
                       CREATE INDEX IF NOT EXISTS stationTable_usernameStation ON STATIONS (username,station)
                     ''')

         #STATIONPLAYLISTS TABLE
         cursor.execute('''
                       CREATE INDEX IF NOT EXISTS stationPlaylistsTable_username ON STATIONPLAYLISTS (username)
                     ''')
         cursor.execute('''
                       CREATE INDEX IF NOT EXISTS stationPlaylistsTable_usernameStation ON STATIONPLAYLISTS (username,station)
                     ''')
         cursor.execute('''
                       CREATE INDEX IF NOT EXISTS stationPlaylistsTable_station ON STATIONPLAYLISTS (station)
                     ''')

         #SONGS TABLE
         cursor.execute('''
                       CREATE INDEX IF NOT EXISTS songsTable_username ON SONGS (username)
                     ''')
         cursor.execute('''
                       CREATE INDEX IF NOT EXISTS songsTable_station ON SONGS (station)
                     ''')
         cursor.execute('''
                       CREATE INDEX IF NOT EXISTS songsTable_playlist ON SONGS (playlist)
                     ''')
         cursor.execute('''
                       CREATE INDEX IF NOT EXISTS songsTable_userStationPlaylist ON SONGS (username,station,playlist)
                     ''')

         #GENRES TABLE
         cursor.execute('''
                       CREATE INDEX IF NOT EXISTS genresTable_genrename ON GENRES (genrename)
                     ''')

         #GROUPS TABLE
         cursor.execute('''
                       CREATE INDEX IF NOT EXISTS groupsTable_username ON GROUPS (username)
                     ''')
         cursor.execute('''
                       CREATE INDEX IF NOT EXISTS groupsTable_usernameGroupName ON GROUPS (username, groupName)
                     ''')
         cursor.execute('''
                       CREATE INDEX IF NOT EXISTS groupsTable_usernameGroupNameStation ON GROUPS (username, groupName, station)
                     ''')

         self.db.commit()      
         
         returnValue = True

      except Exception as err:
         if self.verbose: print(traceback.format_exc())
         self.error = 1
         self.errorMessage = err
         self.log.logMessage(message=err, severity='ERROR') 
         returnValue = False  
      
      return returnValue

#--------------------------------------------------------      
   def row2dict(self, row, fields): 
#--------------------------------------------------------      
      returnDict = {}
      i=0
      for f in fields: 
         try:
            returnDict[f]=row[i]
         except Exception as err: 
            if self.verbose: print(traceback.format_exc())
            if self.verbose: self.log.logMessage(message='(row2dict) %s'%err, severity='WARNING')  
            if self.verbose: self.log.logMessage(message='(row2dict) no se pudo cargar el campo %s'%(f), severity='WARNING')
         i+=1
      return (returnDict)

#--------------------------------------------------------      
   def getAllGVar(self, username = None): 
#--------------------------------------------------------      
      self.resetError()
      cursor = self.db.cursor()
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username  

      sql = 'SELECT gvar1,gvar2,gvar3,gvar4,gvar5,gvar6,gvar7,gvar8,gvar9,gvar10 FROM USERS WHERE username="%s"'%(_user)

      returnValue = []

      try: 
         cursor.execute(sql)
         gvars = cursor.fetchone()
         #print gvars
         v=1
         returnValue = {}
         for val in gvars:
				key='gvar%d'%v
				returnValue[key]=val
				v += 1

      except Exception as err: 
         if self.verbose: print(traceback.format_exc())
         if self.verbose: self.log.logMessage(message='(getAllGVar) %s'%err, severity='ERROR')  
         if self.verbose: self.log.logMessage(message='(getAllGVar) cant get %s'%var, severity='ERROR')
      
      return (returnValue)         

#--------------------------------------------------------      
   def getGVar(self, username = None, var='gvar1'): 
#--------------------------------------------------------      

      self.resetError()
      cursor = self.db.cursor()
      
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username  

      sql = 'SELECT "%s" FROM USERS WHERE username="%s"'%(var,_user)

      returnValue = None
      try: 
         cursor.execute(sql)
         returnValue = cursor.fetchone()[0]

      except Exception as err: 
         if self.verbose: print(traceback.format_exc())
         if self.verbose: self.log.logMessage(message='(getGVar) %s'%err, severity='ERROR')  
         if self.verbose: self.log.logMessage(message='(getGVar) cant get %s'%var, severity='ERROR')
      
      return (returnValue)         

#--------------------------------------------------------      
   def setGVar(self, value, username = None, var='gvar1', commit=False): 
#--------------------------------------------------------      

      self.resetError()
      cursor = self.db.cursor()
      
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username  

      sql = 'UPDATE USERS SET %s=%d WHERE username="%s"'%(var,value,_user)

      try: 
         cursor.execute(sql)
         returnValue = True
         
         if commit: 
            self.db.commit()
            if self.verbose: self.log.logMessage(message='(setGvar) commit transaction after setting [%s] on table USERS'%(var), severity='INFO')


      except Exception as err: 
         if self.verbose: print(traceback.format_exc())
         if self.verbose: self.log.logMessage(message='(getGVar) %s'%err, severity='ERROR')  
         if self.verbose: self.log.logMessage(message='(getGVar) cant get %s'%var, severity='ERROR')
         returnValue = False

      
      return (returnValue)         
         

#--------------------------------------------------------      
   def getUsersDetails(self, username = None, idNumber = None, allUsers=False, admin = 0): 
#--------------------------------------------------------      

      self.resetError()
      cursor = self.db.cursor()
      
      if username == None and idNumber == None: allUsers = True

      sql = 'SELECT * FROM USERS '
      
      if not allUsers: 
         if username != None: 
            sql += 'WHERE username = "%s" '%(username,)
         elif idNumber != None:   
            sql += 'WHERE nfcid = "%s" '%(idNumber,)
         sql += 'AND admin = "%s"'%(admin,)
      else: 
         sql += 'WHERE admin = "%s"'%(admin,)
      
      sql += ' ORDER BY username'
      
      returnUsers = []      
      try: 
         cursor.execute(sql)
            
         
         for user in cursor.fetchall(): 
            returnUsers.append(self.row2dict(user,self.usersFields)) 

      except Exception as err: 
         if self.verbose: print(traceback.format_exc())
         if self.verbose: self.log.logMessage(message='(getUsersDetails) %s'%err, severity='ERROR')  
         if self.verbose: self.log.logMessage(message='(getUsersDetails) no se pudieron obtener detalles de los usuarios', severity='ERROR')
      
      return (returnUsers)         

#--------------------------------------------------------      
   def listUsers(self, userType=None, allFieldsDelimited=False, admin=0): 
#--------------------------------------------------------      
      self.resetError()
      
      adm=admin
      
      resultList = []
      for user in self.getUsersDetails(admin=adm): 
         if userType != None:
            if user['type'] == userType:
               if allFieldsDelimited:
                  resultList.append('[%s],%s,%s'%('e' if user['enabled']==1 else 'd' ,user['username'], user['genre']))
               else:      
                  resultList.append(user['username'])
         else:      
            if allFieldsDelimited:
               resultList.append('[%s],%s,%s'%('e' if user['enabled']==1 else 'd' ,user['username'], user['genre']))
            else:      
               resultList.append(user['username'])
         
      return (resultList)

#--------------------------------------------------------      
   def userExists(self, username, table='USERS'): 
#--------------------------------------------------------      
      self.resetError()
      cursor = self.db.cursor()
      
      sentence='SELECT username FROM %s WHERE UPPER(username) = UPPER(?)'%table
      
      if table=='USERS': 
         sentence += 'AND admin = 0'
      
      user=None
      
      try:
         cursor.execute(sentence, (username,))
         user = cursor.fetchone()
      except Exception as err: 
         if self.verbose: print(traceback.format_exc())
         if self.verbose: self.log.logMessage(message='(userExists) %s'%err, severity='ERROR')  
         if self.verbose: self.log.logMessage(message='(userExists) no se pudo conseguir el usuario %s, problema en la base de datos'%(username), severity='ERROR')
      
      found = user!=None      

      return found

#--------------------------------------------------------      
   def idExists(self, idnumber, table='USERS'): 
#--------------------------------------------------------      
      if idnumber == None: return
      
      self.resetError()
      cursor = self.db.cursor()
      
      sentence='SELECT username FROM "%s" WHERE nfcid = "%s" '%(table,idnumber)
      
      if table=='USERS': 
         sentence += 'AND admin = 0'
            
      cursor.execute(sentence)
      user = cursor.fetchone()
      
      found = user!=None      

      if found:  
         if self.verbose: self.log.logMessage(message='(idExists) %s was found for user %s!'%(idnumber, user[0]), severity='INFO')
      else:
         if self.verbose: self.log.logMessage(message='(idExists) %s was not found!'%idnumber, severity='WARNING')

      return found


#saveactiveuser pending

#--------------------------------------------------------      
   def countPlaylists(self, station, username = None, mediatype=0): 
#--------------------------------------------------------      
      self.resetError()
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username  
      
      returnValue = 0
      try:   
         cursor = self.db.cursor()
         cursor.execute('SELECT COUNT(*) FROM STATIONPLAYLISTS WHERE username = "%s" AND station = "%s" AND mediatype = %s'%(_user, station, mediatype))
         returnValue = cursor.fetchone()[0]
      except Exception as err: 
         if self.verbose: print(traceback.format_exc())
         if self.verbose: self.log.logMessage(message='(countPlaylists) %s'%err, severity='ERROR')  
         if self.verbose: self.log.logMessage(message='(countPlaylists) hubo un problema al interrogar a la tabla stationplaylists!', severity='ERROR')
      
      return returnValue

#--------------------------------------------------------      
   def exportSongsToUserStation(self, station=None, username=None, toStation=None, toUser = None, genre='unknown', stationType='G'): 
#--------------------------------------------------------      
      self.resetError()
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username  
                  
      if station == None:
         _station = self.getActiveStation()
      else:
         _station = station
               
      if toStation != None and toUser != None:    
         try: 
            
            if not self.userExists(toUser):
               if self.verbose: self.log.logMessage(message='(exportSongsToUserStation) user %s was created!'%toUser, severity='INFO')
               self.addUser(toUser)
               
            if not self.stationExists(toStation, username=toUser):
               if self.verbose: self.log.logMessage(message='(exportSongsToUserStation) station %s was created to user %s!'%(toStation, toUser), severity='INFO')
               self.addStation(toStation, username=toUser, genre=genre, stationType='G') 
            
            cursor = self.db.cursor()
            sql = 'SELECT song FROM SONGS WHERE username = ? AND station = ? AND enabled = 1'
    
            cursor.execute(sql, (_user, _station))
            nSongs = cursor.fetchall()

            playlistFile = self.firstUserPlaylistChar+toUser.replace(' ','_')+'__'+toStation.replace(' ','_')

            songsInPlaylist = catFile(self.defaultPlaylistPath+'/'+playlistFile+'.m3u')

            if len(nSongs) > 0:
               songs = []
               for song in nSongs:
               
                  if not song[0] in songsInPlaylist: #no duplicates for eficiency
                     songs.append(song[0])

               writeItems2File(self.defaultPlaylistPath+'/'+playlistFile+'.m3u', songs)

               self.removePlaylistFromStation(playlistFile, toStation, username=toUser)
               self.addPlaylistInStation(playlistFile, toStation, username=toUser, genre=genre, dontPlay=True)
                  
         except Exception as err:
            if self.verbose: print(traceback.format_exc())
            if self.verbose: self.log.logMessage(message='(exportSongsToUserStation) could not export songs!', severity='ERROR')
      
      else:
         if self.verbose: self.log.logMessage(message='(exportSongsToUserStation) must indicate username and station to export to!', severity='ERROR')
      
      return 

#--------------------------------------------------------      
   def play(self, song, statistics=True): 
#--------------------------------------------------------      
      self.resetError()
      self.mp3.play(number=song)
      if statistics:
         self.sumToSongCount(song=song)      

      return self.mp3.getSong()

#--------------------------------------------------------      
   def countSongs(self, station=None, username = None, enabled=True, allStations = False, allSongs = False, mediatype=0): 
#--------------------------------------------------------      
      self.resetError()
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username  
                  
      if station == None:
         _station = self.getActiveStation()
      else:
         _station = station
      
      nSongs = -1
      try: 
         cursor = self.db.cursor()
         sql = 'SELECT COUNT(*) FROM SONGS WHERE username = "%s"'%_user
         if self.userExists(_user):
            if not allSongs:
               if enabled:
                  sql += ' AND enabled = 1'
               else:   
                  sql += ' AND enabled = 0'
            if self.stationExists(_station, _user) and not allStations:
               sql += ' AND station="%s" '%(_station)
 
            cursor.execute(sql)
            nSongs = cursor.fetchone()[0]
              	
      except Exception as err:
         if self.verbose: print(traceback.format_exc())
         if self.verbose: self.log.logMessage(message='(countSongs) problem when reading SONGS table!', severity='ERROR')
      
      return nSongs

#--------------------------------------------------------      
   def countStations(self, username = None, allStations=True): 
#--------------------------------------------------------      
      self.resetError()
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username  
      
      returnValue = 0
         
      try: 
         cursor = self.db.cursor()
         if allStations: #enabled and disabled
            cursor.execute('SELECT COUNT(*) FROM STATIONS WHERE username = "%s"'%_user)
         else: #only enabled
            cursor.execute('SELECT COUNT(*) FROM STATIONS WHERE username = "%s" AND enabled = 1'%_user)

         returnValue = cursor.fetchone()[0]/2
         
      except Exception as err: 
         if self.verbose: print(traceback.format_exc())
         if self.verbose: self.log.logMessage(message='(countStations) problem when reading STATIONS table!', severity='ERROR')
      
      return returnValue

#--------------------------------------------------------      
   def countUsers(self, userType='REGULAR'): 
#--------------------------------------------------------      
      self.resetError()
      
      returnValue = 0
      
      try: 
         cursor = self.db.cursor()
         
         if userType != 'ALL':
            cursor.execute('SELECT COUNT(*) FROM USERS WHERE admin=0 and type = ?',(userType,))
         else:
            cursor.execute('SELECT COUNT(*) FROM USERS WHERE admin=0')

         returnValue = cursor.fetchone()[0]
               
      except Exception as err: 
         if self.verbose: print(traceback.format_exc())
         if self.verbose: self.log.logMessage(message='(coundUsers) %s'%err, severity='ERROR')  
         if self.verbose: self.log.logMessage(message='(countUsers) hubo un problema al interrogar a la tabla users!', severity='ERROR')
      
      return returnValue

#--------------------------------------------------------      
   def genreExists(self, genrename): 
#--------------------------------------------------------      
      self.resetError()

      cursor = self.db.cursor()
      sentence='SELECT genrename FROM GENRES WHERE genrename = ? '
      
      genre=None
      
      try:
         cursor.execute(sentence, (genrename,))
         genre = cursor.fetchone()
      except Exception as err: 
         if self.verbose: print(traceback.format_exc())
         if self.verbose: self.log.logMessage(message='(genreExists) %s'%err, severity='ERROR')  
      
      found = genre!=None      

      return found

#--------------------------------------------------------      
   def listGenres(self): 
#--------------------------------------------------------      
      self.resetError()
      
      returnValue = []
         
      cursor = self.db.cursor()
      cursor.execute('SELECT genrename FROM GENRES ORDER BY genrename')
      genres = cursor.fetchall()
      for genre in genres:
         returnValue.append(genre[0])

      return returnValue

#--------------------------------------------------------      
   def addGenre(self, genrename, commit = False): 
#--------------------------------------------------------      
      self.resetError()
      
      returnValue = ''
         
      if self.genreExists(genrename): 
         if self.verbose: self.log.logMessage(message='(addGenre) genre %s already exists!'%genrename, severity='WARNING')
         returnValue = '(ERROR) genre [%s] already exists!'%genrename
      else:  
         cursor = self.db.cursor()
         cursor.execute('''INSERT INTO GENRES(genrename) VALUES(?)''', (genrename.upper(),))

         if self.verbose: self.log.logMessage(message='(addGenre) genre %s has been added to table GENRES!'%genrename, severity='INFO')
         returnValue = '(OK) [%s] has been added!'%genrename

         if commit: 
            self.db.commit()
            if self.verbose: self.log.logMessage(message='(addGenre) commit transaction after adding genre [%s] on table GENRES'%genrename, severity='INFO')

      return returnValue


#--------------------------------------------------------      
   def modifyArtistGenre(self, artistname, genrename, commit = False): 
#--------------------------------------------------------      
      self.resetError()
      
      returnValue = ''
         
      if not self.userExists(artistname) or not self.genreExists(genrename): 
         if self.verbose: self.log.logMessage(message='(modifyArtistGenre) genre or artistname does not exists!', severity='WARNING')
         returnValue = '(ERROR) genre or artistname does not exists!'
      else:  
         cursor = self.db.cursor()
         cursor.execute('UPDATE USERS SET genre = "%s" WHERE username = "%s"'%(genrename.upper(),artistname,))

         if self.verbose: self.log.logMessage(message='(modifyArtistGenre) genre %s has been modified for artist %s!'%(genrename,artistname), severity='INFO')
         returnValue = '(OK) [%s] has been modified for user %s!'%(genrename, artistname)

         if commit: 
            self.db.commit()
            if self.verbose: self.log.logMessage(message='(modifyArtistGenre) commit transaction after modifying genre [%s] for user %s'%(genrename,artistname), severity='INFO')

      return returnValue


#--------------------------------------------------------      
   def modifyGenre(self, genrename, newgenrename, commit = False): 
#--------------------------------------------------------      
      self.resetError()
      
      returnValue = ''
         
      if not self.genreExists(genrename): 
         if self.verbose: self.log.logMessage(message='(modifyGenre) genre %s does not exists!'%genrename, severity='WARNING')
         returnValue = '(ERROR) genre [%s] does not exists!'%genrename
      else:  
         cursor = self.db.cursor()
         cursor.execute('UPDATE GENRES SET genrename = "%s" WHERE genrename = "%s"'%(newgenrename.upper(),genrename.upper(),))

         if self.verbose: self.log.logMessage(message='(modifyGenre) genre %s has been modified in table GENRES!'%genrename, severity='INFO')
         returnValue = '(OK) [%s] has been modified!'%genrename

         if commit: 
            self.db.commit()
            if self.verbose: self.log.logMessage(message='(modifyGenre) commit transaction after modifying genre [%s] on table GENRES'%genrename, severity='INFO')

      return returnValue

#--------------------------------------------------------      
   def removeGenre(self, genrename, commit = False): 
#--------------------------------------------------------      
      self.resetError()
      
      returnValue = ''
         
      if not self.genreExists(genrename): 
         if self.verbose: self.log.logMessage(message='(removeGenre) genre %s does not exists!'%genrename, severity='WARNING')
         returnValue = '(ERROR) genre [%s] does not exists!'%genrename
      else:  
         cursor = self.db.cursor()
         cursor.execute('DELETE FROM GENRES WHERE genrename = "%s"'%(genrename.upper(),))

         if self.verbose: self.log.logMessage(message='(removeGenre) genre %s has been removed in table GENRES!'%genrename, severity='INFO')
         returnValue = '(OK) [%s] has been removed!'%genrename

         if commit: 
            self.db.commit()
            if self.verbose: self.log.logMessage(message='(removeGenre) commit transaction after removing genre [%s] on table GENRES'%genrename, severity='INFO')

      return returnValue

#--------------------------------------------------------      
   def addUser(self, username, name='', email='', mobile='', passwd='', nfcid='', active=0, volume='50', loginsound='', userType='REGULAR', bio='', url='', similarArtists='', enabled=1, commit = False): 
#--------------------------------------------------------      
      self.resetError()
      
      _user=username

      returnValue = ''
      if username in self.specialUsers: 
         if self.verbose: self.log.logMessage(message='(addUser) %s is a reserved name!'%username, severity='ERROR')
         returnValue = '(ERROR) [%s] is a reserved name!'%username
         
      if self.userExists(username): 
         if self.verbose: self.log.logMessage(message='(addUser) user %s already exists!'%username, severity='WARNING')
         returnValue = '(ERROR) user [%s] already exists!'%username
      else:  
         cursor = self.db.cursor()
         cursor.execute('''INSERT INTO USERS(username, name, email, mobile, passwd, nfcid, active, volume, loginsound, admin, type, enabled, bio, url, similarartists)
         VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (username,name,email,mobile,passwd,nfcid,active,volume, loginsound, 0, userType, enabled, bio, url, similarArtists))

         if self.verbose: self.log.logMessage(message='(addUser) user %s has been added to table USERS!'%username, severity='INFO')
         returnValue = '(OK) [%s] has been added!'%username

         if commit: 
            self.db.commit()
            if self.verbose: self.log.logMessage(message='(addUser) commit transaction after adding user [%s][ on table USERS'%username, severity='INFO')

      return returnValue

#--------------------------------------------------------      
   def modifyUser(self, username, name=None, email=None, mobile=None, passwd=None, nfcid=None, active=0, volume='50', loginsound=None, userType=None, bio=None, url=None, similarArtists=None,commit = False): 
#--------------------------------------------------------      
      self.resetError()
      if username in self.specialUsers: 
         if self.verbose: self.log.logMessage(message='(addUser) %s is a reserved name!'%username, severity='ERROR')
         return

      update=False
      try:   
         if self.userExists(username): 
            sql = 'UPDATE USERS '

            cursor = self.db.cursor()

            if name != None: 
               update=True
               if 'SET' not in sql: 
                  sql += 'SET name="%s"'%name
               else:     
                  sql += 'name="%s"'%name

            if email != None: 
               update=True
               if 'SET' not in sql: 
                  sql += 'SET email="%s"'%email
               else:     
                  sql += ',email="%s"'%email

            if mobile != None: 
               update=True
               if 'SET' not in sql: 
                  sql += 'SET mobile="%s"'%mobile
               else:     
                  sql += ',mobile="%s"'%mobile

            if passwd != None: 
               update=True
               if 'SET' not in sql: 
                  sql += 'SET passwd="%s"'%passwd
               else:     
                  sql += ',passwd="%s"'%passwd

            if nfcid != None: 
               update=True
               if 'SET' not in sql: 
                  sql += 'SET nfcid="%s" '%nfcid
               else:     
                  sql += ',nfcid="%s" '%nfcid

            if userType != None: 
               update=True
               if 'SET' not in sql: 
                  sql += 'SET type="%s" '%userType
               else:     
                  sql += ',type="%s" '%userType

            if loginsound != None: 
               update=True
               if 'SET' not in sql: 
                  sql += 'SET loginsound="%s" '%loginsound
               else:     
                  sql += ',loginsound="%s" '%loginsound

            if bio != None: 
               update=True
               if 'SET' not in sql: 
                  sql += 'SET bio="%s" '%bio
               else:     
                  sql += ',bio="%s" '%bio
         
            if url != None: 
               update=True
               if 'SET' not in sql: 
                  sql += 'SET url="%s" '%url
               else:     
                  sql += ',url="%s" '%url
         
            if similarArtists != None: 
               update=True
               if 'SET' not in sql: 
                  sql += 'SET similarartists="%s" '%similarArtists
               else:     
                  sql += ',similarartists="%s" '%similarArtists
         
            sql += 'WHERE UPPER(username) = UPPER("%s") '%username

      except Exception as err:
	     print err         
      
      if update:         
         self.verbose=True
         cursor.execute(sql)
         if self.verbose: self.log.logMessage(message='(modifyUser) user "%s" has been modify on table USERS!'%username, severity='INFO')
         if commit: 
            self.db.commit()
            if self.verbose: self.log.logMessage(message='(modifyUser) commit transacction after modifying user "%s" on table USERS'%username, severity='INFO')

      self.verbose=False
         
#--------------------------------------------------------      
   def removeUser(self, username, commit=False): 
#--------------------------------------------------------      
      self.resetError()
      returnvalue=''
      if not self.userExists(username): 
         if self.verbose: self.log.logMessage(message='(removeUser) user "%s" does not exists!'%username, severity='ERROR')
         self.error=1
         self.errorMessage = 'user %s does not exists!'%username
         returnValue = '(ERROR) [%s] does not exists!'%username
      else:     
         if not username in self.specialUsers:         
            cursor = self.db.cursor()
            cursor.execute('DELETE FROM USERS WHERE username = ?', (username,))
            cursor.execute('DELETE FROM STATIONS WHERE username = ?', (username,))
            cursor.execute('DELETE FROM STATIONPLAYLISTS WHERE username = ?', (username,))
            cursor.execute('DELETE FROM SONGS WHERE username = ?', (username,))

            playlistFiles = self.firstUserPlaylistChar+username.replace(' ','_')+'__*'
            run_command('rm '+self.defaultPlaylistPath+'/'+playlistFiles+'.m3u')

            if self.isUserActive(username): 
               self.activeUser = None
               self.activeId = None                  

            if self.verbose: self.log.logMessage(message='(removeUser) user "%s" has been deleted from table USERS!'%username, severity='INFO')
            returnValue = '(OK) user [%s] has been deleted!'%username 

            if commit: 
               self.db.commit()
               if self.verbose: self.log.logMessage(message='(removeUser) commit transacction after deleting user "%s" on table USERS'%username, severity='INFO')
         else:
			returnValue = '(ERROR) [%s] is a reserved user!'%username       

      return returnValue		


#--------------------------------------------------------      
   def renameUser(self, oldUserName, newUserName, commit = False): 
#--------------------------------------------------------      
      self.resetError()

      if oldUserName in self.specialUsers: 
         if self.verbose: self.log.logMessage(message='(addUser) %s is a reserved name!'%oldUserName, severity='ERROR')
         return

      if not self.userExists(oldUserName):
         if self.verbose: self.log.logMessage(message='(renameUser) user "%s" does not exists on table USERS, cant be renamed'%oldUserName, severity='ERROR')
      else:   
         if not self.userExists(newUserName):
            if self.verbose: self.log.logMessage(message='(renameUser) renaming user "%s" to "%s" on table USERS'%(oldUserName, newUserName), severity='INFO')
            cursor = self.db.cursor()
            cursor.execute('UPDATE USERS SET username = ? WHERE username = ?', (newUserName, oldUserName, ))
            cursor.execute('UPDATE STATIONPLAYLISTS SET username = ? WHERE username = ?', (newUserName, oldUserName, ))
            cursor.execute('UPDATE STATIONS SET username = ? WHERE username = ?', (newUserName, oldUserName, ))
            cursor.execute('UPDATE STATIONPLAYLISTS SET username = ? WHERE username = ?', (newUserName, oldUserName, ))
            cursor.execute('UPDATE SONGS SET username = ? WHERE username = ?', (newUserName, oldUserName, ))

            self.activeUser = newUserName
            if commit: 
               self.db.commit()
               if self.verbose: self.log.logMessage(message='(renameUser) commit transacction after renaming user "%s" to %s on table USERS'%(oldUserName, newUserName), severity='INFO')
         else: 
            if self.verbose: self.log.logMessage(message='(renameUser) another user exists with name "%s" on table USERS, "%s" cannot be renamed'%(newUserName, oldUserName), severity='ERROR') 

#--------------------------------------------------------      
   def getSimilarArtists(self, username): 
#--------------------------------------------------------      
      returnValue = []
      
      try:
         cursor = self.db.cursor()
      
         sentence='SELECT similarartists FROM USERS WHERE UPPER(username) = UPPER("%s") AND admin = 0'%username
      
         cursor.execute(sentence)
         similars = cursor.fetchone()
         
         if similars != None: 
            for s in similars[0].split(":"):
               if s!='': returnValue.append(s) 
               
      except Exception as err:
         if self.verbose: print err
      
      return returnValue      

#--------------------------------------------------------      
   def isUserEnabled(self, username): 
#--------------------------------------------------------      
      cursor = self.db.cursor()
      
      sentence='SELECT username, enabled FROM USERS WHERE UPPER(username) = UPPER("%s") AND admin = 0'%username
      
      cursor.execute(sentence)
      user = cursor.fetchone()
      
      if user == None: 
         returnValue = False
      else: 
         returnValue = user[1] == 1       
     
      return returnValue      

#--------------------------------------------------------      
   def isUserActive(self, username): 
#--------------------------------------------------------      
      cursor = self.db.cursor()
      
      sentence='SELECT username, active FROM USERS WHERE username = "%s" AND admin = 0'%username
      
      cursor.execute(sentence)
      user = cursor.fetchone()
      
      if user == None: 
         returnValue = False
      else: 
         returnValue = user[1] == 1       
     
      return returnValue      

#--------------------------------------------------------      
   def isIdEnabled(self, idnumber): 
#--------------------------------------------------------      
      cursor = self.db.cursor()
      
      sentence='SELECT username, enabled FROM USERS WHERE nfcid = "%s" AND admin = 0'%idnumber
      
      cursor.execute(sentence)
      user = cursor.fetchone()
      
      if user == None: 
         returnValue = False
      else: 
         returnValue =  user[1] == 1       
     
      return returnValue      

#--------------------------------------------------------      
   def isIdActive(self, idnumber): 
#--------------------------------------------------------      
      cursor = self.db.cursor()
      
      sentence='SELECT username, active FROM USERS WHERE nfcid = "%s" AND admin = 0'%idnumber
      
      cursor.execute(sentence)
      user = cursor.fetchone()
      
      if user == None: 
         returnValue = False
      else: 
         returnValue =  user[1] == 1       
     
      return returnValue      

#--------------------------------------------------------      
   def activateUserById(self, idnumber, sound=False, commit = True, dimm=False, force=False): 
#--------------------------------------------------------      
      self.resetError()
      
      if self.isIdActive(idnumber) and not force: 
         if self.verbose: self.log.logMessage(message='(activateUserById) user "%s" is already active on table USERS'%idnumber, severity='INFO')
      else:   
         if self.idExists(idnumber):
            if self.verbose: self.log.logMessage(message='(activateUserById) activating user "%s" on table USERS'%idnumber, severity='INFO')

            if dimm: 
               self.dimmVolume()
               
            cursor = self.db.cursor()
            cursor.execute('UPDATE USERS SET active = 1 WHERE nfcid = ?', (idnumber,))
            
            if idnumber != self.activeId:
               cursor.execute('UPDATE USERS SET active = 0 WHERE nfcid = ?', (self.activeId,))

            self.activeUser = self.getActiveUser()
            self.activeId=idnumber
            
            if sound: 
               playSound('mpg123 '+self.getActiveUserDetails()[0]['loginsound'])
            
            #self.welcomeUser()
            self.activateContext(clear=True)

            if commit: self.db.commit()

            if dimm: 
               self.dimmVolume(lastVolume=70)
            
         else:   
            if self.verbose: self.log.logMessage(message='(activateUserById) unable to activate user "%s" on table USERS, because it was not found!'%username, severity='WARNING')

#--------------------------------------------------------      
   def activateUserByName(self, username, sound=False, commit = True, dimm=False, force=True): 
#--------------------------------------------------------      
      #print stack()[1][3]
      self.resetError()

      returnValue =''            

      if self.isUserActive(username) and not force: 
         if self.verbose: self.log.logMessage(message='(activateUserByName) user "%s" is already active on table USERS'%username, severity='INFO')
         returnValue =  '(ERROR) user [%s] is already active on table USERS'%username
      else:   
         if self.userExists(username):
            if self.verbose: self.log.logMessage(message='(activateUserByName) activating user "%s" on table USERS'%username, severity='INFO')

            if dimm: 
               self.dimmVolume()

            cursor = self.db.cursor()
            cursor.execute('UPDATE USERS SET active = 1 WHERE username = ?', (username,))            

            if self.activeUser != username:
               cursor.execute('UPDATE USERS SET active = 0 WHERE username = ?', (self.activeUser,))

            self.activeUser = username
            self.activeId = self.getActiveId()
            
            if sound: 
               playSound('mpg123 '+self.getActiveUserDetails()[0]['loginsound'])
            
            #self.welcomeUser()
            self.activateContext(clear=True)

            if commit: self.db.commit()

            if dimm: 
               self.dimmVolume(lastVolume=self.getActiveUserVolume())
            
            returnValue = '(OK) user [%s] was activated'%username
            
         else:   
            if self.verbose: self.log.logMessage(message='(activateUserByName) unable to activate user "%s" on table USERS, because it was not found!'%username, severity='WARNING')
            returnValue =  '(ERROR) user [%s] was not found!'%username

      return returnValue


#--------------------------------------------------------      
   def enableUserByName(self, username, allUsers=False, userType="REGULAR", commit = True): 
#--------------------------------------------------------      
      #print stack()[1][3]
      self.resetError()

      returnValue =''            

      if not allUsers:
         if self.userExists(username):
            if self.verbose: self.log.logMessage(message='(enableUserByName) enabling user "%s" on table USERS'%username, severity='INFO')

            cursor = self.db.cursor()
            cursor.execute('UPDATE USERS SET enabled = 1 WHERE username = ? AND type = ?', (username, userType,))            

            if commit: self.db.commit()
            returnValue = '(OK) user [%s] was enabled'%username
            
         else:   
            if self.verbose: self.log.logMessage(message='(enableUserByName) unable to enable user "%s" on table USERS, because it was not found!'%username, severity='WARNING')
            returnValue =  '(ERROR) user [%s] was not found!'%username
      else:
         cursor = self.db.cursor()
         cursor.execute('UPDATE USERS SET enabled = 1 WHERE type = ?', (userType,))            

         if commit: self.db.commit()
         returnValue = '(OK) all artists were enabled'
         
      return returnValue

#--------------------------------------------------------      
   def enableUserById(self, idnumber, userType="REGULAR", allUsers=False, commit = True): 
#--------------------------------------------------------      
      #print stack()[1][3]
      self.resetError()

      returnValue =''            
      
      if not allUsers:
         if self.userExists(idnumber):
            if self.verbose: self.log.logMessage(message='(enableUserByName) enabling user "%s" on table USERS'%idnumber, severity='INFO')

            cursor = self.db.cursor()
            cursor.execute('UPDATE USERS SET active = 1 WHERE nfcid = ? AND type = ?', (idnumber, userType,))

            if commit: self.db.commit()
            returnValue = '(OK) user [%s] was enabled'%idnumber
            
         else:   
            if self.verbose: self.log.logMessage(message='(enableUserByName) unable to enable user "%s" on table USERS, because it was not found!'%username, severity='WARNING')
            returnValue =  '(ERROR) user [%s] was not found!'%username
      else:
         cursor = self.db.cursor()
         cursor.execute('UPDATE USERS SET enabled = 1 WHERE type = ?', (userType,))            

         if commit: self.db.commit()
         returnValue = '(OK) all artists were enabled'      


      return returnValue

#--------------------------------------------------------      
   def disableUserByName(self, username, userType="REGULAR", allUsers=False, commit = True): 
#--------------------------------------------------------      
      #print stack()[1][3]
      self.resetError()

      returnValue =''            

      if not allUsers:
         if self.userExists(username):
            if self.verbose: self.log.logMessage(message='(disableUserByName) disabling user "%s" on table USERS'%username, severity='INFO')

            cursor = self.db.cursor()
            cursor.execute('UPDATE USERS SET enabled = 0 WHERE username = ? and type = ?', (username,userType,))            

            if commit: self.db.commit()
            returnValue = '(OK) user [%s] was enabled'%username
            
         else:   
            if self.verbose: self.log.logMessage(message='(disableUserByName) unable to disable user "%s" on table USERS, because it was not found!'%username, severity='WARNING')
            returnValue =  '(ERROR) user [%s] was not found!'%username
      else:
         cursor = self.db.cursor()
         cursor.execute('UPDATE USERS SET enabled = 0 WHERE type = ?', (userType,))            

         if commit: self.db.commit()
         returnValue = '(OK) all artists were disaabled'      

      return returnValue

#--------------------------------------------------------      
   def disableUserById(self, idnumber, userType="REGULAR", allUsers=False, commit = True): 
#--------------------------------------------------------      
      #print stack()[1][3]
      self.resetError()

      returnValue =''            

      if not allUsers:
         if self.userExists(idnumber):
            if self.verbose: self.log.logMessage(message='(disableUserById) disabling user "%s" on table USERS'%idnumber, severity='INFO')

            cursor = self.db.cursor()
            cursor.execute('UPDATE USERS SET active = 0 WHERE nfcid = ? AND type = ?', (idnumber, userType,))

            if commit: self.db.commit()
            returnValue = '(OK) user [%s] was disabled'%idnumber
            
         else:   
            if self.verbose: self.log.logMessage(message='(disableUserById) unable to disable user "%s" on table USERS, because it was not found!'%idnumber, severity='WARNING')
            returnValue =  '(ERROR) user [%s] was not found!'%idnumber
      else:
         cursor = self.db.cursor()
         cursor.execute('UPDATE USERS SET enabled = 0 WHERE type = ?', (userType,))            

         if commit: self.db.commit()
         returnValue = '(OK) all artists were disabled'      
         
      return returnValue

#--------------------------------------------------------      
   def deactivateAllUsers(self, commit = True): 
#--------------------------------------------------------      
      self.resetError()

      if self.verbose: self.log.logMessage(message='(deactivateAllUsers) deactivating all users on table USERS', severity='INFO')
      returnValue = '(OK) all users were deactivated'
      cursor = self.db.cursor()
      cursor.execute('UPDATE USERS SET active = 0')
      self.activeUser = None
      self.activeId = None
      self.mp3.clear()
      if commit: self.db.commit()

      return returnValue
#--------------------------------------------------------      
   def dbCommit(self, verbose=None): 
#--------------------------------------------------------      
      
      if verbose==None:
         if self.verbose: self.log.logMessage(message='(dbCommit) writing data to disk!', severity='INFO')
      else: 
         if verbose: self.log.logMessage(message='(dbCommit) writing data to disk!', severity='INFO')  
         
      try: 
         self.db.commit()
      except Exception as err: 
         if self.verbose: print(traceback.format_exc())
         if self.verbose: self.log.logMessage(message='(dbCommit) %s'%err, severity='ERROR')  
         if self.verbose: self.log.logMessage(message='(dbCommit) writing data to disk failed!', severity='ERROR')  
            
       
#--------------------------------------------------------      
   def getActiveUser(self): 
#--------------------------------------------------------      
      sql = 'SELECT username FROM USERS WHERE active = "1"'
      cursor = self.db.cursor()
      cursor.execute(sql)      
      activeUser = cursor.fetchone()
      
      if activeUser != None: 
         try: 
            self.activeUser = activeUser[0]
         except Exception as err: 
            if self.verbose: print(traceback.format_exc())
            if self.verbose: self.log.logMessage(message='(getActiveUser) %s'%err, severity='ERROR')  
            self.activeUser='no user'   
      else: 
         self.activeUser = None
      
      return self.activeUser

#--------------------------------------------------------      
   def getActiveId(self): 
#--------------------------------------------------------      
      activeId = self.getActiveUserDetails()
      
      if len(activeId) == 0: 
         self.activeId = None
      else: 
         try: 
            self.activeId = activeId[0]['nfcid']     
         except Exception as err: 
            if self.verbose: print(traceback.format_exc())
            if self.verbose: self.log.logMessage(message='(getActiveId) %s'%err, severity='ERROR')  
            self.activeId = None   

      return self.activeId

#--------------------------------------------------------      
   def restoreActiveUserVolume(self): 
#--------------------------------------------------------      
      if self.activeUser: 
         try: 
            vol = self.getActiveUserVolume()
            
            if vol < 5: vol = 50
            self.mp3.setVolume(volume=vol)
            returnValue = self.getActiveUserVolume()
         except Exception as err: 
            if self.verbose: print(traceback.format_exc())
            if self.verbose: self.log.logMessage(message='(restoreActiveUserVolume) %s'%err, severity='ERROR')  
            if self.verbose: self.log.logMessage(message='(restoreActiveUserVolume) no se pudo restaurar el volumen del usuario activo', severity='WARNING')
            returnValue = -1
            
      return returnValue 
#--------------------------------------------------------      
   def getActiveUserVolume(self): 
#--------------------------------------------------------      
      try: 
         volume = int(self.getActiveUserDetails()[0]['volume'])
      except Exception as err: 
         if self.verbose: print(traceback.format_exc())
         if self.verbose: self.log.logMessage(message='(getActiveUserVolume) %s'%err, severity='ERROR')  
         volume = 50   
      return volume

#--------------------------------------------------------      
   def getActiveUserDetails(self): 
#--------------------------------------------------------      
      #print 'getActiveUserDetails: called by %s'%inspect.stack()[1][3]

      returnValue = [{}] 
      if self.activeUser == None: 
         return returnValue
      else:   
         try: 
            returnValue = self.getUsersDetails(username = self.activeUser)
         except Exception as err: 
            if self.verbose: print(traceback.format_exc())
            if self.verbose: self.log.logMessage(message='(getActiveUserDetails) %s'%err, severity='ERROR')  
            if self.verbose: self.log.logMessage(message='(getActiveUserDetails) no se pudo cargar el detalle del usuario activo', severity='WARNING')
            returnValue = None   
         return returnValue

#--------------------------------------------------------      
   def shutdown(self): 
#--------------------------------------------------------      
      self.saveContext()
      self.dbCommit()
      vol=int(self.mp3.getVolume())
      self.dimmVolume()
      self.mp3.clear()
      self.mp3.setVolume(volume=vol)
      
      self.db.close()
      
#--------------------------------------------------------      
   def stationExists(self, station, username = None, mediatype=None): 
#--------------------------------------------------------      
      self.resetError()
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   

      st = None
      
      if self.userExists(_user): 
         cursor = self.db.cursor()
         sql = 'SELECT station FROM STATIONS WHERE station = "%s" AND username = "%s" '%(station, _user,)
      
         if mediatype != None:
            sql += 'AND mediatype = %s'%mediatype
         
         cursor.execute(sql)      
            
         st = cursor.fetchone()
      
      return st!=None
      
#--------------------------------------------------------      
   def addStation(self, station, username=None, genre='unknown', stationType='G', commit = False): 
#--------------------------------------------------------      
      self.resetError()      
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   

      returnValue = ''
      
      #stationType defines type of station. There are to major types of stations: (G)eneral, (F)avorites. General are stations are made of playlists
      #predefined by artists. Favotites are special stations created with favorite songs.
      
      if self.userExists(_user):
         if self.stationExists(station, _user): 
            if self.verbose: self.log.logMessage(message='(addStation) station "%s" of %s already exists!'%(station,_user), severity='WARNING')
            returnValue = '(ERROR) station [%s] already exist!'%station
         else:  
            cursor = self.db.cursor()
            cursor.execute('''INSERT INTO STATIONS(username,station,genre,mediatype,activestation,activemediatype,songname,artistname,songpos,timelapsed,state,enabled,type) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)''', (_user,station, genre, 0, 0, 1, 'no title', 'no artist', 0, 0, 'stop',1,stationType))
            cursor.execute('''INSERT INTO STATIONS(username,station,genre,mediatype,activestation,activemediatype,songname,artistname,songpos,timelapsed,state,enabled,type) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)''', (_user,station, genre, 1, 0, 0, 'no title', 'no artist', 0, 0, 'stop',1,stationType))
                        
            if self.verbose: self.log.logMessage(message='(addStation) station "%s" of %s has been added to table STATIONS!'%(station,_user), severity='INFO')
            returnValue = '(OK) station [%s] added to user [%s]'%(station,_user)

            if commit: 
               self.db.commit()
               if self.verbose: self.log.logMessage(message='(addStation) commit transacction after adding station "%s" of %s on table STATIONS'%(station,_user), severity='INFO')
      else:           
         if _user==None: 
            if self.verbose: self.log.logMessage(message='(addStation) no active user found!', severity='ERROR')
            returnValue = '(ERROR) no active user found!'
         else:
            if self.verbose: self.log.logMessage(message='(addStation) user %s not found!'%_user, severity='ERROR')
            returnValue = '(ERROR) user [%s] not found!'%_user
               

      return returnValue
      
#--------------------------------------------------------      
   def renameStation(self, oldStationName, newStationName, username=None, mediatype=0, commit = False): 
#--------------------------------------------------------      
      self.resetError()
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   

      returnValue = ''


      if self.userExists(_user):
         if not self.stationExists(oldStationName, _user, mediatype=mediatype):
            if self.verbose: self.log.logMessage(message='(renameStation) station "%s" does not exists on table STATIONS, cant be renamed'%oldStationName, severity='ERROR')
            returnValue = '(ERROR) station [%s] does not exists, cant be renamed!'%oldStationName
         else:   
            if not self.stationExists(newStationName, _user):
               if self.verbose: self.log.logMessage(message='(renameStation) renaming station "%s" to "%s" on table STATIONS'%(oldStationName, newStationName), severity='INFO')
               cursor = self.db.cursor()
               cursor.execute('UPDATE STATIONS SET station = ? WHERE station = ? AND username = ?', (newStationName, oldStationName, _user,))
               cursor.execute('UPDATE STATIONPLAYLISTS SET station = ? WHERE station = ? AND username = ?', (newStationName, oldStationName, _user,))
               cursor.execute('UPDATE SONGS set station = ? WHERE station = ? AND username = ?', (newStationName, oldStationName, _user,))

               returnValue = '(OK) station [%s] was renamed to "%s"'%(oldStationName,newStationName)
               
               if commit: 
                  self.db.commit()
                  if self.verbose: self.log.logMessage(message='(renameStation) commit transacction after renaming station "%s" to %s on table STATIONS'%(oldStationName, newStationName), severity='INFO')
            else: 
               if self.verbose: self.log.logMessage(message='(renameStation) another station exists with name "%s" on table STATIONS, "%s" cannot be renamed'%(newStationName, oldStationName), severity='ERROR') 
               returnValue ='(ERROR) another station exists with name [%s] on table STATIONS, [%s] cannot be renamed'%(newStationName, oldStationName) 
      else:           
         returnValue = '(ERROR) user [%s] does not exists!, station not renamed'%_user

      return returnValue

#--------------------------------------------------------      
   def removeStation(self, station, username=None, commit = False): 
#--------------------------------------------------------      
      self.resetError()
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   

      returnValue = ''

      if self.userExists(_user):
         if not self.stationExists(station, _user): 
            if self.verbose: self.log.logMessage(message='(removeStation) station "%s" of %s doesnt exists!'%(station,_user), severity='WARNING')
            returnValue = '(ERROR) station "%s" of %s doesnt exists!'%(station,_user)

         else:  
            cursor = self.db.cursor()
            cursor.execute('DELETE FROM STATIONS WHERE station = ? AND username = ?', (station, _user,))
            cursor.execute('DELETE FROM STATIONPLAYLISTS WHERE station = ? AND username = ?', (station, _user,))
            cursor.execute('DELETE FROM SONGS WHERE station = ? AND username = ?', (station, _user,))

            playlistFile = self.firstUserPlaylistChar+_user.replace(' ','_')+'__'+station
            run_command('rm '+self.defaultPlaylistPath+'/'+playlistFile+'.m3u')
             
            if self.verbose: self.log.logMessage(message='(removeStation) station "%s" of %s has been deleted from table STATIONS!'%(station,_user), severity='INFO')
            returnValue = '(OK) station "%s" of %s has been deleted from table STATIONS!'%(station,_user)

            if commit: 
               self.db.commit()
               if self.verbose: self.log.logMessage(message='(removeStation) commit transacction after deleting station "%s" of %s on table STATIONS'%(station,_user), severity='INFO')

      else:           
         returnValue = '(ERROR) user %s does not exists!, station not removed'%_user

      return returnValue

#--------------------------------------------------------      
   def removeAllStationsFrom(self, username, commit = False): 
#--------------------------------------------------------      
      self.resetError()
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   

      if self.userExists(_user):
         if not self.userExists(_user, table='STATIONS'): 
            if self.verbose: self.log.logMessage(message='(removeAllStationsFrom) user %s doesnt have stations!'%(_user), severity='ERROR')
         else:  
            cursor = self.db.cursor()
            cursor.execute('DELETE FROM STATIONS WHERE username = ?', (_user,))
            cursor.execute('DELETE FROM STATIONPLAYLISTS WHERE username = ?', (_user,))
            
            if self.verbose: self.log.logMessage(message='(removeAllStationsFrom) stations of %s has been deleted from table STATIONS!'%(_user), severity='INFO')

            if commit: 
               self.db.commit()
               if self.verbose: self.log.logMessage(message='(removeAllStationsFrom) commit transacction after deleting all station of %s on table STATIONS'%(_user), severity='INFO')

#--------------------------------------------------------      
   def getStationsDetails(self, username=None, allStations=False, fav = False): 
#--------------------------------------------------------      
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   
      
      returnStations = []
      if self.userExists(_user):
         try:
            cursor = self.db.cursor()
         
            sql = '''SELECT * FROM STATIONS '''

            if not allStations:
               sql += 'WHERE username = "%s" '%(_user,)

            if fav: 
               if 'WHERE' in sql: 
                  sql += 'and favorite = 1 '
               else:    
                  sql += 'WHERE favorite = 1 '
         
            sql += 'ORDER BY username,station'
                           
            cursor.execute(sql)
            
            for station in cursor.fetchall(): 
               returnStations.append(self.row2dict(station,self.stationsFields)) 

         except Exception as err: 
            if self.verbose: print(traceback.format_exc())
            if self.verbose: self.log.logMessage(message='(getStationsDetails) %s'%err, severity='ERROR') 
            if self.verbose: self.log.logMessage(message='(getStationsDetails) problemas al obtener los detalles de la estacion activa', severity='ERROR')
      else: 
         if self.verbose: self.log.logMessage(message='(getStationsDetails) user "%s" dont exists'%(_user), severity='ERROR')

         
      return (returnStations) 


#--------------------------------------------------------      
   def listSongsOfPlaylist(self, playlistname, fext='.m3u'): 
#--------------------------------------------------------      
      plFile = self.defaultPlaylistPath+'/'+playlistname+fext
      
      returnList = []
      if os.path.isfile(plFile):
         returnList = catFile(filename=plFile)
      
      return returnList
#--------------------------------------------------------      
   def listStations(self, username=None, stationType='G'): 
#--------------------------------------------------------      
      returnList = []
      #stationType [G]eneral,[F]avorite,[A]ll
      if not stationType in 'GAF':
         stationType = 'G'

      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   
      
      if self.userExists(_user):   
         for station in self.getStationsDetails(username=_user): 
            try: 
               if stationType == 'A':
                  returnList.append(station['station'])
               else:
                  if station['type']==stationType:   
                     returnList.append(station['station'])
                     
            except Exception as err: 
               if self.verbose: print(traceback.format_exc())
               if self.verbose: self.log.logMessage(message='(listStations) %s'%err, severity='ERROR')  
               if self.verbose: self.log.logMessage(message='(listStations) no se pudo cargar la lista de estaciones de la base de datos', severity='ERROR')

         return list(set(returnList)) 

#--------------------------------------------------------      
   def listStationsFormated(self, username=None, stationType='G'): 
#--------------------------------------------------------      
      returnList = []
      #stationType [G]eneral,[F]avorite,[A]ll
      if not stationType in 'GAF':
         stationType = 'G'

      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   
      
      if self.userExists(_user):   
         for station in self.getStationsDetails(username=_user): 
            try: 
               if stationType == 'A':
                  returnList.append("[%s] %s"%('e' if station['enabled']==1 else 'd',station['station']))
               else:
                  if station['type']==stationType:   
                     returnList.append("[%s] %s"%('e' if station['enabled']==1 else 'd',station['station']))
            except Exception as err:
               if self.verbose: print(traceback.format_exc())
               if self.verbose: self.log.logMessage(message='(listStations) %s'%err, severity='ERROR')  
               if self.verbose: self.log.logMessage(message='(listStations) no se pudo cargar la lista de estaciones de la base de datos', severity='ERROR')

         return list(set(returnList)) 

#--------------------------------------------------------      
   def populateSongsOnPickList(self): 
#--------------------------------------------------------      
      _user = self.activeUser
      _station = self.getActiveStation()
      self.jumpToSong.emptyList()
      cursor = self.db.cursor()
      sql='SELECT number FROM SONGS WHERE station = ? AND username = ? AND enabled = 1'
      cursor.execute(sql, (_station, _user))
      stations = cursor.fetchall()

      for station in stations:
         self.jumpToSong.addElement(station[0])

#--------------------------------------------------------      
   def getNextRandomSong(self): 
#--------------------------------------------------------      
      #_user = self.activeUser
      #_station = self.getActiveStation()
      #currentSong = self.mp3.getSongPos()
      #totalSongs = self.countSongs(enabled=True)
      
      returnValue = -1

      if self.jumpToSong.isEmpty():
         self.populateSongsOnPickList()
      try:
         #self.jumpToSong.printList()
         returnValue = self.jumpToSong.pickOneRandomly(differentTo = str(self.getActiveStation()))
      except Exception as pythonError: 
         if self.debug: print(traceback.format_exc()) 

#      if _user !=None and _station!=None and totalSongs>0:
#         cursor = self.db.cursor()
#         sql='SELECT enabled FROM SONGS WHERE station = ? AND username = ? '
#         cursor.execute(sql, (_station, _user))
#         station = cursor.fetchall()
         
#         enabledSongs = []
#         songNumber=1
#         for i in station: 
#            if i[0]==1:
#               enabledSongs.append(songNumber)
#            songNumber += 1   

#         if len(enabledSongs) > 1:
#            while True:
#               song=randint(0,len(enabledSongs)-1)
#               if enabledSongs[song] != currentSong:
#                  returnValue = enabledSongs[song]
#                  break
#         else:
#            returnValue = enabledSongs[0]       

      return returnValue

#--------------------------------------------------------      
   def disableSong(self, songs=(), username=None, stationname=None, disableAll=False, allStations = False, commit=False): 
#--------------------------------------------------------      
      #songs must be a tuble of 1 to many songs to disable
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   

      if stationname == None: 
         _station = self.getActiveStation()
      else: 
         _station = stationname   
            
      returnValue = False
      if _user !=None and _station!=None:
         cursor = self.db.cursor()
         if disableAll:
            if allStations:
               sql = 'UPDATE SONGS SET enabled =0 WHERE username = ?'
               cursor.execute(sql, (_user,))
            else:
               sql = 'UPDATE SONGS SET enabled = 0 WHERE station = ? AND username = ?'
               cursor.execute(sql, (_station, _user))

            #self.mp3.stop()

         else:   
            for song in songs:
               sql = 'UPDATE SONGS SET enabled = 0 WHERE station = ? AND username = ? AND number = ?'
               cursor.execute(sql, (_station, _user, song))
               #if self.countSongs() == 0: self.mp3.stop()
         
         self.populateSongsOnPickList()

         if commit: self.db.commit()

      return returnValue
      
#--------------------------------------------------------      
   def enableSong(self, songs=(), username=None, stationname=None, enableAll = False, allStations = False, commit=False): 
#--------------------------------------------------------      
      #songs must be a tuble of 1 to many songs to disable
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   

      if stationname == None: 
         _station = self.getActiveStation()
      else: 
         _station = stationname   
      
      returnValue = False

      if _user !=None and _station!=None:
         cursor = self.db.cursor()
         if enableAll:
            if allStations:
               sql = 'UPDATE SONGS SET enabled = 1 WHERE username = ?'
               cursor.execute(sql, (_user,))
            else:
               sql = 'UPDATE SONGS SET enabled = 1 WHERE station = ? AND username = ?'
               cursor.execute(sql, (_station, _user))
               #if self.countSongs() == 0:
               #   self.mp3.play(number=str(1))
         else:   
            for song in songs:
               sql = 'UPDATE SONGS SET enabled = 1 WHERE station = ? AND username = ? AND number = ?'
               cursor.execute(sql, (_station, _user, song))
            #if self.countSongs() == 1:
               #self.mp3.play(number=str(song))
         
         self.populateSongsOnPickList()
         
         if commit: self.db.commit()
            
      return returnValue
      
#--------------------------------------------------------      
   def sumToSongCount(self, song=1, username=None, stationname=None, commit=False): 
#--------------------------------------------------------      
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   

      if stationname == None: 
         _station = self.getActiveStation()
      else: 
         _station = stationname   
      
      returnValue = 0

      try: 
         if _user !=None and _station!=None:
            count = self.getSongCount(song, username=_user, stationname=_station)+1
            self.setSongCount(song=song, count=count, username=_user, stationname=_station, commit=commit)         
            returnValue = count

      except Exception as err:
         if self.verbose: print(traceback.format_exc())
            
      return returnValue
      
#--------------------------------------------------------      
   def setSongCount(self, song=1, count=0, username=None, stationname=None, commit=False):
#--------------------------------------------------------      
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   

      if stationname == None: 
         _station = self.getActiveStation()
      else: 
         _station = stationname   
      
      returnValue = 0
      try:
         if _user !=None and _station!=None:
            cursor = self.db.cursor()
            sql = 'UPDATE SONGS SET count = ? WHERE station = ? AND username = ? AND number = ?'
            cursor.execute(sql, (count,_station, _user, song))

            if commit: 
               self.db.commit()

      except Exception as err:
         if self.verbose: print(traceback.format_exc())
            
      return count
      
#--------------------------------------------------------      
   def getSongCount(self, song=1, username=None, stationname=None): 
#--------------------------------------------------------      
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   

      if stationname == None: 
         _station = self.getActiveStation()
      else: 
         _station = stationname   
      
      returnValue = 0
      
      try: 
         if _user !=None and _station!=None:
            cursor = self.db.cursor()
            sql = 'SELECT count FROM SONGS WHERE station = ? AND username = ? AND number = ?'
            cursor.execute(sql, (_station, _user, song))
            returnValue = cursor.fetchone()[0]

      except Exception as err:
         if self.verbose: print(traceback.format_exc())
            
      return returnValue


#--------------------------------------------------------      
   def likeitSong(self, song=1, username=None, stationname=None, commit=False): 
#--------------------------------------------------------      
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   

      if stationname == None: 
         _station = self.getActiveStation()
      else: 
         _station = stationname   
      
      returnValue = False
      try:
         if _user !=None and _station!=None:
            cursor = self.db.cursor()
            sql = 'UPDATE SONGS SET likeit = 1 WHERE station = ? AND username = ? AND number = ?'
            cursor.execute(sql, (_station, _user, song))
            
            self.enableSong(songs=[song,], username=_user, stationname=_station, commit=commit)            

      except Exception as err:
         if self.verbose: print(traceback.format_exc())
            
      return True

#--------------------------------------------------------      
   def dontLikeitSong(self, song=1, username=None, stationname=None, commit=False): 
#--------------------------------------------------------      
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   

      if stationname == None: 
         _station = self.getActiveStation()
      else: 
         _station = stationname   
      
      returnValue = False
      try:
         if _user !=None and _station!=None:
            cursor = self.db.cursor()
            sql = 'UPDATE SONGS SET likeit = -1 WHERE station = ? AND username = ? AND number = ?'
            cursor.execute(sql, (_station, _user, song))
            
            self.disableSong(songs=[song,], username=_user, stationname=_station, commit=commit)            

      except Exception as err:
         if self.verbose: print(traceback.format_exc())
            
      return True

#--------------------------------------------------------      
   def resetLikeitSong(self, song=1, username=None, stationname=None, commit=False): 
#--------------------------------------------------------      
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   

      if stationname == None: 
         _station = self.getActiveStation()
      else: 
         _station = stationname   
      
      returnValue = False
      try:
         if _user !=None and _station!=None:
            cursor = self.db.cursor()
            sql = 'UPDATE SONGS SET likeit = 0 WHERE station = ? AND username = ? AND number = ?'
            cursor.execute(sql, (_station, _user, song))

            if commit: 
               self.db.commit()

      except Exception as err:
         if self.verbose: print(traceback.format_exc())
            
      return True
      
#--------------------------------------------------------      
   def getLikeItValue(self, song=1, username=None, stationname=None): 
#--------------------------------------------------------      
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   

      if stationname == None: 
         _station = self.getActiveStation()
      else: 
         _station = stationname   
      
      returnValue = 0
      
      try: 
         if _user !=None and _station!=None:
            cursor = self.db.cursor()
            sql = 'SELECT likeit FROM SONGS WHERE station = ? AND username = ? AND number = ?'
            cursor.execute(sql, (_station, _user, song))
            returnValue = cursor.fetchone()[0]

      except Exception as err:
         if self.verbose: print(traceback.format_exc())
            
      return returnValue
      
#--------------------------------------------------------      
   def getUserType(self, username=None): 
#--------------------------------------------------------      
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   

      returnValue = 'n/a'
      
      try: 
         if _user !=None:
            cursor = self.db.cursor()
            sql = 'SELECT type FROM USERS WHERE username = ?'
            cursor.execute(sql, (_user,))
            returnValue = cursor.fetchone()[0]

      except Exception as err:
         print(traceback.format_exc())
         if self.verbose: print(traceback.format_exc())
            
      return returnValue
      
#--------------------------------------------------------      
   def isSongEnabled(self, song, username=None, stationname=None): 
#--------------------------------------------------------      
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   

      if stationname == None: 
         _station = self.getActiveStation()
      else: 
         _station = stationname   
      
      returnValue = False
      if _user !=None and _station!=None:
         cursor = self.db.cursor()
         sql='SELECT enabled FROM SONGS WHERE station = ? AND username = ? AND number = ?'
         cursor.execute(sql, (_station, _user, song))
         songs = cursor.fetchone()
         try:
            returnValue = True if songs[0] else False
         except:
            if self.verbose: print(traceback.format_exc())
            returnValue = False
         
      return returnValue
      
#--------------------------------------------------------      
   def listSongs(self, username=None, stationname=None, allSongs=False, allFieldsDelimited=False, delimiter=None): 
#--------------------------------------------------------      
      if delimiter == None: delimiter = ','
      
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   

      if stationname == None: 
         _station = self.getActiveStation()
      else: 
         _station = stationname   
      
      returnValue = []
      if _user !=None and _station!=None:
         cursor = self.db.cursor()
         if allSongs:
            sql='SELECT * FROM SONGS WHERE username = ?'
            cursor.execute(sql, (_user,))
         else:
            sql='SELECT * FROM SONGS WHERE station = ? AND username = ?'
            cursor.execute(sql, (_station, _user))

         songs = cursor.fetchall()
         seqNumber = 1
         for song in songs: 
            try:
               userName = song[0]
               songName = song[3].split("/")[-1].split(".mp3")[0]
               songNumber = song[4]
               enabled = '[e]' if song[5]==1 else '[d]'
               station=song[1]
               playlist=song[2]
               if allFieldsDelimited:
                  returnValue.append("%d%s%s%s%s%s%s%s%s%s%s%s%s"%(seqNumber, delimiter, songNumber, delimiter, enabled, delimiter, songName, delimiter, station, delimiter, playlist, delimiter, userName))
                  seqNumber += 1 
               else:
                  returnValue.append("%d %s %s"%(songNumber, enabled, songName))
                     
            except Exception as err: 
               if self.verbose: print(traceback.format_exc())
            
      return returnValue

#--------------------------------------------------------      
   def getUsersDetailsInDict(self, username = None, idNumber = None, allUsers=False, admin = 0): 
#--------------------------------------------------------      

      self.resetError()
      cursor = self.db.cursor()
      
      if username == None and idNumber == None: allUsers = True

      sql = 'SELECT * FROM USERS '
      
      if not allUsers: 
         if username != None: 
            sql += 'WHERE username = "%s" '%(username,)
         elif idNumber != None:   
            sql += 'WHERE nfcid = "%s" '%(idNumber,)
         sql += 'AND admin = "%s"'%(admin,)
      else: 
         sql += 'WHERE admin = "%s"'%(admin,)
      
      sql += ' ORDER BY username'
      
      returnUsers = {}     
      try: 
         cursor.execute(sql)
            
         
         for user in cursor.fetchall(): 
            returnUsers[self.row2dict(user,self.usersFields)['username']]=(self.row2dict(user,self.usersFields)) 

      except Exception as err: 
         if self.verbose: print(traceback.format_exc())
         if self.verbose: self.log.logMessage(message='(getUsersDetails) %s'%err, severity='ERROR')  
         if self.verbose: self.log.logMessage(message='(getUsersDetails) no se pudieron obtener detalles de los usuarios', severity='ERROR')
      
      return (returnUsers)         

      
#--------------------------------------------------------      
   def listAllSongs(self, delimiter=None): 
#--------------------------------------------------------      
      if delimiter == None: delimiter = ','
      
      allUsers = self.getUsersDetailsInDict()
      returnValue = []
      
      cursor = self.db.cursor()
      sql='SELECT * FROM SONGS'
      cursor.execute(sql)

      songs = cursor.fetchall()
      seqNumber = 1
      for song in songs: 
         try:
            userName = song[0]
            
            if allUsers[userName]['type'] == 'ARTIST':
               songName = song[3].split("/")[-1].split(".mp3")[0]
               songNumber = song[4]
               enabled = '[e]' if song[5]==1 else '[d]'
               station=song[1]
               playlist=song[2]
               returnValue.append("%d%s%s%s%s%s%s%s%s%s%s%s%s"%(seqNumber, delimiter, songNumber, delimiter, enabled, delimiter, songName, delimiter, station, delimiter, playlist, delimiter, userName))
               seqNumber += 1 
                  
         except Exception as err: 
            if self.verbose: print(traceback.format_exc())
            
      return returnValue
      
#--------------------------------------------------------      
   def listArtists(self): 
#--------------------------------------------------------      
      cursor = self.db.cursor()
      sql='SELECT username FROM USERS WHERE type = ?'
      cursor.execute(sql, ("ARTIST",))

      artists = cursor.fetchall()
      returnValue = []
      
      for artist in artists: 
         try:
            if len(artist[0]) > 0: 
               returnValue.append(artist[0])            
         except Exception as err: 
            if self.verbose: print(traceback.format_exc())
            
      return sorted(returnValue)
      
#--------------------------------------------------------      
   def isStationActive(self, station, username=None, mediatype=0): 
#--------------------------------------------------------      
      activeStation = None
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   

      if self.userExists(_user):
         cursor = self.db.cursor()
         sql='SELECT station, username, activestation, activemediatype, mediatype FROM STATIONS WHERE station = ? AND username = ? AND mediatype = ?'
      
         cursor.execute(sql, (station, _user, mediatype,))
         station = cursor.fetchone()
      
         if station != None:
            if station[2] and station[3]: 
               try: 
                  activeStation = station[0]
               except Exception as err: 
                  if self.verbose: print(traceback.format_exc())
                  if self.verbose: self.log.logMessage(message='(isStationActive) %s'%err, severity='ERROR')  
                  if self.verbose: self.log.logMessage(message='(isStationActive) no se pudo determinar si la estacion %s esta activa'%(station), severity='ERROR')
           
      return activeStation != None
      
#--------------------------------------------------------      
   def getActiveStationDetails(self, username = None): 
#--------------------------------------------------------      
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   
         
      result = []
         
      if self.userExists(_user):
         sql = 'SELECT * FROM STATIONS WHERE username = "%s" AND  activestation = 1 AND activemediatype=1 '%(_user,)
      
         cursor = self.db.cursor()
         cursor.execute(sql)            

         returnStations = []
         for station in cursor.fetchall(): 
            returnStations.append(self.row2dict(station,self.stationsFields)) 

         try:  
            result = [] if returnStations == [] else returnStations[0]
         except Exception as err: 
            if self.verbose: print(traceback.format_exc())
            if self.verbose: self.log.logMessage(message='(getActiveStationDetails) %s'%err, severity='ERROR')  
            if self.verbose: self.log.logMessage(message='(getActiveStationDetails) no se pudo cargar el detalle de la estacion activa', severity='ERROR')
            
      return (result)

#--------------------------------------------------------      
   def isStationEnabled(self, station, username = None): 
#--------------------------------------------------------      
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   

      stationEnabled = False
      if self.userExists(_user) and self.stationExists(station, _user):
			sql = 'SELECT enabled FROM STATIONS WHERE station = "%s" AND username = "%s" AND activemediatype = 1 '%(station,_user,)
			cursor = self.db.cursor()
			cursor.execute(sql)      
			enabled = cursor.fetchone()
			if enabled != None: 
				try:
					stationEnabled = True if enabled[0]==1 else False
				except:
					if self.verbose: print(traceback.format_exc()) 
      
      return stationEnabled
      
#--------------------------------------------------------      
   def getActiveStation(self, username = None): 
#--------------------------------------------------------      
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   

      activeStation = None
         
      if self.userExists(_user):

         sql = 'SELECT station FROM STATIONS WHERE username = "%s" AND  activestation = 1 AND activemediatype=1 '%(_user,)
         
         cursor = self.db.cursor()
         cursor.execute(sql)      
      
         station = cursor.fetchone()
      
         if station != None: 
            try:
               activeStation = station[0]
            except Exception as err: 
               if self.verbose: print(traceback.format_exc())
               if self.verbose: self.log.logMessage(message='(getActiveStation) %s'%err, severity='ERROR')  
               if self.verbose: self.log.logMessage(message='(getActiveStation) no se pudo obtener la estacion activa', severity='ERROR')
      
      return activeStation

#--------------------------------------------------------      
   def getStationActiveMediatype(self, station, username=None): 
#--------------------------------------------------------      
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   

      mediatype = None
      if self.userExists(_user):
         try: 
            cursor = self.db.cursor()
            cursor.execute('''SELECT station, mediatype FROM STATIONS WHERE station = ? AND username = ? AND activemediatype=1''',(station, _user,))      
      
            _mt = cursor.fetchone()
        
            if _mt != None:
               mediatype = int(_mt[1])
         except Exception as err: 
            if self.verbose: print(traceback.format_exc())
            if self.verbose: self.log.logMessage(message='(getActiveStationMediatyoe) %s'%err, severity='ERROR')  
            if self.verbose: self.log.logMessage(message='(getStationActiveMediatype) problemas al obtener el Mediatype activo', severity='ERROR')
      else: 
         if self.verbose: self.log.logMessage(message='(getStationActiveMediatype) user "%s" dont exists'%(_user), severity='ERROR')
      
      return mediatype
      
#--------------------------------------------------------      
   def getActiveMediatype(self, username=None): 
#--------------------------------------------------------      
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   

      mediatype = None
      if self.userExists(_user):

         cursor = self.db.cursor()
         cursor.execute('''SELECT station, mediatype FROM STATIONS WHERE username = ? AND  activestation = 1 AND activemediatype=1''',(_user,))      
      
         _mt = cursor.fetchone()
        
         if _mt != None:
            mediatype = int(_mt[1])
      
      return mediatype
            
#--------------------------------------------------------      
   def getActiveMediatype_old(self, username=None): 
#--------------------------------------------------------      
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   

      mediatype = None
      if self.userExists(_user):

         cursor = self.db.cursor()
         cursor.execute('''SELECT station, mediatype FROM STATIONS WHERE username = ? AND  activestation = 1 AND activemediatype=1''',(_user,))      
      
         _mt = cursor.fetchone()
        
         if _mt != None:
            mediatype = int(_mt[1])
      
      return mediatype

#--------------------------------------------------------      
   def activateStation(self, station, username=None, mediatype=None, commit = False, dimm=False): 
#--------------------------------------------------------      
      self.resetError()     
      
      if station == self.getActiveStation(): return '(WARNING) [%s] is already active'%station 
       
      _mt=mediatype

      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   
      
      returnValue = ''
      if mediatype != None:
         if mediatype == 0: 
            mediaUpdate = [1,0]
         else: 
            mediaUpdate = [0,1]   
         
      if self.userExists(_user):   

         if self.stationExists(station, _user, mediatype=_mt):
            if self.verbose: self.log.logMessage(message='(activateStation) activating station "%s" for user "%s" on table STATIONS'%(station,_user), severity='INFO')
            returnValue='(OK) station [%s] for user [%s] was activated'%(station,_user)
           
            if dimm: 
               volume = int(self.getCurrentContextDetails()['volume'])
               self.dimmVolume(lastVolume=0)
 
            self.saveContext()
            
            cursor = self.db.cursor()
            try: 
               if self.getActiveStation(_user) != None: 
				   cursor.execute('UPDATE STATIONS SET activestation = 0 WHERE station = ? AND username = ? ', (self.getActiveStation(_user), _user,))             
            except Exception as err: 
               if self.verbose: print(traceback.format_exc())
               if self.verbose: self.log.logMessage(message='(activateStation) %s'%err, severity='ERROR')  
               if self.verbose: self.log.logMessage(message='(activateStation) table stations was not update for station [%s]'%(station), severity='ERROR')
               returnValue='(ERROR) table stations was not updated for station [%s]'%(station)

            if mediatype != None: 
               try: 
                  cursor.execute('UPDATE STATIONS SET activestation = 1, activemediatype = ? WHERE station = ? AND username = ? AND mediatype = ? AND enabled = 1', (mediaUpdate[0], station, _user, 0))
               except Exception as err: 
                  if self.verbose: print(traceback.format_exc())
                  if self.verbose: self.log.logMessage(message='(activateStation) %s'%err, severity='ERROR')  
                  if self.verbose: self.log.logMessage(message='(activateStation) mediatype [mp3] was not updated for station [%s]'%(station), severity='ERROR')
                  returnValue='(ERROR) mediatype [mp3] was not updated for station [%s]'%(station)
               try: 
                  cursor.execute('UPDATE STATIONS SET activestation = 1, activemediatype = ? WHERE station = ? AND username = ? AND mediatype = ?  AND enabled = 1', (mediaUpdate[1], station, _user, 1))
               except Exception as err: 
                  if self.verbose: print(traceback.format_exc())
                  if self.verbose: self.log.logMessage(message='(activateStation) %s'%err, severity='ERROR')  
                  if self.verbose: self.log.logMessage(message='(activateStation)  mediatype [radio] was not updated for station [%s]'%(station), severity='ERROR')
                  returnValue='(ERROR) mediatype [radio] was not updated for station [%s]'%(station)
            else: 
               try: 
                  cursor.execute('UPDATE STATIONS SET activestation = 1, activemediatype =1 WHERE station = ? AND username = ? AND mediatype = 0 AND enabled = 1', (station, _user))
               except Exception as err: 
                  if self.verbose: print(traceback.format_exc())
                  if self.verbose: self.log.logMessage(message='(activateStation) %s'%err, severity='ERROR')  
                  if self.verbose: self.log.logMessage(message='(activateStation) active station was unabled to be updated', severity='ERROR')
                  returnValue='(ERROR) active station was unabled to be updated'

            if _user == self.getActiveUser(): 
               self.activateContext(clear=True, username=_user) 

            if dimm: 
               self.dimmVolume(lastVolume=volume)
            
            if commit: self.db.commit()

         else:   
            if self.verbose: self.log.logMessage(message='(activateStation) Unable to activate station "%s" for user "%s" on table STATIONS, because %s was not found!'%(station,_user,station), severity='WARNING')
            returnValue = '(ERROR) station [%s] was not found!'%(station)

      else:   
         if self.verbose: self.log.logMessage(message='(activateStation) Unable to activate station "%s" for user "%s" on table STATIONS, because user %s was not found!'%(station,_user,_user), severity='WARNING')
         returnValue='(ERROR) user [%s] was not found!'%(_user)
         
      return returnValue   

#--------------------------------------------------------      
   def disableStation(self, station, username=None, commit=True): 
#--------------------------------------------------------      
      self.resetError()     
      
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   
      
      returnValue = ''
         
      if self.userExists(_user):   

         if self.stationExists(station, _user):
            returnValue='(OK) station [%s] for user [%s] was disabled'%(station,_user)
           
            cursor = self.db.cursor()
            
            try: 
					cursor.execute('UPDATE STATIONS SET enabled = 0 WHERE station = ? AND username = ?', (station, _user))
            except Exception as err: 
					if self.verbose: print(traceback.format_exc())
					if self.verbose: self.log.logMessage(message='(disableStation) %s'%err, severity='ERROR')  
					if self.verbose: self.log.logMessage(message='(disableStation) station [%s] could not been disabled'%(station), severity='ERROR')
					returnValue='(ERROR) station [%s] could not been disabled'%(station)
            
            if commit: self.db.commit()

         else:   
            returnValue = '(ERROR) station [%s] was not found!'%(station)

      else:   
         returnValue='(ERROR) user [%s] was not found!'%(_user)
         
      return returnValue   

#--------------------------------------------------------      
   def disableAllStations(self, username, commit=True): 
#--------------------------------------------------------      
      self.resetError()     
      _user = username
      returnValue = ''
      if self.userExists(_user):   
         returnValue='(OK) all stations for user %s were disabled'%(_user)
         cursor = self.db.cursor()
         try: 
            cursor.execute('UPDATE STATIONS SET enabled = 0 WHERE username = "%s"'%(_user))
         except Exception as err: 
            if self.verbose: print(traceback.format_exc())
            if self.verbose: self.log.logMessage(message='(disableAllStation) %s'%err, severity='ERROR')  
            if self.verbose: self.log.logMessage(message='(disableAllStation) stations could not been disabled', severity='ERROR')
            returnValue='(ERROR) stations could not been disabled'

         self.deactivateAllStations() 
         if commit: self.db.commit()
      else:   
         returnValue='(ERROR) user [%s] was not found!'%(_user)
         
      return returnValue   

#--------------------------------------------------------      
   def enableStation(self, station, username=None, commit=True): 
#--------------------------------------------------------      
      self.resetError()     
      
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   
      
      returnValue = ''
         
      if self.userExists(_user):   

         if self.stationExists(station, _user):
            returnValue='(OK) station [%s] for user [%s] was enabled'%(station,_user)
           
            cursor = self.db.cursor()
            
            try: 
					cursor.execute('UPDATE STATIONS SET enabled = 1 WHERE station = ? AND username = ?', (station, _user))
            except Exception as err: 
					if self.verbose: print(traceback.format_exc())
					if self.verbose: self.log.logMessage(message='(enableStation) %s'%err, severity='ERROR')  
					if self.verbose: self.log.logMessage(message='(enableStation) station [%s] could not been enabled'%(station), severity='ERROR')
					returnValue='(ERROR) station [%s] could not been enabled'%(station)
            
            if commit: self.db.commit()

         else:   
            returnValue = '(ERROR) station [%s] was not found!'%(station)

      else:   
         returnValue='(ERROR) user [%s] was not found!'%(_user)
         
      return returnValue   

#--------------------------------------------------------      
   def enableAllStations(self, username, commit=True): 
#--------------------------------------------------------      
      self.resetError()     
      _user = username   
      returnValue = ''
         
      if self.userExists(_user):   
         returnValue='(OK) all stations for user were enabled'
         cursor = self.db.cursor()
         try: 
            cursor.execute('UPDATE STATIONS SET enabled = 1 WHERE username = "%s"'%(_user))
         except Exception as err: 
            if self.verbose: print(traceback.format_exc())
            if self.verbose: self.log.logMessage(message='(enableAllStation) %s'%err, severity='ERROR')  
            if self.verbose: self.log.logMessage(message='(enableAllStation) stations could not been enabled', severity='ERROR')
            returnValue='(ERROR) stations could not been enabled'
         if commit: self.db.commit()
      else:   
         returnValue='(ERROR) user [%s] was not found!'%(_user)
         
      return returnValue   

#--------------------------------------------------------      
   def deactivateStation(self, station, username=None, mediatype=0, commit = True): 
#--------------------------------------------------------      
      self.resetError()      
      _mt=mediatype

      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   
      
      if self.userExists(_user):
         if self.stationExists(station, _user):
            if self.verbose: self.log.logMessage(message='(deactivateStation) deactivating station "%s" for user "%s" on table STATIONS'%(_user,username), severity='INFO')
            cursor = self.db.cursor()
            cursor.execute('UPDATE STATIONS SET activestation = 0 WHERE station = ? AND username = ?', (station,_user))             
            if commit: self.db.commit()
         else:   
            if self.verbose: self.log.logMessage(message='(deactivateStation) unable to deactivate station "%s" for user "%s" on table STATIONS, because it was not found!'%(_user,username), severity='WARNING')

#--------------------------------------------------------      
   def deactivateAllStations(self, username=None, commit = True): 
#--------------------------------------------------------      
      self.resetError()      
      
      returnValue = ''
      
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   

      if self.userExists(_user):
         if self.verbose: self.log.logMessage(message='deactivating all stations for user "%s" on table STATIONS'%(_user), severity='INFO')
         returnValue = '(OK) deactivating all stations for user [%s]'%(_user)
         cursor = self.db.cursor()
         cursor.execute('UPDATE STATIONS SET activestation = 0 WHERE username = ? ', (_user,))             
         if commit: self.db.commit()
      else:   
         returnValue = '(ERROR) user [%s] does not exist'%(_user)
      
      return returnValue
#--------------------------------------------------------      
   def playlistInStationExists(self, playlist, station, username=None, mediatype=None): 
#--------------------------------------------------------      
      self.resetError()

      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   

      user=None 
      if self.userExists(_user):
         cursor = self.db.cursor()

         if mediatype == None: 
            cursor.execute('''SELECT station FROM STATIONPLAYLISTS WHERE playlist = ? AND station = ? AND username = ?''', (playlist, station, _user,))
         else: 
            cursor.execute('''SELECT station FROM STATIONPLAYLISTS WHERE playlist = ? AND station = ? AND username = ? AND mediatype = ?''', (playlist, station, _user,mediatype,))

         user = cursor.fetchone()

      return user!=None

#--------------------------------------------------------      
   def addPlaylistInStation(self, playlist, station, username=None, mediatype=0, genre="n/a", commit = False, dontPlay=False): 
#--------------------------------------------------------      
      self.resetError()
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username 
         
      returnValue = ''     

      if self.userExists(_user):

         if self.playlistInStationExists(playlist, station, _user): 
            if self.verbose: self.log.logMessage(message='(addPlaylistInStation) playlist [%s] already exists in station [%s] for user [%s]'%(playlist,station,_user), severity='WARNING')
            returnValue ='(ERROR) playlist [%s] already exists in station [%s] for user [%s]'%(playlist,station,_user)
         else:  
            if not self.stationExists(station, _user, mediatype):
               self.addStation(station,username=_user,commit=True)

            tplaylist = self.defaultPlaylistPath+'/'+playlist   
               
            if mediatype==0:
               if not tplaylist.endswith('.m3u'):
                  tplaylist = self.defaultPlaylistPath+'/'+playlist+'.m3u' 
               else:
                  playlist=playlist[:-4]
            else: 
               if not tplaylist.endswith('.pls'):
                  tplaylist = self.defaultPlaylistPath+'/'+playlist+'.pls'
               else:
                  playlist=playlist[:-4]
               
            if os.path.isfile(tplaylist):
               try:
                  cursor = self.db.cursor()
                  cursor.execute('''INSERT INTO STATIONPLAYLISTS(username, station, playlist, mediatype) VALUES(?,?,?,?)''', (_user,station,playlist,mediatype))

                  #add songs to SONGS tables
                  songNumber=1
                  for song in catFile(filename=tplaylist):
                     cursor.execute('''INSERT INTO SONGS(username, station, playlist, song, enabled, count, number, likeit) VALUES(?,?,?,?,?,?,?,?)''', (_user,station,playlist,song,1,0,songNumber,0))
                     songNumber += 1

                  if self.verbose: self.log.logMessage(message='(addPlaylistInStation) playlist [%s] has been added to station [%s] of user [%s] to table STATIONPLAYLISTS!'%(playlist,station,_user), severity='INFO')
                  if station == self.getActiveStation():
                     self.mp3.load([playlist]) 
                  returnValue = '(OK) playlist [%s] has been added to station [%s] of user [%s]\n'%(playlist,station,_user)
                    
                  data = self.getCurrentContextDetails()
                  if commit: 
                     self.db.commit()
                  if self.verbose: self.log.logMessage(message='(addPlaylistInStation) commit transacction after adding playlist [%s] to station [%s] of user [%s] on table STATIONPLAYLISTS'%(playlist,station,_user), severity='INFO')
               except Exception as err:
                  if self.verbose: print(traceback.format_exc())   

            else:
               if self.verbose: self.log.logMessage(message='(ERROR) playlist %s does not exists!'%playlist)
               returnValue = '(ERROR) playlist %s does not exists!\n'%playlist
                  
            
#            else: 
#               if self.verbose: self.log.logMessage(message='(addPlaylistInStation) station [%s] does not exists'%(station), severity='ERROR')
#               returnValue = '(ERROR) station [%s] does not exists for user [%s]'%(station,_user)
      else:
         if _user==None: 
            if self.verbose: self.log.logMessage(message='(addPlaylistInStation) no user active', severity='ERROR')
            returnValue = '(ERROR) no user active\n'
         else: 
            if self.verbose: self.log.logMessage(message='(addPlaylistInStation) user [%s] does not exists'%_user, severity='ERROR')
            returnValue = '(ERROR) user [%s] does not exists\n'%_user

      return returnValue

#--------------------------------------------------------      
   def addPlaylistsInStationByPosition(self, playlists, station, genre="n/a", username=None, mediatype=0, commit = False, dontPlay=False): 
#--------------------------------------------------------      
      self.resetError()
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username 
      
      returnValue = ''     

      if self.userExists(_user):
         
         allPlaylists = list(self.mp3.listPlayLists())
         if not self.stationExists(station, _user, mediatype):
            self.addStation(station, username=_user, genre=genre);

         cursor = self.db.cursor()
         
         for playlist in playlists:
            try:
               if (type(playlist) is str):
                  playlistName = allPlaylists[int(playlist)]
               elif (type(playlist) is int):
                  playlistName = allPlaylists[playlist]

               tplaylist = self.defaultPlaylistPath+'/'+playlistName   
               if mediatype==0:
                  if not tplaylist.endswith('.m3u'):
                     tplaylist = self.defaultPlaylistPath+'/'+playlistName+'.m3u' 
                  else:
                     playlistName=playlistName[:-4]
               else: 
                  if not tplaylist.endswith('.pls'):
                     tplaylist = self.defaultPlaylistPath+'/'+playlistName+'.pls'
                  else:
                     playlistName=playlistName[:-4]

               if os.path.isfile(tplaylist):
                  if not self.playlistInStationExists(playlistName, station, _user):
                     cursor.execute('''INSERT INTO STATIONPLAYLISTS(username, station, playlist, mediatype) VALUES(?,?,?,?)''', (_user,station,playlistName,mediatype))
                     if self.verbose: self.log.logMessage(message='(addPlaylistsInStationByPosition) playlist [%s] has been added to station [%s] of user [%s] to table STATIONPLAYLISTS!'%(playlistName,station,_user), severity='INFO')

                     #add songs to SONGS tables
                     songNumber=1
                     for song in catFile(filename=tplaylist):
                        cursor.execute('''INSERT INTO SONGS(username, station, playlist, song, enabled, count, number, likeit) VALUES(?,?,?,?,?,?,?,?)''', (_user,station,playlist,song,1,0,songNumber,0))
                        songNumber += 1

                     if commit: 
                        self.db.commit()
                        if self.verbose: self.log.logMessage(message='(addPlaylistsInStationByPosition) commit transacction after adding station [%s]'%(station), severity='INFO')

                     returnValue = '(OK) playlists were added to station [%s] of user [%s] to table STATIONPLAYLISTS!\n'%(station,_user)

                  else:
                     if self.verbose: self.log.logMessage(message='(addPlaylistsInStationByPosition) playlist [%s] already exists in station [%s] for user [%s]'%(playlistName,station,_user), severity='WARNING')
                     returnValue = '(ERROR) some or all playlists already exists in station [%s] for user [%s]\n'%(station,_user)

               else:
                  if self.verbose: self.log.logMessage(message='(ERROR) playlist %s does not exists!'%playlistName)
                  returnValue = '(ERROR) playlist %s does not exists!\n'%playlistName

            except Exception as err:
               if self.verbose: print(traceback.format_exc())
               if self.verbose: self.log.logMessage(message='(addPlaylistsInStationByPosition) un error desconocido ha ocurrido', severity='ERROR')
               returnValue = '(ERROR) station cannot be created\n'

      else: #user exists
         if _user==None: 
            if self.verbose: self.log.logMessage(message='(addPlaylistsInStationByPosition) no user active', severity='ERROR')
            returnValue = '(ERROR) no user active\n'
         else: 
            if self.verbose: self.log.logMessage(message='(addPlaylistsInStationByPosition) user [%s] does not exists'%_user, severity='ERROR')
            returnValue = '(ERROR) user [%s] does not exists\n'%_user

      return returnValue
      
#--------------------------------------------------------      
   def addPlaylistsInStation(self, playlists, station, username=None, mediatype=0, genre="n/a", commit = False, dontPlay=False): 
#--------------------------------------------------------      
      self.resetError()
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username 
         
      returnValue = ''     

      if self.userExists(_user):
         #add station if this is not in the STATION table
         if not self.stationExists(station, _user, mediatype):
            self.addStation(station, username=_user, genre=genre);

         if self.stationExists(station, _user, mediatype):
            try:
               cursor = self.db.cursor()
               for playlist in playlists: 
                  tplaylist = self.defaultPlaylistPath+'/'+playlist   
                  if mediatype==0:
                     if not playlist.endswith('.m3u'):
                        tplaylist = self.defaultPlaylistPath+'/'+playlist+'.m3u' 
                     else:
                        playlist=playlist[:-4]
                  else: 
                     if not playlist.endswith('.pls'):
                        tplaylist = self.defaultPlaylistPath+'/'+playlist+'.pls'
                     else:
                        playlist=playlist[:-4]

                  if os.path.isfile(tplaylist):
                     if not self.playlistInStationExists(playlist, station, _user):
                        #add playlist to STATIONPLAYLISTS table
                        cursor.execute('''INSERT INTO STATIONPLAYLISTS(username, station, playlist, mediatype) VALUES(?,?,?,?)''', (_user,station,playlist,mediatype))

                        songNumber=1
                        for song in catFile(filename=tplaylist):
                           cursor.execute('''INSERT INTO SONGS(username, station, playlist, song, enabled, count, number, likeit) VALUES(?,?,?,?,?,?,?,?)''', (_user,station,playlist,song,1,0,songNumber,0))
                           songNumber += 1

                        if self.verbose: self.log.logMessage(message='(addPlaylistsInStation) playlist [%s] has been added to station [%s] of user [%s] to table STATIONPLAYLISTS!'%(playlist,station,_user), severity='INFO')
                        returnValue = '(OK) playlists were added to station [%s] of user [%s] to table STATIONPLAYLISTS!'%(station,_user)

                        if station == self.getActiveStation():
                           self.mp3.load([playlist]) 
                                                        
                        data = self.getCurrentContextDetails()
                        if commit: 
                           self.db.commit()
                           if self.verbose: self.log.logMessage(message='(addPlaylistsInStation) commit transacction after adding playlist [%s] to station [%s] of user [%s] on table STATIONPLAYLISTS'%(playlist,station,_user), severity='INFO')

                     else:
                        if self.verbose: self.log.logMessage(message='(addPlaylistsInStation) playlist [%s] already exists in station [%s] for user [%s]'%(playlist,station,_user), severity='WARNING')
                        returnValue='(ERROR) playlist [%s] already exists in station [%s] for user [%s]\n'%(playlist,station,_user)
                  else: #path exists
                     if self.verbose: self.log.logMessage(message='(ERROR) playlist %s does not exists!'%playlist)
                     returnValue='(ERROR) playlist %s does not exists!\n'%playlist
                  
            except Exception as err:
               if self.verbose: print(traceback.format_exc())   
         else: #station exists 
            if self.verbose: self.log.logMessage(message='(addPlaylistsInStation) station [%s] does not exists'%(station), severity='ERROR')
            returnValue = '(ERROR) station [%s] does not exists for user [%s]'%(station,_user)
      else: #user exists
         if _user==None: 
            if self.verbose: self.log.logMessage(message='(addPlaylistsInStation) no user active', severity='ERROR')
            returnValue = '(ERROR) no user active\n'
         else: 
            if self.verbose: self.log.logMessage(message='(addPlaylistsInStation) user [%s] does not exists'%_user, severity='ERROR')
            returnValue = '(ERROR) user [%s] does not exists\n'%_user

      return returnValue
          
          
#--------------------------------------------------------      
   def removePlaylistFromStation(self, playlist, station, username=None, mediatype=0, commit = False): 
#--------------------------------------------------------      
      self.resetError()
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   

      if playlist.endswith('.m3u') or playlist.endswith('.pls'):
         playlist = playlist[:-4]
         
      returnValue = ''
      if self.userExists(_user):
         if self.stationExists(station, _user, mediatype):
            if not self.playlistInStationExists(playlist, station, _user): 
               if self.verbose: self.log.logMessage(message='(removePlaylistFromStation) playlist %s doesnt exists in station "%s" for user %s'%(playlist,station,_user), severity='ERROR')
               returnValue = '(ERROR) playlist [%s] does not exists in station [%s] for user [%s]'%(playlist,station,_user)
               
            else:  
               cursor = self.db.cursor()
               cursor.execute('DELETE FROM STATIONPLAYLISTS WHERE playlist = ? AND station = ? AND username = ?', (playlist, station, _user,))
               cursor.execute('DELETE FROM SONGS WHERE playlist = ? AND station = ? AND username = ?', (playlist, station, _user,))
               if self.verbose: self.log.logMessage(message='(removePlaylistFromStation) playlist "%s" has been deleted from station "%s" of user "%s" to table STATIONPLAYLISTS!'%(playlist,station,_user), severity='INFO')
               returnValue = '(OK) playlist [%s] has been deleted from station [%s] of user [%s]\n'%(playlist,station,_user)

               if commit: 
                  self.db.commit()
                  if self.verbose: self.log.logMessage(message='(removePlaylistFromStation) commit transacction after deleting playlist "%s" from station "%s" of %s on table STATIONS'%(playlist,station,_user), severity='INFO')
         else:
            returnValue = '(ERROR) station [%s] does not exists\n'%(station)
      else:
         returnValue = '(ERROR) user [%s] does not exists\n'%(_user)
                  
      return returnValue
#--------------------------------------------------------      
   def removeAllPlaylistsFromStation(self, station, username=None, mediatype=0, commit = False): 
#--------------------------------------------------------      
      self.resetError()
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username 
      
      returnValue = ''     

      if self.userExists(_user):
         if self.stationExists(station, _user, mediatype):
            cursor = self.db.cursor()
            cursor.execute('DELETE FROM STATIONPLAYLISTS WHERE station = ? AND username = ?', (station, _user,))
            cursor.execute('DELETE FROM SONGS WHERE station = ? AND username = ?', (station, _user,))

            if self.verbose: self.log.logMessage(message='(removeAllPlaylistsFromStation) all playlists has been deleted from station "%s" of user "%s" to table STATIONPLAYLISTS!'%(station,_user), severity='INFO')

            if commit: 
               self.db.commit()
               if self.verbose: self.log.logMessage(message='(removeAllPlaylistsFromStation) commit transacction after deleting all playlists from station %s of %s on table STATIONPLAYLISTS'%(station, _user), severity='INFO')
            
            returnValue = '(OK) All playlists were removed from station [%s] of user [%s]\n'%(station,_user)   
         else:
            returnValue = '(ERROR) station [%s] does not exists\n'%(station)
      else:
         returnValue = '(ERROR) user [%s] does not exists\n'%(_user)
                  
      return returnValue

#--------------------------------------------------------      
   def removeAllPlaylistsFromUser(self, username = None, mediatype=0, commit = False): 
#--------------------------------------------------------      
      self.resetError()
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   

      if self.userExists(_user):
         cursor = self.db.cursor()
         cursor.execute('DELETE FROM STATIONPLAYLISTS WHERE username = ?', (_user,))
         cursor.execute('DELETE FROM SONGS WHERE username = ?', (_user,))
         if self.verbose: self.log.logMessage(message='(removeAllPlaylistsFromUser) all playlists has been deleted from user "%s" to table STATIONPLAYLISTS!'%(_user), severity='INFO')

         if commit: 
            self.db.commit()
            if self.verbose: self.log.logMessage(message='(removeAllPlaylistsFromUser) commit transacction after deleting all playlists from user %s on table STATIONPLAYLISTS'%(_user), severity='INFO')

         returnValue = '(OK) All playlists were removed from all station of user [%s]\n'%(_user)   
      else:
         returnValue = '(ERROR) user [%s] does not exists\n'%(_user)
                  
      return returnValue

#--------------------------------------------------------      
   def getPlaylistDetailsFromStation(self, station, username=None, playlist = None, mediatype = None): 
#--------------------------------------------------------      
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   

      returnList = []
      if self.userExists(_user):
         try: 
            sql = 'SELECT * FROM STATIONPLAYLISTS '
 
            sql += 'WHERE username = "%s" '%(_user,)
            
            if playlist != None: 
               sql += 'AND playlist LIKE "%s" '%('%'+playlist+'%',)
      
            if mediatype != None: 
               sql += 'AND mediatype = %s '%(mediatype,)

            sql += 'AND station = "%s" ORDER by playlist'%(station,) 

            cursor = self.db.cursor()
            cursor.execute(sql) 
 
            for line in cursor.fetchall(): 
               returnList.append(self.row2dict(line,self.stationPlaylistsFields))          
         except Exception as err: 
            if self.verbose: print(traceback.format_exc())
            if self.verbose: self.log.logMessage(message='(getPlaylistDetailsFromStation) %s'%err, severity='ERROR')  
            if self.verbose: self.log.logMessage(message='(getPlaylistDetailsFromStation) problemas al obtener la lista de detalles de la estaci{on %s'%station, severity='ERROR')

      else:      
         if self.verbose: self.log.logMessage(message='(getPlaylistDetailsFromStation) user "%s" dont exists'%(_user), severity='ERROR')

      return (returnList) 

#--------------------------------------------------------      
   def listActivePlaylists(self): 
#--------------------------------------------------------      
      results = []   
      try: 
         for i in self.getPlaylistDetailsFromStation(self.getActiveStation(), mediatype = self.getActiveMediatype()): 
            results.append(i['playlist'])
      except Exception as err: 
         if self.verbose: print(traceback.format_exc())
         if self.verbose: self.log.logMessage(message='(listActivePlaylists) %s'%err, severity='ERROR')  
         if self.verbose: self.log.logMessage(message='(listActivePlaylists) error al listar los playlists de la estacion activa', severity='ERROR')
         
      return results   

#--------------------------------------------------------      
   def listPlaylists(self, station, mediatype = None, username=None): 
#--------------------------------------------------------      
      results = []   
      if mediatype == None: 
         _mediatype = self.getActiveMediatype()
      else: 
         _mediatype = mediatype         

      if username == None: 
         _user = self.activeUser
      else: 
         _user = username 
               
      try: 
         for i in self.getPlaylistDetailsFromStation(station, username=_user, mediatype = _mediatype): 
            results.append(i['playlist'])
      except Exception as err: 
         if self.verbose: print(traceback.format_exc())
         if self.verbose: self.log.logMessage(message='(listPlayLists) %s'%err, severity='ERROR')  
         if self.verbose: self.log.logMessage(message='(listPlaylists) error al listar los playlists de la estacion %s'%station, severity='ERROR')

      return results   

#--------------------------------------------------------      
   def getPlaylistsDetails(self, username=None, playlist = None, mediatype = None, allPlaylists = False, activeStation = False): 
#--------------------------------------------------------      
      if username == None: 
         _user = self.activeUser
      else: 
         _user = username   

         returnList = []
      if self.userExists(_user):
         try: 
            cursor = self.db.cursor()
      
            sql = 'SELECT * FROM STATIONPLAYLISTS '
            if not allPlaylists:
               if playlist==None: 
                  sql += 'WHERE username = "%s" ORDER BY playlist '%(_user, ) 
               else:   
                  if mediatype != None:
                     if activeStation: 
                        sql = 'WHERE playlist LIKE "%s" AND username = "%s"'%('%'+playlist+'%', _user,)
                     else:
                        sql = 'WHERE playlist LIKE "%s" AND username = "%s"'%('%'+playlist+'%', _user,)
                  else: 
                     sql = 'WHERE playlist LIKE "%s" AND username = "%s" AND mediatype = ?'%('%'+playlist+'%', _user, mediatype)

            sql += 'ORDER BY username, station, playlist, mediatype'
       
            cursor.execute(sql)      
            for line in cursor.fetchall(): 
               returnList.append(self.row2dict(line,self.stationPlaylistsFields))
         except Exception as err: 
            if self.verbose: print(traceback.format_exc())
            if self.verbose: self.log.logMessage(message='(getPlaylistsDetails) %s'%err, severity='ERROR')        
            if self.verbose: self.log.logMessage(message='(getPlaylistsDetails) no se pudo obtener la lista de playlists', severity='ERROR')
      else:      
         if self.verbose: self.log.logMessage(message='(getPlaylistsDetails) user "%s" dont exists'%(_user), severity='ERROR')

      return (returnList) 

#--------------------------------------------------------      
   def printTableStations(self, username=None, activeUser=False): 
#--------------------------------------------------------      
      if activeUser: 
         _user=self.activeUser
      else:
         _user = username   
      
      if username == None and not activeUser: 
         stations = 'SELECT * FROM STATIONS ORDER BY username'
      else: 
         stations = 'SELECT * FROM STATIONS WHERE username = "%s" ORDER BY username'%_user
      
      cursor = self.db.cursor()
      cursor.execute(stations)
      print '-'*80
      print 'TABLE: STATIONS ' + str([f[0] for f in cursor.description])
      print '-'*80
      for row in cursor.fetchall(): print row

#--------------------------------------------------------      
   def printTableUsers(self, username=None, activeUser=False): 
#--------------------------------------------------------      
      if activeUser: 
         _user=self.activeUser
      else:
         _user = username   
      
      if username == None and not activeUser: 
         users = 'SELECT * FROM USERS ORDER BY username'
      else: 
         users = 'SELECT * FROM USERS WHERE username = "%s" ORDER BY username'%_user
      
      cursor = self.db.cursor()
      cursor.execute(users)
      print '-'*80
      print 'TABLE: USERS ' + str([f[0] for f in cursor.description])
      print '-'*80
      for row in cursor.fetchall(): print row

#--------------------------------------------------------      
   def printAllTables(self, username=None, activeUser=False, pAllUsers=False, pAllTables= True, pusers=False, pstations=False, pstationPlaylists=False, puserPlaylists=False, pactivities=False, pspecialists=False):#, pconfig=False ): 
#--------------------------------------------------------      
      
      if activeUser: 
         _user=self.activeUser
      else:
         _user = username   
      
      if username == None and not activeUser or pAllUsers: 
         users = 'SELECT * FROM USERS ORDER BY username'
         stations = 'SELECT * FROM STATIONS ORDER BY username'
         stationPlaylists = 'SELECT * FROM STATIONPLAYLISTS ORDER BY username'
      else: 
         users = 'SELECT * FROM USERS WHERE username = "%s" ORDER BY username'%_user
         stations = 'SELECT * FROM STATIONS WHERE username = "%s" ORDER BY username'%_user
         stationPlaylists = 'SELECT * FROM STATIONPLAYLISTS WHERE username = "%s" ORDER BY username'%_user
      
      if pAllTables: 
         pusers=True
         pstations=Truesql = 'UPDATE USERS SET volume = %s, active = 1'%context['volume']

         pstationPlaylists=True
         puserPlaylists=True
         pactivities=True
         pspecialists=True
         #pconfig=True
      
      cursor = self.db.cursor()
      if pusers:
         cursor.execute(users)
         print '-'*80
         print 'TABLE: USERS ' + str(self.usersFields)
         print '-'*80
         for row in cursor.fetchall(): print row
      
      if pstations:
         cursor.execute(stations)
         print '-'*80
         print 'TABLE: STATIONS ' + str(self.stationsFields)
         print '-'*80
         for row in cursor.fetchall(): print row

      if pstationPlaylists:
         cursor.execute(stationPlaylists)
         print '-'*80
         print 'TABLE: STATIONPLAYLISTS ' + str(self.stationPlaylistsFields)
         print '-'*80
         for row in cursor.fetchall(): print row

#--------------------------------------------------------      
   def getCurrentContextDetails(self): 
#--------------------------------------------------------      
      
      if self.getActiveUser() == None: return
      
      returnData = {}
            
      maxIter = 10
      iterNum = 0

      self.mp3.updateInfo()
      returnData['state']=self.mp3.getPlayState(refresh=False)
      returnData['songpos']=self.mp3.getSongPos(refresh=False)
      returnData['timelapsed']=self.mp3.getSongTimeLapsed(refresh=False)
      returnData['username']=self.activeUser
      returnData['volume']=self.mp3.getVolume(refresh=False)

      returnData['songname']=self.mp3.getSong(refresh=False).replace('"','').replace("\'",'')

      returnData['artistname']=self.mp3.getArtist(refresh=False)
      
      return returnData

#--------------------------------------------------------      
   def dimmVolume(self, lastVolume = 0, steps = 10): 
#--------------------------------------------------------      
      #print 'dimmVolume: called by %s'%inspect.stack()[1][3]

      currentVolume = self.mp3.getVolume(refresh=True)
      cv = currentVolume
           
      if lastVolume > currentVolume: 
         lv = lastVolume - currentVolume
         st = int(lv/steps)
         if lv > steps:
            for i in range(steps): 
               cv += st
               self.mp3.setVolume(cv)
               sleep(.1)
         
         if cv != lastVolume:
            self.mp3.setVolume(lastVolume)

      elif lastVolume <= currentVolume: 
         lv = currentVolume - lastVolume
         st = int(lv/steps)
         if lv > steps:
            for i in range(steps): 
               cv -= st
               self.mp3.setVolume(cv)
               sleep(.1)

         if cv != lastVolume:
            self.mp3.setVolume(lastVolume)
         
#--------------------------------------------------------      
   def saveContext(self, commit = True, verbose=True, extraParams={}): 
#--------------------------------------------------------      
      
      if self.getActiveStation() == None:
         if self.verbose: self.log.logMessage(message='(saveContext) no station is active for user "%s", so context cannot be saved'%(self.activeUser), severity='WARNING')
         return     
      
      updateGvar = ''
      xpar = [None for x in range(10)]
      for key in extraParams:
			index = int(key.split('gvar')[1])-1
			xpar[index] = extraParams[key]
			if extraParams[key] != None:
				updateGvar += ', gvar%d = "%d"'%(index+1,extraParams[key])

      cursor = self.db.cursor()

      context = self.getCurrentContextDetails()
      #if self.verbose: self.log.logMessage(message='(saveContext) saving context for station "%s" of user "%s"'%(self.getActiveStation(), self.activeUser), severity='INFO')
      
      self.mp3.updateInfo()   
      try: 
         sql = 'UPDATE STATIONS SET state = "%s", songpos = %s, timelapsed = %s, songname = "%s", artistname = "%s" WHERE username = "%s" AND  activestation = 1 AND activemediatype=1 '%(context['state'], context['songpos'], context['timelapsed'], context['songname'], context['artistname'], self.activeUser,)
         cursor.execute(sql)      

         sql = 'UPDATE USERS SET volume = %s, active = 1'%context['volume']
         sql += updateGvar
         sql += ' WHERE username = "%s"'%(self.activeUser)
         
         cursor.execute(sql)      
            
         if commit: 
            self.db.commit()

      except Exception as err:
         if self.verbose: print(traceback.format_exc())
         if self.verbose: self.log.logMessage(message='(saveContext) %s'%err, severity='ERROR')  
         if self.verbose: self.log.logMessage(message='(saveContext) no se pudo guardar el contexto del usuaio activo', severity='ERROR')

#--------------------------------------------------------      
   def activateContext(self, username=None, clear=False, play=True): 
#--------------------------------------------------------   
      #print stack()[1][3]

      if username == None: 
         _user = self.activeUser
      else: 
         _user = username 
       
      data=self.getContextInfo()

      station = self.getActiveStation()
      
      mediaType = self.getActiveMediatype()
      if clear: self.mp3.clear() 
      
      if station !=None:
         if self.verbose: self.log.logMessage(message='(activateContext) activating context for user %s on station %s'%(self.activeUser, station), severity='INFO')
         pl = []
         for playlist in self.listPlaylists(station, mediaType, username=_user): 
            if "'" in playlist: 
               playlist=playlist.split("'")[0]+"\\'"+playlist.split("'")[1]
            if mediaType == 1:
               pl.append(playlist+'.pls')
            else:    
               pl.append(playlist)

         self.mp3.load(pl)

         try: 
            self.mp3.seek(position=int(data['songpos']), offset=int(data['timelapsed']))  
         except: 
            if self.verbose: print(traceback.format_exc())

         if data['state']=='play': 
            self.mp3.play()
         else: 
            self.mp3.pause()
            self.mp3.pause()
            
         self.populateSongsOnPickList()

#--------------------------------------------------------      
   def getContextInfo(self): 
#--------------------------------------------------------   
      returnData = {}
      stationInfo = self.getActiveStationDetails(username = self.activeUser)

      if stationInfo != []:
         returnData['mediatype']=stationInfo['mediatype']
         returnData['songpos']=stationInfo['songpos']
         returnData['state']=stationInfo['state']
         returnData['station']=stationInfo['station']
         returnData['genre']=stationInfo['genre']
         returnData['timelapsed']=stationInfo['timelapsed']
         returnData['songname']=stationInfo['songname']
         returnData['artistname']=stationInfo['artistname']
      else: 
         returnData['mediatype']='0'
         returnData['songpos']='0'
         returnData['state']='stop'
         returnData['station']='no active station'
         returnData['genre']=''
         returnData['timelapsed']='0'
         returnData['songname']='no title'
         returnData['artistname']='no artist'
      
      return (returnData)
      
#--------------------------------------------------------      
   def loadMusicContext(self, clear=True): 
#--------------------------------------------------------      
      
      context = self.getContextInfo()
      if clear:
         self.mp3.clear()
      
#--------------------------------------------------------      
   def printActiveUser(self): 
#--------------------------------------------------------      
      print '-'*50
      print 'user: %s'%self.getActiveUser()
      print '-'*50
      print '   stations: '
      print '-'*50
         
      for i in self.listStations(): 
         media = 'mp3' if self.getStationActiveMediatype(i) == 0 else 'radio' 

         if i == self.getActiveStation():
            print '%16s (active) (%s)'%(i,media)
         else: 
            print '%16s          (%s)'%(i,media)
      print '-'*50
      print '   playlists: '
      print '-'*50
      for i in self.listActivePlaylists(): 
         print '     '+i
         

class treeList:
######################################################################################
## changes version 1.6.2 (ago-10-2015                                               ##
## - bug in procedure emptyList()                                                   ##
##   - change for deleting each element of root level                               ##
## - getList() added                                                                ##
######################################################################################

######################################################################################
## treelist version 1.6.2 (beta1)                                                   ##
## Copyright Alejandro Dirgan (@ydirgan, alejandro.dirgan@gmail.com)                ##
## mar-30-2014                                                                      ##
######################################################################################
   #constants no to be modified
   MLEVEL  = 0
   MITEMS  = 1  
   ##Aditional information can be added here ### (-----1------)
   MDATA = 2
   NEXTFIELD = 3
   #############################################
   MLABEL  = NEXTFIELD
   MACTION = NEXTFIELD+1
   MOFFSET = NEXTFIELD+1
   
   MAXLEVEL = 0  
   VISIBLE = True
   INACTIVE=False  
   ROOT = 'Root'
   CMD = 'Command'
   EMPTYCMD = ''
   PATH=''
   FILENAME=''
   CHECKED=False
   
   SUBMENU = 1
   LABEL = 2
   FILE = 3
   DIRECTORY = 4
   
   BEGINNING = -2
   END = -1

######################################################################################
## INIT class treelist                                                              ##
## Creates a empty list that is defined to have only a root entry                   ##
## Structure: [level, number of items, label/list]                                  ##
## Example: List with a second level which contains 4 entries                       ##
## [0, 4, 'Root', [1, 0, 'File'], [1, 0, 'Edit'], [1, 0, 'Tools'], [1, 0, 'Help']]  ##
## Example: Open, Save Items added to File Entry                                    ##
## [1, 2, 'File', [2, -1, 'Open', 'command'], [2, -1, 'Save', 'command']]           ##
######################################################################################
   def __init__(self):
      
      
      self.DATA = {'ACTIVE':self.INACTIVE, 
                   'COMMAND': self.EMPTYCMD, 
                   'VISIBLE':self.VISIBLE, 
                   'PATH': self.PATH, 
                   'TYPE':self.LABEL, 
                   'FILENAME':self.FILENAME, 
                   'CHECKED':self.CHECKED,
                  }
      
      self.ylist = [0,0,self.DATA, self.ROOT]
      self.init()


######################################################################################
##  This is the initialization process for the class                                ##
######################################################################################
   def init(self):
      self.CURRENTLEVEL = self.ylist
      self.CURRENTINDEX = self.MOFFSET   
      self.CURRENTITEM = list()     
      self.CURRENTLEVELTYPE = self.ROOT
      self.trace = list()
      self.EMPTY = True;
      self.MAINCOUNT = 0
      self.INIT = False

 
      self.POSITION=list()

      self.depth = 0

      self.POSITION.append([self.CURRENTLEVEL, self.CURRENTINDEX])
      
      self.BASEPOSITION = list(self.POSITION)
            
      self.findList = list()
      self.findListPos = 0
      

######################################################################################
##  This is a dummy method for demostration purposes                                ##
######################################################################################
   def dummyMethod(self):
      pass

######################################################################################
##  Set active the first element of the first level                                 ##
######################################################################################
   def goTop(self):
      self.setActiveOff()
      self.CURRENTLEVEL = self.ylist
      self.trace = list()
      self.goItemIndex(0)
      self.setActiveOn()
      #print 'goTop() called by %s'%inspect.stack()[1][3]
      return self
     
           
######################################################################################
##  Fill dummy list using a menu as example                                         ##
######################################################################################
   def fillDummyItems(self):
      self.addItem('File', parentName=self.ROOT)
      self.addItem('Open', parentName='File', command=self.dummyMethod)
      self.addItem('Save', parentName='File', command=self.dummyMethod)
      self.addItem('Save as...', parentName='File', command=self.dummyMethod)

      self.addItem('Edit', parentName=self.ROOT)
      self.addItem('Copy', parentName='Edit', command=self.dummyMethod)
      self.addItem('Copy to', parentName='Copy', command=self.dummyMethod)
      self.addItem('To a file', parentName='Copy to', command=self.dummyMethod)
      self.addItem('To dropbox', parentName='Copy to', command=self.dummyMethod)
      self.addItem('Copy from', parentName='Copy', command=self.dummyMethod)
      self.addItem('From file', parentName='Copy from')
      self.addItem('From dropbox', parentName='Copy from', command=self.dummyMethod)

      self.addItem('Cut', parentName='Edit', command=self.dummyMethod)
      self.addItem('Paste', parentName='Edit')

      self.addItem('Tools', parentName=self.ROOT)
      self.addItem('Help', parentName=self.ROOT)

      self.addItem('About...', parentName='Help')

######################################################################################
##  This procedure adds a subtree to the end of the current level                   ##
######################################################################################
   def addSubtree(self, itemName, subtree, name = 'imported', parent='', fromRoot = True):
           
      if self.find(itemName, parentName=parent, exactMatch=True) and isinstance(subtree, treeList) or itemName==self.ROOT:
         position = list(self.BASEPOSITION)
         self.savePosition(mem=position)
         
         if fromRoot: #add subtree including its root that will be renamed as name
            subtree.ylist[self.MLEVEL] =  self.CURRENTLEVEL[self.CURRENTINDEX][self.MLEVEL]+1
            subtree.ylist[self.MLABEL] = name
 
            if itemName==self.ROOT:
               self.ylist[self.MITEMS]=self.ylist[self.MITEMS]+1
               self.ylist.append(subtree.ylist)
               self.replaceLevels(self.ylist, self.ylist[self.MLEVEL])
            else:
               self.CURRENTLEVEL[self.CURRENTINDEX][self.MITEMS]=self.CURRENTLEVEL[self.CURRENTINDEX][self.MITEMS]+1
               self.CURRENTLEVEL[self.CURRENTINDEX][self.MDATA]['TYPE'] = self.SUBMENU
               self.CURRENTLEVEL[self.CURRENTINDEX].append(subtree.ylist)
               self.replaceLevels(self.CURRENTLEVEL, self.CURRENTLEVEL[self.CURRENTINDEX][self.MLEVEL]-1)
         else: #add items below root
            subtree.goTop()
            for item in range(subtree.numberOfItems()):
               subtree.CURRENTITEM[self.MLEVEL]=self.CURRENTLEVEL[self.CURRENTINDEX][self.MLEVEL]+1

               if itemName == self.ROOT:  
                  self.ylist[self.MITEMS]=self.ylist[self.MITEMS]+1
                  self.ylist.append(subtree.CURRENTITEM)
               else: 
                  self.CURRENTLEVEL[self.CURRENTINDEX][self.MITEMS]=self.CURRENTLEVEL[self.CURRENTINDEX][self.MITEMS]+1
                  self.CURRENTLEVEL[self.CURRENTINDEX][self.MDATA]['TYPE'] = self.SUBMENU
                  self.CURRENTLEVEL[self.CURRENTINDEX].append(subtree.CURRENTITEM)
               subtree.goNext()

            if itemName == self.ROOT:  
               self.replaceLevels(self.ylist, self.ylist[self.MLEVEL])
            else:   
               self.replaceLevels(self.CURRENTLEVEL, self.CURRENTLEVEL[self.CURRENTINDEX][self.MLEVEL]-1)
         
         self.restorePosition(mem=position)
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
   def replaceLevels(self, array, level):
      if not self.EMPTY:       
         for entry in array[self.MOFFSET:]:           
            itemType = entry[self.MDATA]['TYPE']
            entry[self.MDATA]['ACTIVE']=self.INACTIVE
            entry[self.MLEVEL]=level+1
            if itemType == self.SUBMENU or itemType == self.DIRECTORY:
               self.replaceLevels(entry, level+1)

######################################################################################
##  Add item to the tree                                                            ##
##                                                                                  ##
##  example: additem('File', parentName = self.ROOT)                                ##
##           add item to a object.ROOT (first level)                                ##
##  example: additem('Save', parentName = 'File', command=saveCommand)              ##
##           add item to File entry and assign a procedure to it                    ##
##  example: additem('Copy')                                                        ##
##           add item to the current activated elemnent                             ##
##                                                                                  ##
## Notes:                                                                           ##
##       - by default all items are added as labels                                 ##
##       - when a item is added, its parent becomes a submenu                       ##
######################################################################################
         ################################################### 
         #append item
         #Additional fields can be added before to functions
         ################################################### 

   def addItem(self,itemName, parentName='', command='',  pathString='', typeItem=LABEL, filename='', position = END, checked=False, debug=False):
      if parentName:
         self.find2add(self.ylist, parentName, itemName, command, pathString, typeItem, position, checked, filename)
      else:	   
         self.addItem2Current(itemName, command, pathString, typeItem, position, checked, filename, debug)
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
   def find2add(self, array, parent, item, command, pathString, typeItem, position, checked, filename):
      self.DATA = {'ACTIVE':self.INACTIVE, 
                   'COMMAND': command, 
                   'VISIBLE':self.VISIBLE, 
                   'PATH': pathString,
                   'TYPE':typeItem, 
                   'FILENAME':filename, 
                   'CHECKED':checked,
                  }

      if array[self.MLABEL] == parent:   
              
         ################################################### 
         #append item
         #Additional fields can be added before field 'item'
         ################################################### 

         if position == self.END:
            array.append([array[self.MLEVEL]+1,0, self.DATA, item])
         elif position == self.BEGINNING: 
            array.insert(self.NEXTFIELD+1, [array[self.MLEVEL]+1,0, self.DATA, item])
         else:
            array.append([array[self.MLEVEL]+1,0, self.DATA, item])
            

         #update maxlevel actually appended
         if array[self.MLEVEL]+1 > self.MAXLEVEL:
            self.MAXLEVEL = array[self.MLEVEL]+1

         array[self.MITEMS] +=1

         self.EMPTY = False
         if parent == self.ROOT: self.MAINCOUNT += 1

         if array[self.MDATA]['TYPE'] != self.DIRECTORY:
            array[self.MDATA]['TYPE']=self.SUBMENU

         if not self.INIT:
            self.INIT = True
            self.CURRENTINDEX = self.MOFFSET
            self.CURRENTITEM = self.CURRENTLEVEL[self.CURRENTINDEX]
            self.setActiveOn()

      else:    
         for entry in array[self.MOFFSET:]:

            #if found it
            if entry[self.MLABEL] == parent:
               ################################################### 
               #append item
               #Additional fields can be added before field 'item'
               ################################################### 
               if position == self.END:
                  entry.append([entry[self.MLEVEL]+1,0,self.DATA, item])
               elif position == self.BEGINNING: 
                  entry.insert(self.NEXTFIELD+1,[entry[self.MLEVEL]+1,0,self.DATA, item])
               else:
                  entry.append([entry[self.MLEVEL]+1,0,self.DATA, item])

               if entry[self.MLEVEL]+1 > self.MAXLEVEL:
                  self.MAXLEVEL = entry[self.MLEVEL]+1

               entry[self.MITEMS] +=1

               self.EMPTY = False
               if parent == self.ROOT: self.MAINCOUNT += 1

               if entry[self.MDATA]['TYPE'] != self.DIRECTORY:
                  entry[self.MDATA]['TYPE']=self.SUBMENU

               if not self.INIT:
                  self.INIT = True
                  self.CURRENTINDEX = self.MOFFSET
                  self.CURRENTITEM = self.CURRENTLEVEL[self.CURRENTINDEX]
                  self.setActiveOn()

            else: #keep looking
               if entry[self.MITEMS] > 0:
                  self.find2add(entry,parent,item, command, pathString, typeItem, position, checked, filename)

######################################################################################
##  Add item to current activated item                                              ##
##                                                                                  ##
##  example: additem('File')                                                        ##
##           add item 'File' to a active item                                       ##
##  example: additem('Save', command=saveCommand)                                   ##
##           add item 'Save' to current item and assign a procedure to it           ##
##                                                                                  ##
######################################################################################
   def addItem2Current(self, item, command='', pathString='', typeItem=LABEL, position=END, checked=False, filename='', debug=False):
	   
      self.DATA = {'ACTIVE':self.INACTIVE, 
                   'COMMAND': command, 
                   'VISIBLE':self.VISIBLE, 
                   'PATH': pathString, 
                   'TYPE':typeItem, 
                   'FILENAME':filename, 
                   'CHECKED':checked,
                  } 
      
      if not self.INIT:
         self.addItem(item, parentName=self.ROOT)
         return
               
      currentItem = self.CURRENTLEVEL[self.MOFFSET+self.activeIndex()]

      ################################################### 
      #append item
      #Additional fields can be added before field 'item'
      ################################################### 
      if position == self.END:
         currentItem.appepyMusicServerLib.pynd([currentItem[self.MLEVEL]+1,0,self.DATA, item])
      elif position == self.BEGINNING:
         currentItem.insert(self.NEXTFIELD+1, [currentItem[self.MLEVEL]+1,0,self.DATA, item])
      else:
         currentItem.append([currentItem[self.MLEVEL]+1,0,self.DATA, item])
      
      #update maxlevel actually appended
      if currentItem[self.MLEVEL]+1 > self.MAXLEVEL:
         self.MAXLEVEL = currentItem[self.MLEVEL]+1

      currentItem[self.MITEMS] +=1

      self.EMPTY = False
      if self.parentName() == self.ROOT: self.MAINCOUNT += 1
      
      if currentItem[self.MDATA]['TYPE'] != self.DIRECTORY:
         currentItem[self.MDATA]['TYPE']=self.SUBMENU 
                           
######################################################################################
##  reset the list to have only the root. All entries and items are eliminated      ##
##  the result is an empty list                                                     ##
######################################################################################
   def emptyList(self):

      if not self.EMPTY:
         self.gotTop()
         for item in self.itemsOfCurrentList():
            self.deleteItem(item)

#revisar porque este metodo produce list out of index
#         self.CURRENTLEVEL = self.ylist
#         self.goItemIndex(0)
#         self.trace=list()
#         self.emptyFindHistory()
#         for i in reversed(range(self.numberOfItems())):
#	    self.CURRENTLEVEL.remove(self.CURRENTLEVEL[self.MOFFSET+i])

#      self.init()

######################################################################################
##  remove all subitems of active entry                                             ##
##  then set the active entry to its ancestor                                       ##
######################################################################################
   def removeAllSubItemsOfActiveEntry(self):
      if not self.EMPTY:
         if self.typeOfActiveItem() == 'SubMenu':
            self.goDown()
            totalItems=self.numberOfItems()
            for i in reversed(range(totalItems)):
                self.CURRENTLEVEL.remove(self.CURRENTLEVEL[self.MOFFSET+i])
            self.CURRENTLEVEL[self.MITEMS]=0
            self.goUp()
      else:
         print 'removeAllSubItemsOfActiveEntry: The list is empty'

######################################################################################
##  remove all subitems of entry entryName                                          ##
##  set entryName as the active entry                                               ##
######################################################################################
   def removeAllSubItemsOfEntry(self, entryName, parent=''):
      if not self.EMPTY:
        self.savePosition()
        if self.find(entryName, parentName=parent):
           self.removeAllSubItemsOfActiveEntry()
           self.find(entryName)
           self.removeLastPosition()
           self.emptyFindHistory()
        else:
           print '%s NOT FOUND'%entryName
           self.restorePosition()
      else:
         print 'removeAllSubItemsOfEntry: The list is empty'

######################################################################################
##  remove active item and its subitems                                             ##
######################################################################################
   def deleteActiveItem(self):
      if not self.EMPTY:
         del self.CURRENTLEVEL[self.CURRENTINDEX]
         self.CURRENTLEVEL[self.MITEMS] -= 1


         if self.CURRENTLEVEL[self.MLABEL] == self.ROOT: self.MAINCOUNT -= 1

         if self.MAINCOUNT == 0:
            self.EMPTY = True
            self.INIT = False
         if self.CURRENTLEVEL[self.MLEVEL] > 0:
            self.goUp()
         else:   
            self.goTop()
      else:
         print 'deleteActiveItem: The list is empty'

      return self
      
######################################################################################
##  delete item itemName (this action remove all subitems too                       ##
######################################################################################        
   def deleteItem(self,itemName, parent='', recursive=False):
      self.found=False
      m=self.BASEPOSITION
      self.savePosition(m)
      if not recursive:
         if parent:
            self.found=self.find(itemName, parentName=parent, exactMatch=True)
         else:   
            self.found=self.find(itemName, exactMatch=True)
         
         if self.found:
            self.deleteActiveItem()
      else:
         self.goTop()
         self.find2delete(self.ylist, itemName, True)

      self.restorePosition(m) 
      self.emptyFindHistory() 
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
   def find2delete(self, array, item, recursive):
      
      for entry in array[self.MOFFSET:]:
         #if found it
         
         if entry[self.MLABEL] == item :        
            self.count = 0   
             
            if not recursive: self.found=True
            
            for i in array[self.MOFFSET:]:
               #if i[self.MDATA]['LABEL'] == item:
               if i[self.MLABEL] == item:
                  break
               self.count += 1
               
            del array[self.count+self.MOFFSET]

            array[self.MITEMS] -= 1
           
            if array[self.MLABEL] == self.ROOT: self.MAINCOUNT -= 1
            if self.MAINCOUNT == 0:
               self.EMPTY = True
               self.INIT = False
           
         else: #keep looking
            if entry[self.MITEMS] > 0 and not self.found:
               self.find2delete(entry,item, recursive)


######################################################################################
##  returns number of found items                                                   ##
######################################################################################        
   def foundItems(self):
      return len(self.findList)

######################################################################################
##  go to the first element found and set it active                                 ##
######################################################################################        
   def findFirst(self):
      if self.findList:
         self.setActiveOff()
         self.CURRENTLEVEL = self.findList[0][0]
         self.CURRENTINDEX = self.findList[0][1]+self.MOFFSET
         self.CURRENTITEM = self.CURRENTLEVEL[self.CURRENTINDEX]
         self.setActiveOn() 

######################################################################################
##  go to the last element found and set it active                                  ##
######################################################################################        
   def findLast(self):
      if self.findList:
         self.setActiveOff()
         self.CURRENTLEVEL = self.findList[-1][0]
         self.CURRENTINDEX = self.findList[-1][1]+self.MOFFSET
         self.CURRENTITEM = self.CURRENTLEVEL[self.CURRENTINDEX]
         self.setActiveOn() 

######################################################################################
##  find Next in the list and set it active                                         ##
######################################################################################        
   def findNext(self):
      if self.findList:
         self.find2listPos = (self.find2listPos + 1)%len(self.findList)
            
         self.setActiveOff()
         self.CURRENTLEVEL = self.findList[self.find2listPos][0]
         self.CURRENTINDEX = self.findList[self.find2listPos][1]+self.MOFFSET
         self.CURRENTITEM = self.CURRENTLEVEL[self.CURRENTINDEX]
         self.setActiveOn() 

######################################################################################
##  find previous in the list and set it active                                     ##
######################################################################################
   def findPrev(self):
      if self.findList:
         self.find2listPos = (self.find2listPos - 1)%len(self.findList)
            
         self.setActiveOff()
         self.CURRENTLEVEL = self.findList[self.find2listPos][0]
         self.CURRENTINDEX = self.findList[self.find2listPos][1]+self.MOFFSET
         self.CURRENTITEM = self.CURRENTLEVEL[self.CURRENTINDEX]
         self.setActiveOn() 


######################################################################################
##  empty find history                                                              ##
######################################################################################
   def emptyFindHistory(self):
      self.findList = list()
      self.find2listPos=0
      
######################################################################################
##  rename label of item                                                            ##
######################################################################################       
   def renameItem(self,itemName, newItemName, parent=''):

      if not self.EMPTY:
         self.found=False
         self.savePosition()
         self.found=self.find(itemName, parentName=parent)
         if self.found:
            self.CURRENTITEM[self.MLABEL]=newItemName     

         self.restorePosition()
         self.emptyFindHistory()

######################################################################################
##  rename label of current item                                                    ##
######################################################################################       
   def renameCurrentItem(self, newItemName):

      if not self.EMPTY:
         self.CURRENTITEM[self.MLABEL]=newItemName      

######################################################################################
##  rename label of current item                                                    ##
######################################################################################       
   def replaceLabel(self, newLabel):

      if not self.EMPTY:
         self.CURRENTITEM[self.MLABEL]=newLabel      

######################################################################################
##  find in the current level                                                       ##
######################################################################################        
   def findInLevel(self,itemName, exactMatch=True, beginWith=False, ignoreCase=True):
      
      if itemName == None: return False
      found = False
      
      ipos = self.activeIndex()
      self.goFirst()
      for item in range(self.numberOfItems()): 
         #print '%s %s'%(itemName, self.activeLabel())
         if beginWith: 
            if ignoreCase:
               if self.activeLabel().lower().startswith(itemName.lower()): 
                  found=True
                  break
            else:      
               if self.activeLabel().startswith(itemName): 
                  found=True
                  break
         if exactMatch: 
            if ignoreCase:
               if itemName.lower() == self.activeLabel().lower(): 
                  found = True
                  break
            else:
               if itemName == self.activeLabel(): 
                  found = True
                  break
         else: 
            if ignoreCase:
               if itemName.lower() in self.activeLabel().lower(): 
                  found = True
                  break
            else:
               if itemName in self.activeLabel(): 
                  found = True
                  break
                  

         self.goNext()   
      if not found:   
         self.goItemIndex(ipos)
      return found
                     
######################################################################################
##  find all items and save them to a list                                          ##
######################################################################################        
   def find(self,itemName, parentName='', exactMatch=False, beginWith=False, ignoreCase=True, acceptDuplicates=False, debug=False):
      self.found = False
      self.findList = list()
      self.savePosition()
      self.goTop()
      self.find2list(self.ylist, itemName, parentName, exactMatch, beginWith, ignoreCase, acceptDuplicates, debug)
      self.restorePosition()
      self.find2listPos=0     
      self.findFirst()
      return self.found

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
   def find2list(self, array, item, parent, exactMatch, beginWith, ignoreCase, acceptDuplicates, debug):


      for entry in array[self.MOFFSET:]: #FOR EACH ENTRY OF CURRENT LEVEL
      
         if not exactMatch: 
            if ignoreCase:
               if not beginWith:
                  match = entry[self.MLABEL].upper().find(item.upper()) >= 0
               else: 
                  match = entry[self.MLABEL].upper().startswith(item.upper())
            else:   
               if not beginWith:
                  match = entry[self.MLABEL].find(item) >= 0
               else: 
                  match = entry[self.MLABEL].startswith(item.upper())
         else: 
            if ignoreCase:
               match = entry[self.MLABEL].upper() == item.upper()
            else:   
               match = entry[self.MLABEL] == item
            
         if match: 
            found=False
            count = 0                            
            

            for i in array[self.MOFFSET:]: 

               if not exactMatch: 
                  if ignoreCase:
                     if not beginWith:
                        match1 = i[self.MLABEL].upper().find(item.upper()) >= 0
                     else:  
                        match1 = i[self.MLABEL].upper().startswith(item.upper())                      
                  else: 
                     if not beginWith:
                        match1 = i[self.MLABEL].find(item) >= 0
                     else: 
                        match1 = i[self.MLABEL].startswith(item)
                        
               else: 
                  if ignoreCase:
                     match1 = i[self.MLABEL].upper() == item.upper()
                  else: 
                     match1 = i[self.LABEL] == item

               if match1 : #FOUND ITEM                  
                  if parent: 
                     if not exactMatch: 
                        if ignoreCase:
                           if not beginWith:
                              match2 = array[self.MLABEL].upper().find(parent.upper()) >= 0
                           else:   
                              match2 = array[self.MLABEL].upper().startswith(parent.upper())
                        else: 
                           if not beginWith:
                              match2 = array[self.MLABEL].find(parent) >= 0
                           else:   
                              match2 = array[self.MLABEL].startswith(parent)
                     else: 
                        if ignoreCase:
                           match2 = array[self.MLABEL].upper() == parent.upper()
                        else: 
                           match2 = array[self.MLABEL] == parent

                     if match2: #FOUND PARENT
                        found=True
                        self.found = True
                  else: 
                     found=True
                     self.found = True
               
                  if found: #verify when beginWith is activated
                     foundInList=False
                     if not acceptDuplicates:
                        for j in range(len(self.findList)): #CHECK FOR DUPLICATED ENTRIES
                           if self.findList[j][0][self.MOFFSET+self.findList[j][1]] == array[self.MOFFSET+count]: 
                              foundInList=True
                     if not foundInList: 
                        self.findList.append([array, count]) #ADD TO FINDLIST IF NOT DUPLICATED
                                       
               count += 1

         if entry[self.MITEMS] > 0: #DOWN ON SUBLIST RECURSIVELY
            self.find2list(entry, item, parent, exactMatch, beginWith, ignoreCase, acceptDuplicates, debug) 

######################################################################################
##  Save the current position for go back purposes                                  ##
######################################################################################
   def savePosition(self, mem=None):
      if self.INIT:
         if mem == None: 
            mem = self.POSITION
            
         self.depth += 1
         mem.append([self.CURRENTLEVEL, self.CURRENTINDEX, self.trace])
         
######################################################################################
##  Restore de active position saved previosly with savePosition                    ##
######################################################################################
   def restorePosition(self, mem=None):

      #print 'restorePosition() called by %s'%inspect.stack()[1][3]

      if self.depth > 0: 
         if mem == None: 
            mem = self.POSITION

         self.setActiveOff()

         self.CURRENTLEVEL = mem[-1][0]
         self.CURRENTINDEX = mem[-1][1]
         self.trace = mem[-1][2]
      
         self.depth -= 1

         del mem[-1]
         try:  
            self.CURRENTITEM = self.CURRENTLEVEL[self.CURRENTINDEX]
         except: 
            pass   
         self.setActiveOn()

######################################################################################
##  remove the last position stored                                                 ##
######################################################################################
   def removeLastPosition(self):
     
      if self.depth > 0: 
         self.depth -= 1
         del self.POSITION[-1]

######################################################################################
##  get list with their hierarquical structure                                      ##
######################################################################################
   def getList(self, root=True):
      
      
      returnValue = []
      if not self.EMPTY:
         returnValue.append(self.ylist[self.MLABEL] if not self.ylist[self.MDATA]['CHECKED'] else self.ylist[self.MLABEL] +'[x]')   

         if not root: 
            rootPath=self.CURRENTLEVEL
         else:
            rootPath=self.ylist

         self.getListRec(rootPath, returnValue)
	 
      return returnValue

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
   def getListRec(self, array, returnValue):
      if not self.EMPTY:        
         for entry in array[self.MOFFSET:]:
            
            if entry[self.MDATA]['ACTIVE']:
               activeLabel = ' (current)'
            else:  
               activeLabel = ''

            itemType = entry[self.MDATA]['TYPE']
            
            indentLevel= entry[self.MLEVEL]
           
            if itemType == self.SUBMENU:
               returnValue.append("%s--> %s%s" % ('    '*indentLevel,entry[self.MLABEL], activeLabel if not entry[self.MDATA]['CHECKED'] else activeLabel + '[x]'))
               self.getListRec(entry, returnValue)
            elif itemType == self.LABEL:
               returnValue.append("%s(L) %s%s" % ('    '*indentLevel,entry[self.MLABEL], activeLabel if not entry[self.MDATA]['CHECKED'] else activeLabel +'[x]'))
            elif itemType == self.FILE:
               returnValue.append("%s(F) %s%s" % ('    '*indentLevel,entry[self.MLABEL], activeLabel if not entry[self.MDATA]['CHECKED'] else activeLabel +'[x]'))
            elif itemType == self.DIRECTORY:
               returnValue.append("%s(D) %s%s" % ('    '*indentLevel,entry[self.MLABEL], activeLabel if not entry[self.MDATA]['CHECKED'] else activeLabel +'[x]'))
               self.getListRec(entry, returnValue)
            elif self.CURRENTITEM[self.MDATA]['COMMAND'] != self.EMPTYCMD:
               returnValue.append("%s*   %s%s" % ('    '*indentLevel,entry[self.MLABEL], activeLabel if not entry[self.MDATA]['CHECKED'] else activeLabel +'[x]'))
      
     
######################################################################################
##  Print list with their hierarquical structure                                    ##
######################################################################################
   def printList(self, root=True):
      if self.EMPTY:
         print 'printList: The list is empty'
      else:  
         print self.ylist[self.MLABEL] if not self.ylist[self.MDATA]['CHECKED'] else self.ylist[self.MLABEL] +'[x]'   

         if not root: 
            rootPath=self.CURRENTLEVEL
         else:
            rootPath=self.ylist

         self.printListRec(rootPath)

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
   def printListRec(self, array):
      if not self.EMPTY:        
         for entry in array[self.MOFFSET:]:
            
            if entry[self.MDATA]['ACTIVE']:
               activeLabel = ' (current)'
            else:  
               activeLabel = ''

            itemType = entry[self.MDATA]['TYPE']
            
            indentLevel= entry[self.MLEVEL]
           
            if itemType == self.SUBMENU:
               print "%s--> %s%s" % ('    '*indentLevel,entry[self.MLABEL], activeLabel if not entry[self.MDATA]['CHECKED'] else activeLabel + '[x]')
               self.printListRec(entry)
            elif itemType == self.LABEL:
               print "%s(L) %s%s" % ('    '*indentLevel,entry[self.MLABEL], activeLabel if not entry[self.MDATA]['CHECKED'] else activeLabel +'[x]')
            elif itemType == self.FILE:
               print "%s(F) %s%s" % ('    '*indentLevel,entry[self.MLABEL], activeLabel if not entry[self.MDATA]['CHECKED'] else activeLabel +'[x]')
            elif itemType == self.DIRECTORY:
               print "%s(D) %s%s" % ('    '*indentLevel,entry[self.MLABEL], activeLabel if not entry[self.MDATA]['CHECKED'] else activeLabel +'[x]')
               self.printListRec(entry)
            elif self.CURRENTITEM[self.MDATA]['COMMAND'] != self.EMPTYCMD:
               print "%s*   %s%s" % ('    '*indentLevel,entry[self.MLABEL], activeLabel if not entry[self.MDATA]['CHECKED'] else activeLabel +'[x]')
              
   
######################################################################################
##  return active item and its attributes as string                                 ##
######################################################################################
   def activeItemInfo(self):
      if not self.EMPTY:
         if self.typeOfActiveItem() == 'SubMenu':
            return '%s: %s: %s (items)'%(self.activeLabel(),self.typeOfActiveItem(), self.CURRENTITEM[self.MITEMS])
         else:
            return '%s: %s'%(self.activeLabel(),self.typeOfActiveItem())

######################################################################################
##  return active item as its were a menu entry                                     ##
######################################################################################
   def activeItemString(self):
      returnValue = ''
      if not self.EMPTY:
         if self.typeOfActiveItem() == 'SubMenu':
            returnValue='[%s]'%(self.activeLabel())
         if self.typeOfActiveItem() == 'Label':
            returnValue='<%s>'%(self.activeLabel())
         if self.typeOfActiveItem() == 'Command':
            returnValue='(%s)'%(self.activeLabel())  
         if self.typeOfActiveItem() == 'Directory':
            returnValue='{%s}'%(self.activeLabel())  
      return returnValue

######################################################################################
##  returns current action of active entry    - DEPRECATED - use command instead    ##
######################################################################################
   def activeAction(self):
      returnValue=''
      if not self.EMPTY and self.typeOfActiveItem() == 'Command':
         #returnValue=self.CURRENTITEM[self.MCOMMAND]           
         returnValue=self.CURRENTITEM[self.MDATA]['COMMAND']          
      return returnValue

######################################################################################
##  returns path from active item                                                   ##
######################################################################################
   def activePath(self):
      returnValue=''
      if not self.EMPTY:
         returnValue=self.CURRENTITEM[self.MDATA]['PATH']         
      return returnValue

######################################################################################
##  returns filename from active item                                               ##
######################################################################################
   def activeFileName(self):
      returnValue=''
      if not self.EMPTY:
         returnValue=self.CURRENTITEM[self.MDATA]['FILENAME']           
      return returnValue

######################################################################################
##  returns full path from active item, including filename                          ##
######################################################################################
   def activeFullName(self):
      returnValue=''
      if not self.EMPTY:
         returnValue='%s/%s'%(self.CURRENTITEM[self.MDATA]['PATH'], self.CURRENTITEM[self.MLABEL])
      return returnValue

######################################################################################
##  check current item                                                              ##
######################################################################################       
   def checkCurrentItem(self, check=True):

      if not self.EMPTY:
         self.CURRENTITEM[self.MDATA]['CHECKED']=check
         
######################################################################################
##  toggle checked status current item                                              ##
######################################################################################       
   def toggleCurrentItem(self, check=True):

      if not self.EMPTY:
         self.CURRENTITEM[self.MDATA]['CHECKED'] =  not self.CURRENTITEM[self.MDATA]['CHECKED']
         
######################################################################################
##  returns stored procedure of active entry                                       ##
######################################################################################
   def command(self):
      returnValue=''
      if not self.EMPTY:
         if self.CURRENTITEM[self.MDATA]['COMMAND'] == self.EMPTYCMD:
            returnValue=self.dummyMethod
         else:   
            returnValue=self.CURRENTITEM[self.MDATA]['COMMAND']    
      return returnValue

######################################################################################
##  returns current active list                                                     ##
######################################################################################
   def activeLevel(self): #former activeList
      returnValue=list()
      if not self.EMPTY:
         returnValue=self.CURRENTLEVEL
      return returnValue  

######################################################################################
##  returns the active entry                                                        ##
######################################################################################
   def activeItem(self):
      returnValue=list()
      if not self.EMPTY:
         self.CURRENTITEM = self.CURRENTLEVEL[self.CURRENTINDEX]     
         returnValue=self.CURRENTITEM
      return returnValue  

######################################################################################
##  returns the active Label                                                        ##
######################################################################################
   def activeLabel(self):
      returnValue=''
      if not self.EMPTY:
         self.activeItem()
         returnValue=self.CURRENTITEM[self.MLABEL]
      return returnValue  

######################################################################################
##  returns the active Index                                                        ##
######################################################################################
   def activeIndex(self):
      returnValue=-1
      if not self.EMPTY:
         returnValue=self.CURRENTINDEX-self.MOFFSET
      return returnValue  
  
######################################################################################
##  returns the active position related to its level                                ##
######################################################################################
   def activePosition(self):
      returnValue=''
      if not self.EMPTY:
         returnValue=str(self.CURRENTINDEX-self.MOFFSET+1)+'/'+str(self.CURRENTLEVEL[self.MITEMS])
      return returnValue  

######################################################################################
##  return True if the active Item has sub items                                    ##
######################################################################################
   def activeEntryHasItems(self):
      returnValue = False
      if not self.EMPTY and self.typeOfActiveItem() == 'SubMenu': returnValue = True
      return returnValue
     
######################################################################################
##  returns number of items of current level                                        ##
######################################################################################
   def numberOfItems(self):
      return self.CURRENTLEVEL[self.MITEMS]

######################################################################################
##  returns number of subItems of current Item                                      ##
######################################################################################
   def numberOfSubItems(self):
      if self.CURRENTITEM[self.MITEMS]>=0:
         returnValue = self.CURRENTITEM[self.MITEMS]
      else:
         returnValue = 0
        
      return returnValue

######################################################################################
##  returns number of Items of upper level                                          ##
######################################################################################
   def numberOfSupraItems(self):
      returnValue=1
      if not self.EMPTY and self.parentName()!=self.ROOT: 
         self.savePosition()
         self.goUp()
         returnValue = self.numberOfItems()
         self.goDown()
         self.restorePosition() 
      return returnValue
      
######################################################################################
##  set current element active (only for internal use)                              ##
######################################################################################
   def setCommand2Current(self, cmd):
      if not self.EMPTY:
         self.CURRENTITEM[self.MDATA]['COMMAND']=cmd
         
######################################################################################
##  set current element active (only for internal use)                              ##
######################################################################################
   def setActiveOn(self):
      if not self.EMPTY:
         self.CURRENTITEM[self.MDATA]['ACTIVE']=True

######################################################################################
##  set current element inactive (only for internal use)                            ##
######################################################################################
   def setActiveOff(self):
      if not self.EMPTY:
         self.CURRENTITEM[self.MDATA]['ACTIVE']=False

######################################################################################
##  go and set active the first entry of current level                              ##
######################################################################################
   def goFirst(self):
      if not self.EMPTY:
         self.setActiveOff()
         self.CURRENTINDEX = self.MOFFSET
         self.CURRENTITEM = self.CURRENTLEVEL[self.CURRENTINDEX]
         self.setActiveOn()
         
      return self   
     
######################################################################################
##  set active the item indicated by index relative to the current level            ##
######################################################################################
   def goItemIndex(self, index):
      if not self.EMPTY:
         self.setActiveOff()
         self.CURRENTINDEX = (index % self.numberOfItems()) + self.MOFFSET
         self.CURRENTITEM = self.CURRENTLEVEL[self.CURRENTINDEX]
         self.setActiveOn()
      
      return self   

######################################################################################
##  set active the item indicated by itemName relative to the current level         ##
######################################################################################
   def goItemName(self, itemName):
      if not self.EMPTY:
         self.setActiveOff()
         count=0
         for i in self.CURRENTLEVEL[self.MOFFSET:]:
            if i[self.MLABEL] == itemName:
               self.CURRENTINDEX = count + self.MOFFSET
            count += 1
           
         self.CURRENTITEM = self.CURRENTLEVEL[self.CURRENTINDEX]
         self.setActiveOn()
      
      return self   

######################################################################################
##  go to the next entry in the current level and set active it active              ##
######################################################################################
   def goNext(self):
      if not self.EMPTY:
         self.setActiveOff()
         if self.CURRENTINDEX < (self.numberOfItems()+self.MOFFSET-1):
            self.CURRENTINDEX += 1
         else:
            self.CURRENTINDEX = self.MOFFSET
     
         self.CURRENTITEM = self.CURRENTLEVEL[self.CURRENTINDEX]
         self.setActiveOn()
         
      return self   

######################################################################################
##  go to the prev entry in the current level and set active it active              ##
######################################################################################
   def goPrev(self):
      if not self.EMPTY:
         self.setActiveOff()
         if self.CURRENTINDEX > self.MOFFSET:
           self.CURRENTINDEX -= 1
         else:
            self.CURRENTINDEX = (self.numberOfItems()+self.MOFFSET-1)
     
         self.CURRENTITEM = self.CURRENTLEVEL[self.CURRENTINDEX]
         self.setActiveOn()

      return self
######################################################################################
##  go to the last entry in the current level and set active it active              ##
######################################################################################
   def goLast(self):
      if not self.EMPTY:
         self.setActiveOff()
         self.CURRENTINDEX = self.numberOfItems()+self.MOFFSET-1
         self.CURRENTITEM = self.CURRENTLEVEL[self.CURRENTINDEX]
         self.setActiveOn()
         
      return self   

######################################################################################
##  if entry has subitems go to the next child level and set the first item active  ##
######################################################################################
   def goDown(self):
      if not self.EMPTY:
         if self.typeOfActiveItem() == 'SubMenu':
            self.setActiveOff()
            self.trace.append([self.CURRENTINDEX,self.CURRENTLEVEL])
            self.CURRENTLEVEL = self.CURRENTLEVEL[self.CURRENTINDEX]
            self.CURRENTINDEX = self.MOFFSET
            self.CURRENTITEM = self.CURRENTLEVEL[self.CURRENTINDEX]
            self.setActiveOn()
      
      return self      

######################################################################################
##  go up to the parent level of the list and set the previous active entry         ##
######################################################################################
   def goUp(self):
      if not self.EMPTY:
         if len(self.trace) > 0:
            self.setActiveOff()
            self.CURRENTLEVEL = self.trace[-1][1]
            self.CURRENTINDEX = self.trace[-1][0]
            self.CURRENTITEM = self.CURRENTLEVEL[self.CURRENTINDEX]
            del self.trace[-1]
            self.setActiveOn()
      
      return self
      
######################################################################################
##  returns the type of the active entry                                            ##
######################################################################################
   def activeItemType(self):
     
      returnType = ''
      if not self.EMPTY:
         self.CURRENTLEVELTYPE = self.CURRENTITEM[self.MITEMS]

         itemType = self.CURRENTITEM[self.MDATA]['TYPE']
         if itemType == self.SUBMENU:
            returnType = 'SubMenu'
         elif itemType == self.LABEL:
            returnType = 'Label'
         elif itemType == self.FILE:
               returnType = 'File'
         elif itemType == self.DIRECTORY:
               returnType = 'Directory'
         elif self.CURRENTITEM[self.MDATA]['COMMAND'] != self.EMPTYCMD:
               returnType = 'Command'
 
      return returnType

######################################################################################
##  returns the type of the active entry                                            ##
######################################################################################
   def typeOfActiveItem(self):

      return self.typeOfItem(self.CURRENTITEM)
     
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
   def typeOfItem(self, item):
      returnType = ''
      if not self.EMPTY:
         self.CURRENTLEVELTYPE = item[self.MITEMS]
         if self.CURRENTLEVELTYPE > 0:
            returnType = 'SubMenu'
         elif self.CURRENTLEVELTYPE == 0:
            if item[self.MDATA]['COMMAND'] == self.EMPTYCMD:
               returnType = 'Label'
            else:   
               returnType = 'Command'
 
      return returnType

######################################################################################
##  print debug info                                                                ##
######################################################################################
   def printDebug(self):
      if not self.EMPTY:
         print 'BEGIN: DEBUG INFORMACION *******************************************************'
         print 'main: CURRENT LEVEL (self.CURRENTLEVEL): '
         print self.CURRENTLEVEL
         print 'main: NUMBER OF ITEMS: %d'%(self.numberOfItems())
         print 'main: ACTIVE ITEM INDEX: %d'%(self.CURRENTINDEX-self.MOFFSET)
         print 'main: ACTIVE ITEM LABEL: %s'%self.activeLabel()
         print 'main: ACTIVE ITEM TYPE: %s'%(self.typeOfActiveItem())
         print 'main: ACTIVE ITEM RAW CONTENT (self.CURRENTITEM): '
         print self.CURRENTITEM
         print 'END: DEBUG INFORMACION *******************************************************'
      else:
         print 'printDebug: The list is empty'
                 
######################################################################################
##  returns a iterable of items that belongs to current list                        ##
######################################################################################
   def itemsOfCurrentList(self):
      temp=list();
      if not self.EMPTY:
         activeItem = self.CURRENTINDEX-self.MOFFSET
         self.goItemIndex(0)
         for i in range(self.numberOfItems()):
            temp.append(self.activeLabel())
            self.goNext()
         self.goItemIndex(activeItem)

      return iter(temp)
 
 
######################################################################################
##  returns the label of the parent name                                            ##
######################################################################################
   def parentName(self):
         return self.CURRENTLEVEL[self.MLABEL]

######################################################################################
##  returns the label of the grand father                                           ##
######################################################################################
   def grandParentName(self): 
      returnValue = 'no grandfather'
      if self.activeLabel() != self.ROOT and self.parentName() != self.ROOT:
         index1=self.activeIndex()
         self.goUp()
         if self.parentName() != self.ROOT:
            index2 = self.activeIndex()
            self.goUp()
            returnValue = self.activeLabel()
            self.goDown().goItemIndex(index2)
          
         self.goDown().goItemIndex(index1)
         
      return returnValue
            
######################################################################################
##  returns a iterable of subitems                                                  ##
######################################################################################
   def subItems(self):
      temp=list()   
      if not self.EMPTY:
         if self.typeOfActiveItem() == 'SubMenu':
            self.goDown()
            temp=self.itemsOfCurrentList()
            self.goUp()

      return iter(temp)
     
######################################################################################
##  load file names as items to itemName                                            ##
######################################################################################
   def loadFiles(self,itemName,path, *ext):
      for filename in [f for f in sorted(os.listdir(path)) if os.path.isfile(os.path.join(path,f))]:
         if len(ext)>0:
            for e in ext:
               if filename.split('.')[-1] == e:
                  self.addItem(filename, parentName=itemName)
         else:        
            self.addItem(filename, parentName=itemName)

######################################################################################
##  load file names as items to active item                                         ##
######################################################################################
   def loadFiles2Current(self, path, *ext):
      for filename in [f for f  in sorted(os.listdir(path)) if os.path.isfile(os.path.join(path,f))]:
         if len(ext)>0:
            for e in ext:
               if filename.split('.')[-1] == e:
                  self.addItem(filename)
         else:        
            self.addItem(filename)

######################################################################################
##  load dir names as items to itemName                                            ##
######################################################################################
   def loadDirs(self,itemName,path):
      for dirname in [f for f  in sorted(os.listdir(path)) if os.path.isdir(os.path.join(path,f))]:
         self.addItem(dirname, parentName=itemName)

######################################################################################
##  load dir names as items to active item                                          ##
######################################################################################
   def loadDirs2Current(self,path):
      for dirname in [f for f  in sorted(os.listdir(path)) if os.path.isdir(os.path.join(path,f))]:
         self.addItem(dirname)

######################################################################################
##  run the procedure stored in item                                                ##
######################################################################################
   def run(self,itemName):
      if not self.EMPTY:
         self.savePosition()
         if self.find(itemName):
            self.command()()
            self.restorePosition()
            self.emptyFindHistory()


######################################################################################
##  returns true if this level has subitems                                         ##
######################################################################################
   def levelHasSubItems(self):
      returnValue=False
      if not self.EMPTY: 
         itemIndex = self.activeIndex() 
         self.goFirst()
         for item in range(self.numberOfItems()):
            if self.numberOfSubItems() > 0: 
               returnValue=True
               break
         self.goItemIndex(itemIndex)
          
      return returnValue
      
######################################################################################
##  load a dir tree and its files on ROOT                                           ##
######################################################################################
   def loadDirTree(self, itemName=ROOT, parent='', path='./', hiddenFiles=False, ext=[], pos=END, debug=False, command={}, deleteExt=False):
            
      self.dirQty = 0
      self.filesQty = 0
      
      if path[-1] =='/': 
         path = path[0:-1]
         
      dirName=path
      path=os.path.abspath(path)[1:].split('/')
      rootBase=path[-1]
      npath = len(path)
      
      if itemName != self.ROOT and not self.find(itemName, parentName=parent): return
      
      self.savePosition()
      
      
      for root, dirs, files in os.walk(os.path.abspath(dirName)):
         if not hiddenFiles:
            files = [f for f in files if not f[0] == '.']
            dirs[:] = [d for d in dirs if not d[0] == '.']      

         dirs=root[1:].split('/')

            
         if len(dirs) == npath:


            self.addItem(rootBase, parentName=itemName, pathString='/'.join(root.split('/')[0:-1]), filename=rootBase, typeItem=self.DIRECTORY, position=pos)
            if debug: print 'adding directory %s to %s: %s: '%(rootBase, itemName, self.activeFullName())

            for fileName in sorted(files):  
               if len(ext)>0:
                  for e in ext:
                     if fileName.split('.')[-1] == e:
                        if fileName.split('.')[-1] in command:                 
                           self.addItem(fileName.split('.')[0] if deleteExt else fileName, parentName=rootBase, pathString=root, filename=fileName, typeItem=self.FILE, command=command[fileName.split('.')[-1]])
                        else:   
                           self.addItem(fileName.split('.')[0] if deleteExt else fileName, parentName=rootBase, pathString=root, filename=fileName, typeItem=self.FILE)
                        self.filesQty += 1
                        if debug: print 'adding file %s to %s: %s'%(fileName,rootBase, self.activeFullName())
               else:
                  if fileName.split('.')[-1] in command:                 
                     self.addItem(fileName.split('.')[0] if deleteExt else fileName, parentName=rootBase, pathString=root, filename=fileName, typeItem=self.FILE, command=command[fileName.split('.')[-1]])
                  else:   
                     self.addItem(fileName.split('.')[0] if deleteExt else fileName, parentName=rootBase, pathString=root, filename=fileName, typeItem=self.FILE)
                  self.filesQty += 1   
                  if debug: print 'adding file %s to %s: %s'%(fileName,rootBase, self.activeFullName())
         else:
            self.addItem(dirs[-1], parentName= dirs[-2], pathString='/'.join(root.split('/')[0:-1]), filename=dirs[-1], typeItem=self.DIRECTORY)
            if debug: print 'adding directory %s to %s: %s'%(dirs[-1], dirs[-2], self.activeFullName())
            self.dirQty += 1
            self.find(dirs[-1], parentName=dirs[-2])             

            for fileName in sorted(files):
               if len(ext)>0:                  
                  for e in ext:
                     if fileName.split('.')[-1] == e: 
                        if fileName.split('.')[-1] in command:                 
                           self.addItem(fileName.split('.')[0] if deleteExt else fileName, pathString=root, filename=fileName, typeItem=self.FILE, command=command[fileName.split('.')[-1]])
                        else:   
                           self.addItem(fileName.split('.')[0] if deleteExt else fileName, pathString=root, filename=fileName, typeItem=self.FILE)
                        self.filesQty += 1
                        if debug: print 'adding file %s to %s: %s'%(fileName,self.activeLabel(), self.activeFullName())
               else:
                  #print 1
                  if fileName.split('.')[-1] in command:                 
                     self.addItem(fileName.split('.')[0] if deleteExt else fileName, pathString=root, filename=fileName, typeItem=self.FILE, command=command[fileName.split('.')[-1]])
                  else: 
                     self.addItem(fileName.split('.')[0] if deleteExt else fileName, pathString=root, filename=fileName, typeItem=self.FILE)
                  self.filesQty += 1
                  if debug: print 'adding file %s to %s: %s'%(fileName,self.activeLabel(), self.activeFullName())


      self.restorePosition()
      self.goDown()
      self.emptyFindHistory()


######################################################################################
##  assign command depending on level                                               ##
######################################################################################
   def assignCommands(self, itemName, parent='', commands=[]):
      
      position = list(self.BASEPOSITION)
      
      self.savePosition(mem=position)
      if self.find(itemName, parentName=parent, exactMatch = True): 
         self.assignCommandInLevels(self.CURRENTITEM, 0, commands)
         
      self.restorePosition(mem=position)   
       
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
   def assignCommandInLevels(self, array, level, commands):
      if not self.EMPTY:  
#         print array[self.MLABEL]     
         try: 
            array[self.MDATA]['COMMAND']=commands[level]  
         except: 
            pass   
         for entry in array[self.MOFFSET:]:           
            itemType = entry[self.MDATA]['TYPE']
            try: 
               entry[self.MDATA]['COMMAND']=commands[level+1]  
            except: 
               pass   
            if itemType == self.SUBMENU or itemType == self.DIRECTORY:
               self.assignCommandInLevels(entry, level + 1, commands)
         
         

################################################################################################################         
## class for creating a TCP server    - tested on Ubuntu, Raspbian                                            ##         
## Alejandro Dirgan - 2016                                                                                    ##
## version 0.5                                                                                                ##
################################################################################################################         
class socketServer():
   STOPLISTENING = False
#-------------------------------------------------------------------------------------------------------------------
   def __init__(self, host='0.0.0.0', port=6768, bufferSize=50*1024, verbose = False):
#-------------------------------------------------------------------------------------------------------------------
      self.resetError()
      self.verbose =  verbose
      self.STOPLISTENING = False
      self.host=host
      self.port=port
      self.function = None
      self.handlerProc = None
      self.bufferSize=bufferSize
      self.socket = None

      try: 
         self.ADDR = (self.host, self.port)
         self.serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         self.serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
         self.serversock.bind(self.ADDR)
         self.serversock.listen(5)
      except Exception as err:
         self.errorMessage = err
         self.error = True 
            
#-------------------------------------------------------------------------------------------------------------------
   def resetError(self):
#-------------------------------------------------------------------------------------------------------------------
      self.error = False
      self.errorMessage = ''

#-------------------------------------------------------------------------------------------------------------------
   def getError(self):
#-------------------------------------------------------------------------------------------------------------------
      returnValue = { 'gotError' : self.error, 'message':self.errorMessage }
      
      return returnValue
      
#-------------------------------------------------------------------------------------------------------------------
   def setHost(self, host):
#-------------------------------------------------------------------------------------------------------------------
      self.host = host
      return self

#-------------------------------------------------------------------------------------------------------------------
   def setPort(self, port):
#-------------------------------------------------------------------------------------------------------------------
      self.port = port
      return self

#-------------------------------------------------------------------------------------------------------------------
   def setBufSize(self, sizeInBytes):
#-------------------------------------------------------------------------------------------------------------------
      self.bufferSize = sizeInBytes
      return self

#-------------------------------------------------------------------------------------------------------------------
   def start(self, inBackground=False):
#-------------------------------------------------------------------------------------------------------------------
      if not self.error:
         if inBackground: 
            thread.start_new_thread(self.listen,())
         else: 
            self.listen()

#-------------------------------------------------------------------------------------------------------------------
   def closeSocket(self):
#-------------------------------------------------------------------------------------------------------------------
      try:
         self.socket.close()
      except:
         pass      
            
#-------------------------------------------------------------------------------------------------------------------
   def listen(self):
#-------------------------------------------------------------------------------------------------------------------
      if self.error: return

      while not self.STOPLISTENING:
          if self.verbose: print 'waiting for connection... listening on port', self.port
          clientsock, addr = self.serversock.accept()
          if self.verbose: print '...connected from:', addr
          if not self.STOPLISTENING: 
             thread.start_new_thread(self.handler, (clientsock, addr))

#-------------------------------------------------------------------------------------------------------------------
   def handler(self,clientsock,addr):
#-------------------------------------------------------------------------------------------------------------------
      if self.error: return
      self.socket = clientsock
      while True:
         try: 
            data = clientsock.recv(self.bufferSize)
         except Exception as err: 
            self.error = True
            self.errorMessage = err
            break
               
         if not data: break
         if self.verbose: print repr(addr) + ' recv:' + repr(data)
         
         if "stopServer67680512" == data.rstrip(): 
            if self.verbose: print 'closing connection on port %s'%self.port
            self.STOPLISTENING=True
            break 
         # type 'close' on client console to close connection from the server side

         try: 
            if self.handlerProc != None: 
               clientsock.send(self.handlerProc(repr(data.rstrip())))
            else: 
               clientsock.send(data)
         except Exception as err: 
            self.error = True
            self.errorMessage = err
            break
               
         if self.verbose: print repr(addr) + ' sent:' + repr(data)


      try:  
         clientsock.close()
         if self.verbose: print 'closing socket'
      except Exception as err: 
         self.error = True
         self.errorMessage = err
         
      if self.verbose: print addr, '- closed connection on port %s'%self.port

#-------------------------------------------------------------------------------------------------------------------
   def stop(self):
#-------------------------------------------------------------------------------------------------------------------
      if not self.error:
         socketClient(port=self.port, command='stopServer67680512')

#-------------------------------------------------------------------------------------------------------------------
   def setBehavior(self, func):
#-------------------------------------------------------------------------------------------------------------------
      self.handlerProc = func
      return self

################################################################################################################         
## class for maintain a list with no repeated elements                                                        ##         
## Alejandro Dirgan - 2016                                                                                    ##
## version 0.1                                                                                                ##
################################################################################################################         
class uniqueElementsList():

#-------------------------------------------------------------------------------------------------------------------
   def __init__(self, maxElements=100):
#-------------------------------------------------------------------------------------------------------------------
      self.elements = []
      self.maxElements=maxElements
      self.numberOfElements = 0

#-------------------------------------------------------------------------------------------------------------------
   def addElement(self, element):
#-------------------------------------------------------------------------------------------------------------------
      returnValue = False
      if not element in self.elements:
			if self.numberOfElements < self.maxElements:
				self.elements.append(element)
				self.numberOfElements += 1
				returnValue = True
			else:
				returnValue = False

      return returnValue

#-------------------------------------------------------------------------------------------------------------------
   def removeElement(self, element):
#-------------------------------------------------------------------------------------------------------------------
      try:
			self.elements.remove(element)
			self.numberOfElements -= 1
			returnValue = True
      except:
			returnValue = False
		
      return returnValue

#-------------------------------------------------------------------------------------------------------------------
   def elementIn(self, element):
#-------------------------------------------------------------------------------------------------------------------
      if element in self.elements:
			return True
      else:
			return False

#-------------------------------------------------------------------------------------------------------------------
   def reachMaxCapacity(self):
#-------------------------------------------------------------------------------------------------------------------
      return True if self.numberOfElements >= self.maxElements else False 

#-------------------------------------------------------------------------------------------------------------------
   def setMaxCapacity(self, maxElements):
#-------------------------------------------------------------------------------------------------------------------
      self.maxElements = maxElements 

#-------------------------------------------------------------------------------------------------------------------
   def emptyList(self):
#-------------------------------------------------------------------------------------------------------------------
		self.elements = []
		self.numberOfElements = 0

#-------------------------------------------------------------------------------------------------------------------
   def quantity(self):
#-------------------------------------------------------------------------------------------------------------------
		return self.numberOfElements
			
################################################################################################################         
## class for pickink random element and removeit from list                                                    ##         
## Alejandro Dirgan - 2016                                                                                    ##
## version 0.1                                                                                                ##
################################################################################################################         
class pickList():

#-------------------------------------------------------------------------------------------------------------------
   def __init__(self):
#-------------------------------------------------------------------------------------------------------------------
      self.elements = []
      self.numberOfElements = 0
      self.lastDuplicateElement = None
      seed()

#-------------------------------------------------------------------------------------------------------------------
   def addElement(self, element, acceptDuplicate=True, maxElements=100):
#-------------------------------------------------------------------------------------------------------------------
      if acceptDuplicate:
           self.elements.append(element)
           self.numberOfElements += 1
      else:
           if element not in self.elements:
              self.elements.append(element)
              self.numberOfElements += 1
           else:
              self.lastDuplicateElement=element
		
      if self.numberOfElements > maxElements: self.pickOneFromHead()
		
      return self

#-------------------------------------------------------------------------------------------------------------------
   def elementIn(self, element):
#-------------------------------------------------------------------------------------------------------------------
      if element in self.elements:
			return True
      else:
			return False

#-------------------------------------------------------------------------------------------------------------------
   def emptyList(self):
#-------------------------------------------------------------------------------------------------------------------
		self.elements = []
		self.numberOfElements = 0

#-------------------------------------------------------------------------------------------------------------------
   def isEmpty(self):
#-------------------------------------------------------------------------------------------------------------------
		return True if self.numberOfElements == 0 else False

#-------------------------------------------------------------------------------------------------------------------
   def removeElement(self, element):
#-------------------------------------------------------------------------------------------------------------------
      try:
			self.elements.remove(element)
			self.numberOfElements -= 1
			returnValue = True
      except:
			returnValue = False
		
      return returnValue
			
#-------------------------------------------------------------------------------------------------------------------
   def pickOneFromTail(self):
#-------------------------------------------------------------------------------------------------------------------

		try:
			returnValue = self.elements[-1]
			del self.elements[-1]
			self.numberOfElements -= 1
		except:
			returnValue = ''

		return returnValue

#-------------------------------------------------------------------------------------------------------------------
   def pickOneFromHead(self):
#-------------------------------------------------------------------------------------------------------------------

		try:
			returnValue = self.elements[0]
			del self.elements[0]
			self.numberOfElements -= 1
		except:
			returnValue = ''

		return returnValue

#-------------------------------------------------------------------------------------------------------------------
   def pickOneRandomly(self, differentTo=''):
#-------------------------------------------------------------------------------------------------------------------

		try:
			timeout=-1
			returnValue = differentTo
			while returnValue == differentTo and timeout<(self.numberOfElements*5):
				element = randint(0,self.numberOfElements-1)
				returnValue = self.elements[element]
				#print '%s, %s, %s\n'%(self.elements, str(element), returnValue)
				if returnValue != differentTo:
					del self.elements[element]
					self.numberOfElements -= 1
					break
				timeout += 1
		except:
			returnValue = ''

		return returnValue

#-------------------------------------------------------------------------------------------------------------------
   def quantity(self):
#-------------------------------------------------------------------------------------------------------------------
		return self.numberOfElements

#################################################
class lastfm():
#################################################
   lastfmKEY='86895df0277228aa9c78cc53d578bfda'
#------------------------------------------------   
   def __init__(self):
#------------------------------------------------   
      self.key=self.lastfmKEY   
      self.similarArtists = []
#------------------------------------------------   
   def getSimilar(self, artist):
#------------------------------------------------   
      if artist != '':
         artist=artist.replace(' ','%20').replace('&','%26')
         url='http://ws.audioscrobbler.com/2.0/?method=artist.getsimilar&artist=%s&api_key=%s&format=json'%(artist, self.key)
         response = urllib.urlopen(url)
         data = json.loads(response.read())
         
         self.similarArtists = []  
         self.artistInfo = {}
         self.albumInfo = {}
         self.artistTopAlbums = []
         self.artistTopTracks = []
         
         try:       
            for artist in data["similarartists"]["artist"]: 
		   	   self.similarArtists.append({'name':artist['name'].encode('utf-8'),'url':artist['url'].encode('utf-8'),'images':artist['image']})
         except:
			 pass
			 
      return self.similarArtists
#------------------------------------------------   
   def getArtistInfo(self, artist):
#------------------------------------------------   
      if artist != '':
         artist=artist.replace(' ','%20').replace('&','%26')
         url='http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&artist=%s&api_key=%s&format=json'%(artist, self.key)
         response = urllib.urlopen(url)
         data = json.loads(response.read())
         
         self.artistInfo = {}  
         
         try:       
            self.artistInfo["bio-content"]=data["artist"]["bio"]["content"]
            self.artistInfo["bio-summary"]=data["artist"]["bio"]["summary"]
            self.artistInfo["bio-links"]=data["artist"]["bio"]["links"]
            self.artistInfo["bio-published"]=data["artist"]["bio"]["published"]
            self.artistInfo["artist-name"]=data["artist"]["name"]
            self.artistInfo["artist-url"]=data["artist"]["url"]
            images={} 
            for artist in data["artist"]["image"]: 
               if len(artist["size"]) != 0:
                  images[artist["size"]]=artist["#text"]
            self.artistInfo["artist-images_d"]=images
            self.artistInfo["artist-mbid"]=data["artist"]["mbid"]

            self.artistInfo["artist-similar_a"]=[]
            for k in data["artist"]["similar"]["artist"]:
               self.artistInfo["artist-similar_a"].append(k["name"])

		   	#   #self.similarArtists.append({'name':artist['name'].encode('utf-8'),'url':artist['url'].encode('utf-8'),'images':artist['image']})
         except:
		    pass
		 			 
      return self.artistInfo
       
#------------------------------------------------   
   def getArtistTopAlbums(self, artist):
#------------------------------------------------   
      if artist != '':
         artist=artist.replace(' ','%20').replace('&','%26')
         url='http://ws.audioscrobbler.com/2.0/?method=artist.gettopalbums&artist=%s&api_key=%s&format=json'%(artist, self.key)
         response = urllib.urlopen(url)
         data = json.loads(response.read())
         
         self.artistTopAlbums = []  
         
         try:       
            for album in data["topalbums"]["album"]:
               self.artistTopAlbums.append(album["name"])
         except:
		    pass
		 			 
		 			 
      return self.artistTopAlbums
       
#------------------------------------------------   
   def getArtistTopTracks(self, artist):
#------------------------------------------------   
      if artist != '':
         artist=artist.replace(' ','%20').replace('&','%26')
         url='http://ws.audioscrobbler.com/2.0/?method=artist.gettoptracks&artist=%s&api_key=%s&format=json'%(artist, self.key)
         response = urllib.urlopen(url)
         data = json.loads(response.read())
         
         self.artistTopTracks = []  
         try:       
            for track in data["toptracks"]["track"]:
               self.artistTopTracks.append(track["name"])
         except:
		    pass
		 			 
		 			 
      return self.artistTopTracks
#------------------------------------------------   
   def getAlbumInfo(self, artist, album):
#------------------------------------------------   
      if artist != '':
         artist=artist.replace(' ','%20').replace('&','%26')
         album=album.replace(' ','%20')
         url='http://ws.audioscrobbler.com/2.0/?method=album.getinfo&artist=%s&album=%s&api_key=%s&format=json'%(artist, album, self.key)
         response = urllib.urlopen(url)
         data = json.loads(response.read())
         
         #print data
         self.albumInfo = {}
         try:       
            #self.albumInfo["album-info"] = data["album"]["wiki"]["content"]
            self.albumInfo["album-published"] = data["album"]["wiki"]["published"]
            self.albumInfo["album-name"] = data["album"]["name"]
            self.albumInfo["album-artist"] = data["album"]["artist"]
            self.albumInfo["album-url"] = data["album"]["url"]
            self.albumInfo["album-mbid"] = data["album"]["mbid"]
            self.albumInfo["album-tags_d"] = data["album"]["tags"]
            self.albumInfo["album-images_a"] = data["album"]["image"]
            self.albumInfo["album-tracks_a"] = []
            for i in data["album"]["tracks"]["track"]:
               self.albumInfo["album-tracks_a"].append(i["name"])
         except:
		    pass
		 			 
		 			 
      return self.albumInfo

#-------------------------------------------------------------------------------------------------------------------
def replaceSpecialChars(string):
#-------------------------------------------------------------------------------------------------------------------
   #chars2replace=u'áéíóúÁÉÍÓÚàèìòùAÈÌÒÙäëïöüÄËÏÖÜñÑ'
   #charsReplaced=u"aeiouAEIOUaeiouAEIOUaeiouaeiounn"
      
   returnValue = string
   
   pos=0
   for c in string:
      if c in chars2replace: 
         print c
         #string = string.replace(c,charsReplaced[pos])
      pos += 1
   #      
   return returnValue   

#################################################
class dirWatchdog():
#################################################

#------------------------------------------------   
	def __init__(self, ignoreFiles="._downloading"):
#------------------------------------------------   
		signal.signal(signal.SIGINT, self.handlerCtrlC)	
		self.errorMessage = "OK: (dirWatchdog)"
		self.dirs2watch = {}
		self.ignoreFiles = ignoreFiles
		
		self.startWatchLoop = False
		self.exitWatchLoop=False
		self.timeforChecking = 5
		self.dirSizeChecking = False
		self.anyChange = False
		self.addedChange = False
		self.removedChange = False
		self.modifiedChange = False
		
		self.timer = timer()
		self.timer.setTimer(timerId='mainLoop',timeoutinseconds=self.timeforChecking)
		self.timer.startTimer('mainLoop')
		
#------------------------------------------------   
	def setTimeForChecking(self, time):
#------------------------------------------------   
		self.timeforChecking = time
        
#------------------------------------------------   
	def getLastMessage(self):
#------------------------------------------------   
		returnValue = self.errorMessage
		self.errorMessage = "OK: (dirWatchdog)"
		return returnValue

#------------------------------------------------   
	def addDir(self, dirName, path):
#------------------------------------------------   
		if not os.path.isdir(path): 
			self.errorMessage = "ERROR: (dirWatchdog) directory: [%s] not found!"%(path)
		else:
			self.errorMessage = "OK: (dirWatchdog) directory: [%s] added to be watched!"%path
			self.dirs2watch[dirName]=[os.path.abspath(path),dict ([(f, None) for f in os.listdir(os.path.abspath(path))]),set(),set(),set()]

#------------------------------------------------   
	def dirHasChanged(self):
#------------------------------------------------   
		returnValue = self.anyChange
		self.anyChange = False
		return returnValue

#------------------------------------------------   
	def dirAdded(self):
#------------------------------------------------   
		returnValue = self.addedChange
		self.addedChange = False
		return returnValue

#------------------------------------------------   
	def dirRemoved(self):
#------------------------------------------------   
		returnValue = self.removedChange
		self.removedChange = False
		return returnValue

#------------------------------------------------   
	def dirModified(self):
#------------------------------------------------   
		returnValue = self.modifiedChange
		self.modifiedChange = False
		return returnValue

#------------------------------------------------   
	def exitWatch(self):
#------------------------------------------------   
		self.exitWatchLoop = True

#------------------------------------------------   
	def startWatch(self):
#------------------------------------------------   
		self.startWatchLoop = True
		YADthread(self.watch).start()
		
#------------------------------------------------   
	def watch(self):
#------------------------------------------------   
		secondTry = False
		while not self.exitWatchLoop:
			if self.timer.trigger('mainLoop'):
				for dirN in self.dirs2watch:
					try:
						currentDir = dict ([(f, os.stat("%s/%s"%(self.dirs2watch[dirN][0],f)).st_mtime) for f in os.listdir (self.dirs2watch[dirN][0])])
					except: pass
					for directory in [newFile for newFile in currentDir if not newFile in self.dirs2watch[dirN][1] and not self.ignoreFiles in newFile]: 
						#print "added"
						self.anyChange = True
						self.addedChange = True
						self.dirs2watch[dirN][2].add(directory)
						self.dirs2watch[dirN][3].discard(directory)

					for directory in [newFile for newFile in self.dirs2watch[dirN][1] if not newFile in currentDir and not self.ignoreFiles in newFile]: 
						#print "removed"
						self.anyChange = True
						self.removedChange = True
						self.dirs2watch[dirN][3].add(directory)
						self.dirs2watch[dirN][2].discard(directory)
					
					if secondTry:
						try:
							for directory in currentDir:
								if currentDir[directory] != self.dirs2watch[dirN][1][directory]:
									#print "modified"
									self.anyChange = True
									self.modifiedChange = True
									self.dirs2watch[dirN][2].discard(directory)
									self.dirs2watch[dirN][3].discard(directory)
									self.dirs2watch[dirN][4].add(directory)
						except:
							pass
					else:
						secondTry = True			
					
					self.dirs2watch[dirN][1] = currentDir
				self.timer.startTimer('mainLoop')
			
			sleep(.1)
		
#------------------------------------------------   
	def popAdded(self, dirName):
#------------------------------------------------   
		returnValue = None
		try:
			returnValue = self.dirs2watch[dirName][2].pop()
		except:
			pass
		
		return returnValue
		
#------------------------------------------------   
	def popRemoved(self, dirName):
#------------------------------------------------   
		returnValue = None
		try:
			returnValue = self.dirs2watch[dirName][3].pop()
		except:
			pass
		
		return returnValue

#------------------------------------------------   
	def popModified(self, dirName):
#------------------------------------------------   
		returnValue = None
		try:
			returnValue = self.dirs2watch[dirName][4].pop()
		except:
			pass
		
		return returnValue

#------------------------------------------------   
	def handlerCtrlC(self, signum, frame):
#------------------------------------------------   
		self.exitWatch()
		exit(0)

      
#-------------------------------------------------------------------------------------------------------------------
if __name__=='__main__':
#-------------------------------------------------------------------------------------------------------------------
	dWatch = dirWatchdog()
	dWatch.addDir("music","/home/ydirgan/disco1TB/Musica")
   
	dWatch.startWatch()
   
	while True:
		if dWatch.dirHasChanged():
			addedElement = dWatch.popAdded("music")
			if addedElement != None: print "purging added element: %s"%addedElement
		
			removedElement = dWatch.popRemoved("music")
			if removedElement != None: print "purging removed element: %s"%removedElement

			modifiedElement = dWatch.popModified("music")
			if modifiedElement != None: print "purging modified element: %s"%modifiedElement
		sleep(.5)
