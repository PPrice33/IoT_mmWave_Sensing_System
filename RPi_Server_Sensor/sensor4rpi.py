import sys
from gui_parser import uartParser

import random
import numpy as np
import time
import math
import struct
import os
import csv
configFileNaam = "ISK6mdefault.cfg"
stopCfgFileNaam = "sensor_stop.cfg"
startCfgFileNaam = "sensor_start.cfg"
CompileGui = 0

class Sensor():
    def __init__(self): # PAUL DELETED THIS ,s_height,az_tilt,elev_tilt, persistentFramesInput

        if (1): #set to 1 to save terminal output to logFile, set 0 to show terminal output
            ts = time.localtime()
            terminalFileName = str('logData/logfile_'+ str(ts[2]) + str(ts[1]) + str(ts[0]) + '_' + str(ts[3]) + str(ts[4]) +'.txt')
            #sys.stdout = open(terminalFileName, 'w')

            print('Python is ', struct.calcsize('P')*8, ' bit')
            print('Python version: ', sys.version_info)
            self.frameTime = 50
            self.graphFin = 1
            self.hGraphFin = 1
            self.threeD = 1
            self.lastFramePoints = np.zeros((5,1))
            self.plotTargets = 1
            self.frameNum = 0
            self.lastTID = []
            self.profile = {'startFreq': 60.25, 'numLoops': 64, 'numTx': 3, 'sensorHeight': 1.5, 'maxRange': 10, 'az_tilt': 0, 'elev_tilt': 5}
            self.lastFrameHadTargets = False
            self.sensorHeight = 1.5
            self.numFrameAvg = 20
            self.configSent = 0
            self.previousFirstZ = 1
            self.yzFlip = 0
            self.configFileName = configFileNaam
            self.stopcfgFileName = stopCfgFileNaam
            self.startcfgFileName = startCfgFileNaam
            #self.fallDetData()
            self.configType = '3D People Counting'
            self.uart = '/dev/ttyUSB0'
            self.data = '/dev/ttyUSB1'
            self.data_recorded = []

    def updateSensorPosition(self):
        try:
            float(self.s_height)
            float(self.az_tilt)
            float(self.elev_tilt)
        except:
            print('fail to update')
            return
        command = 'sensorPosition ' + self.s_height + ' ' + self.az_tilt + ' ' + self.elev_tilt + ' \n'
        self.cThread = sendCommandThread(self.parser,command)
        self.cThread.start(priority=QThread.HighestPriority2)
        self.gz.translate(dx=0,dy=0,dz=self.profile['sensorHeight'])
        self.profile['sensorHeight'] = float(self.s_height)
        self.gz.translate(dx=0,dy=0,dz=self.profile[ 'sensorHeight'])

    def connectCom(self):
        #get parser
        self.parser = uartParser(type=self.configType)
        self.parser.frameTime = self.frameTime
        print('Parser type: ',self.configType)
        #init threads and timers
        # self.uart_thread = parseUartThread(self.parser)
        # if (self.configType != 'Replay'):
        #     self.uart_thread.fin.connect(self.parseData)
        # self.uart_thread.fin.connect(self.updateGraph)
        # self.parseTimer = QTimer()
        # self.parseTimer.setSingleShot(False)
        # self.parseTimer.timeout.connect(self.parseData)
        try:
            #uart = 'COM'+ self.uartCom.text() #deb_gp
            #data = 'COM'+ self.dataCom.text() #deb_gp
            #TODO: find the serial ports automatically.
            self.parser.connectComPorts(self.uart, self.data)
            print('Connected from main') #deb_gp
            #print('Disconnect') #deb_gp
            #TODO: create the disconnect button action
        except Exception as e:
            print (e)
            print('Unable to Connect')
        if (self.configType == 'Replay'):
            self.connectStatus = ('Replay')
        if (self.configType == 'Long Range People Detection'):
            self.frameTime = 400
#
# Select and parse the configuration file
# TODO select the cfgfile automatically based on the profile.

    def sendCfg(self):
        try:
            if (self.configType!= 'Replay'):
                self.parser.sendCfg(self.cfg)
                self.configSent = 1
            #self.parseTimer.start(self.frameTime)
        except Exception as e:
            print(e)
            print ('No cfg file selected!')

    def sendStopCfg(self):
        self.parser.sendCfg(open(self.stopcfgFileName).readlines())

    def sendStartCfg(self):
        self.parser.sendCfg(open(self.startcfgFileName).readlines())
    
    def parseCfg(self):
        cfg_file = open(self.configFileName)
        self.cfg = cfg_file.readlines()
        counter = 0
        chirpCount = 0
        for line in self.cfg:
            args = line.split()
            if (len(args) > 0):
                if (args[0] == 'cfarCfg'):
                    zy = 4
                    #self.cfarConfig = {args[10], args[11], '1'}
                elif (args[0] == 'AllocationParam'):
                    zy=3
                    #self.allocConfig = tuple(args[1:6])
                elif (args[0] == 'GatingParam'):
                    zy=2
                    #self.gatingConfig = tuple(args[1:4])
                elif (args[0] == 'SceneryParam' or args[0] == 'boundaryBox'):
                    self.boundaryLine = counter
                    self.profile['leftX'] = float(args[1])
                    self.profile['rightX'] = float(args[2])
                    self.profile['nearY'] = float(args[3])
                    self.profile['farY'] = float(args[4])
                    if (self.configType== '3D People Counting'):
                        self.profile['bottomZ'] = float(args[5])
                        self.profile['topZ'] = float(args[6])
                    else:
                        self.profile['bottomZ'] = float(3)
                        self.profile['topZ'] = float(3)
                    #self.setBoundaryTextVals(self.profile)
                    #self.boundaryBoxes[0]['checkEnable'].setChecked(True)
                elif (args[0] == 'staticBoundaryBox'):
                    self.staticLine = counter
                elif (args[0] == 'profileCfg'):
                    self.profile['startFreq'] = float(args[2])
                    self.profile['idle'] = float(args[3])
                    self.profile['adcStart'] = float(args[4])
                    self.profile['rampEnd'] = float(args[5])
                    self.profile['slope'] = float(args[8])
                    self.profile['samples'] = float(args[10])
                    self.profile['sampleRate'] = float(args[11])
                    print(self.profile)
                elif (args[0] == 'frameCfg'):
                    self.profile['numLoops'] = float(args[3])
                    self.profile['numTx'] = float(args[2])+1
                elif (args[0] == 'chirpCfg'):
                    chirpCount += 1
                elif (args[0] == 'sensorPosition'):
                    self.profile['sensorHeight'] = float(args[1])
                    self.profile['az_tilt'] = float(args[2])
                    self.profile['elev_tilt'] = float(args[3])
            counter += 1
        self.profile['maxRange'] = self.profile['sampleRate']*1e3*0.9*3e8/(2*self.profile['slope']*1e12)
        #update boundary box
        #self.drawBoundaryGrid(self.profile['maxRange']) #2D legacy version
        #self.gz.translate(0, 0, 3 self.profile['sensorHeight']) #reposition the ground level to be at sensor height
        #self.changeBoundaryBox() #redraw bbox from cfg file values
        #update chirp table values
        bw = self.profile['samples']/(self.profile['sampleRate']*1e3)*self.profile['slope']*1e12
        rangeRes = 3e8/(2*bw)
        Tc = (self.profile['idle']*1e6 + self.profile[ 'rampEnd']*1e6)*chirpCount
        lda = 3e8/(self.profile['startFreq']*1e9)
        maxVelocity = lda/(4*Tc)
        velocityRes = lda/(2*Tc*self.profile['numLoops']*self.profile['numTx'])
        #self.configTable.setItem(1,1,QTableWidgetItem(str(self.profile['maxRange'])[:5]))
        #self.configTable.setItem(2,1,QTableWidgetItem(str(rangeRes)[:5]))
        #self.configTable.setItem(3,1,QTableWidgetItem(str(maxVelocity)[:5]))
        #self.configTable.setItem(4,1,QTableWidgetItem(str(velocityRes)[:5]))
        #update sensor position
        #print(str(self.profile['az_tilt']))
        #print(str(self.profile['elev_tilt']))
        #print(str(self.profile['sensorHeight']))

    def readData(self):
        #data_rec = self.parser.tlvHeader(data)
        self.parser.parserType = "DoubleCOMPort"
        data = self.parser.readAndParseUartDoubleCOMPort()
        return data
        ## PAUL THE DATA (TID POSITION) IS BEING PRINTED FROM WITHIN parseTLV.py

