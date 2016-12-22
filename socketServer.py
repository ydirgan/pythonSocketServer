#https://www.python.org/dev/peps/pep-0263/t
# coding: utf-8

import unicodedata
import os, sys
from time import sleep
import traceback
import threading
import platform
from socketServerLib import socketServer, socketClient, gmailBox
from socketServerLib import logFacility, timer, dateTime, internet_on
from socketServerLib import shellCommand, humanize_duration

from inspect import stack


################################################################################################################         
## class for creating a Socket Server - tested on Ubuntu, Raspbian                                            ##         
## Alejandro Dirgan - 2017                                                                                    ##
################################################################################################################         
class tcpServer():

   HOMEPATH = '/tmp'
   PORT = 3533
   TCPSERVER_VERSION = '0.1.1'

#HISTORY OF CHANGES
#  0.1    creation
#  0.1.1  add serverName, check existance of homedir, better error habdle at main, change default port to 3533

#-------------------------------------------------------------------------------------------------------------------
   def __init__(self, host='0.0.0.0', port=None, bufferSize=10*1024, homePath=None, appName='tcpServer', verbose = False, debug=False):
#-------------------------------------------------------------------------------------------------------------------
      self.pid = os.getpid()
      self.arch = platform.machine()
      self.errorMessage = ''
      self.errorCode = 0
      self.error = False
      self.appName = appName
      self.defaultUser = self.appName
      self.home = os.path.abspath(homePath)
      self.initFile = self.home+'/'+self.appName+'.pid'
      self.finishFile = self.home+'/'+self.appName+'.stop'
      self.verbose = verbose
      self.spaceSeparator = '_'
      self.debug=debug
      self.header = False
      self.time2saveContext = 10
      self.module = self.appName
      
      self.lockTcpServer = threading.Lock()
      
      self.timers = timer()
      self.uptime = dateTime()
      self.uptime.startTimer()
      self.host=host

            
      self.avoidCharsArray = ["'","(",")","[","]","{","}","<",">",",",".","?","^","%","$","#","@","!","|",":",";","~"," -",'"']
      
      self.gmail=gmailBox("alejandro.dirgan@gmail.com","Pl@t@n@67680512");
      self.gmail.setVerbose(verbose=False)
      
      self.logFile = self.home + '/%s.log'%self.appName
      self.log = logFacility(module=self.appName, logFile = self.logFile )
      
      for i in shellCommand('ps -ef | grep %s.py | grep -v grep  | grep -v %s | wc -l'%(self.appName, self.appName)).run():
         processCount = int(i)
         
      if processCount > 2: 
         self._logMessage('(init) there is another instance of %s running... exiting'%(self.appName), verbose = True) 
         exit(1)
         
      if port == None:
         self.port = self.PORT
      else:
         if port < 1000 or port > 9000:   
            self.errorMessage = 'port number have to be in range of 1000 - 9000'
            self.errorCode = 1004
            self.error = True
            self._logMessage(self.errorMessage, severity='ERROR', verbose = True) 
            exit(1)
         else:
            self.port = port   
      
      self.version = self.appName + ' ' + self.TCPSERVER_VERSION
   
      if not os.path.isdir(self.home): 
         self.errorMessage = 'home directory %s does not exists'%self.home
         self.errorCode = 1001
         self.error = True
         self._logMessage(self.errorMessage, verbose = True) 
         exit(1)

      if not os.path.isfile(self.initFile): #or forceStart:
         shellCommand('echo %s > %s'%(self.pid,self.initFile)).run()
      else:
         self._logMessage('(init) %s is running or is in a unestable state...\n(init) Stop the process or remove %s file'%(self.appName,self.initFile), verbose = True) 
         exit(1)
      
      self._logMessage('(init) starting %s!'%self.appName, verbose = True) 
      self._logMessage('(init) home directory is %s'%(self.home), verbose = True) 


      if '(OK)' in socketClient(host=self.host,port=self.port,command='about')[0]:
         self._logMessage('(init) there is another instance of %s running... exiting'%(self.appName), verbose = True) 
         exit(1)
         
      self.bufferSize = bufferSize
      self.loopDelay = .7
      self.tcpServerExit = False
      
      self.passwd = 'D1rg@n'
                   
      self.internetIsOn = internet_on()   

      self.defineMessages()

      self._logMessage('(init) listening on port %s'%self.port, verbose = True) 
      self._logMessage('(init) this process is identified by: %s'%self.pid, verbose = True) 

      self.socketServer = socketServer(host=self.host, port=self.port) 
      self.socketServer.setBehavior(self.tcpServer).start(inBackground=True)
            
      self.eventLoop()      

#------------------------------------------------   
   def removeChars(self, string, chars):
#------------------------------------------------   
      returnValue = string
		
      for i in chars: 
         returnValue=returnValue.replace(i,"")
		
      return returnValue   
		
#-------------------------------------------------------------------------------------------------------------------
   def _logMessage(self, message, user = None, verbose = False):
#-------------------------------------------------------------------------------------------------------------------
      if verbose:
         if user != None:
            message += ', executed by %s'%user
            
         self.log.logMessage(message)

#-------------------------------------------------------------------------------------------------------------------
   def defineMessages(self):
#-------------------------------------------------------------------------------------------------------------------
      self.helpMessage = {
      
      'about'                  : 'USAGE: about [help]\n',
      'headeron'               : 'USAGE: headerOn [help]\n',
      'headeroff'              : 'USAGE: headerOff [help]\n',
      'getheader'              : 'USAGE: getHeader [help]\n',
      'debugon'                : 'USAGE: debugOn [help]\n',
      'debugoff'               : 'USAGE: debugOff [help]\n',
      'getdebug'               : 'USAGE: getDebug [help]\n',
      'verboseon'              : 'USAGE: verboseOn [help]\n',
      'verboseoff'             : 'USAGE: verboseOff [help]\n',
      'getverbose'             : 'USAGE: getVerbose [help]\n',
      'restart'                : 'USAGE: restart [help]\n',
      'getpid'                 : 'USAGE: getPid [help]\n',
      'commands'               : 'USAGE: commands [filter=word] [help]\n',
     
      }
      
      
      self.severity  = { 'ok': '(OK)',
                         'info': '(INFO)',
                         'warning': '(WARNING)',
                         'error': '(ERROR)',
                         'panic': '(PANIC)',
                        }
      
#-------------------------------------------------------------------------------------------------------------------
   def getError(self):
#-------------------------------------------------------------------------------------------------------------------
      returnValue = {'error':self.error,
                     'errorCode': self.errorCode,
                     'errorMessage': self.errorMessage
                    }
      
      return returnValue

#-------------------------------------------------------------------------------------------------------------------
   def check4ExitFile(self):
#-------------------------------------------------------------------------------------------------------------------
      if os.path.exists(self.finishFile):
         shellCommand('rm %s'%self.finishFile).run()
         self.stopServer(0,0)

#-------------------------------------------------------------------------------------------------------------------
   def eventLoop(self):
#-------------------------------------------------------------------------------------------------------------------
      self.updateDB = True
      self._logMessage('(eventLoop) entering event loop!', verbose = True) 
            
      self.countSongs = 1

      songPercent = 0         
      
      self.artist = ''
         
      while not self.tcpServerExit:
         self.lockTcpServer.acquire()
         try:         
                                    
            self.check4ExitFile()
           
         except Exception as pythonError: 
            if self.debug: print(traceback.format_exc()) 
         finally:
            self.lockTcpServer.release()
         
         sleep(self.loopDelay)   

      #*** END OF Eventloop

      self._logMessage('(eventLoop) %s is stopped!'%self.appName, verbose = True) 
      
        
#-------------------------------------------------------------------------------------------------------------------
   def stopServer(self, signum, frame):
#-------------------------------------------------------------------------------------------------------------------
      self._logMessage('(stopServer) stopping %s after %s'%(self.appName,humanize_duration(self.uptime.timeLapsed())), verbose = True) 

      self.socketServer.stop()
      
      if os.path.isfile(self.initFile): #or forceStart:
         shellCommand('rm %s'%self.initFile).run()
      else:
         self._logMessage('(init) control file %s was not found'%(self.appName,self.initFile), verbose = True) 
         exit(1)

      self.tcpServerExit = True

#-------------------------------------------------------------------------------------------------------------------
   def normalizeParameters(self, fpars,p1024,ars):
#-------------------------------------------------------------------------------------------------------------------
      for key in pars:
         try: 
            fpars[key] = pars[key].replace('#',' ')
         except Exception as pythonError: 
            if self.debug: print(traceback.format_exc()) 
            fpars[key] = ''

#-------------------------------------------------------------------------------------------------------------------
   def executeCommand(self, command, parameters):
#-------------------------------------------------------------------------------------------------------------------
      #print stack()[1][3]
      command = command.replace("'",'').lower()
      returnValue = ''
      executeCommandError = False
      executeCommandString = ''
      executeCommand = True
      activeVars = {}   
      pythonError = ''

      header=self.header
      try:
         if parameters['headeron']==None: 
            header = True
      except Exception as pythonError:
         pass
         ##if self.debug: print(traceback.format_exc()) 

      try: 
         if parameters['help'] == None: 
            try: 
               returnValue = self.helpMessage[command]
            except Exception as pythonError:
               if self.debug: print(traceback.format_exc()) 
               returnValue = 'help not available for <command> %s\n'%command     
            return returnValue
      except Exception as pythonError: 
         pass
         #if self.debug: print(traceback.format_exc()) 
         
            
      #self._logMessage('(executeCommand) responding to keyword <%s>'%command, user = self.musicMngt.getActiveUser(), verbose = self.verbose) 

      ################################# 
      ################################# Help Commands
      #################################
      ########################################################################################
      if command == 'about': 

         if not executeCommandError and executeCommand:
            returnValue = '%s [%s]\n'%(self.severity['ok'],self.version)

      ########################################################################################
      elif command == '': 

         if not executeCommandError and executeCommand:
            returnValue = '%s\n'%self.severity['ok']
         
      ########################################################################################
      elif command == 'commands': 
         returnValue = ''
         commandName = ''
         commandParameters = []

         try: 
            _filter = parameters['filter']
         except Exception as pythonError: 
            if self.debug: print(traceback.format_exc()) 
            _filter=''
         
         for key in sorted(self.helpMessage): 
            if _filter in key:
               commandName = self.helpMessage[key].split('USAGE: ')[1].split()[0]
               commandParameters = self.helpMessage[key].split('USAGE: ')[1].split()[1:]
               returnValue += '%25s : %s\n'%(commandName,''.join(commandParameters))
   
      ########################################################################################
      elif command == 'verboseoff': 

         if not executeCommandError and executeCommand:
            self.verbose = False
            returnValue = '%s setting verbose [Off]\n'%(self.severity['ok'])

      ########################################################################################
      elif command == 'verboseon': 

         if not executeCommandError and executeCommand:
            self.verbose = True
            returnValue = '%s setting verbose [On]\n'%(self.severity['ok'])

      ########################################################################################
      elif command == 'getverbose': 
         try:
            if self.verbose:
               returnValue = '%s On\n'%(self.severity['ok']) 
            else:
               returnValue = '%s Off\n'%(self.severity['ok']) 
         except Exception as pythonError: 
            if self.debug: print(traceback.format_exc()) 
            executeCommandError = True  
            returnValue = '%s <%s> not executed\n'%(self.severity['error'], command)

      ########################################################################################
      elif command == 'debugon': 

         if not executeCommandError and executeCommand:
            self.debug = True
            returnValue = '%s setting debug [On]\n'%(self.severity['ok'])

      ########################################################################################
      elif command == 'debugoff': 

         if not executeCommandError and executeCommand:
            self.debug = False
            returnValue = '%s setting debug [Off]\n'%(self.severity['ok'])

      ########################################################################################
      elif command == 'getdebug': 
         try:
            if self.debug:
               returnValue = '%s On\n'%(self.severity['ok']) 
            else:
               returnValue = '%s Off\n'%(self.severity['ok']) 
         except Exception as pythonError: 
            if self.debug: print(traceback.format_exc()) 
            executeCommandError = True  
            returnValue = '%s <%s> not executed\n'%(self.severity['error'], command)

      ########################################################################################
      elif command == 'restart': 
         returnValue = '%s not implemented\n'%self.severity['ok']

         #if not executeCommandError and executeCommand:
         #   returnValue = '%s restarting...\n'%(self.severity['info'])
         #   shellCommand('rm %s'%self.initFile).run()
         #   self.saveContext()   
         #   os.execl('/home/ydirgan/python/musicServer','musicServerd', 'restart')

      ########################################################################################
      elif command == 'getpid': 

         if not executeCommandError and executeCommand:
            returnValue = '%s pid [%s]\n'%(self.severity['ok'],self.pid)

      ########################################################################################
      else: 
         executeCommandError = True  
         executeCommandString = '(tcpServer) unknown command <%s>'%command
         returnValue = '%s unknown command\n'%(self.severity['error']) 
      
      if self.verbose and executeCommandError: 
         if executeCommandString == '':
            executeCommandString = '(tcpServer) <%s> command error:\n\n %s'%(command,pythonError)  
         
         self.log.logMessage(executeCommandString, severity='ERROR')
      
      return returnValue

#-------------------------------------------------------------------------------------------------------------------
   def tcpServer(self, command):
#-------------------------------------------------------------------------------------------------------------------
      #print stack()[1][3]
      returnValue = ''
      
      #rules: p1=value,p2=value,..,pn=value
      #rules: no spaces beetwen parameters
      #rules: if strings are needed as value of parameter replace spaces by self.spaceSeparator
      #rules: p1="do this thing" must be specified as p1=do_this_thing
      self.lockTcpServer.acquire()
      try:
         try:
            if self.debug:
               self._logMessage('(tcpServer) processing requirement', verbose = self.verbose) 

            parameters = {}

            if len(command.split(' ')) == 1:
               cmd = command             
            else:   
               cmd = command.replace('\'', '').split(' ')
               prmts=cmd[1]
               cmd = cmd[0].strip()
               for dupla in prmts.replace('\'', '').split(','):
                  p1=''
                  p2=''
                  parameter = dupla.split('=')
                  p1=parameter[0].strip().lower()
                  try:
                     p2=parameter[1]
                  except Exception as pythonError: 
                     p2=None             
                  parameters[p1]=p2   
            
         
            if self.debug:
               self._logMessage('(tcpServer) command %s'%cmd, verbose = self.verbose) 
               self._logMessage('(tcpServer) parameters %s'%parameters, verbose = self.verbose) 

            returnValue = self.executeCommand(cmd,parameters)
   
         except Exception as pythonError: 
            if self.debug: print(traceback.format_exc()) 
            self._logMessage('(tcpServer) command error: %s\n'%pythonError, severity='ERROR', verbose = self.verbose)             
            returnValue = '%s command not executed\n'%(self.severity['error'])

      finally:
         self.lockTcpServer.release()
      
      return returnValue


##########################################################
### BEGIN MAIN          ##################################
##########################################################
##########################################################
#--------------------------------------------------------      
def printBanner():
   print '''
  _            ____                           
 | |_ ___ _ __/ ___|  ___ _ ____   _____ _ __ 
 | __/ __| '_ \___ \ / _ \ '__\ \ / / _ \ '__|
 | || (__| |_) |__) |  __/ |   \ V /  __/ |   
  \__\___| .__/____/ \___|_|    \_/ \___|_|   
         |_|                                  
'''
   
#--------------------------------------------------------      
if __name__ == '__main__':
#--------------------------------------------------------      
   _homeDir = None
   _port = None
   _serverName = None
   _verbose = False
   
   _defaultPort = 3533
   _defaultHome = '/tmp'
   _defaultServerName = 'socketServer'
   
   for arg in sys.argv:
      if 'help' in arg.lower():
         print 'socketServer.py [port=%s] [homedir=%s] [serverName=%s] [verbose=True]'%(_defaultPort, _defaultHome, _defaultServerName)
         exit(1)
         
      if 'verbose' in arg.lower():
         try: 
            if arg.split('=')[1] == 'True':
               _verbose = True
            elif arg.split('=')[1] == 'False':
               _verbose = False
            else:
               _verbose = False
         except Exception as pythonError: 
            pass
      
      if 'homedir' in arg.lower():
         try: 
            if arg.split('=')[1]:
               _homeDir = os.path.abspath(arg.split('=')[1])
               print '(OK) HOME directory was supplied as homeDir=%s'%_homeDir
         except Exception as pythonError: 
            pass
      
      if 'port' in arg.lower():
         try: 
            if arg.split('=')[1]:
               _port = int(arg.split('=')[1])
               print '(OK) PORT was supplied as port=%d'%_port
         except Exception as pythonError: 
            pass
            
      if 'servername' in arg.lower():
         try: 
            if arg.split('=')[1]:
               _serverName = arg.split('=')[1]
               print '(OK) SERVERNAME was supplied as %s'%_serverName
         except Exception as pythonError: 
            pass
            
   print '--------------------------------------------------------------------------'
   printBanner()        
   print '--------------------------------------------------------------------------'

   if _homeDir == None:
      _homeDir = _defaultHome
      
   if _port == None:
      _port=_defaultPort

   if _serverName == None:
      _serverName=_defaultServerName
      
   if not os.path.isdir(_homeDir): 
      print "(ERROR) homeDir=%s does not exists"%_homeDir
      exit(1)   
        
   try:
	
      print 'socketServer.py [port=%s] [homedir=%s] [serverName=%s] [verbose=True]'%(_port,_homeDir, _serverName)
      print 'to stop the server touch %s/%s.stop'%(_homeDir, _serverName)
    
      server = tcpServer(port=_port, homePath=_homeDir, appName=_serverName, verbose=_verbose)

   except Exception as pythonError: 
      print(traceback.format_exc()) 
      


