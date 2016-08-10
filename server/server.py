import socket 
import select
import sys
import time
import os

port = 4295
userfile = os.path.dirname(os.path.realpath(__file__))+"/user.txt"


r1 = [3,0,0,6,4,7,2 ,1 ,0 ,1]
r2 = [3,2,1,6,7,0,2 ,10,3 ,1]
e  = [4,5,6,7,8,9,10,11,12,13]

elements = 14

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("", port))
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.listen(1)

clients = []
clientstatus = []

user = []

def log(m):
    print m

def closeConn(sock, mess):
    sock.send("close")
    sock.close()
    clients.remove(sock)
    if mess != "":
        log(mess)

def saveUser():
    file = open(userfile,"w")
    for o in user:
        line = o[0]
        for i in range(1,len(o)):
            line = line + "," + str(o[i])
        file.write(line + "\n")
    file.close()

def closeServer():
    for c in clients:
        c.close()
    time.sleep(2)
    server.close()
    sys.exit(0)

def editPossession(userid, element, dir):
    if element > 3:
        global user
        (user[userid])[element+2-4] = (user[userid])[element+2-4] + dir

def getPossession(userid,element):
    if element > 3:
        return (user[userid])[element+2-4]
    else:
        return 2

try:
    log("+++ Server started (Port: "+str(port)+")")
    for line in open(userfile):
        u = line.strip().split(",")
        if len(u) > 1:
            for i in range(2, len(u)):
                u[i] = int(u[i])
            for i in range((elements-4)-(len(u)-2)):
                u.append(0)
            user.append(u)
    saveUser()
    
    while True: 
        lesen, schreiben, oob = select.select([server] + clients, 
                                              [], [])

        for sock in lesen: 
            if sock is server: 
                client, addr = server.accept() 
                clients.append(client)
                log("+++ Client "+addr[0]+" verbunden")
            else: 
                nachricht = sock.recv(1024) 
                ip = sock.getpeername()[0] 
                if nachricht:
                    
                    parts = nachricht.split(" ", )
                  
                    if len(parts) < 3: #zu wenig argumente
                        closeConn(sock, "+++ Fehler bei Vebindung zu " + ip)
                    elif parts[0] == "r" and len(parts) == 3: # register
                        found = False
                        for o in user:
                            if o[0] == parts[1]:
                                found = True
                        if found:
                            sock.send("used")
                        else:
                            sock.send("ok")
                            u = [parts[1],parts[2]]
                            for i in range(elements-4):
                                u.append(0)
                            user.append(u)
                            saveUser()
                    elif parts[0] == "l":
                        login = -1
                        for i in range(len(user)):
                            u = user[i]
                            if u[0] == parts[1] and u[1] == parts[2]:
                                login = i

                        if login == -1:
                            sock.send("user")
                        else:
                            #print nachricht
                            u = user[login]
                            if len(parts) == 3:
                                sock.send("Hi")
                            elif u[0] == "root" and parts[3] == "close":
                                log("+++ Server closed by root")
                                sock.send("server closed")
                                closeServer()
                            elif parts[3] == "showPossession":
                                ergebnis = str(u[2])
                                for i in range(3, len(u)):
                                    ergebnis = ergebnis + "," + str(u[i])
                                sock.send(ergebnis)
                            elif parts[3] == "check" and len(parts) == 5:
                                n = int(parts[4])
                                if int(getPossession(login,n)) > 0:
                                    sock.send("ok")
                                else:
                                    sock.send("false")
                            elif parts[3] == "doublecheck" and len(parts) == 5:
                                n = int(parts[4])
                                if int(getPossession(login,n)) > 1:
                                    sock.send("ok")
                                else:
                                    sock.send("false")
                            elif parts[3] == "mix" and len(parts) == 6:
                                n1 = int(parts[4])
                                n2 = int(parts[5])
                                i = -1
                                for c in range(len(r1)):
                                    if (r1[c] == n1 and r2[c] == n2) or (r1[c] == n2 and r2[c] == n1):
                                        i = c
                                if i != -1:
                                    sock.send(str(e[i]))
                                    editPossession(login, n1, -1)
                                    editPossession(login, n2, -1)
                                    editPossession(login, e[i], 1)
                                    saveUser()
                                else:
                                    sock.send("false")
                            else:
                                sock.send("unknown")
                    else:
                        closeConn(sock, "+++ Fehler bei Vebindung zu " + ip)
                else:
                    closeConn(sock, "+++ Verbindung zu "+ip+" beendet")
finally: 
    closeServer()
