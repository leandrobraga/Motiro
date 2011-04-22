# -*- coding:utf-8 -*-
import socket
conected = "conected"

host = ""
port = 230885

socket_tcp = socket.socket(socket.AF_INET,socket.SOCk_STREAM)

origin = (host,port)

socket_tcp.bind(origin)
socket_tcp.listen(1)

while True:
    con,server = tcp.accept()

    while True:
        msg = con.recv(1024)
        if not msg : break
        if msg == conected:
            socket_tcp.send("OKMAN")
    socket_tcp.close()













