#!/usr/bin/env python

import serial, time, requests, os, json, requests
import glob, sys

BAUDRATE = 115200
BAUDRATE2 = 0
URL = "http://192.168.0.200:8080/data" #"http://192.168.0.200:9742/data"
headers = {"Content-type":"application/json","Accept":"application/json"}
ser = serial.Serial()
ser2 = serial.Serial()
path = os.path.join(os.path.expanduser('~'), 'Documents')
pathPort = path + "/portserial.txt" #"/home/rp8w-r8/Documents/portserial.txt"
pathFile = path + "/message.txt" #"/home/rp8w-r8/Documents/message.txt"
pathBaud = path + "/baudrate.txt" #"/home/rp8w-r8/Documents/baudrate.txt"
pathOtherDevice = path + "/portserial.txt"
alert = False
alertShutDown = False
payload = {}
portArduino = ""
firstConfig  = True
data = ""
ruta = ""
estado = ""

def portConfiguration():
    global portArduino, ser, BAUDRATE, BAUDRATE2, pathBaud, ruta, estado, firstConfig
    try:
        firstConfig = True
        if os.path.isfile(pathFile):
            with open(pathFile, "w") as k: #pone vacio el archivo
                k.write("")
        
        if os.path.isfile(pathBaud):
            with open(pathBaud, "r") as r: #pone los baudios
                BAUDRATE2 = int(r.read())
        
        ctrl = True
        result = []
        ruta = ""
        estado= ""
        ports = glob.glob('/dev/tty[A-Za-z]*')
        for port1 in ports:
            try:
                s = serial.Serial(port1)
                s.close()
                result.append(port1)
            except (OSError, serial.SerialException):
                pass
        
        for port2 in result:
            try:
                if "USB" in port2:
                    count = 0
                    print("puerto: " + port2)
                    ser = serial.Serial(port2, BAUDRATE)
                    ser.bytesize = serial.EIGHTBITS #number of bits per bytes
                    ser.parity = serial.PARITY_NONE #set parity check: no parity
                    ser.stopbits = serial.STOPBITS_ONE #number of stop bits
                    ser.xonxoff = False    #disable software flow control
                    ser.rtscts = False     #disable hardware (RTS/CTS) flow control
                    ser.dsrdtr = False     #disable hardware (DSR/DTR) flow control
                    
                    while ctrl:
                        ser.write("OK".encode())
                        time.sleep(2)
                        if(ser.in_waiting > 0):
                            response = ser.readline().decode("utf-8")
                            print("responde: " + response)
                            if(response == "OK\r\n"):
                                ctrl = False
                                portArduino = port2
                                getAllPorts()
                                getDataUSB(ser,URL,headers,alert,alertShutDown,payload)
                            else:
                                count = count + 1
                                ser.flushInput()
                                ser.flushOutput()
                        else:
                            print("no ha llegado")
                            count = count + 1
                            ser.flushInput()
                            ser.flushOutput()
                            
                        if(count > 6):
                            break
                            
            except Exception as e:
                print("Error" + str(e))
                portConfiguration()
        
        print("no encontraste el puerto")
        time.sleep(1)
        ser.close()
        portConfiguration()

    except Exception as e:
        print("Error en el puerto: " + str(e))
        portConfiguration()
        #with open("/tmp/pruebaPython.txt", "a+") as f:
        #    f.write("Error en el programa: " + str(e) + "\r\n")
                

def getDataUSB(ser,URL,headers,alert,alertShutDown,payload):
    global portArduino, pathFile, pathPort, BAUDRATE, BAUDRATE2, ser2, ruta, estado, firstConfig, data
    try:
        if(ser.isOpen):
            firstConfig = True
            ser.flushInput() #flush input buffer, discarding all its contents
            ser.flushOutput()#flush output buffer, aborting current output
            while True:
                time.sleep(0.5)
                if (ser.in_waiting > 0):
                    response = ser.readline().decode("utf-8")
                    print("llega: " + response)
                    if(response == "OFF\r\n"):
                        payload = {"data": "OFF"}
                        alertShutDown = True
                    elif(response == "PANICO\r\n"):
                        payload = {"data": "PANICO"}
                        alert = True

                    if(alert == True):
                        resp = requests.post(URL, json = payload, headers = headers)
                        if(resp.status_code == 200):
                            ser.flushInput()
                            ser.flushOutput()
                        else:
                            print("paquete no enviado")
                        alert = False
                    if(alertShutDown == True):
                        print("apagando sistema")
                        os.system("systemctl poweroff -i")
                        time.sleep(2)  
                else:
                    try:
                        if(firstConfig == True):

                            if(ser2.isOpen() == False):
                                with open(pathPort, "r") as f2:
                                    prt = f2.readline()
                                    ser2 = serial.Serial(prt, BAUDRATE2)
                                    ser2.bytesize = serial.EIGHTBITS #number of bits per bytes
                                    ser2.parity = serial.PARITY_NONE #set parity check: no parity
                                    ser2.stopbits = serial.STOPBITS_ONE #number of stop bits
                                    ser2.xonxoff = False    #disable software flow control
                                    ser2.rtscts = False     #disable hardware (RTS/CTS) flow control
                                    ser2.dsrdtr = False     #disable hardware (DSR/DTR) flow control
                                    firstConfig = False
                        
                        if(ser2.in_waiting > 0):
                            data = ser2.readline().decode("utf-8")
                            if(data == "FT-STATUS" or data == "FT-STATUS\r\n"):
                                with open(pathFile, "r") as s:
                                    x = s.read()
                                if(len(x) > 0): #verifica que el archivo tenga algo
                                    with open(pathFile, "r") as f:
                                        while True:
                                            dat = f.readline()
                                            if(dat.endswith("\r\n")):
                                                if(len(dat) != 2):
                                                    dat = dat[:-2] #elimina \r\n
                                            elif(dat.endswith("\n")):
                                                if(len(dat) != 2):
                                                    dat = dat[:-1] #elimina \n
                                            elif(dat.endswith("\r")):
                                                if(len(dat) != 2):
                                                    dat = dat[:-1] #elimina \r
                                                
                                            if not dat:
                                                if(len(dat) != 2):
                                                    print("enviando estado: " + estado)
                                                    ser2.write(estado.encode())
                                                    count = len(open(pathFile).readlines())
                                                    if(count >= 20):
                                                        with open(pathFile, "w") as k: #poner vacio el archivo
                                                            k.write("")
                                                    data = ""
                                                    time.sleep(0.5)
                                                    break
                                            else:
                                                if(dat.count(':') == 1):
                                                    index1 = dat.index(':')
                                                    if(dat[0:index1] == "FR-STATUS"):
                                                        if(len(dat[index1 + 1:len(dat)]) == 3):
                                                            if(len(dat) <= 15):
                                                                estado = dat + "\r\n"
                                                    elif(dat[0:index1] == "FR-ROUTE"):
                                                        if(dat[index1 + 1:len(dat)] == "PANIC" or dat[index1 + 1:len(dat)] == "PANIC\r\n" or dat[index1 + 1:len(dat)] == "TEST" or dat[index1 + 1:len(dat)] == "TEST\r\n" ):
                                                            ruta = dat
                                                        elif(dat[index1 + 1:len(dat)].count('>') == 1):
                                                            ruta = dat
                                else:
                                    if(estado != ""):
                                        print("enviando estado: " + estado)
                                        ser2.write(estado.encode())
                                        time.sleep(0.5)
                            elif(data == "FT-ROUTE" or data == "FT-ROUTE\r\n"):
                                with open(pathFile, "r") as s:
                                    x = s.read()
                                if(len(x) > 0):
                                    with open(pathFile, "r") as f:
                                        while True:
                                            dat = f.readline()
                                            if(dat.endswith("\r\n")):
                                                if(len(dat) != 2):
                                                    dat = dat[:-2] #elimina \r\n
                                            elif(dat.endswith("\n")):
                                                if(len(dat) != 2):
                                                    dat = dat[:-1] #elimina \n
                                            elif(dat.endswith("\r")):
                                                if(len(dat) != 2):
                                                    dat = dat[:-1] #elimina \r
                                            
                                            if not dat:
                                                if(len(dat) != 2):
                                                    print("enviando ruta: " + ruta)
                                                    ser2.write(ruta.encode())
                                                    count = len(open(pathFile).readlines())
                                                    if(count >= 20):
                                                        with open(pathFile, "w") as k: #poner vacio el archivo
                                                            k.write("")
                                                    time.sleep(0.5)
                                                    data = ""
                                                    break
                                            else:
                                                if(dat.count(':') == 1):
                                                    index1 = dat.index(':')
                                                    if(dat[0:index1] == "FR-ROUTE"):
                                                        if(dat[index1 + 1:len(dat)] == "PANIC" or dat[index1 + 1:len(dat)] == "PANIC\r\n" or dat[index1 + 1:len(dat)] == "TEST" or dat[index1 + 1:len(dat)] == "TEST\r\n" ):
                                                            ruta = dat
                                                        elif(dat[index1 + 1:len(dat)].count('>') == 1):
                                                            ruta = dat
                                                    elif(dat[0:index1] == "FR-STATUS"):
                                                        if(dat.endswith("\n")):
                                                            if(len(dat) != 2):
                                                                dat = dat[:-1] #elimina \n
                                                                if(len(dat[index1 + 1:len(dat)]) == 3):
                                                                    if(len(dat) <= 15):
                                                                        estado = dat + "\r\n"
                                                        elif(dat.endswith("\r\n")):
                                                            if(len(dat) != 2):
                                                                dat = dat[:-2] #elimina \r\n
                                                                if(len(dat[index1 + 1:len(dat)]) == 3):
                                                                    if(len(dat) <= 15):
                                                                        estado = dat + "\r\n"
                                                        elif(dat.endswith("\r")):
                                                            if(len(dat) != 2):
                                                                dat = dat[:-1] #elimina \r
                                                                if(len(dat[index1 + 1:len(dat)]) == 3):
                                                                    if(len(dat) <= 15):
                                                                        estado = dat + "\r\n"
                                                        else:
                                                            if(len(dat[index1 + 1:len(dat)]) == 5 or len(dat[index1 + 1:len(dat)]) == 3):
                                                                if(len(dat) <= 15):
                                                                    estado = dat
                                else:
                                    if(ruta != ""):
                                        print("enviando ruta: " + ruta)
                                        ser2.write(ruta.encode())
                                        time.sleep(0.5)
                            else:
                                data = ""
                                ser2.flushInput()
                                ser2.flushOutput()
                        else:
                            data = ""
                            ser2.flushInput()
                            ser2.flushOutput()
                    except Exception as e:
                        print("Error: " + str(e))
                        if(ser2.isOpen()):
                            ser2.close()
                        getDataUSB(ser,URL,headers,alert,alertShutDown,payload)

        else:
            print("puerto cerrado")
            if(ser2.isOpen()):
                ser2.close()
            if(ser.isOpen()):
                ser.close()
            portConfiguration()
    except Exception as e:
        print("Error en la comunicacion USB: " + str(e) + "\r\n")
        portConfiguration()

def getAllPorts():
    global portArduino, ruta, estado, pathOtherDevice
    ports = glob.glob('/dev/tty[A-Za-z]*')
    result = [] 
    for port1 in ports:
        try:
            if("USB" in port1):
                #s = serial.Serial(port1)
                #s.close()
                result.append(port1)
        except (OSError, serial.SerialException):
            pass
    
    for portAux in result:
        try:
            if("USB" in portAux):
                if(portAux == portArduino):
                    print("puerto del arduino es: " + portArduino)
                else:
                    print("el otro puerto es: " + portAux)
                    with open(pathOtherDevice, "w") as f:
                        f.write(portAux)
        except Exception as e:
            print("Error en el serial")
            portConfiguration()

if __name__ == '__main__':
    portConfiguration()
