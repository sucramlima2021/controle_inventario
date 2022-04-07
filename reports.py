from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.styles import getSampleStyleSheet
import sqlite3
import os
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QTableWidget,QTableWidgetItem,QHeaderView,QComboBox,QMessageBox
from unidecode import unidecode


banco = sqlite3.connect('inventario.db')
cursor = banco.cursor()
cursor.execute('SELECT nome FROM empresa')
empresa = cursor.fetchone()

if empresa:
    empresa = str(empresa[0])
banco.close()
yy = 0
ppp = 0
data = []
ordena = ''
colwidth = []
valor = 0
def listar_todos_itens(ordem, val):
    global yy
    global data 
    global ordena
    global ppp
    global colwidth
    global valor
    valor = val
    if valor == 2:
        colwidth = [1*cm, 5*cm, 3*cm, 3*cm, 2*cm, 3*cm, 2.5*cm]
    else:
        colwidth = [1*cm, 6*cm, 4*cm, 3*cm, 2*cm, 3*cm]
    
    

    if ordem != '':
        ordena = 'ORDER BY ' + str(ordem)
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()

    cursor.execute('SELECT c.*, l.nome, p.nome, d.nome FROM componentes AS c INNER JOIN locais AS l ON c.localizacao = l.id LEFT JOIN categorias AS d On c.categoria = d.id LEFT JOIN computadores AS p ON c.computador = p.id '+ str(ordena) +';')
    
    relatorio = cursor.fetchall()

    cursor.execute("SELECT SUM(valor) AS 'total' FROM componentes;")
    valor_total = cursor.fetchone()
    tot = valor_total[0]

    styles = getSampleStyleSheet()
    style = styles["BodyText"]

    canv = Canvas("doc.pdf", pagesize=letter)
    
    
    def quebra():
        
        global yy
        global data 
        global ppp
        global valor
        global colwidth
        gg = Paragraph("<bold><font size=12>Controle de Inventário - Relatórios</font></bold>", style)
        pp = Paragraph("<bold><font size=10>Empresa: "+empresa+"</font></bold>", style)
        header = Paragraph("<bold><font size=18>Listagem - Todos os itens cadastrados</font></bold>", style)
        pag = Paragraph("<bold><font size=8>Pagina: "+ str(ppp) +"</font></bold>", style)    
        t = Table(data, colwidth)
        t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.25, colors.black), ("FONTSIZE", (1, 0), (-1,-1), 7),
                            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]))
        data_len = len(data)

        for each in range(data_len):
            if each % 2 == 0:
                bg_color = colors.whitesmoke
            else:
                bg_color = colors.lightgrey

            t.setStyle(TableStyle([('BACKGROUND', (0, each), (-1, each), bg_color)]))

        aW = 540
        aH = 720

        w, h = header.wrap(aW, aH)
        gg.wrap(540, 750)
        pag.wrap(540, 750)
        pp.wrap(540, 780)
        gg.drawOn(canv, 72, 750)
        pag.drawOn(canv, 480, 750)
        pp.drawOn(canv, 72, 770)
        header.drawOn(canv, 72, aH)
        aH = aH - h
        w, h = t.wrap(aW, aH)
        t.drawOn(canv, 10, aH-h)

        canv.showPage()
        yy = 0
        
        if valor == 2:
            data = [['ID', 'Nome', 'Item Composto', 'Localização', 'Quantidade', 'Serial', 'Valor']]
        else:
            data = [['ID', 'Nome', 'Item Composto', 'Localização', 'Quantidade', 'Serial']]





    if valor == 2:
        data = [['99999', 'Nome', 'Item Composto', 'Localização', 'Quantidade', 'Serial', 'Valor']]
    else:
        data = [['99999', 'Nome', 'Item Composto', 'Localização', 'Quantidade', 'Serial']]
    
    for dados in relatorio:
        comp = ''
        
        if dados[11]:
            comp = str(dados[11])
        if valor == 2:
            data.append([dados[0], str(dados[1])[:40], str(comp)[:15], str(dados[10])[:15], 'N/D', str(dados[8])[:16], str(dados[3]).replace('.', ',')[:11]])
            
        else:    
            data.append([dados[0], str(dados[1])[:40], str(comp)[:20], str(dados[10])[:20], 'N/D', str(dados[8])[:16]])
        yy = yy + 1

        if yy == 35:
            ppp = ppp + 1
            quebra()

    t = Table(data, colwidth)
    t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.25, colors.black), ("FONTSIZE", (0, 0), (-1,-1), 7),
                        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]))
    data_len = len(data)

    for each in range(data_len):
        if each % 2 == 0:
            bg_color = colors.whitesmoke
        else:
            bg_color = colors.lightgrey

        t.setStyle(TableStyle([('BACKGROUND', (0, each), (-1, each), bg_color)]))

    gg = Paragraph("<bold><font size=12>Controle de Inventário - Relatórios</font></bold>", style)
    pp = Paragraph("<bold><font size=10>Empresa: "+empresa+"</font></bold>", style)
    header = Paragraph("<bold><font size=18>Listagem - Todos os itens cadastrados</font></bold>", style)
    ppp = ppp + 1
    pag = Paragraph("<bold><font size=8>Pagina: "+ str(ppp) +"</font></bold>", style)

    total_txt = ""
    if valor == 2:
        
        pega = str(tot).replace('.', ',')
        ve = pega.find(',')
        pos = int(ve) + 3
        valor = pega[:int(pos)]
        total_txt = "Valor Total dos itens: R$"+ str(valor) 
    
    total = Paragraph("<bold><font size=8>" + str(total_txt) + "</font></bold>", style)
    
    aW = 540
    aH = 720

    w, h = header.wrap(aW, aH)
    gg.wrap(540, 750)
    pag.wrap(540, 750)
    pp.wrap(540, 780)
    gg.drawOn(canv, 72, 750)
    pag.drawOn(canv, 480, 750)
    pp.drawOn(canv, 72, 770)
    header.drawOn(canv, 72, aH)
    aH = aH - h
    w, h = t.wrap(aW, aH)
    t.drawOn(canv, 10, aH-h)
    total.wrap(200, 200)
    total.drawOn(canv, 480, 10)
    canv.showPage()
    banco.close()

    try:
        canv.save()
        os.startfile('doc.pdf')
    except:
        
        
        msgBox = QMessageBox()
        msgBox.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
        msgBox.setWindowTitle("Relatório em uso")
        msgBox.setText("Não foi possível emitir este relatório. Feche ou renomeie o arquivo contendo o relatório anterior e depois tente novamente.")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()

def listar_itens_integridade(ordem, val, integridade):
    global yy
    global data 
    global ordena
    global ppp
    global colwidth
    global valor
    valor = val
    if valor == 2:
        colwidth = [2*cm, 6*cm, 3*cm, 3*cm, 4*cm, 2.5*cm]
    else:
        colwidth = [2*cm, 6*cm, 4*cm, 4*cm, 4*cm]
    
    yy = 0
    ppp = 0
    data = []
    ordena = ''
    
    if ordem != '':
        ordena = 'ORDER BY ' + str(ordem)
    
    integr = str(integridade)
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    
    cursor.execute("SELECT c.id, c.nome, c.valor, c.serie, l.nome, p.nome FROM componentes AS c INNER JOIN locais AS l ON c.localizacao = l.id LEFT JOIN computadores AS p ON c.computador = p.id WHERE c.integridade = '" + integr + "' "+ str(ordena) +";")
    
    relatorio = cursor.fetchall()

    cursor.execute("SELECT SUM(valor) AS 'total' FROM componentes WHERE integridade = '" + integr + "';")
    valor_total = cursor.fetchone()
    tot = valor_total[0]

    styles = getSampleStyleSheet()
    style = styles["BodyText"]

    canv = Canvas("doc.pdf", pagesize=letter)
    
    
    def quebra():
         
        global yy
        global data 
        global ppp
        global valor
        global colwidth
        gg = Paragraph("<bold><font size=12>Controle de Inventário - Relatórios</font></bold>", style)
        pp = Paragraph("<bold><font size=10>Empresa: "+empresa+"</font></bold>", style)
        header = Paragraph("<bold><font size=18>Listagem - Itens com a Integridade = "+ integr +"</font></bold>", style)
        pag = Paragraph("<bold><font size=8>Pagina: "+ str(ppp) +"</font></bold>", style)    
        t = Table(data, colwidth)
        t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.25, colors.black), ("FONTSIZE", (1, 0), (-1,-1), 10),
                            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]))
        data_len = len(data)

        for each in range(data_len):
            if each % 2 == 0:
                bg_color = colors.whitesmoke
            else:
                bg_color = colors.lightgrey

            t.setStyle(TableStyle([('BACKGROUND', (0, each), (-1, each), bg_color)]))

        aW = 540
        aH = 720

        w, h = header.wrap(aW, aH)
        gg.wrap(540, 750)
        pag.wrap(540, 750)
        pp.wrap(540, 780)
        gg.drawOn(canv, 72, 750)
        pag.drawOn(canv, 480, 750)
        pp.drawOn(canv, 72, 770)
        header.drawOn(canv, 72, aH)
        aH = aH - h
        w, h = t.wrap(aW, aH)
        t.drawOn(canv, 10, aH-h)

        canv.showPage()
        yy = 0
        
        if valor == 2:
            data = [['ID', 'Nome', 'Item Composto', 'Localização', 'Serial', 'Valor']]
        else:
            data = [['ID', 'Nome', 'Item Composto', 'Localização', 'Serial']]





    if valor == 2:
        data = [['ID', 'Nome', 'Item Composto', 'Localização', 'Serial', 'Valor']]
    else:
        data = [['ID', 'Nome', 'Item Composto', 'Localização', 'Serial']]
    
    for dados in relatorio:
        comp = ''
        
        if dados[5]:
            comp = str(dados[5])
        if valor == 2:
            data.append([dados[0], str(dados[1])[:28], str(comp)[:15], str(dados[4])[:15], str(dados[3])[:16], str(dados[2]).replace('.', ',')[:11]])
            
        else:    
            data.append([dados[0], str(dados[1])[:28], str(comp)[:20], str(dados[4])[:20], str(dados[3])[:16]])
        yy = yy + 1

        if yy == 35:
            ppp = ppp + 1
            quebra()

    t = Table(data, colwidth)
    t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.25, colors.black), ("FONTSIZE", (1, 0), (-1,-1), 10),
                        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]))
    data_len = len(data)

    for each in range(data_len):
        if each % 2 == 0:
            bg_color = colors.whitesmoke
        else:
            bg_color = colors.lightgrey

        t.setStyle(TableStyle([('BACKGROUND', (0, each), (-1, each), bg_color)]))

    gg = Paragraph("<bold><font size=12>Controle de Inventário - Relatórios</font></bold>", style)
    pp = Paragraph("<bold><font size=10>Empresa: "+empresa+"</font></bold>", style)
    header = Paragraph("<bold><font size=18>Listagem - Itens com a Integridade = "+ integr +"</font></bold>", style)
    ppp = ppp + 1
    pag = Paragraph("<bold><font size=8>Pagina: "+ str(ppp) +"</font></bold>", style)

    total_txt = ""
    if valor == 2:
       
        pega = str(tot).replace('.', ',')
        ve = pega.find(',')
        pos = int(ve) + 3
        valor = pega[:int(pos)]
        total_txt = "Valor Total dos itens: R$"+ str(valor) 
    
    total = Paragraph("<bold><font size=8>" + str(total_txt) + "</font></bold>", style)
    
    aW = 540
    aH = 720

    w, h = header.wrap(aW, aH)
    gg.wrap(540, 750)
    pag.wrap(540, 750)
    pp.wrap(540, 780)
    gg.drawOn(canv, 72, 750)
    pag.drawOn(canv, 480, 750)
    pp.drawOn(canv, 72, 770)
    header.drawOn(canv, 72, aH)
    aH = aH - h
    w, h = t.wrap(aW, aH)
    t.drawOn(canv, 10, aH-h)
    total.wrap(200, 200)
    total.drawOn(canv, 480, 10)
    canv.showPage()
    banco.close()

    try:
        canv.save()
        os.startfile('doc.pdf')
    except:
        
        
        msgBox = QMessageBox()
        msgBox.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
        msgBox.setWindowTitle("Relatório em uso")
        msgBox.setText("Não foi possível emitir este relatório. Feche ou renomeie o arquivo contendo o relatório anterior e depois tente novamente.")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()

def listar_itens_categoria(ordem, val, cat):
    global yy
    global data
    global ordena
    global ppp
    global colwidth
    global valor
    valor = val
    if valor == 2:
        colwidth = [2*cm, 6*cm, 3*cm, 3*cm, 4*cm, 2.5*cm]
    else:
        colwidth = [2*cm, 6*cm, 4*cm, 4*cm, 4*cm]
    
    yy = 0
    ppp = 0
    data = []
    ordena = ''
    
    if ordem != '':
        ordena = 'ORDER BY ' + str(ordem)
    
    cat = str(cat)
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    
    cursor.execute("SELECT c.id, c.nome, c.valor, c.serie, l.nome, p.nome, d.nome FROM componentes AS c INNER JOIN locais AS l ON c.localizacao = l.id INNER JOIN categorias AS d ON c.categoria = d.id LEFT JOIN computadores AS p ON c.computador = p.id WHERE d.nome = '" + cat + "' "+ str(ordena) +";")
    
    relatorio = cursor.fetchall()

    cursor.execute("SELECT SUM(c.valor) AS 'total' FROM componentes AS c INNER JOIN categorias AS d ON c.categoria = d.id WHERE d.nome = '" + cat + "';")
    valor_total = cursor.fetchone()
    tot = valor_total[0]

    styles = getSampleStyleSheet()
    style = styles["BodyText"]

    canv = Canvas("doc.pdf", pagesize=letter)
    
    
    def quebra():
         
        global yy
        global data 
        global ppp
        global valor
        global colwidth
        gg = Paragraph("<bold><font size=12>Controle de Inventário - Relatórios</font></bold>", style)
        pp = Paragraph("<bold><font size=10>Empresa: "+empresa+"</font></bold>", style)
        header = Paragraph("<bold><font size=18>Listagem - Itens da Categoria: "+ cat +"</font></bold>", style)
        pag = Paragraph("<bold><font size=8>Pagina: "+ str(ppp) +"</font></bold>", style)    
        t = Table(data, colwidth)
        t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.25, colors.black), ("FONTSIZE", (1, 0), (-1,-1), 10),
                            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]))
        data_len = len(data)

        for each in range(data_len):
            if each % 2 == 0:
                bg_color = colors.whitesmoke
            else:
                bg_color = colors.lightgrey

            t.setStyle(TableStyle([('BACKGROUND', (0, each), (-1, each), bg_color)]))

        aW = 540
        aH = 720

        w, h = header.wrap(aW, aH)
        gg.wrap(540, 750)
        pag.wrap(540, 750)
        pp.wrap(540, 780)
        gg.drawOn(canv, 72, 750)
        pag.drawOn(canv, 480, 750)
        pp.drawOn(canv, 72, 770)
        header.drawOn(canv, 72, aH)
        aH = aH - h
        w, h = t.wrap(aW, aH)
        t.drawOn(canv, 10, aH-h)

        canv.showPage()
        yy = 0
        
        if valor == 2:
            data = [['ID', 'Nome', 'Item Composto', 'Localização', 'Serial', 'Valor']]
        else:
            data = [['ID', 'Nome', 'Item Composto', 'Localização', 'Serial']]





    if valor == 2:
        data = [['ID', 'Nome', 'Item Composto', 'Localização', 'Serial', 'Valor']]
    else:
        data = [['ID', 'Nome', 'Item Composto', 'Localização', 'Serial']]
    
    for dados in relatorio:
        comp = ''
        
        if dados[5]:
            comp = str(dados[5])
        if valor == 2:
            data.append([dados[0], str(dados[1])[:28], str(comp)[:15], str(dados[4])[:15], str(dados[3])[:16], str(dados[2]).replace('.', ',')[:11]])
            
        else:    
            data.append([dados[0], str(dados[1])[:28], str(comp)[:20], str(dados[4])[:20], str(dados[3])[:16]])
        yy = yy + 1

        if yy == 35:
            ppp = ppp + 1
            quebra()

    t = Table(data, colwidth)
    t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.25, colors.black), ("FONTSIZE", (1, 0), (-1,-1), 10),
                        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]))
    data_len = len(data)

    for each in range(data_len):
        if each % 2 == 0:
            bg_color = colors.whitesmoke
        else:
            bg_color = colors.lightgrey

        t.setStyle(TableStyle([('BACKGROUND', (0, each), (-1, each), bg_color)]))

    gg = Paragraph("<bold><font size=12>Controle de Inventário - Relatórios</font></bold>", style)
    pp = Paragraph("<bold><font size=10>Empresa: "+empresa+"</font></bold>", style)
    header = Paragraph("<bold><font size=18>Listagem - Itens da Categoria: "+ cat +"</font></bold>", style)
    ppp = ppp + 1
    pag = Paragraph("<bold><font size=8>Pagina: "+ str(ppp) +"</font></bold>", style)

    total_txt = ""
    if valor == 2:
        
        pega = str(tot).replace('.', ',')
        ve = pega.find(',')
        pos = int(ve) + 3
        valor = pega[:int(pos)]
        total_txt = "Valor Total dos itens: R$"+ str(valor) 
    
    total = Paragraph("<bold><font size=8>" + str(total_txt) + "</font></bold>", style)
    
    aW = 540
    aH = 720

    w, h = header.wrap(aW, aH)
    gg.wrap(540, 750)
    pag.wrap(540, 750)
    pp.wrap(540, 780)
    gg.drawOn(canv, 72, 750)
    pag.drawOn(canv, 480, 750)
    pp.drawOn(canv, 72, 770)
    header.drawOn(canv, 72, aH)
    aH = aH - h
    w, h = t.wrap(aW, aH)
    t.drawOn(canv, 10, aH-h)
    total.wrap(200, 200)
    total.drawOn(canv, 480, 10)
    canv.showPage()
    banco.close()

    try:
        canv.save()
        os.startfile('doc.pdf')
    except:
        
        
        msgBox = QMessageBox()
        msgBox.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
        msgBox.setWindowTitle("Relatório em uso")
        msgBox.setText("Não foi possível emitir este relatório. Feche ou renomeie o arquivo contendo o relatório anterior e depois tente novamente.")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()

def listar_itens_local(ordem, val, loc):
    global yy
    global data 
    global ppp
    global ordena
    global colwidth
    global valor
    valor = val
    if valor == 2:
        colwidth = [2*cm, 6*cm, 3*cm, 3*cm, 4*cm, 2.5*cm]
    else:
        colwidth = [2*cm, 6*cm, 4*cm, 4*cm, 4*cm]
    
    yy = 0
    ppp = 0
    data = []
    ordena = ''
    
    if ordem != '':
        ordena = 'ORDER BY ' + str(ordem)
    
    loc = str(loc)
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    
    cursor.execute("SELECT c.id, c.nome, c.valor, c.serie, l.nome, p.nome, c.integridade FROM componentes AS c INNER JOIN locais AS l ON c.localizacao = l.id LEFT JOIN computadores AS p ON c.computador = p.id WHERE l.nome = '" + loc + "' "+ str(ordena) +";")
    
    relatorio = cursor.fetchall()
    cursor.execute("SELECT SUM(c.valor) AS 'total' FROM componentes AS c INNER JOIN locais AS l ON c.localizacao = l.id WHERE l.nome = '" + loc + "';")
    valor_total = cursor.fetchone()
    tot = valor_total[0]

    styles = getSampleStyleSheet()
    style = styles["BodyText"]

    canv = Canvas("doc.pdf", pagesize=letter)
    
    
    def quebra():
         
        global yy
        global data 
        global ppp
        global valor
        global colwidth
        gg = Paragraph("<bold><font size=12>Controle de Inventário - Relatórios</font></bold>", style)
        pp = Paragraph("<bold><font size=10>Empresa: "+empresa+"</font></bold>", style)
        header = Paragraph("<bold><font size=18>Listagem - Itens do local: "+ loc +"</font></bold>", style)
        pag = Paragraph("<bold><font size=8>Pagina: "+ str(ppp) +"</font></bold>", style)    
        t = Table(data, colwidth)
        t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.25, colors.black), ("FONTSIZE", (1, 0), (-1,-1), 10),
                            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]))
        data_len = len(data)

        for each in range(data_len):
            if each % 2 == 0:
                bg_color = colors.whitesmoke
            else:
                bg_color = colors.lightgrey

            t.setStyle(TableStyle([('BACKGROUND', (0, each), (-1, each), bg_color)]))

        aW = 540
        aH = 720

        w, h = header.wrap(aW, aH)
        gg.wrap(540, 750)
        pag.wrap(540, 750)
        pp.wrap(540, 780)
        gg.drawOn(canv, 72, 750)
        pag.drawOn(canv, 480, 750)
        pp.drawOn(canv, 72, 770)
        header.drawOn(canv, 72, aH)
        aH = aH - h
        w, h = t.wrap(aW, aH)
        t.drawOn(canv, 10, aH-h)

        canv.showPage()
        yy = 0
        
        if valor == 2:
            data = [['ID', 'Nome', 'Item Composto', 'Integridade', 'Serial', 'Valor']]
        else:
            data = [['ID', 'Nome', 'Item Composto', 'Integridade', 'Serial']]





    if valor == 2:
        data = [['ID', 'Nome', 'Item Composto', 'Integridade', 'Serial', 'Valor']]
    else:
        data = [['ID', 'Nome', 'Item Composto', 'Integridade', 'Serial']]
    
    for dados in relatorio:
        comp = ''
        
        if dados[5]:
            comp = str(dados[5])
        if valor == 2:
            data.append([dados[0], str(dados[1])[:28], str(comp)[:15], str(dados[6])[:15], str(dados[3])[:16], str(dados[2]).replace('.', ',')[:11]])
            
        else:    
            data.append([dados[0], str(dados[1])[:28], str(comp)[:20], str(dados[6])[:20], str(dados[3])[:16]])
        yy = yy + 1

        if yy == 35:
            ppp = ppp + 1
            quebra()

    t = Table(data, colwidth)
    t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.25, colors.black), ("FONTSIZE", (1, 0), (-1,-1), 10),
                        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]))
    data_len = len(data)

    for each in range(data_len):
        if each % 2 == 0:
            bg_color = colors.whitesmoke
        else:
            bg_color = colors.lightgrey

        t.setStyle(TableStyle([('BACKGROUND', (0, each), (-1, each), bg_color)]))

    gg = Paragraph("<bold><font size=12>Controle de Inventário - Relatórios</font></bold>", style)
    pp = Paragraph("<bold><font size=10>Empresa: "+empresa+"</font></bold>", style)
    header = Paragraph("<bold><font size=18>Listagem - Itens do local: "+ loc +"</font></bold>", style)
    ppp = ppp + 1
    pag = Paragraph("<bold><font size=8>Pagina: "+ str(ppp) +"</font></bold>", style)

    total_txt = ""
    if valor == 2:
        
        pega = str(tot).replace('.', ',')
        ve = pega.find(',')
        pos = int(ve) + 3
        valor = pega[:int(pos)]
        total_txt = "Valor Total dos itens: R$"+ str(valor) 
    
    total = Paragraph("<bold><font size=8>" + str(total_txt) + "</font></bold>", style)
    
    aW = 540
    aH = 720

    w, h = header.wrap(aW, aH)
    gg.wrap(540, 750)
    pag.wrap(540, 750)
    pp.wrap(540, 780)
    gg.drawOn(canv, 72, 750)
    pag.drawOn(canv, 480, 750)
    pp.drawOn(canv, 72, 770)
    header.drawOn(canv, 72, aH)
    aH = aH - h
    w, h = t.wrap(aW, aH)
    t.drawOn(canv, 10, aH-h)
    total.wrap(200, 200)
    total.drawOn(canv, 480, 10)
    canv.showPage()
    banco.close()

    try:
        canv.save()
        os.startfile('doc.pdf')
    except:
        
        
        msgBox = QMessageBox()
        msgBox.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
        msgBox.setWindowTitle("Relatório em uso")
        msgBox.setText("Não foi possível emitir este relatório. Feche ou renomeie o arquivo contendo o relatório anterior e depois tente novamente.")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()

def listar_todos_computadores(ordem, val):
    global yy
    global data 
    global ppp
    global ordena
    global colwidth
    global valor
    valor = val
    if valor == 2:
        colwidth = [2*cm, 6*cm, 3*cm, 2*cm, 3.5*cm, 3.5*cm]
    else:
        colwidth = [2*cm, 6*cm, 4*cm, 4*cm, 4*cm]
    
    yy = 0
    ppp = 0
    data = []
    ordena = ''
    
    if ordem != '':
        ordena = str(ordem)
    
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    
    cursor.execute("SELECT c.id, c.nome, c.valor, c.serie, l.nome, p.nome FROM componentes AS c INNER JOIN locais AS l ON c.localizacao = l.id INNER JOIN computadores AS p ON c.computador = p.id ORDER BY p.nome "+ str(ordena) +";")

    relatorio = cursor.fetchall()

    cursor.execute("SELECT SUM(c.valor) AS 'total' FROM componentes AS c INNER JOIN computadores AS p ON c.computador = p.id;")
    valor_total = cursor.fetchone()
    tot = valor_total[0]

    styles = getSampleStyleSheet()
    style = styles["BodyText"]

    canv = Canvas("doc.pdf", pagesize=letter)
    
    
    def quebra():
         
        global yy
        global data 
        global ppp
        global valor
        global colwidth
        gg = Paragraph("<bold><font size=12>Controle de Inventário - Relatórios</font></bold>", style)
        pp = Paragraph("<bold><font size=10>Empresa: "+empresa+"</font></bold>", style)
        header = Paragraph("<bold><font size=18>Listagem - Todos os Itens Compostos</font></bold>", style)
        pag = Paragraph("<bold><font size=8>Pagina: "+ str(ppp) +"</font></bold>", style)    
        t = Table(data, colwidth)
        t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.25, colors.black), ("FONTSIZE", (1, 0), (-1,-1), 10),
                            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]))
        data_len = len(data)

        for each in range(data_len):
            if each % 2 == 0:
                bg_color = colors.whitesmoke
            else:
                bg_color = colors.lightgrey

            t.setStyle(TableStyle([('BACKGROUND', (0, each), (-1, each), bg_color)]))

        aW = 540
        aH = 720

        w, h = header.wrap(aW, aH)
        gg.wrap(540, 750)
        pag.wrap(540, 750)
        pp.wrap(540, 780)
        gg.drawOn(canv, 72, 750)
        pag.drawOn(canv, 480, 750)
        pp.drawOn(canv, 72, 770)
        header.drawOn(canv, 72, aH)
        aH = aH - h
        w, h = t.wrap(aW, aH)
        t.drawOn(canv, 10, aH-h)

        canv.showPage()
        yy = 0
        
        if valor == 2:
            data = [['ID', 'Nome', 'Serial', 'Valor', 'Localização', 'Item Composto']]
        else:
            data = [['ID', 'Nome', 'Serial', 'Localização', 'Item Composto']]





    if valor == 2:
        data = [['ID', 'Nome', 'Serial', 'Valor', 'Localização', 'Item Composto']]
    else:
        data = [['ID', 'Nome', 'Serial', 'Localização', 'Item Composto']]
    
    for dados in relatorio:
        comp = ''
        
        if dados[5]:
            comp = str(dados[5])
        if valor == 2:
            data.append([dados[0], str(dados[1])[:28], str(dados[3])[:15], str(dados[2]).replace('.', ',')[:11], str(dados[4])[:15], str(comp)[:15]])
            
        else:    
            data.append([dados[0], str(dados[1])[:28], str(dados[3])[:15], str(dados[4])[:20], str(comp)[:20]])
        yy = yy + 1

        if yy == 35:
            ppp = ppp + 1
            quebra()

    t = Table(data, colwidth)
    t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.25, colors.black), ("FONTSIZE", (1, 0), (-1,-1), 10),
                        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]))
    data_len = len(data)

    for each in range(data_len):
        if each % 2 == 0:
            bg_color = colors.whitesmoke
        else:
            bg_color = colors.lightgrey

        t.setStyle(TableStyle([('BACKGROUND', (0, each), (-1, each), bg_color)]))

    gg = Paragraph("<bold><font size=12>Controle de Inventário - Relatórios</font></bold>", style)
    pp = Paragraph("<bold><font size=10>Empresa: "+empresa+"</font></bold>", style)
    header = Paragraph("<bold><font size=18>Listagem - Todos os Itens Compostos</font></bold>", style)
    ppp = ppp + 1
    pag = Paragraph("<bold><font size=8>Pagina: "+ str(ppp) +"</font></bold>", style)

    total_txt = ""
    if valor == 2:
        
        pega = str(tot).replace('.', ',')
        ve = pega.find(',')
        pos = int(ve) + 3
        valor = pega[:int(pos)]
        total_txt = "Valor Total dos itens: R$"+ str(valor) 
    
    total = Paragraph("<bold><font size=8>" + str(total_txt) + "</font></bold>", style)
    
    aW = 540
    aH = 720

    w, h = header.wrap(aW, aH)
    gg.wrap(540, 750)
    pag.wrap(540, 750)
    pp.wrap(540, 780)
    gg.drawOn(canv, 72, 750)
    pag.drawOn(canv, 480, 750)
    pp.drawOn(canv, 72, 770)
    header.drawOn(canv, 72, aH)
    aH = aH - h
    w, h = t.wrap(aW, aH)
    t.drawOn(canv, 10, aH-h)
    total.wrap(200, 200)
    total.drawOn(canv, 480, 10)
    canv.showPage()
    banco.close()

    try:
        canv.save()
        os.startfile('doc.pdf')
    except:
        
        
        msgBox = QMessageBox()
        msgBox.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
        msgBox.setWindowTitle("Relatório em uso")
        msgBox.setText("Não foi possível emitir este relatório. Feche ou renomeie o arquivo contendo o relatório anterior e depois tente novamente.")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()

def listar_itens_computador(ordem, val, cptd):
    global yy
    global data 
    global ppp
    global ordena
    global colwidth
    global valor
    valor = val
    if valor == 2:
        colwidth = [2*cm, 6*cm, 5*cm, 5*cm, 2.5*cm]
    else:
        colwidth = [2*cm, 6*cm, 6*cm, 6*cm]
    
    yy = 0
    ppp = 0
    data = []
    ordena = ''
    
    if ordem != '':
        ordena = 'GROUP BY ' + str(ordem)
    
    cptd = str(cptd)
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    
    cursor.execute("SELECT c.id, c.nome, c.valor, c.serie, l.nome, p.nome FROM componentes AS c INNER JOIN locais AS l ON c.localizacao = l.id INNER JOIN computadores AS p ON c.computador = p.id WHERE p.nome = '" + cptd + "' "+ str(ordena) +";")
    
    relatorio = cursor.fetchall()

    cursor.execute("SELECT SUM(c.valor) AS 'total' FROM componentes AS c INNER JOIN computadores AS p ON c.computador = p.id WHERE p.nome = '" + cptd + "';")
    valor_total = cursor.fetchone()
    tot = valor_total[0]


    styles = getSampleStyleSheet()
    style = styles["BodyText"]

    canv = Canvas("doc.pdf", pagesize=letter)
    
    
    def quebra():
         
        global yy
        global data 
        global ppp
        global valor
        global colwidth
        gg = Paragraph("<bold><font size=12>Controle de Inventário - Relatórios</font></bold>", style)
        pp = Paragraph("<bold><font size=10>Empresa: "+empresa+"</font></bold>", style)
        header = Paragraph("<bold><font size=18>Listagem - Itens Compostos: "+ cptd +"</font></bold>", style)
        pag = Paragraph("<bold><font size=8>Pagina: "+ str(ppp) +"</font></bold>", style)    
        t = Table(data, colwidth)
        t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.25, colors.black), ("FONTSIZE", (1, 0), (-1,-1), 10),
                            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]))
        data_len = len(data)

        for each in range(data_len):
            if each % 2 == 0:
                bg_color = colors.whitesmoke
            else:
                bg_color = colors.lightgrey

            t.setStyle(TableStyle([('BACKGROUND', (0, each), (-1, each), bg_color)]))

        aW = 540
        aH = 720

        w, h = header.wrap(aW, aH)
        gg.wrap(540, 750)
        pag.wrap(540, 750)
        pp.wrap(540, 780)
        gg.drawOn(canv, 72, 750)
        pag.drawOn(canv, 480, 750)
        pp.drawOn(canv, 72, 770)
        header.drawOn(canv, 72, aH)
        aH = aH - h
        w, h = t.wrap(aW, aH)
        t.drawOn(canv, 10, aH-h)

        canv.showPage()
        yy = 0
        
        if valor == 2:
            data = [['ID', 'Nome', 'Localização', 'Serial', 'Valor']]
        else:
            data = [['ID', 'Nome', 'Localização', 'Serial']]





    if valor == 2:
        data = [['ID', 'Nome', 'Localização', 'Serial', 'Valor']]
    else:
        data = [['ID', 'Nome', 'Localização', 'Serial']]
    
    for dados in relatorio:
        comp = ''
        
        
        if valor == 2:
            data.append([dados[0], str(dados[1])[:28], str(dados[4])[:20], str(dados[3])[:20], str(dados[2]).replace('.', ',')[:11]])
    
        else:    
            data.append([dados[0], str(dados[1])[:28], str(dados[4])[:28], str(dados[3])[:28]])
        yy = yy + 1

        if yy == 35:
            ppp = ppp + 1
            quebra()

    t = Table(data, colwidth)
    t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.25, colors.black), ("FONTSIZE", (1, 0), (-1,-1), 10),
                        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]))
    data_len = len(data)

    for each in range(data_len):
        if each % 2 == 0:
            bg_color = colors.whitesmoke
        else:
            bg_color = colors.lightgrey

        t.setStyle(TableStyle([('BACKGROUND', (0, each), (-1, each), bg_color)]))

    gg = Paragraph("<bold><font size=12>Controle de Inventário - Relatórios</font></bold>", style)
    pp = Paragraph("<bold><font size=10>Empresa: "+empresa+"</font></bold>", style)
    header = Paragraph("<bold><font size=18>Listagem - Itens Compostos: "+ cptd +"</font></bold>", style)
    ppp = ppp + 1
    pag = Paragraph("<bold><font size=8>Pagina: "+ str(ppp) +"</font></bold>", style)

    total_txt = ""
    if valor == 2:
        
        pega = str(tot).replace('.', ',')
        ve = pega.find(',')
        pos = int(ve) + 3
        valor = pega[:int(pos)]
        total_txt = "Valor Total dos itens: R$"+ str(valor) 
    
    total = Paragraph("<bold><font size=8>" + str(total_txt) + "</font></bold>", style)
    
    aW = 540
    aH = 720

    w, h = header.wrap(aW, aH)
    gg.wrap(540, 750)
    pag.wrap(540, 750)
    pp.wrap(540, 780)
    gg.drawOn(canv, 72, 750)
    pag.drawOn(canv, 480, 750)
    pp.drawOn(canv, 72, 770)
    header.drawOn(canv, 72, aH)
    aH = aH - h
    w, h = t.wrap(aW, aH)
    t.drawOn(canv, 10, aH-h)
    total.wrap(200, 200)
    total.drawOn(canv, 480, 10)
    canv.showPage()
    banco.close()

    try:
        canv.save()
        os.startfile('doc.pdf')
    except:
        
        
        msgBox = QMessageBox()
        msgBox.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
        msgBox.setWindowTitle("Relatório em uso")
        msgBox.setText("Não foi possível emitir este relatório. Feche ou renomeie o arquivo contendo o relatório anterior e depois tente novamente.")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()



def listar_local_computador(ordem, val, loc):
    global yy
    global data 
    global ppp
    global ordena
    global colwidth
    global valor
    valor = val
    if valor == 2:
        colwidth = [2*cm, 6*cm, 5*cm, 5*cm, 2.5*cm]
    else:
        colwidth = [2*cm, 6*cm, 6*cm, 6*cm]
    
    yy = 0
    ppp = 0
    data = []
    ordena = ''
    
    if ordem != '':
        ordena = ', ' + str(ordem)
    
    loc = str(loc)
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    
    cursor.execute("SELECT c.id, c.nome, c.valor, c.serie, l.nome, p.nome FROM componentes AS c INNER JOIN locais AS l ON c.localizacao = l.id INNER JOIN computadores AS p ON c.computador = p.id WHERE l.nome = '" + loc + "' ORDER BY p.nome"+ str(ordena) +";")
    
    relatorio = cursor.fetchall()

    cursor.execute("SELECT SUM(c.valor) AS 'total' FROM componentes AS c INNER JOIN locais AS l ON c.localizacao = l.id INNER JOIN computadores AS p ON c.computador = p.id WHERE l.nome = '" + loc + "';")
    valor_total = cursor.fetchone()
    tot = valor_total[0]


    styles = getSampleStyleSheet()
    style = styles["BodyText"]

    canv = Canvas("doc.pdf", pagesize=letter)
    
    
    def quebra():
         
        global yy
        global data 
        global ppp
        global valor
        global colwidth
        gg = Paragraph("<bold><font size=12>Controle de Inventário - Relatórios</font></bold>", style)
        pp = Paragraph("<bold><font size=10>Empresa: "+empresa+"</font></bold>", style)
        header = Paragraph("<bold><font size=18>Listagem - Itens Compostos do local: "+ loc +"</font></bold>", style)
        pag = Paragraph("<bold><font size=8>Pagina: "+ str(ppp) +"</font></bold>", style)    
        t = Table(data, colwidth)
        t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.25, colors.black), ("FONTSIZE", (1, 0), (-1,-1), 10),
                            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]))
        data_len = len(data)

        for each in range(data_len):
            if each % 2 == 0:
                bg_color = colors.whitesmoke
            else:
                bg_color = colors.lightgrey

            t.setStyle(TableStyle([('BACKGROUND', (0, each), (-1, each), bg_color)]))

        aW = 540
        aH = 720

        w, h = header.wrap(aW, aH)
        gg.wrap(540, 750)
        pag.wrap(540, 750)
        pp.wrap(540, 780)
        gg.drawOn(canv, 72, 750)
        pag.drawOn(canv, 480, 750)
        pp.drawOn(canv, 72, 770)
        header.drawOn(canv, 72, aH)
        aH = aH - h
        w, h = t.wrap(aW, aH)
        t.drawOn(canv, 10, aH-h)

        canv.showPage()
        yy = 0
        
        if valor == 2:
            data = [['ID', 'Nome', 'Item Composto', 'Serial', 'Valor']]
        else:
            data = [['ID', 'Nome', 'Item Composto', 'Serial']]





    if valor == 2:
        data = [['ID', 'Nome', 'Item Composto', 'Serial', 'Valor']]
    else:
        data = [['ID', 'Nome', 'Item Composto', 'Serial']]
    
    for dados in relatorio:
        comp = ''
        
        
        if valor == 2:
            data.append([dados[0], str(dados[1])[:28], str(dados[5])[:20], str(dados[3])[:20], str(dados[2]).replace('.', ',')[:11]])
            
        else:    
            data.append([dados[0], str(dados[1])[:28], str(dados[5])[:28], str(dados[3])[:28]])
        yy = yy + 1

        if yy == 35:
            ppp = ppp + 1
            quebra()

    t = Table(data, colwidth)
    t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.25, colors.black), ("FONTSIZE", (1, 0), (-1,-1), 10),
                        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]))
    data_len = len(data)

    for each in range(data_len):
        if each % 2 == 0:
            bg_color = colors.whitesmoke
        else:
            bg_color = colors.lightgrey

        t.setStyle(TableStyle([('BACKGROUND', (0, each), (-1, each), bg_color)]))

    gg = Paragraph("<bold><font size=12>Controle de Inventário - Relatórios</font></bold>", style)
    pp = Paragraph("<bold><font size=10>Empresa: "+empresa+"</font></bold>", style)
    header = Paragraph("<bold><font size=18>Listagem - Itens Compostos do local: "+ loc +"</font></bold>", style)
    ppp = ppp + 1
    pag = Paragraph("<bold><font size=8>Pagina: "+ str(ppp) +"</font></bold>", style)

    total_txt = ""
    if valor == 2:
        
        pega = str(tot).replace('.', ',')
        ve = pega.find(',')
        pos = int(ve) + 3
        valor = pega[:int(pos)]
        total_txt = "Valor Total dos itens: R$"+ str(valor) 
    
    total = Paragraph("<bold><font size=8>" + str(total_txt) + "</font></bold>", style)
    
    aW = 540
    aH = 720

    w, h = header.wrap(aW, aH)
    gg.wrap(540, 750)
    pag.wrap(540, 750)
    pp.wrap(540, 780)
    gg.drawOn(canv, 72, 750)
    pag.drawOn(canv, 480, 750)
    pp.drawOn(canv, 72, 770)
    header.drawOn(canv, 72, aH)
    aH = aH - h
    w, h = t.wrap(aW, aH)
    t.drawOn(canv, 10, aH-h)
    total.wrap(200, 200)
    total.drawOn(canv, 480, 10)
    canv.showPage()
    banco.close()

    try:
        canv.save()
        os.startfile('doc.pdf')
    except:
        
        
        msgBox = QMessageBox()
        msgBox.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
        msgBox.setWindowTitle("Relatório em uso")
        msgBox.setText("Não foi possível emitir este relatório. Feche ou renomeie o arquivo contendo o relatório anterior e depois tente novamente.")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()