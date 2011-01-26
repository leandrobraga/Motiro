# -*- coding: utf-8 -*-

import wmi
import subprocess

class InfoMotherBoard():

    def __init__(self):
        global system
        system = wmi.WMI()
        self.manufacturer = self.get_manufacturer()
        self.model = self.get_model()
        self.slots = self.get_slots()
        self.info_mother_board = {"Mother_Board":[
                                    {
                                     "Manufacturer":self.manufacturer,
                                     "Model":self.model,
                                     "Solts":self.slots
                                     }
                                   ]

                                 }


    def __repr__(self):
       print "%s - %s" %(self.manufacturer,self.model)

    def get_manufacturer(self):
        for my_sys in system.Win32_BaseBoard():
            return my_sys.Manufacturer

    def get_model(self):
        for my_sys in system.Win32_BaseBoard():
            return my_sys.Product

    def get_slots(self):
        dmidecode_out = subprocess.Popen("dmidecode.exe -t 9",stdout = subprocess.PIPE)
        self.slots = list()
        for line in dmidecode_out.stdout:
            if line.rfind("System Slot Information") != -1:
                slots_temp = list()
                for x in range(0,3):
                    temp = dmidecode_out.stdout.next().strip().split(":")
                    slots_temp.append(temp)
                self.slots.append(slots_temp)
        return self.slots

