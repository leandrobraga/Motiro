# -*- coding: iso-8859-1 -*-

import wx,map_net
from time import sleep

class MainWindow(wx.Frame):
    def __init__(self,parent,id,title):
        wx.Frame.__init__(self,parent,id,title)
        panel = wx.Panel(self,1)
        menu_bar = wx.MenuBar()
        panel.SetBackgroundColour("white")

        file = wx.Menu()
        quit = wx.MenuItem(file,wx.ID_EXIT,"Sair\t CTRL+Q","Sair do Sistema")
        refresh = wx.MenuItem(file,wx.ID_REFRESH,"Atualizar\t F5","Atualiza a tela")
        close_all = wx.MenuItem(file,wx.ID_CLOSE_ALL,"Fechar Tudo\t CTRL+SHIFT+W","Fecha todas as janelas")
        close = wx.MenuItem(file,wx.ID_CLOSE,"Fechar\t CTRL+W","Fecha janela atual")
        file.AppendSeparator()
        file.AppendItem(close)
        file.AppendItem(close_all)
        file.AppendSeparator()
        file.AppendItem(refresh)
        file.AppendSeparator()
        file.AppendItem(quit)
        menu_bar.Append(file,"&Arquivo")

        ID_MAP = 2001
        ID_CONFIG_MAP = 2002
        network = wx.Menu()
        map = wx.MenuItem(network,ID_MAP,"Mapear Rede","Mapea os compuatodores ativos na rede")
        config_map = wx.MenuItem(network,ID_CONFIG_MAP,"Configurações da rede","Permite alterar configurações da rede que se deseja obter informações")
        network.AppendItem(map)
        network.AppendItem(config_map)
        menu_bar.Append(network,"&Rede")

        self.CreateStatusBar()

        self.SetMenuBar(menu_bar)

        self.Bind(wx.EVT_MENU, self.close_window, id=quit.GetId())
        self.Bind(wx.EVT_CLOSE, self.close_window)
        self.Bind(wx.EVT_MENU,self.map_network,id=ID_MAP)

        self.Maximize()

        self.Show()

    def close_window(self,event):
        close_dial = wx.MessageDialog(None, 'Tem certeza que deseja sair?', 'Sair',
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

        ret = close_dial.ShowModal()

        if ret == wx.ID_YES:
            self.Destroy()
            exit()
        else:
            event.Veto()

    def map_network(self,event):
        map_dial = map_net.MapNetwork()
        map_dial.MakeModal(True)


