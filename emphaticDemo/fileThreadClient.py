#! /usr/bin/env python3

# Echo client program
import socket, sys, re
import params
from framedSock import FramedStreamSock
from threading import Thread
import time

switchesVarDefaults = (
    (('-s', '--server'), 'server', "localhost:50001"),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )


progname = "framedClient"
paramMap = params.parseParams(switchesVarDefaults)

server, usage, debug  = paramMap["server"], paramMap["usage"], paramMap["debug"]

if usage:
    params.usage()


try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)
except:
    print("Can't parse server:port from '%s'" % server)
    sys.exit(1)

#if len(sys.argv) is not 2:
#    print("Not enough arguments were given")
#    sys.exit()

#print(sys.argv[1])
#fileName = "test.txt"
##### Type thread
class ClientThread(Thread):
    ##### Constructor
    def __init__(self, serverHost, serverPort, debug):
        Thread.__init__(self, daemon=False)
        self.serverHost, self.serverPort, self.debug = serverHost, serverPort, debug
        self.start()
    def run(self):
        ##### Same connect code as before
        s = None
        for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                print("creating sock: af=%d, type=%d, proto=%d" % (af, socktype, proto))
                s = socket.socket(af, socktype, proto)
            except socket.error as msg:
                print(" error: %s" % msg)
                s = None
                continue
            try:
                print(" attempting to connect to %s" % repr(sa))
                s.connect(sa)
            except socket.error as msg:
                print(" error: %s" % msg)
                s.close()
                s = None
                continue
            break
        
        if s is None:
            print('could not open socket')
            sys.exit(1)
            
        fs = FramedStreamSock(s, debug=debug)

        fileName = ("test.txt").encode()
        ##### Will make sure that the file name doesn't contain new lines or spaces
        while (re.search('\n',fileName.decode()) != None):
            decodedName = fileName.decode()
            if decodedName == '':
                os.write(2,("File does not exist\n").encode)
                sys.exit()
            elif decodedName[0] == ' ':
                fileName = fileName[1:]
            elif decodedName[-1] == ' ' or decodedName[-1] == '\n':
                fileName = fileName[:-1]
                
        if fileName == '':
            os.write(2,("File does not exist\n").encode)
            sys.exit()

            ##### Attempt to open file
        try:
            file = open(fileName.decode(),'r')
        except FileNotFoundError:
            os.write(2, ("File does not exist\n").encode())
            sys.exit()

        ##### Sends the file name first so that server knows what to save as
        fs.sendmsg(fileName)

        #print (os.environ['PATH'])
        ##### Will send file 100 bytes at a time
        file = open(fileName,'r')
        while True:
            fileText = file.read()
            
            ##### breaks loop at end of file
            if not fileText:
                break
                #file.close()
                #sys.exit()
            print(fileText)
            
            #print("sending at most 100 bytes")
            fs.sendmsg(fileText.encode())

        file.close()
        #time.sleep(3)
        print("plox")
        print("received:", fs.receivemsg())
                
       #print("sending hello world")
       #fs.sendmsg(b"hello world")
       #print("received:", fs.receivemsg())

       #fs.sendmsg(b"hello world")
       #print("received:", fs.receivemsg())

##### Make 100 clients to test?
#for i in range(1):
ClientThread(serverHost, serverPort, debug)

