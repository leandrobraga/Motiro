# -*- coding: latin-1 -*-

import wx

class Printer():
    def __init__(self,parent):
        self.parent = parent
        self.print_data = wx.PrintData()

    def PageSetup(self):
        dial_data = wx.PageSetupDialogData(self.print_data)
        dial_print = wx.PageSetupDialog(self.parent, dial_data)
        if dial_print.ShowModal() == wx.ID_OK:
            newdata = dial_data.GetPrintData()
            self.print_data = wx.PrintData(newdata)
            paperid = dial_data.GetPaperId()
            self.print_data.SetPaperId(paperid)
        dial_print.Destroy()

