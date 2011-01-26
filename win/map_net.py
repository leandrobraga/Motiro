# -*- coding: latin-1 -*-
#This a stupid coment. All right?
import wx,socket,wmi,ping,ImageRenderer,os
import wx.grid
from wx.html import HtmlEasyPrinting

class MapNetwork(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self,None,-1,"Mapa da Rede",style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN )

        vbox = wx.BoxSizer(wx.VERTICAL)
        panel1 = wx.Panel(self,-1)

        ID_MAP = 2001
        ID_CONFIG_MAP = 2002
        ID_PDF = 2003


        toolbar = self.CreateToolBar()
        toolbar.AddLabelTool(ID_MAP,'',wx.Bitmap('../icon/win/map_net.png'),shortHelp='Mapea a rede local')
        toolbar.AddSeparator()
        toolbar.AddLabelTool(wx.ID_PRINT,'',wx.Bitmap('../icon/win/print.png'),shortHelp='Imprimir')
        toolbar.AddLabelTool(ID_PDF,'',wx.Bitmap('../icon/win/pdf.png'),shortHelp='Gerar PDF')
        toolbar.AddSeparator()
        toolbar.AddLabelTool(wx.ID_EXIT, '', wx.Bitmap('../icon/win/exit.png'),shortHelp='Fecha esta janela')
        toolbar.Realize()


        self.grid = wx.grid.Grid(panel1)
        self.grid.CreateGrid(0,3)
        self.grid.SetColLabelValue(0,"Endereco IP")
        self.grid.SetColSize(0,170)
        self.grid.SetColLabelValue(1,"Nome")
        self.grid.SetColSize(1,170)
        self.grid.SetColLabelValue(2,"Status")
        self.grid.SetColSize(2,50)
        self.grid.SetRowLabelSize(0)
        self.grid.ForceRefresh()
        self.grid.EnableEditing(False)


        vbox.Add(self.grid, 5, wx.EXPAND | wx.ALL)

        panel1.SetSizer(vbox)
        self.CreateStatusBar()

        self.Bind(wx.EVT_CLOSE, self.close_window)
        self.Bind(wx.EVT_TOOL,self.close_window,id=wx.ID_EXIT)
        self.Bind(wx.EVT_TOOL,self.map_net,id=ID_MAP)
        self.Bind(wx.EVT_TOOL,self.on_printer,id=wx.ID_PRINT)

        self.Centre()
        self.Show()

    def close_window(self,event):
        self.MakeModal(False)
        self.Destroy()

    def map_net(self,event):
        ID_MAP_ALL_NET = 20011
        ID_MAP_RANGE_NET = 20012
        ID_MAP_GET_ALL_IP = 20013
        ID_MAP_COMBO = 20014

        net_interface = self.get_names_interface_network()
        number_interface = len(net_interface)

        if number_interface >= 1:
            self.map_dial = wx.Dialog(None,-1,"Definir intervalo de IP's",size=(250,220))

            label_1 = wx.StaticText(self.map_dial,-1,"Dispositivo:",pos=(10,10))
            card_net_name = self.get_names_interface_network()

            self.card_net = list()
            for item in card_net_name:
                self.card_net.append(item["interface_names"][0]["name"])

            self.combo_interface = wx.ComboBox(self.map_dial,ID_MAP_COMBO,choices=self.card_net,style=wx.CB_READONLY,pos=(70,5),size=(165,-1))
            self.combo_interface.SetValue(self.card_net[0])

            label_2 = wx.StaticText(self.map_dial,-1,"Defina um intervalo:",pos=(10,25))
            label_start = wx.StaticText(self.map_dial,-1,"Início:",pos=(20,50))
            self.textctrl_start = wx.TextCtrl(self.map_dial,-1,pos=(55,45))
            label_stop = wx.StaticText(self.map_dial,-1,"Fim:",pos=(20,80))
            self.textctrl_stop = wx.TextCtrl(self.map_dial,-1,pos=(55,75))

            btn_all_net = wx.Button(self.map_dial,ID_MAP_GET_ALL_IP,"Toda Rede",(55,100),(60,30))
            btn_ok_map = wx.Button(self.map_dial,wx.ID_OK,"OK",(35,145),(60,30))
            btn_cancel_map = wx.Button(self.map_dial,wx.ID_CANCEL,"Cancelar",(105,145),(60,30))

            self.map_dial.Bind(wx.EVT_BUTTON,self.get_all_net,id=ID_MAP_GET_ALL_IP)
            self.map_dial.Bind(wx.EVT_BUTTON,self.scan_network,btn_ok_map)

        else :
            pass

        self.map_dial.ShowModal()
        self.map_dial.Destroy()

    def get_names_interface_network(self):
        interfaces_names = list()
        w = wmi.WMI()
        for interface in w.Win32_NetworkAdapter():
            if type(interface.NetConnectionID) == unicode and (interface.NetConnectionStatus == 2):
                interfaces_names.append({"interface_names":[
                                    {"name":interface.Name,"net_conection_id":interface.NetConnectionID.encode("latin-1")},
                                    ]
                              })
            else:
                continue

        return interfaces_names

    def ip_mask_of_card_net(self,select_card):
        w = wmi.WMI()
        ip_mask = tuple()

        for interface in w.Win32_NetworkAdapterConfiguration():
            try:
                interface.Caption.index(self.card_net[select_card])
                ip_interface = interface.IPAddress[0].split(".")
                mask_interface = interface.IPSubnet[0].split(".")
                ip_mask = (ip_interface,mask_interface)
                return ip_mask
            except ValueError:
                pass

    def get_all_net(self,event):

        count = 0
        ip_start = list()
        ip_stop = list()
        ip_mask = self.ip_mask_of_card_net(self.combo_interface.GetCurrentSelection())
        ip_interface = ip_mask[0]
        mask_interface = ip_mask[1]
        for mask in mask_interface:
            if int(mask) == 255:
                ip_start.append(int(ip_interface[count]))
                ip_stop.append(int(ip_interface[count]))
            elif int(mask) == 0 and count >= 3:
                ip_start.append(1)
                ip_stop.append(254)
            elif int(mask) == 0 and count <= 3:
                ip_start.append(0)
                ip_stop.append(255)
            count += 1
        start = []
        stop = []
        for x in range(len(ip_start)):
            start.append(str(ip_start[x]))
            start.append(".")
            stop.append(str(ip_stop[x]))
            stop.append(".")

        start.pop()
        stop.pop()
        start = "".join(start)
        stop = "".join(stop)
        self.textctrl_start.SetValue(start)
        self.textctrl_stop.SetValue(stop)

    def scan_network(self,event):

        import time
        self.time_last_scan = "%s:%s" %(time.localtime()[3],time.localtime()[4])
        self.map_dial.Destroy()
        self.current_card_net = self.combo_interface.GetCurrentSelection()
        mask_interface = self.ip_mask_of_card_net(self.current_card_net)[1]
        check_net = ping.Ping()

        start_range = self.textctrl_start.Value
        stop_range = self.textctrl_stop.Value
        start_range = start_range.split(".")
        stop_range = stop_range.split(".")

        row = 0
        for host_ip in self.range_ip(start_range,stop_range,mask_interface):
            host_ip = "".join(host_ip)
            host = check_net.ping(host_ip)
            on_line = wx.Bitmap('../icon/win/on_line.png',wx.BITMAP_TYPE_PNG)
            off_line = wx.Bitmap('../icon/win/off_line.png',wx.BITMAP_TYPE_PNG)
            on_line_renderer = ImageRenderer.ImageRenderer(on_line)
            off_line_renderer =ImageRenderer.ImageRenderer(off_line)

            if host["status"] == 1:
                self.grid.InsertRows(row,1,True)
                self.grid.SetCellValue(row,0,host_ip)
                if host["name"] != "":
                    self.grid.SetCellValue(row,1,host["name"])
                else:
                    self.grid.SetCellValue(row,1,"Host sem nome")
                self.grid.SetCellRenderer(row,2,on_line_renderer)
                self.grid.SetColSize(2,on_line.GetWidth()+10)
                self.grid.SetRowSize(row,on_line.GetHeight()+10)
                self.grid.SetCellValue(row,2,str(host["status"]))

            else:
                self.grid.InsertRows(row,1,True)
                self.grid.SetCellValue(row,0,host_ip)
                self.grid.SetCellValue(row,1," ---- ")
                self.grid.SetCellRenderer(row,2,off_line_renderer)
                self.grid.SetColSize(2,off_line.GetWidth()+10)
                self.grid.SetRowSize(row,off_line.GetHeight()+10)
                self.grid.SetCellValue(row,2,str(host["status"]))

            self.grid.ForceRefresh()
            row += 1

    def range_ip(self,start_range,stop_range,mask_interface):

        if int(mask_interface[0]) == 255 and int(mask_interface[1]) == 255 and int(mask_interface[2]) == 255 and int(mask_interface[3]) != 255:
            while int(start_range[3]) <= int(stop_range[3]):
                ip_ping = tuple()
                ip_ping=(str(start_range[0]),".",str(start_range[1]),".",
                        str(start_range[2]),".",str(start_range[3]))
                yield ip_ping
                start_range[3]=int(start_range[3])+1

    def on_printer(self,event):

       self.create_reports_net()
       self.printer = HtmlEasyPrinting(name='Printing', parentWindow=None)
       self.printer.GetPrintData().SetPaperId(wx.PAPER_A4)
       self.printer.PrintFile('screenshot.htm')
       #depois tem que deletar esse arquivo screnhost e trocar o nome dele tb neh

    def create_reports_net(self):
        from datetime import date
        date_last_scan = date.today()
        ip_and_mask = self.ip_mask_of_card_net(self.current_card_net)
        report =  '''
                <html>\n
                <head>\n
                <style type="text/css" media="all">
                    body {
                    width:600px;
                    font: 80%/1.2 Arial, Helvetica, sans-serif;
                    margin:30px auto;
                    padding:0;
                   color:#666;
                    }

                    table {
                        width:550px;
                        border-collapse: collapse;
                        border: 2px solid #999;
                        margin:0 auto;

                    }

                    caption {
                       text-align: right;
                       margin-bottom: 0.3em;
                       border-bottom: 1px solid #333;
                       padding-right: 0.3em;
                   }

                    head tr th {
                        text-align:center;
                        border-bottom: 2px solid #999;
                        border-left: 2px solid #999;
                   }

                    tr td, tr th {
                        padding: 1px 5px;
                        text-align:left;
                        font-size: 0.9em;
                        border: 1px dotted #333;
                    }

                    tfoot tr td {
                        text-align:center;
                        border-top: 2px solid #999;
                   }

                </style>\n
                </head>\n
                    <body>\n
                        <center><h1>Relatório de Rede</h1></center>\n
                '''
        report = report +  "<center><h3>Este relatório apresenta os status de conexão dos host da rede %s às %s horas do dia %s </h3></center>\n<table>\n"   %(ip_and_mask[0],self.time_last_scan,date_last_scan.strftime("%d/%m/%Y"))
        f = file('screenshot.htm', 'w')
        f.write(report)
        f.close()
        #for row in xrange(self.grid.GetNumberRows()):
        #    ip = self.grid.GetCellValue(row,0)
        #    nome = self.grid.GetCellValue(row,1)
        #    status = self.grid.GetCellValue(row,2)









app = wx.App()
MapNetwork()
app.MainLoop()
