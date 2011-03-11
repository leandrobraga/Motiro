# -*- coding: iso-8859-1 -*-
import cStringIO
import ho.pisa
import wx
from threading import Thread

class Report(Thread):
    def __init__(self,data,ip_net,mask_interface,file_name):

        Thread.__init__(self)

        self.data_hosts = data
        self.ip_net = ip_net
        self.mask_interface = mask_interface
        self.file_name = file_name

    def run(self):

        self.create_pdf(self.file_name)

    def create_report_html(self,data_hosts):
        ip_net = ".".join(self.ip_net)
        mask_interface = ".".join(self.mask_interface)
        number_of_host = len(data_hosts)
        host_per_page = 50
        current_page = 1
        total_pages = (number_of_host/host_per_page)+1

        html_report_0 = """
             <html>
                <head>
                    <meta http-equiv="content-type" content="text/html; charset=iso-8859-1">
                    <style>
                        @page {
                        margin: 1cm;

                        @frame head{
                            -pdf-frame-content: headContent;
                            top: 1cm;
                            margin-left: 1cm;
                            margin-right: 1cm;
                        }
                        @frame page_number {
                            -pdf-frame-content: pageNumberContent;
                            top: 1.5cm;
                            display:block;
                            position:absolute;
                            left:650px;
                        }
                        @frame caption {
                            -pdf-frame-content: captionContent;
                            display:block;
                            position:absolute;
                            top:80px;
                            left:495px;

                        }

                        @frame footer {
                            -pdf-frame-content: footerContent;
                            bottom: 1cm;
                            margin-left: 1cm;
                            margin-right: 1cm;
                            height: 1cm;
                        }
                    }
                </style>
            </head>
            <body>"""


        html_report_1 =  "<div id=\"headContent\"><center><h2>Relatório de Status de Conexão</h2></center><h5 id=\"pageNumberContent\">Página <pdf:pagenumber/> de %s</h5>" %(total_pages)

        html_report_2 =  """
                <hr>
                </div>
                <br><br><br><br>
                <div id="captionContent">
        """


        html_report_3 = "Rede %s / %s" %(ip_net,mask_interface)


        html_report_4 = """
            </div>
                <table>
                <thead>
                    <tr>
                        <th>Endereço IP</th>
                        <th>Nome</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>"""

        count = 0
        body_table_report = str()
        total_count =0
        last = str(html_report_0) + str(html_report_1) + str(html_report_2) + str(html_report_3) + str(html_report_4)
        for host in data_hosts:
            if count<=host_per_page:
                body_table_report = str(body_table_report) +"<tr><th>%s</th><th>%s</th><th>%s</th></tr>" %(str(host[0]),str(host[1]),str(host[2]))
                count +=1
                total_count +=1

            else:
                body_table_report = str(body_table_report) + "</tbody></table><div id=\"footerContent\"><hr> Gerado em %s às %s </div><pdf:nextpage>" %(self.get_date(),self.get_time())
                body_table_report = str(body_table_report) + str(html_report_1) + str(html_report_2) + str(html_report_3) + str(html_report_4)
                body_table_report = str(body_table_report) + "<tr><th>%s</th><th>%s</th><th>%s</th></tr>" %(str(host[0]),str(host[1]),str(host[2]))
                count = 0
                total_count +=1


            if total_count == number_of_host:
                body_table_report = str(body_table_report) + "</tbody></table><div id=\"footerContent\"><hr> Gerado em %s às %s </div></body></html>" %(self.get_date(),self.get_time())


        last = str(last) + str(body_table_report)

        return last

    def create_pdf(self,file_name="report_map_net.pdf"):
        html = self.create_report_html(self.data_hosts)
        ho.pisa.showLogging()
        var_file = file(file_name, "wb")
        pdf = ho.pisa.CreatePDF(cStringIO.StringIO(html),var_file)
        var_file.close()
        return not pdf.err

    def get_time(self):
        import time
        if time.localtime()[4] < 10:
            hours = "%s:0%s" %(time.localtime()[3],time.localtime()[4])
        else:
            hours = "%s:%s" %(time.localtime()[3],time.localtime()[4])

        return hours

    def get_date(self):
        import datetime
        today = datetime.date.today()
        return today.strftime('%d/%m/%Y')

