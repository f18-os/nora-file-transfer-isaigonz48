#! /usr/bin/env python3
import sys, os, socket, params, time, re
from threading import Thread
from framedSock import FramedStreamSock

switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)

debug, listenPort = paramMap['debug'], paramMap['listenPort']

if paramMap['usage']:
    params.usage()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listener socket
bindAddr = ("127.0.0.1", listenPort)
lsock.bind(bindAddr)
lsock.listen(5)
print("listening on:", bindAddr)

##### extends thread
class ServerThread(Thread):
    requestCount = 0            # one instance / class!!!!!!
    def __init__(self, sock, debug):
        Thread.__init__(self, daemon=True)
        ##### make streamSock, set to fsock
        self.fsock, self.debug = FramedStreamSock(sock, debug), debug
        self.start()
    def run(self):
        while True:
            #msg = self.fsock.receivemsg()

            totalFile = ""
            fileName = self.fsock.receivemsg()
            print(fileName.decode())
            #while True:
    
            payload = self.fsock.receivemsg()
            if not payload:
                break

                #self.fsock.sendmsg(payload)
                                
            print(payload.decode())
            if debug: print("rec'd: ", payload)
            totalFile += payload.decode()
            print ("one only plox")

            print("here??")
            ##### in case file did not exist on client side
            if not fileName:
                sys.exit()

            ##### checks if file already exists, adds a number to the name if yes
            repeatCounter = 0
            decodedName = fileName.decode()
            
            filesInDir = os.listdir(os.getcwd())
            while True:
                ##### got this if statement from "Harwee" on stackoverflow
                if decodedName in filesInDir:
                    #print ("reapeat")
                    repeatCounter += 1
                    splitName = re.split("\.", decodedName)
                    if (repeatCounter > 1):
                        splitName[0] = splitName[0][:-1]
                    decodedName = (splitName[0] + ("%d." % repeatCounter) + splitName[1]) 
                else:
                    file = open(decodedName, 'w')
                    break


            print("wut")
            
            file.write(totalFile)
        
            file.close()
        
            print("Am i here")
            
            #if not msg:
            #    if self.debug: print(self.fsock, "server thread done")
            #    return
            ##### race condition
            requestNum = ServerThread.requestCount
            time.sleep(0.001)
            ServerThread.requestCount = requestNum + 1
            msg = ("%s! (%d)" % (totalFile.encode(), requestNum)).encode()
            self.fsock.sendmsg(totalFile.encode())
            break

while True:
    ##### Create new object of type thread to handle each new connection
    sock, addr = lsock.accept()
    ServerThread(sock, debug)
