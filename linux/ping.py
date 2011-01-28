#! /usr/bin/python
#! -*- coding:utf-8 -*-
#TESTE do GIT - testando novamente
import socket,struct,os,binascii
class Ping:
    def __init__(self):
        pass

    def checksum(self,source_string):
        """
        I'm not too confident that this is right but testing seems
        to suggest that it gives the same answers as in_cksum in ping.c
        """
        sum = 0
        countTo = (len(source_string)/2)*2
        count = 0
        while count<countTo:
            thisVal = ord(source_string[count + 1])*256 + ord(source_string[count])
            sum = sum + thisVal
            sum = sum & 0xffffffff # Necessary?
            count = count + 2

        if countTo<len(source_string):
            sum = sum + ord(source_string[len(source_string) - 1])
            sum = sum & 0xffffffff # Necessary?

        sum = (sum >> 16)  +  (sum & 0xffff)
        sum = sum + (sum >> 16)
        answer = ~sum
        answer = answer & 0xffff

        # Swap bytes. Bugger me if I know why.
        answer = answer >> 8 | (answer << 8 & 0xff00)

        return answer

    def send_echo(self,socket_icmp,addres):
        self.type = 8
        self.code = 0
        self.check = 0
        self.id = os.getpid()
        self.seq = 0
        data = "ELLEN"

        packet_icmp = struct.pack("!bbHHhp",self.type,self.code,
                                       self.check,self.id,self.seq,data)

        self.check =  self.checksum(packet_icmp)

        packet_icmp = struct.pack("!bbHHhp",self.type,self.code,
                                       self.check,self.id,self.seq,data)

        bytes_sended = socket_icmp.sendto(packet_icmp,(addres,1))

        if bytes_sended == -1:
            exit(-1)

        return self.id

    def receive_echo(self,socket_icmp,id_packet):
        import time
        while True:
            time.sleep(1)
            try:
                socket_icmp.settimeout(1)
                packet_icmp,addres = socket_icmp.recvfrom(1024)
                icmp_header = packet_icmp[20:28]
                type,code,check,id ,seq = struct.unpack("!bbHHh",icmp_header)

                if id_packet == id:
                    try:
                        host_name = socket.gethostbyaddr(addres[0])
                        host={"name":host_name[0],"status":1}
                    except socket.error:
                        host={"name":"","status":1}
                    return host
                else:
                    host={"name":"","status":0}
                    return host
            except socket.error :
                host={"name":"","status":0}
                return host

    def ping(self,addres):
        socket_icmp = socket.socket(socket.AF_INET, socket.SOCK_RAW,
                                    socket.getprotobyname('icmp'))

        id_packet = self.send_echo(socket_icmp,addres)
        host = self.receive_echo(socket_icmp,id_packet)

        socket_icmp.close()

        return host
