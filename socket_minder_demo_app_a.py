#!/usr/bin/env python
# socket_minder_demo_app.py
"""
Copyright (c) 2014 ContinuumBridge Limited

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
ModuleName = "socket_minder_demo_app" 

import sys
import os.path
import time
import logging
from cbcommslib import CbApp
from cbconfig import *

class App(CbApp):
    def __init__(self, argv):
        logging.basicConfig(filename=CB_LOGFILE,level=CB_LOGGING_LEVEL,format='%(asctime)s %(message)s')
        self.appClass = "control"
        self.state = "stopped"
        self.gotSwitch = False
        self.sensorsID = [] 
        self.switchID = ""
        self.alarm = False
        self.rightButton = False
        self.leftButton = False
        # Super-class init must be called
        CbApp.__init__(self, argv)

    def setState(self, action):
        self.state = action
        msg = {"id": self.id,
               "status": "state",
               "state": self.state}
        self.sendManagerMessage(msg)

    def onAdaptorService(self, message):
        #logging.debug("%s onadaptorService, message: %s", ModuleName, message)
        for p in message["service"]:
            if p["characteristic"] == "buttons":
                self.sensorsID.append(message["id"])
                req = {"id": self.id,
                      "request": "service",
                      "service": [
                                    {"characteristic": "buttons",
                                     "interval": 0
                                    }
                                 ]
                      }
                self.sendMessage(req, message["id"])
                #logging.debug("%s onadaptorservice, req: %s", ModuleName, req)
            elif p["characteristic"] == "binary_sensor":
                self.sensorsID.append(message["id"])
                req = {"id": self.id,
                      "request": "service",
                      "service": [
                                    {"characteristic": "binary_sensor",
                                     "interval": 0
                                    }
                                 ]
                      }
                self.sendMessage(req, message["id"])
            elif p["characteristic"] == "switch":
                self.switchID = message["id"]
                self.gotSwitch = True
                #logging.debug("%s switchID: %s", ModuleName, self.switchID)
        self.setState("running")

    def onAdaptorData(self, message):
        #logging.debug("%s %s message: %s", ModuleName, self.id, str(message))
        if message["id"] in self.sensorsID:
            if self.gotSwitch:
                if message["characteristic"] == "buttons":
                    if message["data"]["rightButton"] == 1:
                        self.rightButton = True
                    if message["data"]["rightButton"] == 0:
                        self.rightButton = False
                    elif message["data"]["leftButton"] == 1:
                        self.leftButton = True
                        logging.debug("%s Left button was pressed", ModuleName)
                elif message["characteristic"] == "binary_sensor":
                    if message["data"] == "on":
                        self.alarm = True
                    elif message["data"] == "off":
                        self.alarm = False
                if self.alarm:
                    command = {"id": self.id,
                               "request": "command",
                               "data": "off"
                              }
                    self.sendMessage(command, self.switchID)
                elif self.rightButton:
                    command = {"id": self.id,
                               "request": "command",
                               "data": "on"
                              }
                    self.sendMessage(command, self.switchID)
                elif self.leftButton:
                    command = {"id": self.id,
                               "request": "command",
                               "data": "off"
                              }
                    self.sendMessage(command, self.switchID)
        elif message["id"] == self.switchID:
            self.switchState = message["body"]

    def onConfigureMessage(self, config):
        #logging.debug("%s onConfigureMessage, config: %s", ModuleName, config)
        self.setState("starting")

if __name__ == '__main__':
    App(sys.argv)
