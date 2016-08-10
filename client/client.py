#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys
import os.path
import time
import readline
import socket
import getpass

def clear():
    pass
    os.system("clear")

languages = ["en", "de"]
l = []
start = 35

def load_language_file(name):
    global l
    l = []
    for line in open(name):
        l.append(line.strip())

load_language_file("en")


clear()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 4295))

username = ""
password = ""

menu = 0

def showHelp():
    clear()
    print l[10]
    raw_input()

def showMessage(m):
    clear()
    print m
    time.sleep(0.5)

def yesno(question):
    clear()
    print question + " ("+l[12]+","+l[13]+")"
    print
    antwort = raw_input()
    if antwort == l[12]:
        return True
    else:
        return False

def selectOn(title,list):
    work = True
    while work:
        work = False
        clear()
        print title
        print
        available = []
        for i in range(len(list)):
            if list[i] != "":
                print str(i) + ": " + list[i]
                available.append(i)
        print
        selected = raw_input("").strip()
        if selected.isdigit():
            intselected = int(selected)
            if intselected in available:
                return intselected
            else:
                work = True
        else:
            work = True
    clear()

def closeSocket(m):
    if m != "":
        print m
    s.close()
    clear()
    sys.exit(0)

def login():
    global username
    global password
    username = ""
    password = ""
    work = True
    while work:
        intlogin = selectOn(l[0], [l[1], l[2], l[23]])
        clear()
        if intlogin == 2:
            exitGame()
        else:
            print l[1+intlogin]
            print
            i1 = raw_input(l[3] + ": ").replace(" ","________")
            i2 = getpass.getpass(l[4] + ": ").replace(" ","________")
            clear()
            if intlogin == 0:
                s.send("l "+i1+" "+i2)
                antwort = s.recv(1024)
                if antwort == "Hi":
                    username = i1
                    password = i2
                    showMessage(l[5])
                    work = False
                elif antwort == "user":
                    showMessage(l[6])
                else:
                    closeSocket(l[8])
            elif intlogin == 1:
                s.send("r "+i1+" "+i2)
                antwort = s.recv(1024)
                if antwort == "ok":
                    username = i1
                    password = i2
                    showMessage(l[9])
                    work = False
                elif antwort == "used":
                    showMessage(l[7])
                else:
                    closeSocket(l[8])
            time.sleep(1)
            clear()

def send(command):
    clear()
    print "Loading Data..."
    s.send("l "+username+" "+password+" "+command)
    antwort = s.recv(1024)
    if antwort == "close":
        closeSocket(l[8])
    else:
        return antwort

def exitGame():
    if yesno(l[14]):
        sys.exit(0)

def getName(n):
    if start+n >= len(l):
        return l[33]
    else:
        return l[start+n]

def getPossession(title):
    antwort = send("showPossession")
    possession = title + "\n\n"
    possession = possession + "0: " + getName(0) + ": " + l[11] + "\n"
    possession = possession + "1: " + getName(1) + ": " + l[11] + "\n"
    possession = possession + "2: " + getName(2) + ": " + l[11] + "\n"
    possession = possession + "3: " + getName(3) + ": " + l[11] + "\n"
    parts = antwort.split(",")
    for i in range(len(parts)):
        o = int(parts[i])
        if o != 0:
            possession = possession + str(i+4) + ": " + getName(i+4) + ": " + str(o) + "\n"
    return possession

def getPossessionAsArray():
    antwort = send("showPossession")
    possession = []
    possession.append(getName(0) + ": " + l[11])
    possession.append(getName(1) + ": " + l[11])
    possession.append(getName(2) + ": " + l[11])
    possession.append(getName(3) + ": " + l[11])
    parts = antwort.split(",")
    for i in range(len(parts)):
        o = int(parts[i])
        if o != 0:
            possession.append(getName(i+4) + ": " + str(o))
        else:
            possession.append("")
    return possession

def mix():
    sel = getPossessionAsArray()
    sel.append(l[26])
    first = selectOn(l[28],sel)
    if first < len(sel)-1:
        if send("check "+str(first)) == "false":
            showMessage(l[16])
        else:
            sel = getPossessionAsArray()
            sel.append(l[30])
            second = selectOn(l[29],sel)
            if second < len(sel)-1:
                if (first != second and send("check "+str(second)) == "false") or (first == second and send("doublecheck "+str(second)) == "false"):
                    showMessage(l[16])
                else:
                    antwort = send("mix "+str(first)+" "+str(second))
                    if antwort != "false":
                        showMessage(getName(first)+" + "+getName(second)+" -> "+getName(int(antwort)))
                    else:
                        showMessage(l[17])
            else:
                global menu
                menu = 0
    else:
        global menu
        menu = 0

def changeLanguage():
    new_language = selectOn(l[34],languages)
    load_language_file(languages[new_language])

def openMenu(n):
    clear()
    global menu
    menu = n
    if n == 0:
        antwort = 0
        if username != "root":
            antwort = selectOn(l[18],[l[19],l[20],l[22],l[23]])
        else:
            antwort = selectOn(l[18],[l[19],l[20],l[22],l[23],l[31]])
        if antwort == 0:
            menu = 1
            mix()
        #openMenu(1)
        elif antwort == 1:
            openMenu(2)
        elif antwort == 2:
            if yesno(l[27]):
                login()
        elif antwort == 3:
            exitGame()
        elif antwort == 4:
            if yesno(l[32]):
                send("close")
                closeSocket("")
    elif n == 1:
        #antwort = selectOn(getPossession(l[19]), [l[24],l[26]])
        #if antwort == 0:
        #    mix()
        #elif antwort == 1:
        #    openMenu(0)
        mix()
    elif n == 2:
        antwort = selectOn(l[20], [l[25],l[26]])
        if antwort == 0:
            changeLanguage()
        # elif antwort == 1:
        openMenu(0)

try:
    while True:
        if username == "":
            login()
        openMenu(menu)
finally:
    closeSocket("")
