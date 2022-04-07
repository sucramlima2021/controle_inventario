from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QTableWidget,QTableWidgetItem,QHeaderView,QComboBox,QMessageBox,QInputDialog, QFileDialog
from unidecode import unidecode
import rsc
import sqlite3
import sys
from datetime import datetime
from reports import *
import win32con, win32api, os
import random
import string

tipo_usuario = 1
usuario_logado = ""
part_number = ''
op = 0

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('programa.ui', self) # Load the .ui file
    def closeEvent(self, event):

        msgBox = QMessageBox()
        msgBox.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
        msgBox.setWindowTitle("Encerrar sistema")
        msgBox.setText("Você realmente quer encerrar o sistema?")
        msgBox.setStandardButtons(QMessageBox.Yes)
        msgBox.addButton(QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.No)
        if(msgBox.exec() == QMessageBox.Yes):
            form1.close()
            logs.close()
            event.accept()
        else:
            event.ignore()

app=QtWidgets.QApplication([])

form1=uic.loadUi("login.ui")
form1.setWindowIcon(QtGui.QIcon('logo_inventario.png'))

primeiro_usuario=uic.loadUi("inicio.ui")
primeiro_usuario.setWindowIcon(QtGui.QIcon('logo_inventario.png'))

#form=uic.loadUi("programa.ui")
form = Ui()
form.setWindowIcon(QtGui.QIcon('logo_inventario.png'))

logs=uic.loadUi("logs.ui")
logs.setWindowIcon(QtGui.QIcon('logo_inventario.png'))

progresso=uic.loadUi("progresso.ui")
progresso.setWindowIcon(QtGui.QIcon('logo_inventario.png'))

form_serial=uic.loadUi("form_serial.ui")
form_serial.setWindowIcon(QtGui.QIcon('logo_inventario.png'))


# funções pagina principal
def fecha():
    form.close()
    form1.close()
    logs.close()

def home():
    form.stackedWidget.setCurrentWidget(form.home_page)

def itens_pesquisa():
    form.stackedWidget.setCurrentWidget(form.itens_page)
    form.stackedWidget_itens.setCurrentWidget(form.itens_pesquisa_page)

    # habilita botoes a serem usados
    form.itens_gravar_btn.setEnabled(False)
    form.itens_cancelar_btn.setEnabled(False)
    form.itens_incluir_btn.setEnabled(True)
    form.itens_pesquisar_btn.setEnabled(True)
    form.itens_alterar_btn.setEnabled(False)
    form.itens_excluir_btn.setEnabled(False)
    form.itens_gravar_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    form.itens_cancelar_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    form.itens_alterar_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    form.itens_excluir_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    form.itens_incluir_btn.setStyleSheet("background-color: rgb(255, 255, 255);")
    form.itens_pesquisar_btn.setStyleSheet("background-color: rgb(255, 255, 255);")
    
    #cria a estrutura da tabela de listagem
    header = form.itens_tabela.horizontalHeader()
    header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
    header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
    header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
    header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
    header.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
    header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
    header.setSectionResizeMode(6, QtWidgets.QHeaderView.ResizeToContents)
    header.setSectionResizeMode(7, QtWidgets.QHeaderView.ResizeToContents)
    header.setSectionResizeMode(8, QtWidgets.QHeaderView.Stretch)
    form.itens_tabela.clearContents()
    form.itens_tabela.setRowCount( 0)
    form.itens_tabela.setHorizontalHeaderLabels(['ID','Nome','Categoria','Valor','Localização','Integridade','Item Composto', 'Nº de série', 'Observações'])
    form.itens_tabela.horizontalHeader().setVisible(True)
    
    #popula a tabela com os itens do banco de dados
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    cursor.execute('SELECT c.*, l.nome, p.nome, d.nome FROM componentes AS c INNER JOIN locais AS l ON c.localizacao = l.id LEFT JOIN categorias AS d On c.categoria = d.id LEFT JOIN computadores AS p ON c.computador = p.id;')
    for linha in cursor.fetchall():
        rowPosition = form.itens_tabela.rowCount()
        form.itens_tabela.insertRow(rowPosition)
        form.itens_tabela.setItem(rowPosition, 0, QTableWidgetItem(str(linha[0])))
        form.itens_tabela.setItem(rowPosition, 1, QTableWidgetItem(str(linha[1])))
        if not linha[12]:
            form.itens_tabela.setItem(rowPosition, 2, QTableWidgetItem(' '))
        else:
            form.itens_tabela.setItem(rowPosition, 2, QTableWidgetItem(str(linha[12])))
        form.itens_tabela.setItem(rowPosition, 3, QTableWidgetItem('R$ ' + str(linha[3]).replace('.',',')))
        form.itens_tabela.setItem(rowPosition, 4, QTableWidgetItem(str(linha[10])))
        form.itens_tabela.setItem(rowPosition, 5, QTableWidgetItem(str(linha[5])))
        if not linha[11]:
           form.itens_tabela.setItem(rowPosition, 6, QTableWidgetItem('Este item não faz parte de um item Composto.'))
        else:    
           form.itens_tabela.setItem(rowPosition, 6, QTableWidgetItem(str(linha[11])))
        form.itens_tabela.setItem(rowPosition, 7, QTableWidgetItem(str(linha[8])))
        form.itens_tabela.setItem(rowPosition, 8, QTableWidgetItem(str(linha[9])))
    
    cursor.execute("SELECT * FROM locais")
    form.itens_combo_localizacao.clear()
    for linha in cursor.fetchall():
        form.itens_combo_localizacao.addItem(str(linha[1]))

    cursor.execute("SELECT * FROM computadores")
    form.itens_combo_computador.clear()
    for linha in cursor.fetchall():
        form.itens_combo_computador.addItem(str(linha[1]))
    
    cursor.execute("SELECT * FROM categorias")
    form.itens_combo_categoria.clear()
    for linha in cursor.fetchall():
        form.itens_combo_categoria.addItem(str(linha[1]))

    banco.close()
def locais_pesquisa():
    form.locais_gravar_btn.setEnabled(False)
    form.locais_cancelar_btn.setEnabled(False)
    form.locais_incluir_btn.setEnabled(True)
    form.locais_pesquisar_btn.setEnabled(True)
    form.locais_alterar_btn.setEnabled(False)
    form.locais_excluir_btn.setEnabled(False)
    form.locais_gravar_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    form.locais_cancelar_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    form.locais_alterar_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    form.locais_excluir_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    form.locais_incluir_btn.setStyleSheet("background-color: rgb(255, 255, 255);")
    form.locais_pesquisar_btn.setStyleSheet("background-color: rgb(255, 255, 255);")


    form.stackedWidget.setCurrentWidget(form.locais_page)
    form.stackedWidget_locais.setCurrentWidget(form.locais_pesquisar_page)

    header = form.locais_tabela.horizontalHeader()
    header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
    header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
    header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
    header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
    
    form.locais_tabela.clearContents()
    form.locais_tabela.setRowCount( 0)
    
    form.locais_tabela.setHorizontalHeaderLabels(['ID','Nome','Descrição','Referência'])
    form.locais_tabela.horizontalHeader().setVisible(True)
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    cursor.execute('SELECT * FROM locais;')
    for linha in cursor.fetchall():
        rowPosition = form.locais_tabela.rowCount()
        form.locais_tabela.insertRow(rowPosition)
        form.locais_tabela.setItem(rowPosition, 0, QTableWidgetItem(str(linha[0])))
        form.locais_tabela.setItem(rowPosition, 1, QTableWidgetItem(str(linha[1])))
        form.locais_tabela.setItem(rowPosition, 2, QTableWidgetItem(str(linha[2])))
        form.locais_tabela.setItem(rowPosition, 3, QTableWidgetItem(str(linha[3])))
               
    
    

    banco.close()
def computadores_pesquisa():
    form.computadores_gravar_btn.setEnabled(False)
    form.computadores_cancelar_btn.setEnabled(False)
    form.computadores_incluir_btn.setEnabled(True)
    form.computadores_pesquisar_btn.setEnabled(True)
    form.computadores_alterar_btn.setEnabled(False)
    form.computadores_excluir_btn.setEnabled(False)
    form.computadores_gravar_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    form.computadores_cancelar_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    form.computadores_alterar_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    form.computadores_excluir_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    form.computadores_incluir_btn.setStyleSheet("background-color: rgb(255, 255, 255);")
    form.computadores_pesquisar_btn.setStyleSheet("background-color: rgb(255, 255, 255);")


    form.stackedWidget.setCurrentWidget(form.computadores_page)
    form.stackedWidget_computadores.setCurrentWidget(form.computadores_pesquisar_page)

    header = form.computadores_tabela.horizontalHeader()
    header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
    header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
    header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
    header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
    header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
    header.setSectionResizeMode(5, QtWidgets.QHeaderView.Stretch)
    
    form.computadores_tabela.clearContents()
    form.computadores_tabela.setRowCount( 0)
    
    form.computadores_tabela.setHorizontalHeaderLabels(['ID','Nome','Descrição','Localização'])
    form.computadores_tabela.horizontalHeader().setVisible(True)
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    cursor.execute('SELECT c.*, l.nome FROM computadores AS c INNER JOIN locais AS l ON c.localizacao = l.id;')
    for linha in cursor.fetchall():
        rowPosition = form.computadores_tabela.rowCount()
        form.computadores_tabela.insertRow(rowPosition)
        form.computadores_tabela.setItem(rowPosition, 0, QTableWidgetItem(str(linha[0])))
        form.computadores_tabela.setItem(rowPosition, 1, QTableWidgetItem(str(linha[1])))
        form.computadores_tabela.setItem(rowPosition, 2, QTableWidgetItem(str(linha[3])))
        form.computadores_tabela.setItem(rowPosition, 3, QTableWidgetItem(str(linha[8])))
        form.computadores_tabela.setItem(rowPosition, 4, QTableWidgetItem(str(linha[4])))
        form.computadores_tabela.setItem(rowPosition, 5, QTableWidgetItem(str(linha[5])))
                 
    
    cursor.execute("SELECT * FROM locais")
    form.computadores_p_localizacao_combo.clear()
    for linha in cursor.fetchall():
        form.computadores_p_localizacao_combo.addItem(str(linha[1]))

   

    banco.close()
def relatorios_pesquisa():
    form.stackedWidget.setCurrentWidget(form.relatorios_page)
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    #popula combobox_2
    cursor.execute("SELECT nome FROM categorias;")
    ctg = cursor.fetchall()
    form.comboBox_2.clear()
    for nome in ctg:
        form.comboBox_2.addItem(nome[0])
    form.comboBox_2.setCurrentIndex(0)
    
    #popula combobox_3 / 4
    cursor.execute("SELECT nome FROM locais;")
    loc = cursor.fetchall()
    form.comboBox_3.clear()
    form.comboBox_4.clear()
    for nome in loc:
        form.comboBox_3.addItem(nome[0])
        form.comboBox_4.addItem(nome[0])
    form.comboBox_3.setCurrentIndex(0)
    form.comboBox_4.setCurrentIndex(0)
    #popula combobox_5
    cursor.execute("SELECT nome FROM computadores;")
    comp = cursor.fetchall()
    form.comboBox_5.clear()
    for nome in comp:
        form.comboBox_5.addItem(nome[0])
    form.comboBox_5.setCurrentIndex(0)
    
    banco.close()

def categorias_pesquisa():
    form.categorias_gravar_btn.setEnabled(False)
    form.categorias_cancelar_btn.setEnabled(False)
    form.categorias_incluir_btn.setEnabled(True)
    form.categorias_pesquisar_btn.setEnabled(True)
    form.categorias_alterar_btn.setEnabled(False)
    form.categorias_excluir_btn.setEnabled(False)
    form.categorias_gravar_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    form.categorias_cancelar_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    form.categorias_alterar_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    form.categorias_excluir_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    form.categorias_incluir_btn.setStyleSheet("background-color: rgb(255, 255, 255);")
    form.categorias_pesquisar_btn.setStyleSheet("background-color: rgb(255, 255, 255);")

    form.stackedWidget.setCurrentWidget(form.categorias_page)
    form.stackedWidget_categorias.setCurrentWidget(form.categorias_pesquisar_page)

    header = form.categorias_tabela.horizontalHeader()
    header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
    header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
    header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
    
    
    form.categorias_tabela.clearContents()
    form.categorias_tabela.setRowCount( 0)
    
    form.categorias_tabela.setHorizontalHeaderLabels(['ID','Nome','Descrição'])
    form.categorias_tabela.horizontalHeader().setVisible(True)
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    cursor.execute('SELECT * FROM categorias;')
    for linha in cursor.fetchall():
        rowPosition = form.categorias_tabela.rowCount()
        form.categorias_tabela.insertRow(rowPosition)
        form.categorias_tabela.setItem(rowPosition, 0, QTableWidgetItem(str(linha[0])))
        form.categorias_tabela.setItem(rowPosition, 1, QTableWidgetItem(str(linha[1])))
        form.categorias_tabela.setItem(rowPosition, 2, QTableWidgetItem(str(linha[2])))
        
               
    
    

    banco.close()
def usuarios_pesquisa():
    form.usuarios_gravar_btn.setEnabled(False)
    form.usuarios_cancelar_btn.setEnabled(False)
    form.usuarios_incluir_btn.setEnabled(True)
    form.usuarios_pesquisar_btn.setEnabled(True)
    form.usuarios_alterar_btn.setEnabled(False)
    form.usuarios_excluir_btn.setEnabled(False)
    form.usuarios_gravar_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    form.usuarios_cancelar_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    form.usuarios_alterar_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    form.usuarios_excluir_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    form.usuarios_incluir_btn.setStyleSheet("background-color: rgb(255, 255, 255);")
    form.usuarios_pesquisar_btn.setStyleSheet("background-color: rgb(255, 255, 255);")

    form.stackedWidget.setCurrentWidget(form.usuarios_page)
    form.stackedWidget_usuarios.setCurrentWidget(form.usuarios_pesquisar_page)

    header = form.usuarios_tabela.horizontalHeader()
    header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
    header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
    header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
    header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
    
    
    form.usuarios_tabela.clearContents()
    form.usuarios_tabela.setRowCount( 0)
    
    form.usuarios_tabela.setHorizontalHeaderLabels(['ID','Nome','Username', 'Tipo de Usuário'])
    form.usuarios_tabela.horizontalHeader().setVisible(True)
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    cursor.execute('SELECT * FROM usuarios;')
    for linha in cursor.fetchall():
        rowPosition = form.usuarios_tabela.rowCount()
        form.usuarios_tabela.insertRow(rowPosition)
        form.usuarios_tabela.setItem(rowPosition, 0, QTableWidgetItem(str(linha[0])))
        form.usuarios_tabela.setItem(rowPosition, 1, QTableWidgetItem(str(linha[1])))
        form.usuarios_tabela.setItem(rowPosition, 2, QTableWidgetItem(str(linha[2])))
        if linha[4] == 1:
            form.usuarios_tabela.setItem(rowPosition, 3, QTableWidgetItem('Administrador'))
        elif linha[4] == 2:
            form.usuarios_tabela.setItem(rowPosition, 3, QTableWidgetItem('Usuário'))

    
    

    banco.close()









#funções Itens Gerais
#chamar páginas
#incluir
def itens_incluir_page():
    
    # habilita botoes a serem usados
    form.itens_gravar_btn.setEnabled(True)
    form.itens_cancelar_btn.setEnabled(True)
    form.itens_incluir_btn.setEnabled(False)
    form.itens_pesquisar_btn.setEnabled(False)
    form.itens_alterar_btn.setEnabled(False)
    form.itens_excluir_btn.setEnabled(False)
    form.itens_gravar_btn.setStyleSheet("background-color: rgb(255, 255, 255)")
    form.itens_cancelar_btn.setStyleSheet("background-color: rgb(255, 255, 255)")
    form.itens_incluir_btn.setStyleSheet("background-color: rgb(58, 58, 58);")
    form.itens_pesquisar_btn.setStyleSheet("background-color: rgb(58, 58, 58);")
    form.itens_alterar_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    form.itens_excluir_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    

    #inicia banco de dados e preenche as combo boxes
    form.stackedWidget_itens.setCurrentWidget(form.itens_cadastro_page)
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
       
    cursor.execute("SELECT * FROM locais")
    form.itens_c_localizacao_combo.clear()
    form.itens_c_localizacao_combo.addItem('Locallização:')
    for linha in cursor.fetchall():
        form.itens_c_localizacao_combo.addItem(str(linha[1]))

    cursor.execute("SELECT * FROM computadores")
    form.itens_c_computador_combo.clear()
    form.itens_c_computador_combo.addItem('Item Composto:')
    for linha in cursor.fetchall():
        form.itens_c_computador_combo.addItem(str(linha[1]))

    cursor.execute("SELECT * FROM categorias")
    form.itens_c_categoria_combo.clear()
    form.itens_c_categoria_combo.addItem('Categoria:')
    for linha in cursor.fetchall():
        form.itens_c_categoria_combo.addItem(str(linha[1]))

    banco.close()
   
    form.itens_c_categoria_combo.setCurrentIndex(0)
    form.itens_c_nome_txt.setText('')
    form.itens_c_valor_txt.setText('')
    form.itens_c_serie_txt.setText('')
    form.itens_c_obs_txt.setText('')
    form.itens_c_integridade_combo.setCurrentIndex(0)
    form.itens_c_computador_combo.setCurrentIndex(0)
    form.itens_c_localizacao_combo.setCurrentIndex(0)

#alterar / excluir
def itens_seleciona_item():
    tt = form.itens_tabela.selectedItems()
    kk = form.itens_tabela.row(tt[0])
    global gg
    gg = form.itens_tabela.item(kk,0)
    gg = gg.text()
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    cursor.execute("SELECT * FROM componentes WHERE id = " + str(gg) + ";")
    dados = cursor.fetchone()
    cursor.execute("SELECT * FROM categorias")
    form.itens_a_categoria_combo.clear()
    categoria = cursor.fetchall()
    indice = 0
    
    for linha in categoria:
        form.itens_a_categoria_combo.addItem(str(linha[1]))
        if linha[0] == dados[2]:
             form.itens_a_categoria_combo.setCurrentIndex(indice)
        else:
            indice = indice + 1


    cursor.execute("SELECT * FROM locais")
    form.itens_a_localizacao_combo.clear()
    locais = cursor.fetchall()
    indice1 = 0
    
    for linha in locais:
        form.itens_a_localizacao_combo.addItem(str(linha[1]))
        if linha[0] == dados[4]:
             form.itens_a_localizacao_combo.setCurrentIndex(indice1)
        else:
            indice1 = indice1 + 1

    cursor.execute("SELECT * FROM computadores")
    form.itens_a_computador_combo.clear()
    indice2 = 0
    comps = cursor.fetchall()
    for linha in comps:
        form.itens_a_computador_combo.addItem(str(linha[1]))
        if linha[0] == dados[6]:
             form.itens_a_computador_combo.setCurrentIndex(indice2)
        else:
             indice2 = indice2 + 1

    if not dados[6]:
        form.itens_a_checkbox.setChecked(False)
        form.itens_a_computador_combo.setEnabled(False)
        form.itens_a_localizacao_combo.setEnabled(True)
    else:
        form.itens_a_checkbox.setChecked(True)
        form.itens_a_computador_combo.setEnabled(True)
        form.itens_a_localizacao_combo.setEnabled(False)
        
    form.itens_a_nome_txt.setText(dados[1])
    
    form.itens_a_valor_txt.setText(str(dados[3]))

    integridade_index = 0
    if dados[5] == 'Funcionando':
        integridade_index = 0
    elif dados[5] == 'Guardado - Funcionando':
        integridade_index = 1
    elif dados[5] == 'Quebrado':
        integridade_index = 2
    form.itens_a_integridade_combo.setCurrentIndex(integridade_index)
    form.itens_a_serie_txt.setText(str(dados[8]))
    
    form.itens_a_obs_txt.setText(str(dados[9]))
    
    banco.close()

     # habilita botoes a serem usados
    form.itens_gravar_btn.setEnabled(False)
    form.itens_cancelar_btn.setEnabled(True)
    form.itens_incluir_btn.setEnabled(True)
    form.itens_pesquisar_btn.setEnabled(True)
    if tipo_usuario == 1:
        form.itens_alterar_btn.setEnabled(True)
        form.itens_excluir_btn.setEnabled(True)    
    elif tipo_usuario == 2:
        form.itens_alterar_btn.setEnabled(False)
        form.itens_excluir_btn.setEnabled(False)
    form.itens_gravar_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    form.itens_cancelar_btn.setStyleSheet("background-color: rgb(255, 255, 255)")
    form.itens_incluir_btn.setStyleSheet("background-color: rgb(255, 255, 255);")
    form.itens_pesquisar_btn.setStyleSheet("background-color: rgb(255, 255, 255);")
    form.itens_alterar_btn.setStyleSheet("background-color: rgb(255, 255, 255)")
    form.itens_excluir_btn.setStyleSheet("background-color: rgb(255, 255, 255)")
    
    

        
    form.stackedWidget.setCurrentWidget(form.itens_page)
    form.stackedWidget_itens.setCurrentWidget(form.itens_alterar_page)
#pesquisar está na pagina principal

#controles página de pesquisa
def itens_pesquisa_consulta_id():
    valor = form.itens_p_id_txt.text()
    if valor != "" and valor.isnumeric():
        form.itens_tabela.clearContents()
        form.itens_tabela.setRowCount( 0)
        banco = sqlite3.connect('inventario.db')
        cursor = banco.cursor()
    
        cursor.execute('SELECT c.*, l.nome, p.nome, d.nome FROM componentes AS c INNER JOIN locais AS l ON c.localizacao = l.id INNER JOIN categorias AS d On c.categoria = d.id LEFT JOIN computadores AS p ON c.computador = p.id WHERE C.id = ' + valor + ';')
        for linha in cursor.fetchall():
            rowPosition = form.itens_tabela.rowCount()
            form.itens_tabela.insertRow(rowPosition)
            form.itens_tabela.setItem(rowPosition, 0, QTableWidgetItem(str(linha[0])))
            form.itens_tabela.setItem(rowPosition, 1, QTableWidgetItem(str(linha[1])))
            form.itens_tabela.setItem(rowPosition, 2, QTableWidgetItem(str(linha[12])))
            form.itens_tabela.setItem(rowPosition, 3, QTableWidgetItem('R$ ' + str(linha[3]).replace('.',',')))
            form.itens_tabela.setItem(rowPosition, 4, QTableWidgetItem(str(linha[10])))
            form.itens_tabela.setItem(rowPosition, 5, QTableWidgetItem(str(linha[5])))
            if not linha[11]:
                form.itens_tabela.setItem(rowPosition, 6, QTableWidgetItem('Este item não faz parte de um Item Composto.'))
            else:    
                form.itens_tabela.setItem(rowPosition, 6, QTableWidgetItem(str(linha[11])))
            form.itens_tabela.setItem(rowPosition, 7, QTableWidgetItem(str(linha[8])))
            form.itens_tabela.setItem(rowPosition, 8, QTableWidgetItem(str(linha[9])))
         
        banco.close()
def itens_pesquisa_consulta_nome():
    valor = unidecode(form.itens_p_nome_txt.text())
    if valor != "":
        form.itens_tabela.clearContents()
        form.itens_tabela.setRowCount( 0)
        banco = sqlite3.connect('inventario.db')
        cursor = banco.cursor()
     
        cursor.execute("SELECT c.*, l.nome, p.nome, d.nome FROM componentes AS c INNER JOIN locais AS l ON c.localizacao = l.id INNER JOIN categorias AS d On c.categoria = d.id LEFT JOIN computadores AS p ON c.computador = p.id WHERE c.nome_acento LIKE '%" + valor + "%';")
        for linha in cursor.fetchall():
            rowPosition = form.itens_tabela.rowCount()
            form.itens_tabela.insertRow(rowPosition)
            form.itens_tabela.setItem(rowPosition, 0, QTableWidgetItem(str(linha[0])))
            form.itens_tabela.setItem(rowPosition, 1, QTableWidgetItem(str(linha[1])))
            form.itens_tabela.setItem(rowPosition, 2, QTableWidgetItem(str(linha[12])))
            form.itens_tabela.setItem(rowPosition, 3, QTableWidgetItem('R$ ' + str(linha[3]).replace('.',',')))
            form.itens_tabela.setItem(rowPosition, 4, QTableWidgetItem(str(linha[10])))
            form.itens_tabela.setItem(rowPosition, 5, QTableWidgetItem(str(linha[5])))
            if not linha[11]:
                form.itens_tabela.setItem(rowPosition, 6, QTableWidgetItem('Este item não faz parte de um Item Composto.'))
            else:    
                form.itens_tabela.setItem(rowPosition, 6, QTableWidgetItem(str(linha[11])))
            form.itens_tabela.setItem(rowPosition, 7, QTableWidgetItem(str(linha[8])))
            form.itens_tabela.setItem(rowPosition, 8, QTableWidgetItem(str(linha[9])))
         
        banco.close()
def itens_pesquisa_consulta_categoria():
    valor = form.itens_combo_categoria.currentText()
    if valor != "":
        form.itens_tabela.clearContents()
        form.itens_tabela.setRowCount( 0)
        banco = sqlite3.connect('inventario.db')
        cursor = banco.cursor()
     
        cursor.execute("SELECT c.*, l.nome, p.nome, d.nome FROM componentes AS c INNER JOIN locais AS l ON c.localizacao = l.id INNER JOIN categorias AS d On c.categoria = d.id LEFT JOIN computadores AS p ON c.computador = p.id WHERE d.nome = '" + valor + "';")
        for linha in cursor.fetchall():
            rowPosition = form.itens_tabela.rowCount()
            form.itens_tabela.insertRow(rowPosition)
            form.itens_tabela.setItem(rowPosition, 0, QTableWidgetItem(str(linha[0])))
            form.itens_tabela.setItem(rowPosition, 1, QTableWidgetItem(str(linha[1])))
            form.itens_tabela.setItem(rowPosition, 2, QTableWidgetItem(str(linha[12])))
            form.itens_tabela.setItem(rowPosition, 3, QTableWidgetItem('R$ ' + str(linha[3]).replace('.',',')))
            form.itens_tabela.setItem(rowPosition, 4, QTableWidgetItem(str(linha[10])))
            form.itens_tabela.setItem(rowPosition, 5, QTableWidgetItem(str(linha[5])))
            if not linha[11]:
                form.itens_tabela.setItem(rowPosition, 6, QTableWidgetItem('Este item não faz parte de um item Composto.'))
            else:    
                form.itens_tabela.setItem(rowPosition, 6, QTableWidgetItem(str(linha[11])))
            form.itens_tabela.setItem(rowPosition, 7, QTableWidgetItem(str(linha[8])))
            form.itens_tabela.setItem(rowPosition, 8, QTableWidgetItem(str(linha[9])))
         
        banco.close()
def itens_pesquisa_consulta_local():
    valor = form.itens_combo_localizacao.currentText()
    if valor != "":
        form.itens_tabela.clearContents()
        form.itens_tabela.setRowCount( 0)
        banco = sqlite3.connect('inventario.db')
        cursor = banco.cursor()
     
        cursor.execute("SELECT c.*, l.nome, p.nome, d.nome FROM componentes AS c INNER JOIN locais AS l ON c.localizacao = l.id INNER JOIN categorias AS d On c.categoria = d.id LEFT JOIN computadores AS p ON c.computador = p.id WHERE l.nome = '" + valor + "';")
        for linha in cursor.fetchall():
            rowPosition = form.itens_tabela.rowCount()
            form.itens_tabela.insertRow(rowPosition)
            form.itens_tabela.setItem(rowPosition, 0, QTableWidgetItem(str(linha[0])))
            form.itens_tabela.setItem(rowPosition, 1, QTableWidgetItem(str(linha[1])))
            form.itens_tabela.setItem(rowPosition, 2, QTableWidgetItem(str(linha[12])))
            form.itens_tabela.setItem(rowPosition, 3, QTableWidgetItem('R$ ' + str(linha[3]).replace('.',',')))
            form.itens_tabela.setItem(rowPosition, 4, QTableWidgetItem(str(linha[10])))
            form.itens_tabela.setItem(rowPosition, 5, QTableWidgetItem(str(linha[5])))
            if not linha[11]:
                form.itens_tabela.setItem(rowPosition, 6, QTableWidgetItem('Este item não faz parte de um Item Composto.'))
            else:    
                form.itens_tabela.setItem(rowPosition, 6, QTableWidgetItem(str(linha[11])))
            form.itens_tabela.setItem(rowPosition, 7, QTableWidgetItem(str(linha[8])))
            form.itens_tabela.setItem(rowPosition, 8, QTableWidgetItem(str(linha[9])))
         
        banco.close()
def itens_pesquisa_consulta_computador():
    valor = form.itens_combo_computador.currentText()
    if valor != "":
        form.itens_tabela.clearContents()
        form.itens_tabela.setRowCount( 0)
        banco = sqlite3.connect('inventario.db')
        cursor = banco.cursor()
     
        cursor.execute("SELECT c.*, l.nome, p.nome, d.nome FROM componentes AS c INNER JOIN locais AS l ON c.localizacao = l.id INNER JOIN categorias AS d On c.categoria = d.id LEFT JOIN computadores AS p ON c.computador = p.id WHERE p.nome = '" + valor + "';")
        for linha in cursor.fetchall():
            rowPosition = form.itens_tabela.rowCount()
            form.itens_tabela.insertRow(rowPosition)
            form.itens_tabela.setItem(rowPosition, 0, QTableWidgetItem(str(linha[0])))
            form.itens_tabela.setItem(rowPosition, 1, QTableWidgetItem(str(linha[1])))
            form.itens_tabela.setItem(rowPosition, 2, QTableWidgetItem(str(linha[12])))
            form.itens_tabela.setItem(rowPosition, 3, QTableWidgetItem('R$ ' + str(linha[3]).replace('.',',')))
            form.itens_tabela.setItem(rowPosition, 4, QTableWidgetItem(str(linha[10])))
            form.itens_tabela.setItem(rowPosition, 5, QTableWidgetItem(str(linha[5])))
            if not linha[11]:
                form.itens_tabela.setItem(rowPosition, 6, QTableWidgetItem('Este item não faz parte de um Item Composto.'))
            else:    
                form.itens_tabela.setItem(rowPosition, 6, QTableWidgetItem(str(linha[11])))
            form.itens_tabela.setItem(rowPosition, 7, QTableWidgetItem(str(linha[8])))
            form.itens_tabela.setItem(rowPosition, 8, QTableWidgetItem(str(linha[9])))
         
        banco.close()
def itens_pesquisa_consulta_integridade():
    valor = form.itens_combo_integridade.currentText()
    if valor != "":
        form.itens_tabela.clearContents()
        form.itens_tabela.setRowCount( 0)
        banco = sqlite3.connect('inventario.db')
        cursor = banco.cursor()
     
        cursor.execute("SELECT c.*, l.nome, p.nome, d.nome FROM componentes AS c INNER JOIN locais AS l ON c.localizacao = l.id INNER JOIN categorias AS d On c.categoria = d.id LEFT JOIN computadores AS p ON c.computador = p.id WHERE c.integridade = '" + valor + "';")
        for linha in cursor.fetchall():
            rowPosition = form.itens_tabela.rowCount()
            form.itens_tabela.insertRow(rowPosition)
            form.itens_tabela.setItem(rowPosition, 0, QTableWidgetItem(str(linha[0])))
            form.itens_tabela.setItem(rowPosition, 1, QTableWidgetItem(str(linha[1])))
            form.itens_tabela.setItem(rowPosition, 2, QTableWidgetItem(str(linha[12])))
            form.itens_tabela.setItem(rowPosition, 3, QTableWidgetItem('R$ ' + str(linha[3]).replace('.',',')))
            form.itens_tabela.setItem(rowPosition, 4, QTableWidgetItem(str(linha[10])))
            form.itens_tabela.setItem(rowPosition, 5, QTableWidgetItem(str(linha[5])))
            if not linha[11]:
                form.itens_tabela.setItem(rowPosition, 6, QTableWidgetItem('Este item não faz parte de um item Composto.'))
            else:    
                form.itens_tabela.setItem(rowPosition, 6, QTableWidgetItem(str(linha[11])))
            form.itens_tabela.setItem(rowPosition, 7, QTableWidgetItem(str(linha[8])))
            form.itens_tabela.setItem(rowPosition, 8, QTableWidgetItem(str(linha[9])))
         
        banco.close()
def filtros_itens():
    cod = form.rb_id_itens
    nome = form.rb_nome_itens
    cat = form.rb_categoria_itens
    local = form.rb_localizacao_itens
    integr = form.rb_integridade_itens
    comp = form.rb_computador_itens

    if cod.isChecked():
        
        form.itens_p_id_txt.setReadOnly(False)
        form.itens_p_nome_txt.setReadOnly(True)
        form.itens_p_nome_txt.setText('')
        form.itens_combo_categoria.setEnabled(False)
        form.itens_combo_categoria.setCurrentIndex(-1)
        form.itens_combo_localizacao.setEnabled(False)
        form.itens_combo_localizacao.setCurrentIndex(-1)
        form.itens_combo_integridade.setEnabled(False)
        form.itens_combo_integridade.setCurrentIndex(-1)
        form.itens_combo_computador.setEnabled(False)
        form.itens_combo_computador.setCurrentIndex(-1)
        
        

    elif nome.isChecked():
        form.itens_p_nome_txt.setReadOnly(False)
        form.itens_p_id_txt.setReadOnly(True)
        form.itens_p_id_txt.setText('')
        form.itens_combo_categoria.setEnabled(False)
        form.itens_combo_categoria.setCurrentIndex(-1)
        form.itens_combo_localizacao.setEnabled(False)
        form.itens_combo_localizacao.setCurrentIndex(-1)
        form.itens_combo_integridade.setEnabled(False)
        form.itens_combo_integridade.setCurrentIndex(-1)
        form.itens_combo_computador.setEnabled(False)
        form.itens_combo_computador.setCurrentIndex(-1)

    elif cat.isChecked():
        form.itens_combo_categoria.setEnabled(True)
        form.itens_p_id_txt.setReadOnly(True)
        form.itens_p_id_txt.setText('')
        form.itens_p_nome_txt.setReadOnly(True)
        form.itens_p_nome_txt.setText('')
        form.itens_combo_localizacao.setEnabled(False)
        form.itens_combo_localizacao.setCurrentIndex(-1)
        form.itens_combo_integridade.setEnabled(False)
        form.itens_combo_integridade.setCurrentIndex(-1)
        form.itens_combo_computador.setEnabled(False)
        form.itens_combo_computador.setCurrentIndex(-1)

    elif local.isChecked():
        form.itens_p_id_txt.setReadOnly(True)
        form.itens_p_id_txt.setText('')
        form.itens_p_nome_txt.setReadOnly(True)
        form.itens_p_nome_txt.setText('')
        form.itens_combo_categoria.setEnabled(False)
        form.itens_combo_categoria.setCurrentIndex(-1)
        form.itens_combo_localizacao.setEnabled(True)
        form.itens_combo_integridade.setEnabled(False)
        form.itens_combo_integridade.setCurrentIndex(-1)
        form.itens_combo_computador.setEnabled(False)
        form.itens_combo_computador.setCurrentIndex(-1)

    elif integr.isChecked():
        form.itens_p_id_txt.setReadOnly(True)
        form.itens_p_id_txt.setText('')
        form.itens_p_nome_txt.setReadOnly(True)
        form.itens_p_nome_txt.setText('')
        form.itens_combo_categoria.setEnabled(False)
        form.itens_combo_categoria.setCurrentIndex(-1)
        form.itens_combo_localizacao.setEnabled(False)
        form.itens_combo_localizacao.setCurrentIndex(-1)
        form.itens_combo_integridade.setEnabled(True)
        form.itens_combo_computador.setEnabled(False)
        form.itens_combo_computador.setCurrentIndex(-1)

    elif comp.isChecked():
        form.itens_p_id_txt.setReadOnly(True)
        form.itens_p_id_txt.setText('')
        form.itens_p_nome_txt.setReadOnly(True)
        form.itens_p_nome_txt.setText('')
        form.itens_combo_categoria.setEnabled(False)
        form.itens_combo_categoria.setCurrentIndex(-1)
        form.itens_combo_localizacao.setEnabled(False)
        form.itens_combo_localizacao.setCurrentIndex(-1)
        form.itens_combo_integridade.setEnabled(False)
        form.itens_combo_integridade.setCurrentIndex(-1)
        form.itens_combo_computador.setEnabled(True)

#controles página incluir
def itens_incluir_item_comp():
    if form.itens_c_checkbox.isChecked():
        form.itens_c_localizacao_combo.setEnabled(False)
        form.itens_c_computador_combo.setEnabled(True)
    
    else:
        form.itens_c_computador_combo.setEnabled(False)
        form.itens_c_localizacao_combo.setEnabled(True)

        banco = sqlite3.connect('inventario.db')
        cursor = banco.cursor()
        cursor.execute("SELECT * FROM locais")
        form.itens_c_localizacao_combo.clear()
        form.itens_c_localizacao_combo.addItem('Localização:')
        for linha in cursor.fetchall():
            form.itens_c_localizacao_combo.addItem(str(linha[1]))
        form.itens_c_localizacao_combo.setCurrentIndex(0)

def itens_incluir_popula_combo_local():
    if form.itens_c_checkbox.isChecked():

        valor = form.itens_c_computador_combo.currentText()
        banco = sqlite3.connect('inventario.db')
        cursor = banco.cursor()
        cursor.execute("SELECT l.nome, l.id FROM locais AS l INNER JOIN computadores AS p ON l.id = p.localizacao WHERE p.nome = '" + valor + "';")
        localizacao = cursor.fetchone()
        form.itens_c_localizacao_combo.clear()
        form.itens_c_localizacao_combo.addItem(localizacao[0])
        form.itens_c_localizacao_combo.setCurrentIndex(0)
        banco.close()
def itens_cadastrar_itens():
    
    nome = form.itens_c_nome_txt.text()
    categoria = form.itens_c_categoria_combo.currentText()
    valor = form.itens_c_valor_txt.text()
    valor = valor.replace(',', '.')
    integridade = form.itens_c_integridade_combo.currentText()
    if integridade == 'Integridade:':
        integridade = ''
    
    local = form.itens_c_localizacao_combo.currentText()
    computador = form.itens_c_computador_combo.currentText()
    nome_acento = unidecode(nome)
    serie = form.itens_c_serie_txt.text()
    obs = form.itens_c_obs_txt.text()
    sql = ""
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()

    cursor.execute("SELECT id FROM categorias WHERE nome = '" + categoria + "';")
    cat = cursor.fetchone()
    if cat:
        cat = str(cat[0])
    else:
        cat = 1
    if nome == '':
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
        msg.setText("Erro")
        msg.setInformativeText('Nome não pode ficar em branco.')
        msg.setWindowTitle("Erro")
        msg.exec_()
    else:
        cursor.execute("SELECT id FROM locais WHERE nome = '" + local + "';")
        pega = cursor.fetchone()
        if not pega:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
            msg.setText("Erro")
            msg.setInformativeText('Informe a localização do item')
            msg.setWindowTitle("Erro")
            msg.exec_()
        else:
            pega = str(pega[0])
            cursor.execute("SELECT id FROM computadores WHERE nome = '" + computador + "';")
            pega_comp = cursor.fetchone()
            if not pega_comp:
                sql = "INSERT INTO componentes (nome, categoria, valor, localizacao, integridade, nome_acento, serie, obs) VALUES('"+ nome +"', '"+ str(cat) +"', '"+ str(valor) +"', '"+ pega +"', '"+ integridade +"', '"+ nome_acento +"', '"+ serie +"', '"+ obs +"');"
            else:
                pega_comp = str(pega_comp[0])
                sql = "INSERT INTO componentes (nome, categoria, valor, localizacao, integridade, computador, nome_acento, serie, obs) VALUES('"+ nome +"', "+ str(cat) +", "+ str(valor) +", "+ pega +", '"+ integridade +"', "+ pega_comp +", '"+ nome_acento +"', '"+ serie +"', '"+ obs +"');"
        
        
       
            cursor.execute(sql)
            banco.commit()

            cursor.execute("SELECT id FROM componentes WHERE nome = '"+ nome +"';")
            gg = cursor.fetchall()
            codigo = gg[(-1)]
            agora = datetime.now()
            agora = str(agora)[:19]
            cursor.execute("INSERT INTO log (tabela, nome, codigo, operacao, data, usuario) VALUES ('1','"+ nome +"', "+ str(codigo[0]) +", 1, '"+ agora +"',"+ str(usuario_logado) +");")
            banco.commit()
        
       
            banco.close()
    
            itens_pesquisa()

#controles página alterar/excluir
def itens_alterar_item_comp():
    if form.itens_a_checkbox.isChecked():
        form.itens_a_localizacao_combo.setEnabled(False)
        form.itens_a_computador_combo.setEnabled(True)
    
    else:
        form.itens_a_computador_combo.setEnabled(False)
        form.itens_a_localizacao_combo.setEnabled(True)
        form.itens_a_computador_combo.setCurrentIndex(-1)
        banco = sqlite3.connect('inventario.db')
        cursor = banco.cursor()
        cursor.execute("SELECT * FROM locais")
        form.itens_a_localizacao_combo.clear()
        for linha in cursor.fetchall():
            form.itens_a_localizacao_combo.addItem(str(linha[1]))
        banco.close()
def itens_alterar_popula_combo_local():
    if form.itens_a_checkbox.isChecked():

        valor = form.itens_a_computador_combo.currentText()
        banco = sqlite3.connect('inventario.db')
        cursor = banco.cursor()
        cursor.execute("SELECT l.nome, l.id FROM locais AS l INNER JOIN computadores AS p ON l.id = p.localizacao WHERE p.nome = '" + valor + "';")
        localizacao = cursor.fetchone()
        form.itens_a_localizacao_combo.clear()
        form.itens_a_localizacao_combo.addItem(localizacao[0])
        form.itens_a_localizacao_combo.setCurrentIndex(0)
        banco.close()
def itens_exclui():

    msgBox = QMessageBox()
    msgBox.setWindowTitle("Confirmação de Exclusão")
    msgBox.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
    msgBox.setText("Você realmente quer excluir este registro?")
    msgBox.setStandardButtons(QMessageBox.Yes)
    msgBox.addButton(QMessageBox.No)
    msgBox.setDefaultButton(QMessageBox.No)
    if(msgBox.exec() == QMessageBox.Yes):
        banco = sqlite3.connect('inventario.db')
        cursor = banco.cursor()
        cursor.execute("SELECT nome FROM componentes WHERE id = "+ gg +";")
        nome = cursor.fetchone()
        nome = nome[0]
        cursor.execute("DELETE FROM componentes WHERE id = '" + gg + "';")
        banco.commit()
        agora = datetime.now()
        agora = str(agora)[:19]
        cursor.execute("INSERT INTO log (tabela, nome, codigo, operacao, data, usuario) VALUES ('1','"+ nome +"', "+ str(gg) +", 3, '"+ agora +"',"+ str(usuario_logado) +");")
        banco.commit()
        banco.close()
        itens_pesquisa()
def itens_alterar():
    nome = form.itens_a_nome_txt.text()
    categoria = form.itens_a_categoria_combo.currentText()
    valor = form.itens_a_valor_txt.text()
    valor = valor.replace(',', '.')
    integridade = form.itens_a_integridade_combo.currentText()
    local = form.itens_a_localizacao_combo.currentText()
    computador = form.itens_a_computador_combo.currentText()
    nome_acento = unidecode(nome)
    serie = form.itens_a_serie_txt.text()
    obs = form.itens_a_obs_txt.text()
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    sql = ""
    

    cursor.execute("SELECT id FROM categorias WHERE nome = '" + categoria + "';")
    cat = cursor.fetchone()
    if cat:
        cat = str(cat[0])
    else:
        cat = 0
    if nome == '':
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
        msg.setText("Erro")
        msg.setInformativeText('Nome não pode ficar em branco.')
        msg.setWindowTitle("Erro")
        msg.exec_()
    else:

        cursor.execute("SELECT id FROM locais WHERE nome = '" + local + "';")
        pega = cursor.fetchone()
        if not pega:
            msg = QMessageBox()
            msg.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Erro")
            msg.setInformativeText('Informe a localização do item')
            msg.setWindowTitle("Erro")
            msg.exec_()
        else:
            pega = str(pega[0])
            cursor.execute("SELECT id FROM computadores WHERE nome = '" + computador + "';")
            pega_comp = cursor.fetchone()
            if pega_comp:
                pega_comp = str(pega_comp[0])
                sql = "UPDATE componentes SET nome = '"+ nome +"', categoria = "+ str(cat) +", valor = "+ str(valor) +", localizacao = "+ str(pega) +", integridade = '"+ integridade +"', computador = "+ str(pega_comp) +", nome_acento = '"+ nome_acento +"', serie = '"+ serie +"', obs = '"+ obs +"' WHERE id = '" + gg + "';"
            else:
                sql = "UPDATE componentes SET nome = '"+ nome +"', categoria = "+ str(cat) +", valor = "+ str(valor) +", localizacao = "+ str(pega) +", integridade = '"+ integridade +"', computador = 0, nome_acento = '"+ nome_acento +"', serie = '"+ serie +"', obs = '"+ obs +"' WHERE id = '" + gg + "';"

            cursor.execute("SELECT * FROM componentes WHERE id = '" + gg + "';")
            compara = cursor.fetchone()
            
            
            msgBox = QMessageBox()
            msgBox.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
            msgBox.setWindowTitle("Confirmação de Alteração")
            msgBox.setText("Você realmente quer alterar este registro?")
            msgBox.setStandardButtons(QMessageBox.Yes)
            msgBox.addButton(QMessageBox.No)
            msgBox.setDefaultButton(QMessageBox.No)
            if(msgBox.exec() == QMessageBox.Yes):
                cursor.execute(sql)

                banco.commit()
                agora = datetime.now()
                agora = str(agora)[:19]
                cursor.execute("INSERT INTO log (tabela, nome, codigo, operacao, data, usuario) VALUES ('1','"+ nome +"', "+ str(gg) +", 2, '"+ agora +"',"+ str(usuario_logado) +");")
                banco.commit()
                cursor.execute("SELECT id FROM log;")
                pega_log = cursor.fetchall()
                pega_id_log = pega_log[(-1)]
                alt = []
                if compara[1] != nome:
                    alt.append(['Nome', compara[1], nome, pega_id_log[0]])
                if str(compara[2]) != cat:
                    alt.append(['Categoria', compara[2], cat, pega_id_log[0]])
                if str(compara[3]) != valor:
                    alt.append(['Valor', compara[3], valor, pega_id_log[0]])
                
                if str(compara[4]) != pega:
                    alt.append(['Localização', compara[4], pega, pega_id_log[0]])
                if compara[5] != integridade:
                    alt.append(['Integridade', compara[5], integridade, pega_id_log[0]])
                if pega_comp and str(compara[6]) != pega_comp:
                    alt.append(['Computador', compara[6], pega_comp[0], pega_id_log[0]])
                if compara[8] != serie:
                    alt.append(['Serial', compara[8], serie, pega_id_log[0]])
                if compara[9] != obs:
                    alt.append(['Observações', compara[9], obs, pega_id_log[0]])
                
                
                for linha in alt:
                    cursor.execute("INSERT INTO alteracoes(campo, ant, atual, altera_id) VALUES('"+ str(linha[0]) +"', '"+ str(linha[1]) +"', '"+ str(linha[2]) +"', '"+ str(linha[3]) +"');")
                    banco.commit()
        
        
                banco.close()
                itens_pesquisa()










#funções computadores
# chamar paginas
#incluir
def computadores_incluir_page():
    # habilita botoes a serem usados
    form.computadores_gravar_btn.setEnabled(True)
    form.computadores_cancelar_btn.setEnabled(True)
    form.computadores_incluir_btn.setEnabled(False)
    form.computadores_pesquisar_btn.setEnabled(False)
    form.computadores_alterar_btn.setEnabled(False)
    form.computadores_excluir_btn.setEnabled(False)
    form.computadores_gravar_btn.setStyleSheet("background-color: rgb(255, 255, 255)")
    form.computadores_cancelar_btn.setStyleSheet("background-color: rgb(255, 255, 255)")
    form.computadores_incluir_btn.setStyleSheet("background-color: rgb(58, 58, 58);")
    form.computadores_pesquisar_btn.setStyleSheet("background-color: rgb(58, 58, 58);")
    form.computadores_alterar_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    form.computadores_excluir_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    

    #inicia banco de dados e preenche as combo boxes
    form.stackedWidget_computadores.setCurrentWidget(form.computadores_cadastrar_page)
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
       
    cursor.execute("SELECT * FROM locais")
    form.computadores_c_localizacao_combo.clear()
    for linha in cursor.fetchall():
        form.computadores_c_localizacao_combo.addItem(str(linha[1]))

    banco.close()
#alterar / excluir
def computadores_seleciona_item():
    tt = form.computadores_tabela.selectedItems()
    kk = form.computadores_tabela.row(tt[0])
    global comp_id
    comp_id = form.computadores_tabela.item(kk,0)
    comp_id = comp_id.text()
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    cursor.execute("SELECT * FROM computadores WHERE id = " + comp_id + ";")
    dados = cursor.fetchone()

    cursor.execute("SELECT id, nome FROM locais")
    form.computadores_a_localizacao_combo.clear()
    locais = cursor.fetchall()
    indice1 = 0
    
    for linha in locais:
        form.computadores_a_localizacao_combo.addItem(str(linha[1]))
        if linha[0] == dados[2]:
             form.computadores_a_localizacao_combo.setCurrentIndex(indice1)
        else:
            indice1 = indice1 + 1

    
    form.computadores_a_nome_txt.setText(dados[1])
    form.computadores_a_descricao_txt.setText(dados[3])
    form.computadores_a_serie_txt.setText(str(dados[4]))
    form.computadores_a_obs_txt.setText(str(dados[5]))
    banco.close()

     # habilita botoes a serem usados
    form.computadores_gravar_btn.setEnabled(False)
    form.computadores_cancelar_btn.setEnabled(True)
    form.computadores_incluir_btn.setEnabled(True)
    form.computadores_pesquisar_btn.setEnabled(True)
    if tipo_usuario == 1:
        form.computadores_alterar_btn.setEnabled(True)
        form.computadores_excluir_btn.setEnabled(True)
    elif tipo_usuario == 2:
        form.computadores_alterar_btn.setEnabled(False)
        form.computadores_excluir_btn.setEnabled(False)
    form.computadores_gravar_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    form.computadores_cancelar_btn.setStyleSheet("background-color: rgb(255, 255, 255)")
    form.computadores_incluir_btn.setStyleSheet("background-color: rgb(255, 255, 255);")
    form.computadores_pesquisar_btn.setStyleSheet("background-color: rgb(255, 255, 255);")
    form.computadores_alterar_btn.setStyleSheet("background-color: rgb(255, 255, 255)")
    form.computadores_excluir_btn.setStyleSheet("background-color: rgb(255, 255, 255)")
    form.stackedWidget.setCurrentWidget(form.computadores_page)
    form.stackedWidget_computadores.setCurrentWidget(form.computadores_alterar_page)
#pesquisar está na pagina principal

#controles página de pesquisa
def computadores_pesquisa_consulta_id():
    valor = form.computadores_p_id_txt.text()
    if valor != "" and valor.isnumeric():
        form.computadores_tabela.clearContents()
        form.computadores_tabela.setRowCount( 0)
        banco = sqlite3.connect('inventario.db')
        cursor = banco.cursor()
    
        cursor.execute('SELECT c.*, l.nome FROM computadores AS c INNER JOIN locais AS l ON c.localizacao = l.id WHERE c.id = ' + valor + ';')
        for linha in cursor.fetchall():
            rowPosition = form.computadores_tabela.rowCount()
            form.computadores_tabela.insertRow(rowPosition)
            form.computadores_tabela.setItem(rowPosition, 0, QTableWidgetItem(str(linha[0])))
            form.computadores_tabela.setItem(rowPosition, 1, QTableWidgetItem(str(linha[1])))
            form.computadores_tabela.setItem(rowPosition, 2, QTableWidgetItem(str(linha[3])))
            form.computadores_tabela.setItem(rowPosition, 3, QTableWidgetItem(str(linha[8])))
            form.computadores_tabela.setItem(rowPosition, 4, QTableWidgetItem(str(linha[4])))
            form.computadores_tabela.setItem(rowPosition, 5, QTableWidgetItem(str(linha[5])))
            
        banco.close()
def computadores_pesquisa_consulta_nome():
    valor = unidecode(form.computadores_p_nome_txt.text())
    if valor != "":
        form.computadores_tabela.clearContents()
        form.computadores_tabela.setRowCount( 0)
        banco = sqlite3.connect('inventario.db')
        cursor = banco.cursor()
     
        cursor.execute("SELECT c.*, l.nome FROM computadores AS c INNER JOIN locais AS l ON c.localizacao = l.id WHERE c.nome_acento LIKE '%" + valor + "%';")
        for linha in cursor.fetchall():
            rowPosition = form.computadores_tabela.rowCount()
            form.computadores_tabela.insertRow(rowPosition)
            form.computadores_tabela.setItem(rowPosition, 0, QTableWidgetItem(str(linha[0])))
            form.computadores_tabela.setItem(rowPosition, 1, QTableWidgetItem(str(linha[1])))
            form.computadores_tabela.setItem(rowPosition, 2, QTableWidgetItem(str(linha[3])))
            form.computadores_tabela.setItem(rowPosition, 3, QTableWidgetItem(str(linha[8])))
            form.computadores_tabela.setItem(rowPosition, 4, QTableWidgetItem(str(linha[4])))
            form.computadores_tabela.setItem(rowPosition, 5, QTableWidgetItem(str(linha[5])))
         
        banco.close()
def computadores_pesquisa_consulta_descricao():
    valor = unidecode(form.itens_p_descricao_txt.text())
    if valor != "":
        form.computadores_tabela.clearContents()
        form.computadores_tabela.setRowCount( 0)
        banco = sqlite3.connect('inventario.db')
        cursor = banco.cursor()
     
        cursor.execute("SELECT c.*, l.nome FROM computadores AS c INNER JOIN locais AS l ON c.localizacao = l.id WHERE c.descricao_acento LIKE '%" + valor + "%';")
        for linha in cursor.fetchall():
            rowPosition = form.computadores_tabela.rowCount()
            form.computadores_tabela.insertRow(rowPosition)
            form.computadores_tabela.setItem(rowPosition, 0, QTableWidgetItem(str(linha[0])))
            form.computadores_tabela.setItem(rowPosition, 1, QTableWidgetItem(str(linha[1])))
            form.computadores_tabela.setItem(rowPosition, 2, QTableWidgetItem(str(linha[3])))
            form.computadores_tabela.setItem(rowPosition, 3, QTableWidgetItem(str(linha[8])))
            form.computadores_tabela.setItem(rowPosition, 4, QTableWidgetItem(str(linha[4])))
            form.computadores_tabela.setItem(rowPosition, 5, QTableWidgetItem(str(linha[5])))
         
        banco.close()
def computadores_pesquisa_consulta_local():
    valor = form.computadores_p_localizacao_combo.currentText()
    if valor != "":
        form.computadores_tabela.clearContents()
        form.computadores_tabela.setRowCount( 0)
        banco = sqlite3.connect('inventario.db')
        cursor = banco.cursor()
     
        cursor.execute("SELECT c.*, l.nome FROM computadores AS c INNER JOIN locais AS l ON c.localizacao = l.id WHERE l.nome ='" + valor + "';")
        
        for linha in cursor.fetchall():
            rowPosition = form.computadores_tabela.rowCount()
            form.computadores_tabela.insertRow(rowPosition)
            form.computadores_tabela.setItem(rowPosition, 0, QTableWidgetItem(str(linha[0])))
            form.computadores_tabela.setItem(rowPosition, 1, QTableWidgetItem(str(linha[1])))
            form.computadores_tabela.setItem(rowPosition, 2, QTableWidgetItem(str(linha[3])))
            form.computadores_tabela.setItem(rowPosition, 3, QTableWidgetItem(str(linha[8])))
            form.computadores_tabela.setItem(rowPosition, 4, QTableWidgetItem(str(linha[4])))
            form.computadores_tabela.setItem(rowPosition, 5, QTableWidgetItem(str(linha[5])))
         
        banco.close()
def filtros_computadores():
    cod = form.rb_id_computadores
    nome = form.rb_nome_computadores
    descr = form.rb_descricao_computadores
    local = form.rb_localizacao_computadores
    
    if cod.isChecked():
        
        form.computadores_p_id_txt.setReadOnly(False)
        form.computadores_p_nome_txt.setReadOnly(True)
        form.computadores_p_nome_txt.setText('')
        form.computadores_p_descricao_txt.setReadOnly(True)
        form.computadores_p_descricao_txt.setText('')
        form.computadores_p_localizacao_combo.setEnabled(False)
        form.computadores_p_localizacao_combo.setCurrentIndex(-1)
            
        

    elif nome.isChecked():

        form.computadores_p_id_txt.setReadOnly(True)
        form.computadores_p_nome_txt.setReadOnly(False)
        form.computadores_p_id_txt.setText('')
        form.computadores_p_descricao_txt.setReadOnly(True)
        form.computadores_p_descricao_txt.setText('')
        form.computadores_p_localizacao_combo.setEnabled(False)
        form.computadores_p_localizacao_combo.setCurrentIndex(-1)

    elif descr.isChecked():

        form.computadores_p_id_txt.setReadOnly(True)
        form.computadores_p_nome_txt.setReadOnly(True)
        form.computadores_p_nome_txt.setText('')
        form.computadores_p_descricao_txt.setReadOnly(False)
        form.computadores_p_id_txt.setText('')
        form.computadores_p_localizacao_combo.setEnabled(False)
        form.computadores_p_localizacao_combo.setCurrentIndex(-1)

    elif local.isChecked():

        form.computadores_p_id_txt.setReadOnly(True)
        form.computadores_p_nome_txt.setReadOnly(True)
        form.computadores_p_nome_txt.setText('')
        form.computadores_p_descricao_txt.setReadOnly(True)
        form.computadores_p_descricao_txt.setText('')
        form.computadores_p_localizacao_combo.setEnabled(True)
        form.computadores_p_id_txt.setText('')


#controles página incluir
def computadores_cadastrar():
    
    nome = form.computadores_c_nome_txt.text()
    descricao = form.computadores_c_descricao_txt.text()
    local = form.computadores_c_localizacao_combo.currentText()
    nome_acento = unidecode(nome)
    descricao_acento = unidecode(descricao)
    serie = form.computadores_c_serie_txt.text()
    obs = form.computadores_c_obs_txt.text()
    sql = ""
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()

    if nome == '':
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
        msg.setText("Erro")
        msg.setInformativeText('Nome não pode ficar em branco.')
        msg.setWindowTitle("Erro")
        msg.exec_()
    else:
    
        cursor.execute("SELECT id FROM locais WHERE nome = '" + local + "';")
        pega = cursor.fetchone()
        if not pega:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
            msg.setText("Erro")
            msg.setInformativeText('Informe a localização do Item')
            msg.setWindowTitle("Erro")
            msg.exec_()
        else:
            pega = str(pega[0])
            sql = "INSERT INTO computadores (nome, descricao, localizacao, nome_acento, descricao_acento, serie, obs) VALUES('"+ nome +"', '"+ descricao +"', "+ pega +", '"+ nome_acento +"', '"+ descricao_acento +"', '"+ serie +"', '"+ obs +"');"
            cursor.execute(sql)
            banco.commit()
            cursor.execute("SELECT id FROM computadores WHERE nome = '"+ nome +"';")
            gg = cursor.fetchall()
            codigo = gg[(-1)]
            agora = datetime.now()
            agora = str(agora)[:19]
            cursor.execute("INSERT INTO log (tabela, nome, codigo, operacao, data, usuario) VALUES ('2','"+ nome +"', "+ str(codigo[0]) +", 1, '"+ agora +"',"+ str(usuario_logado) +");")
            banco.commit()
   
            banco.close()
            computadores_pesquisa()

#controles página alterar/excluir
def computadores_exclui():

    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    cursor.execute("select id FROM componentes WHERE computador = '" + comp_id + "';")
    ve = cursor.fetchall()
    if ve:
        msgBox = QMessageBox()
        msgBox.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
        msgBox.setWindowTitle("Registro Vinculado")
        msgBox.setText("Você não pode excluir este registro, pois ele está vinculado a outros registros no banco de dados.")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()
        
    else:

        msgBox = QMessageBox()
        msgBox.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
        msgBox.setWindowTitle("Confirmação de Exclusão")
        msgBox.setText("Você realmente quer excluir este registro?")
        msgBox.setStandardButtons(QMessageBox.Yes)
        msgBox.addButton(QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.No)
        if(msgBox.exec() == QMessageBox.Yes):
            banco = sqlite3.connect('inventario.db')
            cursor = banco.cursor()
            cursor.execute("SELECT nome FROM computadores WHERE id = "+ comp_id +";")
            nome = cursor.fetchone()
            nome = nome[0]
            cursor.execute("DELETE FROM computadores WHERE id = "+ comp_id +";")
            
            banco.commit()
            agora = datetime.now()
            agora = str(agora)[:19]
            cursor.execute("INSERT INTO log (tabela, nome, codigo, operacao, data, usuario) VALUES ('2','"+ nome +"', "+ comp_id +", 3, '"+ agora +"',"+ str(usuario_logado) +");")
            banco.commit()
            banco.close()
            computadores_pesquisa()
def computadores_alterar():
    nome = form.computadores_a_nome_txt.text()
    descricao = form.computadores_a_descricao_txt.text()
    local = form.computadores_a_localizacao_combo.currentText()
    nome_acento = unidecode(nome)
    descricao_acento = unidecode(descricao)
    serie = form.computadores_a_serie_txt.text()
    obs = form.computadores_a_obs_txt.text()

    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    sql = ""    
    if nome == '':
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
        msg.setText("Erro")
        msg.setInformativeText('Nome não pode ficar em branco.')
        msg.setWindowTitle("Erro")
        msg.exec_()
    else:    
        cursor.execute("SELECT id FROM locais WHERE nome = '" + local + "';")
        pega = cursor.fetchone()
        if not pega:
            msg = QMessageBox()
            msg.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Erro")
            msg.setInformativeText('Informe a localização do item')
            msg.setWindowTitle("Erro")
            msg.exec_()
        else:
            pega = str(pega[0])
            sql = "UPDATE computadores SET nome = '"+ nome +"', descricao = '"+ descricao +"', localizacao = "+ str(pega) +", nome_acento = '"+ nome_acento +"', descricao_acento = '"+ descricao_acento +"', serie = '"+ serie +"', obs = '"+ obs +"' WHERE id = '" + comp_id + "';"

            cursor.execute("SELECT * FROM computadores WHERE id = '" + comp_id + "';")
            compara = cursor.fetchone()
            
                
            msgBox = QMessageBox()
            msgBox.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
            msgBox.setWindowTitle("Confirmação de Alteração")
            msgBox.setText("Você realmente quer alterar este registro?")
            msgBox.setStandardButtons(QMessageBox.Yes)
            msgBox.addButton(QMessageBox.No)
            msgBox.setDefaultButton(QMessageBox.No)
            if(msgBox.exec() == QMessageBox.Yes):
                cursor.execute(sql)
                banco.commit()
                cursor.execute("UPDATE componentes SET localizacao = "+str(pega)+" WHERE computador = '"+ comp_id + "';")
                banco.commit()
                agora = datetime.now()
                agora = str(agora)[:19]
                cursor.execute("INSERT INTO log (tabela, nome, codigo, operacao, data, usuario) VALUES ('2','"+ nome +"', "+ comp_id +", 2, '"+ agora +"',"+ str(usuario_logado) +");")
                banco.commit()
                
                cursor.execute("SELECT id FROM log;")
                pega_log = cursor.fetchall()
                pega_id_log = pega_log[(-1)]
                alt = []
                if compara[1] != nome:
                    alt.append(['Nome', compara[1], nome, pega_id_log[0]])
                
                if str(compara[3]) != descricao:
                    alt.append(['Descrição', compara[3], descricao, pega_id_log[0]])
                
                if str(compara[2]) != pega:
                    alt.append(['Localização', compara[2], pega, pega_id_log[0]])
                        
                if compara[6] != serie:
                    alt.append(['Serial', compara[6], serie, pega_id_log[0]])
                
                if compara[7] != obs:
                    alt.append(['Observações', compara[7], obs, pega_id_log[0]])
                
                
                for linha in alt:
                    cursor.execute("INSERT INTO alteracoes(campo, ant, atual, altera_id) VALUES('"+ str(linha[0]) +"', '"+ str(linha[1]) +"', '"+ str(linha[2]) +"', '"+ str(linha[3]) +"');")
                    banco.commit()
            
                banco.close()
                computadores_pesquisa()
    










#funções locais
# chamar paginas
#incluir
def locais_incluir_page():
    # habilita botoes a serem usados
    form.locais_gravar_btn.setEnabled(True)
    form.locais_cancelar_btn.setEnabled(True)
    form.locais_incluir_btn.setEnabled(False)
    form.locais_pesquisar_btn.setEnabled(False)
    form.locais_alterar_btn.setEnabled(False)
    form.locais_excluir_btn.setEnabled(False)
    form.locais_gravar_btn.setStyleSheet("background-color: rgb(255, 255, 255)")
    form.locais_cancelar_btn.setStyleSheet("background-color: rgb(255, 255, 255)")
    form.locais_incluir_btn.setStyleSheet("background-color: rgb(58, 58, 58);")
    form.locais_pesquisar_btn.setStyleSheet("background-color: rgb(58, 58, 58);")
    form.locais_alterar_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    form.locais_excluir_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    

    
    form.stackedWidget_locais.setCurrentWidget(form.locais_cadastrar_page)
    
#alterar / excluir
def locais_seleciona_item():
    tt = form.locais_tabela.selectedItems()
    kk = form.locais_tabela.row(tt[0])
    global locais_id
    locais_id = form.locais_tabela.item(kk,0)
    locais_id = locais_id.text()
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    cursor.execute("SELECT * FROM locais WHERE id = " + locais_id + ";")
    dados = cursor.fetchone()
    form.locais_a_nome_txt.setText(dados[1])
    form.locais_a_descricao_txt.setText(dados[2])
    form.locais_a_referencia_txt.setText(str(dados[3]))
   
    banco.close()

     # habilita botoes a serem usados
    form.locais_gravar_btn.setEnabled(False)
    form.locais_cancelar_btn.setEnabled(True)
    form.locais_incluir_btn.setEnabled(True)
    form.locais_pesquisar_btn.setEnabled(True)
    if tipo_usuario == 1:
        form.locais_alterar_btn.setEnabled(True)
        form.locais_excluir_btn.setEnabled(True)
    elif tipo_usuario == 2:
        form.locais_alterar_btn.setEnabled(False)
        form.locais_excluir_btn.setEnabled(False)
    
    form.locais_gravar_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    form.locais_cancelar_btn.setStyleSheet("background-color: rgb(255, 255, 255)")
    form.locais_incluir_btn.setStyleSheet("background-color: rgb(255, 255, 255);")
    form.locais_pesquisar_btn.setStyleSheet("background-color: rgb(255, 255, 255);")
    form.locais_alterar_btn.setStyleSheet("background-color: rgb(255, 255, 255)")
    form.locais_excluir_btn.setStyleSheet("background-color: rgb(255, 255, 255)")
    form.stackedWidget.setCurrentWidget(form.locais_page)
    form.stackedWidget_locais.setCurrentWidget(form.locais_alterar_page)

#pesquisar está na pagina principal

#controles página de pesquisa
def locais_pesquisa_consulta_id():
    valor = form.locais_p_id_txt.text()
    if valor != "" and valor.isnumeric():
        form.locais_tabela.clearContents()
        form.locais_tabela.setRowCount( 0)
        banco = sqlite3.connect('inventario.db')
        cursor = banco.cursor()
    
        cursor.execute('SELECT * FROM locais WHERE id = ' + valor + ';')
        for linha in cursor.fetchall():
            rowPosition = form.locais_tabela.rowCount()
            form.locais_tabela.insertRow(rowPosition)
            form.locais_tabela.setItem(rowPosition, 0, QTableWidgetItem(str(linha[0])))
            form.locais_tabela.setItem(rowPosition, 1, QTableWidgetItem(str(linha[1])))
            form.locais_tabela.setItem(rowPosition, 2, QTableWidgetItem(str(linha[2])))
            form.locais_tabela.setItem(rowPosition, 3, QTableWidgetItem(str(linha[3])))
            
            
        banco.close()
def locais_pesquisa_consulta_nome():
    valor = unidecode(form.locais_p_nome_txt.text())
    if valor != "":
        form.locais_tabela.clearContents()
        form.locais_tabela.setRowCount( 0)
        banco = sqlite3.connect('inventario.db')
        cursor = banco.cursor()
     
        cursor.execute("SELECT * FROM locais WHERE nome_acento LIKE '%" + valor + "%';")
        for linha in cursor.fetchall():
            rowPosition = form.locais_tabela.rowCount()
            form.locais_tabela.insertRow(rowPosition)
            form.locais_tabela.setItem(rowPosition, 0, QTableWidgetItem(str(linha[0])))
            form.locais_tabela.setItem(rowPosition, 1, QTableWidgetItem(str(linha[1])))
            form.locais_tabela.setItem(rowPosition, 2, QTableWidgetItem(str(linha[3])))
            form.locais_tabela.setItem(rowPosition, 3, QTableWidgetItem(str(linha[4])))
            

         
        banco.close()
def locais_pesquisa_consulta_descricao():
    valor = unidecode(form.locais_p_descricao_txt.text())
    if valor != "":
        form.locais_tabela.clearContents()
        form.locais_tabela.setRowCount( 0)
        banco = sqlite3.connect('inventario.db')
        cursor = banco.cursor()
     
        cursor.execute("SELECT * FROM locais WHERE descricao_acento LIKE '%" + valor + "%';")
        for linha in cursor.fetchall():
            rowPosition = form.locais_tabela.rowCount()
            form.locais_tabela.insertRow(rowPosition)
            form.locais_tabela.setItem(rowPosition, 0, QTableWidgetItem(str(linha[0])))
            form.locais_tabela.setItem(rowPosition, 1, QTableWidgetItem(str(linha[1])))
            form.locais_tabela.setItem(rowPosition, 2, QTableWidgetItem(str(linha[2])))
            form.locais_tabela.setItem(rowPosition, 3, QTableWidgetItem(str(linha[3])))

            
         
        banco.close()
def locais_pesquisa_consulta_referencia():
    valor = form.locais_p_referencia_txt.text()
    if valor != "":
        form.locais_tabela.clearContents()
        form.locais_tabela.setRowCount( 0)
        banco = sqlite3.connect('inventario.db')
        cursor = banco.cursor()
     
        cursor.execute("SELECT * FROM locais WHERE referencia_acento LIKE '%" + valor + "%';")
        
        for linha in cursor.fetchall():
            rowPosition = form.locais_tabela.rowCount()
            form.locais_tabela.insertRow(rowPosition)
            form.locais_tabela.setItem(rowPosition, 0, QTableWidgetItem(str(linha[0])))
            form.locais_tabela.setItem(rowPosition, 1, QTableWidgetItem(str(linha[1])))
            form.locais_tabela.setItem(rowPosition, 2, QTableWidgetItem(str(linha[2])))
            form.locais_tabela.setItem(rowPosition, 3, QTableWidgetItem(str(linha[3])))

            
         
        banco.close()
def filtros_locais():
    cod = form.rb_id_locais
    nome = form.rb_nome_locais
    descr = form.rb_descricao_locais
    ref = form.rb_referencia_locais
    
    if cod.isChecked():
        
        form.locais_p_id_txt.setReadOnly(False)
        form.locais_p_nome_txt.setReadOnly(True)
        form.locais_p_nome_txt.setText('')
        form.locais_p_descricao_txt.setReadOnly(True)
        form.locais_p_descricao_txt.setText('')
        form.locais_p_referencia_txt.setReadOnly(True)
        form.locais_p_referencia_txt.setText('')
        
            
        

    elif nome.isChecked():

        form.locais_p_id_txt.setReadOnly(True)
        form.locais_p_nome_txt.setReadOnly(False)
        form.locais_p_id_txt.setText('')
        form.locais_p_descricao_txt.setReadOnly(True)
        form.locais_p_descricao_txt.setText('')
        form.locais_p_referencia_txt.setReadOnly(True)
        form.locais_p_referencia_txt.setText('')

    elif descr.isChecked():

        form.locais_p_id_txt.setReadOnly(True)
        form.locais_p_nome_txt.setReadOnly(True)
        form.locais_p_nome_txt.setText('')
        form.locais_p_descricao_txt.setReadOnly(False)
        form.locais_p_id_txt.setText('')
        form.locais_p_referencia_txt.setReadOnly(True)
        form.locais_p_referencia_txt.setText('')

    elif ref.isChecked():

        form.locais_p_id_txt.setReadOnly(True)
        form.locais_p_nome_txt.setReadOnly(True)
        form.locais_p_nome_txt.setText('')
        form.locais_p_descricao_txt.setReadOnly(True)
        form.locais_p_descricao_txt.setText('')
        form.locais_p_referencia_txt.setReadOnly(False)
      
#controles página incluir
def locais_cadastrar():
    
    nome = form.locais_c_nome_txt.text()
    descricao = form.locais_c_descricao_txt.text()
    referencia = form.locais_c_referencia_txt.text()
    nome_acento = unidecode(nome)
    descricao_acento = unidecode(descricao)
    referencia_acento = unidecode(referencia)
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    if nome == '':
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
        msg.setText("Erro")
        msg.setInformativeText('Nome não pode ficar em branco.')
        msg.setWindowTitle("Erro")
        msg.exec_()
    else:
        sql = "INSERT INTO locais (nome, descricao, referencia, nome_acento, descricao_acento, referencia_acento) VALUES('"+ nome +"', '"+ descricao +"', '"+ referencia +"', '"+ nome_acento +"', '"+ descricao_acento +"', '"+ referencia_acento +"');"
        cursor.execute(sql)
        banco.commit()
        cursor.execute("SELECT id FROM locais WHERE nome = '"+ nome +"';")
        gg = cursor.fetchall()
        codigo = gg[(-1)]
        agora = datetime.now()
        agora = str(agora)[:19]
        cursor.execute("INSERT INTO log (tabela, nome, codigo, operacao, data, usuario) VALUES ('3','"+ nome +"', "+ str(codigo[0]) +", 1, '"+ agora +"',"+ str(usuario_logado) +");")
        banco.commit()
   
        banco.close()
        locais_pesquisa()


#controles página alterar/excluir
def locais_exclui():
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    cursor.execute("select id FROM componentes WHERE localizacao = '" + locais_id + "';")
    ve = cursor.fetchall()
    if ve:
        msgBox = QMessageBox()
        msgBox.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
        msgBox.setWindowTitle("Registro Vinculado")
        msgBox.setText("Você não pode excluir este registro, pois ele está vinculado a outros registros no banco de dados.")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()
        
    else:
        msgBox = QMessageBox()
        msgBox.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
        msgBox.setWindowTitle("Confirmação de Exclusão")
        msgBox.setText("Você realmente quer excluir este registro?")
        msgBox.setStandardButtons(QMessageBox.Yes)
        msgBox.addButton(QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.No)
        if(msgBox.exec() == QMessageBox.Yes):
            banco = sqlite3.connect('inventario.db')
            cursor = banco.cursor()
            cursor.execute("SELECT nome FROM locais WHERE id = "+ locais_id +";")
            nome = cursor.fetchone()
            nome = nome[0]
            cursor.execute("DELETE FROM locais WHERE id = '" + locais_id + "';")
        
            banco.commit()
            agora = datetime.now()
            agora = str(agora)[:19]
            cursor.execute("INSERT INTO log (tabela, nome, codigo, operacao, data, usuario) VALUES ('3','"+ nome +"', "+ locais_id +", 3, '"+ agora +"',"+ str(usuario_logado) +");")
            banco.commit()
            banco.close()
            locais_pesquisa()

def locais_alterar():
    nome = form.locais_a_nome_txt.text()
    descricao = form.locais_a_descricao_txt.text()
    referencia = form.locais_a_referencia_txt.text()
    nome_acento = unidecode(nome)
    descricao_acento = unidecode(descricao)
    referencia_acento = unidecode(referencia)

    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    sql = "UPDATE locais SET nome = '"+ nome +"', descricao = '"+ descricao +"', referencia = '"+ referencia +"', nome_acento = '"+ nome_acento +"', descricao_acento = '"+ descricao_acento +"', referencia_acento = '"+ referencia_acento +"' WHERE id = '" + locais_id + "';"
    if nome == '':
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
        msg.setText("Erro")
        msg.setInformativeText('Nome não pode ficar em branco.')
        msg.setWindowTitle("Erro")
        msg.exec_()
    else:
        cursor.execute("SELECT * FROM locais WHERE id = '" + locais_id + "';")
        compara = cursor.fetchone()
        
        
            
        msgBox = QMessageBox()
        msgBox.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
        msgBox.setWindowTitle("Confirmação de Alteração")
        msgBox.setText("Você realmente quer alterar este registro?")
        msgBox.setStandardButtons(QMessageBox.Yes)
        msgBox.addButton(QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.No)
        if(msgBox.exec() == QMessageBox.Yes):
            cursor.execute(sql)

            banco.commit()
            agora = datetime.now()
            agora = str(agora)[:19]
            cursor.execute("INSERT INTO log (tabela, nome, codigo, operacao, data, usuario) VALUES ('3','"+ nome +"', "+ locais_id +", 2, '"+ agora +"',"+ str(usuario_logado) +");")
            banco.commit()

            cursor.execute("SELECT id FROM log;")
            pega_log = cursor.fetchall()
            pega_id_log = pega_log[(-1)]
            alt = []
            if compara[1] != nome:
                alt.append(['Nome', compara[1], nome, pega_id_log[0]])
            
            if str(compara[2]) != descricao:
                alt.append(['Descrição', compara[2], descricao, pega_id_log[0]])
            
            if str(compara[3]) != referencia:
                alt.append(['Referência', compara[3], referencia, pega_id_log[0]])
                    
                    
            
            for linha in alt:
                cursor.execute("INSERT INTO alteracoes(campo, ant, atual, altera_id) VALUES('"+ str(linha[0]) +"', '"+ str(linha[1]) +"', '"+ str(linha[2]) +"', '"+ str(linha[3]) +"');")
                banco.commit()

            banco.close()
            locais_pesquisa()










#funções categorias
# chamar paginas
#incluir
def categorias_incluir_page():
    # habilita botoes a serem usados
    form.categorias_gravar_btn.setEnabled(True)
    form.categorias_cancelar_btn.setEnabled(True)
    form.categorias_incluir_btn.setEnabled(False)
    form.categorias_pesquisar_btn.setEnabled(False)
    form.categorias_alterar_btn.setEnabled(False)
    form.categorias_excluir_btn.setEnabled(False)
    form.categorias_gravar_btn.setStyleSheet("background-color: rgb(255, 255, 255)")
    form.categorias_cancelar_btn.setStyleSheet("background-color: rgb(255, 255, 255)")
    form.categorias_incluir_btn.setStyleSheet("background-color: rgb(58, 58, 58);")
    form.categorias_pesquisar_btn.setStyleSheet("background-color: rgb(58, 58, 58);")
    form.categorias_alterar_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    form.categorias_excluir_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    

    
    form.stackedWidget_categorias.setCurrentWidget(form.categorias_cadastrar_page)
    
#alterar / excluir
def categorias_seleciona_item():
    tt = form.categorias_tabela.selectedItems()
    kk = form.categorias_tabela.row(tt[0])
    global categorias_id
    categorias_id = form.categorias_tabela.item(kk,0)
    categorias_id = categorias_id.text()
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    cursor.execute("SELECT * FROM categorias WHERE id = " + categorias_id + ";")
    dados = cursor.fetchone()
    form.categorias_a_nome_txt.setText(dados[1])
    form.categorias_a_descricao_txt.setText(dados[2])
   
    banco.close()

     # habilita botoes a serem usados
    form.categorias_gravar_btn.setEnabled(False)
    form.categorias_cancelar_btn.setEnabled(True)
    form.categorias_incluir_btn.setEnabled(True)
    form.categorias_pesquisar_btn.setEnabled(True)
    if tipo_usuario == 1:
        form.categorias_alterar_btn.setEnabled(True)
        form.categorias_excluir_btn.setEnabled(True)
    elif tipo_usuario == 2:
        form.categorias_alterar_btn.setEnabled(False)
        form.categorias_excluir_btn.setEnabled(False)
    
    form.categorias_gravar_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    form.categorias_cancelar_btn.setStyleSheet("background-color: rgb(255, 255, 255)")
    form.categorias_incluir_btn.setStyleSheet("background-color: rgb(255, 255, 255);")
    form.categorias_pesquisar_btn.setStyleSheet("background-color: rgb(255, 255, 255);")
    form.categorias_alterar_btn.setStyleSheet("background-color: rgb(255, 255, 255)")
    form.categorias_excluir_btn.setStyleSheet("background-color: rgb(255, 255, 255)")
    form.stackedWidget.setCurrentWidget(form.categorias_page)
    form.stackedWidget_categorias.setCurrentWidget(form.categorias_alterar_page)

#pesquisar está na pagina principal

#controles página de pesquisa
def categorias_pesquisa_consulta_id():
    valor = form.categorias_p_id_txt.text()
    if valor != "" and valor.isnumeric():
        form.categorias_tabela.clearContents()
        form.categorias_tabela.setRowCount( 0)
        banco = sqlite3.connect('inventario.db')
        cursor = banco.cursor()
    
        cursor.execute('SELECT * FROM categorias WHERE id = ' + valor + ';')
        for linha in cursor.fetchall():
            rowPosition = form.categorias_tabela.rowCount()
            form.categorias_tabela.insertRow(rowPosition)
            form.categorias_tabela.setItem(rowPosition, 0, QTableWidgetItem(str(linha[0])))
            form.categorias_tabela.setItem(rowPosition, 1, QTableWidgetItem(str(linha[1])))
            form.categorias_tabela.setItem(rowPosition, 2, QTableWidgetItem(str(linha[2])))
            
            
        banco.close()
def categorias_pesquisa_consulta_nome():
    valor = unidecode(form.categorias_p_nome_txt.text())
    if valor != "":
        form.categorias_tabela.clearContents()
        form.categorias_tabela.setRowCount( 0)
        banco = sqlite3.connect('inventario.db')
        cursor = banco.cursor()
     
        cursor.execute("SELECT * FROM categorias WHERE nome_acento LIKE '%" + valor + "%';")
        for linha in cursor.fetchall():
            rowPosition = form.categorias_tabela.rowCount()
            form.categorias_tabela.insertRow(rowPosition)
            form.categorias_tabela.setItem(rowPosition, 0, QTableWidgetItem(str(linha[0])))
            form.categorias_tabela.setItem(rowPosition, 1, QTableWidgetItem(str(linha[1])))
            form.categorias_tabela.setItem(rowPosition, 2, QTableWidgetItem(str(linha[3])))
                        

         
        banco.close()
def filtros_categorias():
    cod = form.rb_id_categorias
    nome = form.rb_nome_categorias
    
    if cod.isChecked():
        
        form.categorias_p_id_txt.setReadOnly(False)
        form.categorias_p_nome_txt.setReadOnly(True)
        form.categorias_p_nome_txt.setText('')
        
        
            
        

    elif nome.isChecked():

        form.categorias_p_id_txt.setReadOnly(True)
        form.categorias_p_nome_txt.setReadOnly(False)
        form.categorias_p_id_txt.setText('')
        
    
      
#controles página incluir
def categorias_cadastrar():
    
    nome = form.categorias_c_nome_txt.text()
    descricao = form.categorias_c_descricao_txt.text()
    nome_acento = unidecode(nome)
    descricao_acento = unidecode(descricao)
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    sql = "INSERT INTO categorias (nome, descricao, nome_acento, descricao_acento) VALUES('"+ nome +"', '"+ descricao +"', '"+ nome_acento +"', '"+ descricao_acento +"');"
    if nome == '':
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
        msg.setText("Erro")
        msg.setInformativeText('Nome não pode ficar em branco.')
        msg.setWindowTitle("Erro")
        msg.exec_()
    else:
        cursor.execute(sql)
        banco.commit()
        cursor.execute("SELECT id FROM categorias WHERE nome = '"+ nome +"';")
        gg = cursor.fetchall()
        codigo = gg[(-1)]
        agora = datetime.now()
        agora = str(agora)[:19]
        cursor.execute("INSERT INTO log (tabela, nome, codigo, operacao, data, usuario) VALUES ('4','"+ nome +"', "+ str(codigo[0]) +", 1, '"+ agora +"',"+ str(usuario_logado) +");")
        banco.commit()
   
        banco.close()
        categorias_pesquisa()

#controles página alterar/excluir
def categorias_exclui():

    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    cursor.execute("select id FROM componentes WHERE categoria = '" + categorias_id + "';")
    ve = cursor.fetchall()
    if ve:
        msgBox = QMessageBox()
        msgBox.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
        msgBox.setWindowTitle("Registro Vinculado")
        msgBox.setText("Você não pode excluir este registro, pois ele está vinculado a outros registros no banco de dados.")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()
        
    else:
    
     
        msgBox = QMessageBox()
        msgBox.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
        msgBox.setWindowTitle("Confirmação de Exclusão")
        msgBox.setText("Você realmente quer excluir este registro?")
        msgBox.setStandardButtons(QMessageBox.Yes)
        msgBox.addButton(QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.No)
        if(msgBox.exec() == QMessageBox.Yes):
            banco = sqlite3.connect('inventario.db')
            cursor = banco.cursor()
            cursor.execute("SELECT nome FROM categorias WHERE id = "+ categorias_id +";")
            nome = cursor.fetchone()
            nome = nome[0]
            cursor.execute("DELETE FROM categorias WHERE id = '" + categorias_id + "';")
            
            banco.commit()
            agora = datetime.now()
            agora = str(agora)[:19]
            cursor.execute("INSERT INTO log (tabela, nome, codigo, operacao, data, usuario) VALUES ('4','"+ nome +"', "+ categorias_id +", 3, '"+ agora +"',"+ str(usuario_logado) +");")
            banco.commit()
            banco.close()
            categorias_pesquisa()

def categorias_alterar():
    nome = form.categorias_a_nome_txt.text()
    descricao = form.categorias_a_descricao_txt.text()
    nome_acento = unidecode(nome)
    descricao_acento = unidecode(descricao)
    

    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    sql = "UPDATE categorias SET nome = '"+ nome +"', descricao = '"+ descricao +"',  nome_acento = '"+ nome_acento +"', descricao_acento = '"+ descricao_acento +"' WHERE id = '" + categorias_id + "';"
    if nome == '':
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
        msg.setText("Erro")
        msg.setInformativeText('Nome não pode ficar em branco.')
        msg.setWindowTitle("Erro")
        msg.exec_()
    else:
        cursor.execute("SELECT * FROM categorias WHERE id = '" + categorias_id + "';")
        compara = cursor.fetchone()
        
            
        msgBox = QMessageBox()
        msgBox.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
        msgBox.setWindowTitle("Confirmação de Alteração")
        msgBox.setText("Você realmente quer alterar este registro?")
        msgBox.setStandardButtons(QMessageBox.Yes)
        msgBox.addButton(QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.No)
        if(msgBox.exec() == QMessageBox.Yes):
            cursor.execute(sql)

            banco.commit()
            agora = datetime.now()
            agora = str(agora)[:19]
            cursor.execute("INSERT INTO log (tabela, nome, codigo, operacao, data, usuario) VALUES ('4','"+ nome +"', "+ categorias_id +", 2, '"+ agora +"',"+ str(usuario_logado) +");")
            banco.commit()
        
            cursor.execute("SELECT id FROM log;")
            pega_log = cursor.fetchall()
            pega_id_log = pega_log[(-1)]
            alt = []
            if compara[1] != nome:
                alt.append(['Nome', compara[1], nome, pega_id_log[0]])
            
            if str(compara[2]) != descricao:
                alt.append(['Descrição', compara[2], descricao, pega_id_log[0]])
                    
            
            for linha in alt:
                cursor.execute("INSERT INTO alteracoes(campo, ant, atual, altera_id) VALUES('"+ str(linha[0]) +"', '"+ str(linha[1]) +"', '"+ str(linha[2]) +"', '"+ str(linha[3]) +"');")
                banco.commit()
    
            banco.close()
            categorias_pesquisa()










#funções usuarios
# chamar paginas
#incluir
def usuarios_incluir_page():
    # habilita botoes a serem usados
    form.usuarios_gravar_btn.setEnabled(True)
    form.usuarios_cancelar_btn.setEnabled(True)
    form.usuarios_incluir_btn.setEnabled(False)
    form.usuarios_pesquisar_btn.setEnabled(False)
    form.usuarios_alterar_btn.setEnabled(False)
    form.usuarios_excluir_btn.setEnabled(False)
    form.usuarios_gravar_btn.setStyleSheet("background-color: rgb(255, 255, 255)")
    form.usuarios_cancelar_btn.setStyleSheet("background-color: rgb(255, 255, 255)")
    form.usuarios_incluir_btn.setStyleSheet("background-color: rgb(58, 58, 58);")
    form.usuarios_pesquisar_btn.setStyleSheet("background-color: rgb(58, 58, 58);")
    form.usuarios_alterar_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    form.usuarios_excluir_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    

    
    form.stackedWidget_usuarios.setCurrentWidget(form.usuarios_cadastrar_page)
    
#alterar / excluir
def usuarios_seleciona_item():
    tt = form.usuarios_tabela.selectedItems()
    kk = form.usuarios_tabela.row(tt[0])
    global usuarios_id
    usuarios_id = form.usuarios_tabela.item(kk,0)
    usuarios_id = usuarios_id.text()
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = " + usuarios_id + ";")
    dados = cursor.fetchone()
    form.usuarios_a_nome_txt.setText(dados[1])
    form.usuarios_a_username_txt.setText(dados[2])
    if dados[4] == 1:
        form.usuarios_a_tipo_combo.setCurrentIndex(0)
    elif dados[4] == 2:
        form.usuarios_a_tipo_combo.setCurrentIndex(1)
    form.usuarios_a_senha_txt.setEchoMode(QtWidgets.QLineEdit.Password)
    form.usuarios_a_senha_txt.setText(dados[3])
    banco.close()

     # habilita botoes a serem usados
    form.usuarios_gravar_btn.setEnabled(False)
    form.usuarios_cancelar_btn.setEnabled(True)
    form.usuarios_incluir_btn.setEnabled(True)
    form.usuarios_pesquisar_btn.setEnabled(True)
    if tipo_usuario == 1:
        form.usuarios_alterar_btn.setEnabled(True)
        form.usuarios_excluir_btn.setEnabled(True)
    elif tipo_usuario == 2:
        form.usuarios_alterar_btn.setEnabled(False)
        form.usuarios_excluir_btn.setEnabled(False)
    
    form.usuarios_gravar_btn.setStyleSheet("background-color: rgb(58, 58, 58)")
    form.usuarios_cancelar_btn.setStyleSheet("background-color: rgb(255, 255, 255)")
    form.usuarios_incluir_btn.setStyleSheet("background-color: rgb(255, 255, 255);")
    form.usuarios_pesquisar_btn.setStyleSheet("background-color: rgb(255, 255, 255);")
    form.usuarios_alterar_btn.setStyleSheet("background-color: rgb(255, 255, 255)")
    form.usuarios_excluir_btn.setStyleSheet("background-color: rgb(255, 255, 255)")
    form.stackedWidget.setCurrentWidget(form.usuarios_page)
    form.stackedWidget_usuarios.setCurrentWidget(form.usuarios_alterar_page)

#pesquisar está na pagina principal

#controles página de pesquisa
def usuarios_pesquisa_consulta_id():
    valor = form.usuarios_p_id_txt.text()
    if valor != "" and valor.isnumeric():
        form.usuarios_tabela.clearContents()
        form.usuarios_tabela.setRowCount( 0)
        banco = sqlite3.connect('inventario.db')
        cursor = banco.cursor()
    
        cursor.execute('SELECT * FROM usuarios WHERE id = ' + valor + ';')
        for linha in cursor.fetchall():
            rowPosition = form.usuarios_tabela.rowCount()
            form.usuarios_tabela.insertRow(rowPosition)
            form.usuarios_tabela.setItem(rowPosition, 0, QTableWidgetItem(str(linha[0])))
            form.usuarios_tabela.setItem(rowPosition, 1, QTableWidgetItem(str(linha[1])))
            form.usuarios_tabela.setItem(rowPosition, 2, QTableWidgetItem(str(linha[2])))
            if linha[4] == 1:
                form.usuarios_tabela.setItem(rowPosition, 3, QTableWidgetItem("Administrador"))
            if linha[4] == 2:
                form.usuarios_tabela.setItem(rowPosition, 3, QTableWidgetItem("Usuário"))
           
            
                        
            
        banco.close()

def usuarios_pesquisa_consulta_nome():
    valor = unidecode(form.usuarios_p_nome_txt.text())
    if valor != "":
        form.usuarios_tabela.clearContents()
        form.usuarios_tabela.setRowCount( 0)
        banco = sqlite3.connect('inventario.db')
        cursor = banco.cursor()
     
        cursor.execute("SELECT * FROM usuarios WHERE nome_acento LIKE '%" + valor + "%';")
        for linha in cursor.fetchall():
            rowPosition = form.usuarios_tabela.rowCount()
            form.usuarios_tabela.insertRow(rowPosition)
            form.usuarios_tabela.setItem(rowPosition, 0, QTableWidgetItem(str(linha[0])))
            form.usuarios_tabela.setItem(rowPosition, 1, QTableWidgetItem(str(linha[1])))
            form.usuarios_tabela.setItem(rowPosition, 2, QTableWidgetItem(str(linha[3])))
            if linha[4] == 1:
                form.usuarios_tabela.setItem(rowPosition, 3, QTableWidgetItem("Administrador"))
            if linha[4] == 2:
                form.usuarios_tabela.setItem(rowPosition, 3, QTableWidgetItem("Usuário"))
           
            

         
        banco.close()
def usuarios_pesquisa_consulta_username():
    valor = form.usuarios_p_username_txt.text()
    if valor != "":
        form.usuarios_tabela.clearContents()
        form.usuarios_tabela.setRowCount( 0)
        banco = sqlite3.connect('inventario.db')
        cursor = banco.cursor()
     
        cursor.execute("SELECT * FROM usuarios WHERE username LIKE '%" + valor + "%';")
        for linha in cursor.fetchall():
            rowPosition = form.usuarios_tabela.rowCount()
            form.usuarios_tabela.insertRow(rowPosition)
            form.usuarios_tabela.setItem(rowPosition, 0, QTableWidgetItem(str(linha[0])))
            form.usuarios_tabela.setItem(rowPosition, 1, QTableWidgetItem(str(linha[1])))
            form.usuarios_tabela.setItem(rowPosition, 2, QTableWidgetItem(str(linha[2])))
            if linha[4] == 1:
                form.usuarios_tabela.setItem(rowPosition, 3, QTableWidgetItem("Administrador"))
            if linha[4] == 2:
                form.usuarios_tabela.setItem(rowPosition, 3, QTableWidgetItem("Usuário"))
            
         
        banco.close()
def usuarios_pesquisa_consulta_tipo():
    valor = form.usuarios_p_tipo_combo.currentText()
    if valor == "Administrador":
        valor = 1
    if valor == "Usuário":
        valor = 2
   
    if valor != "":
        form.usuarios_tabela.clearContents()
        form.usuarios_tabela.setRowCount( 0)
        banco = sqlite3.connect('inventario.db')
        cursor = banco.cursor()
     
        cursor.execute("SELECT * FROM usuarios WHERE tipo = " + str(valor) + ";")
        
        for linha in cursor.fetchall():
            rowPosition = form.usuarios_tabela.rowCount()
            form.usuarios_tabela.insertRow(rowPosition)
            form.usuarios_tabela.setItem(rowPosition, 0, QTableWidgetItem(str(linha[0])))
            form.usuarios_tabela.setItem(rowPosition, 1, QTableWidgetItem(str(linha[1])))
            form.usuarios_tabela.setItem(rowPosition, 2, QTableWidgetItem(str(linha[2])))
            if linha[4] == 1:
                form.usuarios_tabela.setItem(rowPosition, 3, QTableWidgetItem("Administrador"))
            if linha[4] == 2:
                form.usuarios_tabela.setItem(rowPosition, 3, QTableWidgetItem("Usuário"))
            
         
        banco.close()
def filtros_usuarios():
    cod = form.rb_id_usuarios
    nome = form.rb_nome_usuarios
    username = form.rb_username_usuarios
    tipo = form.rb_tipo_usuarios
    
    if cod.isChecked():
        
        form.usuarios_p_id_txt.setReadOnly(False)
        form.usuarios_p_nome_txt.setReadOnly(True)
        form.usuarios_p_nome_txt.setText('')
        form.usuarios_p_username_txt.setReadOnly(True)
        form.usuarios_p_username_txt.setText('')
        form.usuarios_p_tipo_combo.setEnabled(False)
        form.usuarios_p_tipo_combo.setCurrentIndex(-1)
        
            
        

    elif nome.isChecked():

        form.usuarios_p_id_txt.setReadOnly(True)
        form.usuarios_p_nome_txt.setReadOnly(False)
        form.usuarios_p_id_txt.setText('')
        form.usuarios_p_username_txt.setReadOnly(True)
        form.usuarios_p_username_txt.setText('')
        form.usuarios_p_tipo_combo.setEnabled(False)
        form.usuarios_p_tipo_combo.setCurrentIndex(-1)

    elif username.isChecked():

        form.usuarios_p_id_txt.setReadOnly(True)
        form.usuarios_p_nome_txt.setReadOnly(True)
        form.usuarios_p_nome_txt.setText('')
        form.usuarios_p_username_txt.setReadOnly(False)
        form.usuarios_p_id_txt.setText('')
        form.usuarios_p_tipo_combo.setEnabled(False)
        form.usuarios_p_tipo_combo.setCurrentIndex(-1)

    elif tipo.isChecked():

        form.usuarios_p_id_txt.setReadOnly(True)
        form.usuarios_p_id_txt.setText('')
        form.usuarios_p_nome_txt.setReadOnly(True)
        form.usuarios_p_nome_txt.setText('')
        form.usuarios_p_username_txt.setReadOnly(True)
        form.usuarios_p_username_txt.setText('')
        form.usuarios_p_tipo_combo.setEnabled(True)
        
      
#controles página incluir
def usuarios_cadastrar():
    
    nome = form.usuarios_c_nome_txt.text()
    username = form.usuarios_c_username_txt.text()
    senha = form.usuarios_c_senha_txt.text()
    confirma = form.usuarios_c_confirma_txt.text()
    nome_acento = unidecode(nome)
    tipo = form.usuarios_c_tipo_combo.currentText()
    if tipo == 'Administrador':
        tipo = 1
    elif tipo == 'Usuário':
        tipo = 2
    if senha == confirma:
        if nome == '':
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
            msg.setText("Erro")
            msg.setInformativeText('Nome não pode ficar em branco.')
            msg.setWindowTitle("Erro")
            msg.exec_()
        else:
            banco = sqlite3.connect('inventario.db')
            cursor = banco.cursor()
            sql = "INSERT INTO usuarios (nome, username, tipo, nome_acento, senha) VALUES('"+ nome +"', '"+ username +"', "+ str(tipo) +", '"+ nome_acento +"', '"+ senha +"');"
            cursor.execute(sql)
            banco.commit()
            cursor.execute("SELECT id FROM usuarios WHERE nome = '"+ nome +"';")
            gg = cursor.fetchall()
            codigo = gg[(-1)]
            agora = datetime.now()
            agora = str(agora)[:19]
            cursor.execute("INSERT INTO log (tabela, nome, codigo, operacao, data, usuario) VALUES ('5','"+ nome +"', "+ str(codigo[0]) +", 1, '"+ agora +"',"+ str(usuario_logado) +");")
            banco.commit()
   
            banco.close()
            usuarios_pesquisa()
    else:
        msgBox = QMessageBox()
        msgBox.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
        msgBox.setWindowTitle("Confirmar senha")
        msgBox.setText("A senha não foi confirmada. Por favor verifique o campo de confirmação.")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()

    

#controles página alterar/excluir
def usuarios_exclui():
    
    msgBox = QMessageBox()
    msgBox.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
    msgBox.setWindowTitle("Confirmação de Exclusão")
    msgBox.setText("Você realmente quer excluir este registro?")
    msgBox.setStandardButtons(QMessageBox.Yes)
    msgBox.addButton(QMessageBox.No)
    msgBox.setDefaultButton(QMessageBox.No)
    if(msgBox.exec() == QMessageBox.Yes):
        banco = sqlite3.connect('inventario.db')
        cursor = banco.cursor()
        cursor.execute("SELECT nome FROM usuarios WHERE id = "+ usuarios_id +";")
        nome = cursor.fetchone()
        nome = nome[0]
        cursor.execute("DELETE FROM usuarios WHERE id = '" + usuarios_id + "';")
        
        banco.commit()
        agora = datetime.now()
        agora = str(agora)[:19]
        cursor.execute("INSERT INTO log (tabela, nome, codigo, operacao, data, usuario) VALUES ('5','"+ nome +"', "+ usuarios_id +", 3, '"+ agora +"',"+ str(usuario_logado) +");")
        banco.commit()
        banco.close()
        usuarios_pesquisa()

def usuarios_alterar():
    nome = form.usuarios_a_nome_txt.text()
    username = form.usuarios_a_username_txt.text()
    senha = form.usuarios_a_senha_txt.text()
    confirma = form.usuarios_a_confirma_txt.text()
    nome_acento = unidecode(nome)
    tipo = form.usuarios_a_tipo_combo.currentText()
    if tipo == 'Administrador':
        tipo = 1
    elif tipo == 'Usuário':
        tipo = 2
    if senha == confirma:
        if nome == '':
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
            msg.setText("Erro")
            msg.setInformativeText('Nome não pode ficar em branco.')
            msg.setWindowTitle("Erro")
            msg.exec_()
        else:
            banco = sqlite3.connect('inventario.db')
            cursor = banco.cursor()
            sql = "UPDATE usuarios SET nome = '"+ nome +"', username = '"+ username +"', tipo = "+ str(tipo) +", nome_acento = '"+ nome_acento +"', senha = '"+ senha +"' WHERE id = '" + usuarios_id + "';"

            cursor.execute("SELECT * FROM usuarios WHERE id = '" + usuarios_id + "';")
            compara = cursor.fetchone()
            
            msgBox = QMessageBox()
            msgBox.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
            msgBox.setWindowTitle("Confirmação de Alteração")
            msgBox.setText("Você realmente quer alterar este registro?")
            msgBox.setStandardButtons(QMessageBox.Yes)
            msgBox.addButton(QMessageBox.No)
            msgBox.setDefaultButton(QMessageBox.No)
            if(msgBox.exec() == QMessageBox.Yes):
                cursor.execute(sql)

                banco.commit()
                agora = datetime.now()
                agora = str(agora)[:19]
                cursor.execute("INSERT INTO log (tabela, nome, codigo, operacao, data, usuario) VALUES ('5','"+ nome +"', "+ usuarios_id +", 2, '"+ agora +"',"+ str(usuario_logado) +");")
                banco.commit()
                
                
                cursor.execute("SELECT id FROM log;")
                pega_log = cursor.fetchall()
                pega_id_log = pega_log[(-1)]
                alt = []
                if compara[1] != nome:
                    alt.append(['Nome', compara[1], nome, pega_id_log[0]])
                
                if str(compara[2]) != username:
                    alt.append(['Username', compara[2], username, pega_id_log[0]])

                if str(compara[3]) != tipo:
                    alt.append(['Tipo de usuário', compara[3], tipo, pega_id_log[0]])
                
                if str(compara[5]) != senha:
                    alt.append(['Senha', '***', '***', pega_id_log[0]])
                        
                
                for linha in alt:
                    cursor.execute("INSERT INTO alteracoes(campo, ant, atual, altera_id) VALUES('"+ str(linha[0]) +"', '"+ str(linha[1]) +"', '"+ str(linha[2]) +"', '"+ str(linha[3]) +"');")
                    banco.commit()

                banco.close()
                usuarios_pesquisa()
    else:
        msgBox = QMessageBox()
        msgBox.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
        msgBox.setWindowTitle("Confirmar senha")
        msgBox.setText("A senha não foi confirmada. Por favor verifique o campo de confirmação.")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()


#backup
def backup_db():
    banco = sqlite3.connect("inventario.db")
    diretorio = QFileDialog.getExistingDirectory(None, 'Escolha uma pasta para salvar o Backup')
    print(diretorio)
    bck = sqlite3.connect(diretorio + "/backup_controle_inventario.db")
    with bck:
        banco.backup(bck)
    bck.close()
    banco.close()

    msgBox = QMessageBox()
    msgBox.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
    msgBox.setWindowTitle("Confirmação de Backup")
    msgBox.setText("O backup do banco de dados foi realizado com sucesso. \nO nome do arquivo gerado é 'backup_controle_inventario.db'")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec()

#relatórios
def chama_listar_todos_itens():
    ordem = ''
    valor = ''
    if form.radioButton.isChecked():
        ordem = 'c.id'
    if form.radioButton_2.isChecked():
        ordem = 'c.nome'
    if form.radioButton_3.isChecked():
        ordem = 'l.nome'
    if form.checkBox.isChecked():
        valor = 2
    listar_todos_itens(ordem, valor)

def chama_listar_itens_integridade():
    ordem = ''
    valor = ''
    integridade = form.comboBox.currentText()
    if form.radioButton_5.isChecked():
        ordem = 'c.id'
    if form.radioButton_6.isChecked():
        ordem = 'c.nome'
    if form.radioButton_4.isChecked():
        ordem = 'l.nome'
    if form.checkBox_2.isChecked():
        valor = 2
    listar_itens_integridade(ordem, valor, integridade)

def chama_listar_itens_categoria():
    ordem = ''
    valor = ''
    cat = form.comboBox_2.currentText()
    if form.radioButton_7.isChecked():
        ordem = 'c.id'
    if form.radioButton_8.isChecked():
        ordem = 'c.nome'
    if form.radioButton_9.isChecked():
        ordem = 'l.nome'
    if form.checkBox_3.isChecked():
        valor = 2
    listar_itens_categoria(ordem, valor, cat)

def chama_listar_itens_local():
    ordem = ''
    valor = ''
    loc = form.comboBox_3.currentText()
    if form.radioButton_10.isChecked():
        ordem = 'c.id'
    if form.radioButton_11.isChecked():
        ordem = 'c.nome'
    if form.radioButton_12.isChecked():
        ordem = 'c.integridade'
    if form.checkBox_4.isChecked():
        valor = 2
    listar_itens_local(ordem, valor, loc)

def chama_listar_todos_computadores():
    ordem = ''
    valor = ''
    
    if form.radioButton_15.isChecked():
        ordem = ', c.id'
    if form.radioButton_13.isChecked():
        ordem = ', c.nome'
    if form.radioButton_14.isChecked():
        ordem = ', l.nome'
    if form.checkBox_5.isChecked():
        valor = 2
    listar_todos_computadores(ordem, valor)

def chama_listar_itens_computador():
    ordem = ''
    valor = ''
    cptd = form.comboBox_5.currentText()
    if form.radioButton_19.isChecked():
        ordem = 'c.id'
    if form.radioButton_18.isChecked():
        ordem = 'c.nome'
    
    if form.checkBox_6.isChecked():
        valor = 2
    listar_itens_computador(ordem, valor, cptd)

def chama_listar_local_computador():
    ordem = ''
    valor = ''
    loc = form.comboBox_4.currentText()
    if form.radioButton_19.isChecked():
        ordem = 'c.id'
    if form.radioButton_18.isChecked():
        ordem = 'c.nome'
    
    if form.checkBox_7.isChecked():
        valor = 2
    listar_local_computador(ordem, valor, loc)






def chama_logs():
    header = logs.lista.horizontalHeader()
    header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
    header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
    header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
    header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
    header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
    header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
    header.setSectionResizeMode(6, QtWidgets.QHeaderView.ResizeToContents)
    

    logs.lista.clearContents()
    logs.lista.setRowCount( 0)
    
    logs.lista.setHorizontalHeaderLabels(['ID','Tabela','Código','Nome','Operação','Data','Usuário'])
    logs.lista.horizontalHeader().setVisible(True)
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    cursor.execute('SELECT * FROM log ORDER BY data DESC;')
    for linha in cursor.fetchall():
        if linha[1] == 1:
            tab = 'Itens Gerais'
        if linha[1] == 2:
            tab = 'Itens compostos'
        if linha[1] == 3:
            tab = 'Locais'
        if linha[1] == 4:
            tab = 'Categorias'
        if linha[1] == 5:
            tab = 'Usuários'
        if linha[3] == 1:
            op = 'Inclusão'
        if linha[3] == 2:
            op = 'Alteração'
        if linha[3] == 3:
            op = 'Exclusão'

        rowPosition = logs.lista.rowCount()
        logs.lista.insertRow(rowPosition)
        logs.lista.setItem(rowPosition, 0, QTableWidgetItem(str(linha[0])))
        logs.lista.setItem(rowPosition, 1, QTableWidgetItem(str(tab)))
        logs.lista.setItem(rowPosition, 3, QTableWidgetItem(str(linha[2])[:30]))
        logs.lista.setItem(rowPosition, 4, QTableWidgetItem(str(op)))
        logs.lista.setItem(rowPosition, 5, QTableWidgetItem(str(linha[4])))
        logs.lista.setItem(rowPosition, 6, QTableWidgetItem(str(linha[5])))
        logs.lista.setItem(rowPosition, 2, QTableWidgetItem(str(linha[6])))
        
    
   
    banco.close()
    logs.stackedWidget.setCurrentWidget(logs.page)
    logs.show()
def fecha_logs():
    logs.close()
def logs_alteracoes():
    tt = logs.lista.selectedItems()
    kk = logs.lista.row(tt[0])
    
    pega_log = logs.lista.item(kk,0)
    pega_log = pega_log.text()
    
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    sql = "SELECT * FROM alteracoes WHERE altera_id = " + pega_log + ";"
    
    cursor.execute(sql)
    dados = cursor.fetchall()
    
    banco.close()
    
    if dados:
        
        header = logs.lista2.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        
        

        logs.lista2.clearContents()
        logs.lista2.setRowCount( 0)
        
        logs.lista2.setHorizontalHeaderLabels(['ID','campo','Anterior','Atual','ID_Item'])
        logs.lista2.horizontalHeader().setVisible(True)
       
        for linha in dados:
           

            rowPosition = logs.lista2.rowCount()
            logs.lista2.insertRow(rowPosition)
            logs.lista2.setItem(rowPosition, 0, QTableWidgetItem(str(linha[0])))
            
            logs.lista2.setItem(rowPosition, 1, QTableWidgetItem(str(linha[1])))
            
            logs.lista2.setItem(rowPosition, 2, QTableWidgetItem(str(linha[2])))
            logs.lista2.setItem(rowPosition, 3, QTableWidgetItem(str(linha[3])))
            logs.lista2.setItem(rowPosition, 4, QTableWidgetItem(str(linha[4])))
        logs.stackedWidget.setCurrentWidget(logs.page_2)

def volta_logs():
    logs.stackedWidget.setCurrentWidget(logs.page)  






# botões principais  
form.itens_gerais_btn.clicked.connect(itens_pesquisa)
form.computadores_btn.clicked.connect(computadores_pesquisa)
form.locais_btn.clicked.connect(locais_pesquisa)
form.home_btn.clicked.connect(home)
form.sair_btn.clicked.connect(fecha)
form.relatorios_btn.clicked.connect(relatorios_pesquisa)
form.categorias_btn.clicked.connect(categorias_pesquisa)
form.usuarios_btn.clicked.connect(usuarios_pesquisa)

# controles itens gerais
form.itens_gravar_btn.clicked.connect(itens_cadastrar_itens)
form.itens_cancelar_btn.clicked.connect(itens_pesquisa)
form.itens_incluir_btn.clicked.connect(itens_incluir_page)
form.itens_pesquisar_btn.clicked.connect(itens_pesquisa)
form.itens_alterar_btn.clicked.connect(itens_alterar)
form.itens_excluir_btn.clicked.connect(itens_exclui)

# controle tabela itens gerais
form.itens_tabela.doubleClicked.connect(itens_seleciona_item)

# controle radio button pesquisa itens gerais
form.rb_id_itens.clicked.connect(filtros_itens)
form.rb_nome_itens.clicked.connect(filtros_itens)
form.rb_categoria_itens.clicked.connect(filtros_itens)
form.rb_localizacao_itens.clicked.connect(filtros_itens)
form.rb_integridade_itens.clicked.connect(filtros_itens)
form.rb_computador_itens.clicked.connect(filtros_itens)

# controle campos de texto pesquisa itens gerais
form.itens_p_id_txt.textChanged[str].connect(itens_pesquisa_consulta_id)
form.itens_p_nome_txt.textChanged[str].connect(itens_pesquisa_consulta_nome)


# controle combo box pesquisa itens gerais
form.itens_combo_localizacao.activated.connect(itens_pesquisa_consulta_local)
form.itens_combo_computador.activated.connect(itens_pesquisa_consulta_computador)
form.itens_combo_integridade.activated.connect(itens_pesquisa_consulta_integridade)
form.itens_combo_categoria.activated.connect(itens_pesquisa_consulta_categoria)

# controle Incluir itens gerais
form.itens_c_checkbox.clicked.connect(itens_incluir_item_comp)
form.itens_c_computador_combo.activated.connect(itens_incluir_popula_combo_local)

# controle Alterar / Excluir itens gerais
form.itens_a_checkbox.clicked.connect(itens_alterar_item_comp)
form.itens_a_computador_combo.activated.connect(itens_alterar_popula_combo_local)



# controles Computadores
form.computadores_gravar_btn.clicked.connect(computadores_cadastrar)
form.computadores_cancelar_btn.clicked.connect(computadores_pesquisa)
form.computadores_incluir_btn.clicked.connect(computadores_incluir_page)
form.computadores_pesquisar_btn.clicked.connect(computadores_pesquisa)
form.computadores_alterar_btn.clicked.connect(computadores_alterar)
form.computadores_excluir_btn.clicked.connect(computadores_exclui)

# controle tabela computadores
form.computadores_tabela.doubleClicked.connect(computadores_seleciona_item)

# controle radio button pesquisa computadores
form.rb_id_computadores.clicked.connect(filtros_computadores)
form.rb_nome_computadores.clicked.connect(filtros_computadores)
form.rb_descricao_computadores.clicked.connect(filtros_computadores)
form.rb_localizacao_computadores.clicked.connect(filtros_computadores)

# controle campos de texto pesquisa Computadores
form.computadores_p_id_txt.textChanged[str].connect(computadores_pesquisa_consulta_id)
form.computadores_p_nome_txt.textChanged[str].connect(computadores_pesquisa_consulta_nome)
form.computadores_p_descricao_txt.textChanged[str].connect(computadores_pesquisa_consulta_descricao)

# controle combo box pesquisa computadores
form.computadores_p_localizacao_combo.activated.connect(computadores_pesquisa_consulta_local)










# controles Locais
form.locais_gravar_btn.clicked.connect(locais_cadastrar)
form.locais_cancelar_btn.clicked.connect(locais_pesquisa)
form.locais_incluir_btn.clicked.connect(locais_incluir_page)
form.locais_pesquisar_btn.clicked.connect(locais_pesquisa)
form.locais_alterar_btn.clicked.connect(locais_alterar)
form.locais_excluir_btn.clicked.connect(locais_exclui)

# controle tabela locais
form.locais_tabela.doubleClicked.connect(locais_seleciona_item)

# controle radio button pesquisa locais
form.rb_id_locais.clicked.connect(filtros_locais)
form.rb_nome_locais.clicked.connect(filtros_locais)
form.rb_descricao_locais.clicked.connect(filtros_locais)
form.rb_referencia_locais.clicked.connect(filtros_locais)

# controle campos de texto pesquisa Locais
form.locais_p_id_txt.textChanged[str].connect(locais_pesquisa_consulta_id)
form.locais_p_nome_txt.textChanged[str].connect(locais_pesquisa_consulta_nome)
form.locais_p_descricao_txt.textChanged[str].connect(locais_pesquisa_consulta_descricao)
form.locais_p_referencia_txt.textChanged[str].connect(locais_pesquisa_consulta_referencia)










# controles Categorias
form.categorias_gravar_btn.clicked.connect(categorias_cadastrar)
form.categorias_cancelar_btn.clicked.connect(categorias_pesquisa)
form.categorias_incluir_btn.clicked.connect(categorias_incluir_page)
form.categorias_pesquisar_btn.clicked.connect(categorias_pesquisa)
form.categorias_alterar_btn.clicked.connect(categorias_alterar)
form.categorias_excluir_btn.clicked.connect(categorias_exclui)

# controle tabela categorias
form.categorias_tabela.doubleClicked.connect(categorias_seleciona_item)

# controle radio button pesquisa categorias
form.rb_id_categorias.clicked.connect(filtros_categorias)
form.rb_nome_categorias.clicked.connect(filtros_categorias)

# controle campos de texto pesquisa Categorias
form.categorias_p_id_txt.textChanged[str].connect(categorias_pesquisa_consulta_id)
form.categorias_p_nome_txt.textChanged[str].connect(categorias_pesquisa_consulta_nome)










# controles Usuarios
form.usuarios_gravar_btn.clicked.connect(usuarios_cadastrar)
form.usuarios_cancelar_btn.clicked.connect(usuarios_pesquisa)
form.usuarios_incluir_btn.clicked.connect(usuarios_incluir_page)
form.usuarios_pesquisar_btn.clicked.connect(usuarios_pesquisa)
form.usuarios_alterar_btn.clicked.connect(usuarios_alterar)
form.usuarios_excluir_btn.clicked.connect(usuarios_exclui)

# controle tabela usuarios
form.usuarios_tabela.doubleClicked.connect(usuarios_seleciona_item)

# controle radio button pesquisa usuarios
form.rb_id_usuarios.clicked.connect(filtros_usuarios)
form.rb_nome_usuarios.clicked.connect(filtros_usuarios)
form.rb_username_usuarios.clicked.connect(filtros_usuarios)
form.rb_tipo_usuarios.clicked.connect(filtros_usuarios)

# controle campos de texto pesquisa Usuarios
form.usuarios_p_id_txt.textChanged[str].connect(usuarios_pesquisa_consulta_id)
form.usuarios_p_nome_txt.textChanged[str].connect(usuarios_pesquisa_consulta_nome)
form.usuarios_p_username_txt.textChanged[str].connect(usuarios_pesquisa_consulta_username)
form.usuarios_p_tipo_combo.activated.connect(usuarios_pesquisa_consulta_tipo)





#controle dos relatorios:
form.pushButton.clicked.connect(chama_listar_todos_itens)
form.pushButton_2.clicked.connect(chama_listar_itens_integridade)
form.pushButton_3.clicked.connect(chama_listar_itens_categoria)
form.pushButton_4.clicked.connect(chama_listar_itens_local)
form.pushButton_5.clicked.connect(chama_listar_todos_computadores)
form.pushButton_7.clicked.connect(chama_listar_itens_computador)
form.pushButton_6.clicked.connect(chama_listar_local_computador)

#controle dos logs
form.pushButton_8.clicked.connect(chama_logs)
logs.pushButton.clicked.connect(fecha_logs)
logs.lista.doubleClicked.connect(logs_alteracoes)
logs.pushButton_2.clicked.connect(volta_logs)






# controle para fazer o backup do banco de dados
form.backup_btn.clicked.connect(backup_db)

def verifica_empresa():
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    sql = "SELECT nome FROM empresa;"
    cursor.execute(sql)
    existe = cursor.fetchone()
    
    if existe:
        form.label.setText("Software licenciado para: " + str(existe[0]))
    else:
        
        text, ok = QInputDialog.getText(None ,"Nome da Empresa:", "Digite o nome da sua empresa")
        
        if (ok and text != ''):
            cursor.execute("INSERT INTO empresa (nome) VALUES ('"+text+"');")
            banco.commit()
    banco.close()




def loga():
    
    global tipo_usuario
    global usuario_logado
    usuario = form1.usuario_txt.text()
    senha = form1.senha_txt.text()
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    sql = "SELECT * FROM usuarios WHERE username = '"+ usuario +"';"
    cursor.execute(sql)
    dados = cursor.fetchone()
    banco.close()
    if dados:
        if senha == dados[3]:    
            tipo_usuario = dados[4]
            usuario_logado = dados[0]
            form.show()
            form1.close()
            verifica_empresa()
            
            if tipo_usuario == 1:
                form.frame_17.setVisible(True)
                form.frame_18.setVisible(True)
                  
            elif tipo_usuario == 2:
                form.frame_17.setVisible(False)
                form.frame_18.setVisible(False)
        else:
            msgBox = QMessageBox()
            msgBox.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
            msgBox.setWindowTitle("Erro")
            msgBox.setText("Senha Inválida!")
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec()
            

    else:
        msgBox = QMessageBox()
        msgBox.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
        msgBox.setWindowTitle("Erro")
        msgBox.setText("Usuário não encontrado")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()


def conf_primeiro_usuario():
    progresso.barra_progresso.setValue(95)
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    cursor.execute("SELECT nome from usuarios;")
    ve = cursor.fetchall()
    if len(ve) == 0:
        progresso.close()
        primeiro_usuario.show()
    else:
        progresso.close()
        form1.show()

def primeiro_usuario_grava():
    nome = primeiro_usuario.t1_inicio_nome.text()
    username = primeiro_usuario.t2_inicio_usuario.text()
    senha = primeiro_usuario.t3_inicio_senha.text()
    confirma = primeiro_usuario.t4_inicio_senha2.text()
    nome_acento = unidecode(nome)
    if senha == confirma:
        banco = sqlite3.connect('inventario.db')
        cursor = banco.cursor()
        sql = "INSERT INTO usuarios (nome, username, tipo, nome_acento, senha) VALUES('"+ nome +"', '"+ username +"', 1, '"+ nome_acento +"', '"+ senha +"');"
        cursor.execute(sql)
        banco.commit()
        banco.close()
        form1.show()
        primeiro_usuario.close()
    else:
        msgBox = QMessageBox()
        msgBox.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
        msgBox.setWindowTitle("Confirmar senha")
        msgBox.setText("A senha não foi confirmada. Por favor verifique o campo de confirmação.")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()
    




def closeEvent(self, event):
    msgBox = QMessageBox()
    msgBox.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
    msgBox.setWindowTitle("Encerrar sistema")
    msgBox.setText("Você realmente quer encerrar o sistema?")
    msgBox.setStandardButtons(QMessageBox.Yes)
    msgBox.addButton(QMessageBox.No)
    msgBox.setDefaultButton(QMessageBox.No)
    if(msgBox.exec() == QMessageBox.Yes):
        event.accept()
    else:
        event.ignore()


def pega_part_number():
    global part_number
    progresso.barra_progresso.setValue(50)
    file = 'c:/windows/setup_invent.txt'
    try:
        f = open(file, 'r')
        part_number = f.read()
        
        valida()
    except:
        if not f:
            msgBox = QMessageBox()
            msgBox.setWindowIcon(QtGui.QIcon('logo_inventario.png'))
            msgBox.setWindowTitle("Erro no sistema!")
            msgBox.setText("um arquivo necessário para a execução do sistema está ausente!\nContacte o Suporte.")
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec()
        
        


def valida():
    global op

    progresso.barra_progresso.setValue(75)
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    sql = "SELECT numero_serial FROM serial;"
    cursor.execute(sql)
    serial = cursor.fetchone()
    banco.close()
    if serial:
        op = 1
        conf_serial(str(serial[0]))

    else:
        op = 2
        form_serial.lbl_part_number.setText(part_number)
        form_serial.show()
        
    
def conf_serial(n_serial):
    
    
    base = []

    for i in part_number:
        base.append(i)

    
    p1 = 0
    letras = list(string.ascii_lowercase)
    
    for i in base:
        p1 = p1 + int(i)

    p2 = str(p1)[0]
    p3 = str(p1)[1:]
    p4 = letras[int(p2)]
    p5 = letras[int(p3)]
    p6 = int(base[6]) + int(base[7]) + int(base[10]) 
    p7 = int(base[15]) + int(base[14]) + int(base[13])
    p8 = 0
    if p6 > p7:
        p8 = p6 % p7
    else:
        p8 = p7 % p6 
    p9 = p1 ** 3
    p10 = str(p9)[0]
    p11 = str(p9)[-1]
    p12 = letras[int(p10)*2]
    p13 = letras[int(p11) + 10 - int(p10)]
    if p6 + int(base[14]) > 25:
        p14 = str(p6)[-1]
    else: 
        p14 = letras[p6 + int(base[14])] 

    result = str(p5) + str(p12) + str(p3) + str(p4) + str(p10) + str(p13) + str(p8) + str(p2) + str(p14) + str(p11)

    if n_serial == result:
        conf_primeiro_usuario()
    else:
        form_serial.label.setText('O Serial não é válido.')
        form_serial.label_2.setText('Digite um serial válido para o Part Number abaixo.')
        form_serial.lbl_part_number.setText(part_number)
        form_serial.serial_txt.setText(n_serial)
        form_serial.show()

def grava_serial():
    serial = form_serial.serial_txt.text()
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    
    
    if op == 1:
        sql = "UPDATE serial SET numero_serial = '"+ serial +"';"
        cursor.execute(sql)
        banco.commit()

    else:
        sql = "INSERT INTO serial (numero_serial) VALUES ('"+ serial +"');"
        cursor.execute(sql)
        banco.commit()

    banco.close()
    form_serial.close()
    valida()


def primeira_execucao():
    progresso.barra_progresso.setValue(25)
    banco = sqlite3.connect('inventario.db')
    cursor = banco.cursor()
    sql = "SELECT execucao FROM executa;"
    cursor.execute(sql)
    executa = cursor.fetchone()
    banco.close()
    if executa:
        pega_part_number()        
    else: 
        file = 'c:/windows/setup_invent.txt'
        try:
            f = open(file, 'r')
            if f:
               pass
            f.close()
        except:
            p_number = random.randrange(1000000000000000, 9999999999999999)
            f = open(file, 'w')
            f.write(str(p_number))
            f.close()
            win32api.SetFileAttributes(file,win32con.FILE_ATTRIBUTE_HIDDEN)

        banco = sqlite3.connect('inventario.db')
        cursor = banco.cursor()
        sql = "INSERT INTO executa (execucao) VALUES (1);"
        cursor.execute(sql)
        banco.commit()
        banco.close()
        pega_part_number()
    
    





progresso.show()
primeira_execucao()
primeiro_usuario.t5_inicio_entra.clicked.connect(primeiro_usuario_grava)
form_serial.serial_grava.clicked.connect(grava_serial)
form1.entra.clicked.connect(loga)
sys.exit(app.exec_())
