# -*- coding: iso-8859-1 -*-
#This a stupid coment. All right?
import wx,socket,ping,wmi,ImageRenderer,os
import wx.grid
import CreateReport
import os
import win32print,win32api
from threading import Thread



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
        self.grid.SetColLabelValue(0,"Endere�o IP")
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
        self.Bind(wx.EVT_TOOL,self.create_report_map_net,id=ID_PDF)

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

            label_2 = wx.StaticText(self.map_dial,-1,"Defina um intervalo:",pos=(10,30))
            label_start = wx.StaticText(self.map_dial,-1,"In�cio:",pos=(20,55))
            self.textctrl_start = wx.TextCtrl(self.map_dial,-1,pos=(55,50))
            label_stop = wx.StaticText(self.map_dial,-1,"Fim:",pos=(20,85))
            self.textctrl_stop = wx.TextCtrl(self.map_dial,-1,pos=(55,80))

            btn_all_net = wx.Button(self.map_dial,ID_MAP_GET_ALL_IP,"Toda Rede",(55,105),(60,30))
            btn_ok_map = wx.Button(self.map_dial,wx.ID_OK,"OK",(35,150),(60,30))
            btn_cancel_map = wx.Button(self.map_dial,wx.ID_CANCEL,"Cancelar",(105,150),(60,30))

            self.map_dial.Bind(wx.EVT_BUTTON,self.get_all_net,id=ID_MAP_GET_ALL_IP)
            self.map_dial.Bind(wx.EVT_BUTTON,self.scan_network,btn_ok_map)

            self.map_dial.ShowModal()

        else :
            self.dial_error = wx.MessageDialog(None,"N�o foi encontrado nem um tipo \nde placa de rede ativa!",'Erro',wx.OK|wx.ICON_ERROR)
            self.dial_error.ShowModal()

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
                ip_start.append(str(ip_interface[count]))
                ip_stop.append(str(ip_interface[count]))
            elif int(mask) == 0 and count >= 3:
                ip_start.append(str(1))
                ip_stop.append(str(254))
            elif int(mask) == 0 and count <= 3:
                ip_start.append(str(0))
                ip_stop.append(str(255))
            count += 1

        start = ".".join(ip_start)
        stop = ".".join(ip_stop)
        self.textctrl_start.SetValue(start)
        self.textctrl_stop.SetValue(stop)

    def scan_network(self,event):

        self.time_of_last_scan = self.get_time()
        self.map_dial.Destroy()


        self.clear_grid(self.grid)

        self.current_card_net = self.combo_interface.GetCurrentSelection()

        self.ip_card_net = self.ip_mask_of_card_net(self.current_card_net)[0]
        self.mask_interface = self.ip_mask_of_card_net(self.current_card_net)[1]
        self.ip_net = self.get_ip_net(self.current_card_net)

        check_net = ping.Ping()

        start_range = self.textctrl_start.Value
        stop_range = self.textctrl_stop.Value
        start_range = start_range.split(".")
        stop_range = stop_range.split(".")
        if int(stop_range[3]) >= int(start_range[3]):

            max_progress = int(stop_range[3])-int(start_range[3])

            progress_dial = wx.ProgressDialog("Verificando a rede",
                                              "Esta opera��o pode demorar um pouco!",
                                              maximum=max_progress,
                                              parent=self,
                                              style = (wx.PD_APP_MODAL | wx.PD_CAN_ABORT
                                                       |wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME |wx.PD_AUTO_HIDE)
                                            )


            row = 0
            keep_going = True
            for host_ip in self.range_ip(start_range,stop_range,self.mask_interface):
                if keep_going:
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
                    if max_progress !=0:
                        keep_going,skip = progress_dial.Update(row)


                    row += 1
                else:
                    break

            progress_dial.Destroy()
        else:
            dial_error = wx.MessageDialog(None,"O endere�o de in�cio deve ser menor do que o de fim!",'Erro',wx.OK|wx.ICON_ERROR)
            dial_error.ShowModal()

    def range_ip(self,start_range,stop_range,mask_interface):

        if int(mask_interface[0]) == 255 and int(mask_interface[1]) == 255 and int(mask_interface[2]) == 255 and int(mask_interface[3]) != 255:
            while int(start_range[3]) <= int(stop_range[3]):
                ip_ping = tuple()
                ip_ping=(str(start_range[0]),".",str(start_range[1]),".",
                        str(start_range[2]),".",str(start_range[3]))
                yield ip_ping
                start_range[3]=int(start_range[3])+1


    def on_printer(self,event):
        import printout,time

        from wx.html import HtmlEasyPrinting
        data_hosts = self.get_data_host()
        self.pdata = wx.PrintDialogData()
        #self.pdata.SetPaperId(wx.PAPER_LETTER)
        ##self.pdata.SetOrientation(wx.PORTRAIT)
        #self.margins = (wx.Point(15,15), wx.Point(15,15))

        if data_hosts == []:
            dial_report_error = wx.MessageDialog(None,"O relat�rio s� pode ser gerado\n ap�s um mapeamento da rede",'Erro',wx.OK|wx.ICON_ERROR)
            dial_report_error.ShowModal()
        else:
            report = CreateReport.Report(data_hosts,self.ip_net,self.mask_interface)
            path_file = os.path.abspath("tmp/report_tmp.pdf")
            report.create_pdf(path_file)

            dial_print = wx.PrintDialog(self,self.pdata)
            if dial_print.ShowModal() == wx.ID_OK:

                pdata = dial_print.PrintData
                printer_name = pdata.GetPrinterName()
                printers = self.get_name_printers()

                for printer in printers:
                    if printer.upper().rfind(printer_name.upper()) != -1:
                        default_printer = win32print.GetDefaultPrinter()
                        print default_printer
                        win32print.SetDefaultPrinter(printer_name)
                        print win32print.GetDefaultPrinter()
                        oi = win32api.ShellExecute (0, "print", path_file, None, ".", 0)
                        time.sleep(2)
                        win32print.SetDefaultPrinter(default_printer)
                        print win32print.GetDefaultPrinter()

                        return 1

            else:
                print "odsfsof"

    def get_ip_net(self,select_card):
        ip_mask = self.ip_mask_of_card_net(select_card)
        ip_interface = ip_mask[0]
        mask_interface = ip_mask[1]
        ip_net = list()
        count = 0
        for mask in mask_interface:
            if int(mask) == 255:
                ip_net.append(str(ip_interface[count]))
            elif int(mask) == 0:
                ip_net.append(str(0))
            count += 1
        return ip_net

    def clear_grid(self,grid):
        number_rows = grid.GetNumberRows()
        if number_rows !=0:
            grid.DeleteRows(0,number_rows,1)
        else:
            pass

    def get_time(self):
        import time
        if time.localtime()[4] < 10:
            hours = "%s:0%s" %(time.localtime()[3],time.localtime()[4])
        else:
            hours = "%s:%s" %(time.localtime()[3],time.localtime()[4])

        return hours

    def get_data_host(self):
        rows = self.grid.GetNumberRows()
        hosts = list()
        if rows !=0:
            for row in range(rows):
                ip = self.grid.GetCellValue(row,0)
                name = self.grid.GetCellValue(row,1)
                status = self.grid.GetCellValue(row,2)
                hosts.append((ip,name,status))
        elif rows == 1:
            pass

        return hosts

    def create_report_map_net(self,event):
        data_hosts = self.get_data_host()
        if data_hosts == []:
            dial_report_error = wx.MessageDialog(None,"O relat�rio s� pode ser gerado\n ap�s um mapeamento da rede",'Erro',wx.OK|wx.ICON_ERROR)
            dial_report_error.ShowModal()
        else:
            wildcard = "PDF Files (*.pdf)|.pdf"
            dlg_create_pdf = wx.FileDialog(self,message="Salvar como",defaultDir=" ",wildcard=wildcard,style=wx.SAVE)
            if dlg_create_pdf.ShowModal() == wx.ID_OK:
                path_file = dlg_create_pdf.GetPath()
                report = CreateReport.Report(data_hosts,self.ip_net,self.mask_interface,path_file)
                thread_create_pdf = Thread(target=report.create_pdf,args=(path_file,))
                thread_create_pdf.start()
                thread_create_pdf.join()
                return 1
        return 0

    def get_name_printers(self):
        printers_local = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL,None,1)
        printers_network = win32print.EnumPrinters(win32print.PRINTER_ENUM_CONNECTIONS,None,1)

        printers = list()

        for printer in printers_local:
            printers.append(printer[2])

        for printer in printers_network:
            printers.append(printer[2])

        return printers




app = wx.App()
MapNetwork()
app.MainLoop()
