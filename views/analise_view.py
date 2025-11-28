from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                               QComboBox, QPushButton, QFrame, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QMessageBox)
from PySide6.QtCore import Qt
import qtawesome as qta
from controllers import AnaliseController

STYLE_SHEET = """
QWidget { background-color: #12161f; color: #dce1e8; font-family: 'Segoe UI'; font-size: 13px; }
QFrame#FormCard { background-color: #1b212d; border-radius: 8px; border: 1px solid #2c3545; }
QLabel#SectionTitle { color: #8ab4f8; font-size: 15px; font-weight: bold; border-bottom: 1px solid #2c3545; padding-bottom: 5px; }
QLineEdit, QComboBox { background-color: #171c26; border: 1px solid #2c3545; padding: 6px; color: #e0e6ed; border-radius: 4px; }
QTableWidget { background-color: #171c26; border: none; alternate-background-color: #202736; }
QHeaderView::section { background-color: #283042; color: #e0e6ed; padding: 6px; border: 1px solid #2c3545; font-weight: bold; }
QPushButton#btn_proc { background-color: #2e7d32; color: white; border: 1px solid #1b5e20; padding: 8px; border-radius: 4px; font-weight: bold; }
QPushButton#btn_proc:hover { background-color: #388e3c; }
QPushButton#btn_imp { background-color: #c62828; color: white; border: 1px solid #b71c1c; padding: 8px; border-radius: 4px; font-weight: bold; }
QPushButton#btn_imp:hover { background-color: #d32f2f; }
"""

class PageAnalise(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = AnaliseController()
        self.setStyleSheet(STYLE_SHEET)
        
        layout = QVBoxLayout(self)
        
        # Tabela
        card_tabela = QFrame(objectName="FormCard")
        layout_tabela = QVBoxLayout(card_tabela)
        lbl_lista = QLabel("Itens Aguardando Análise")
        lbl_lista.setObjectName("SectionTitle")
        layout_tabela.addWidget(lbl_lista)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "NF", "Produto", "Desc", "Data Lanç."])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.itemClicked.connect(self.carregar_item)
        layout_tabela.addWidget(self.table)
        layout.addWidget(card_tabela)
        
        # Form
        card_form = QFrame(objectName="FormCard")
        form_layout = QVBoxLayout(card_form)
        lbl_analise = QLabel("Dados da Análise Técnica")
        lbl_analise.setObjectName("SectionTitle")
        form_layout.addWidget(lbl_analise)
        
        row1 = QHBoxLayout()
        self.txt_id = QLineEdit(placeholderText="ID", readOnly=True)
        self.txt_id.setFixedWidth(60)
        self.txt_serie = QLineEdit(placeholderText="Nº Série")
        self.cb_origem = QComboBox()
        self.cb_origem.addItems(["Produzido", "Revenda"])
        self.txt_forn = QLineEdit(placeholderText="Fornecedor")
        
        row1.addWidget(QLabel("ID:"))
        row1.addWidget(self.txt_id)
        row1.addWidget(QLabel("Série:"))
        row1.addWidget(self.txt_serie)
        row1.addWidget(QLabel("Origem:"))
        row1.addWidget(self.cb_origem)
        row1.addWidget(self.txt_forn)
        form_layout.addLayout(row1)
        
        row2 = QHBoxLayout()
        self.cb_avaria = QComboBox()
        # Mock de avarias - O ideal é vir do controller
        self.cb_avaria.addItem("Selecione Avaria...", None)
        self.cb_avaria.addItem("001 - Dano Físico", "001")
        self.cb_avaria.addItem("002 - Defeito Elétrico", "002")
        
        self.txt_desc_avaria = QLineEdit(placeholderText="Laudo Técnico / Obs")
        
        self.btn_proc = QPushButton(" PROCEDENTE")
        self.btn_proc.setObjectName("btn_proc")
        self.btn_proc.setIcon(qta.icon('fa5s.check', color='white'))
        self.btn_proc.clicked.connect(lambda: self.salvar("Procedente"))
        
        self.btn_imp = QPushButton(" IMPROCEDENTE")
        self.btn_imp.setObjectName("btn_imp")
        self.btn_imp.setIcon(qta.icon('fa5s.times', color='white'))
        self.btn_imp.clicked.connect(lambda: self.salvar("Improcedente"))
        
        row2.addWidget(QLabel("Avaria:"))
        row2.addWidget(self.cb_avaria)
        row2.addWidget(self.txt_desc_avaria)
        row2.addWidget(self.btn_proc)
        row2.addWidget(self.btn_imp)
        form_layout.addLayout(row2)
        
        layout.addWidget(card_form)
        self.carregar_tabela()

    def carregar_tabela(self):
        itens = self.controller.listar_pendentes()
        self.table.setRowCount(0)
        for row, item in enumerate(itens):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(item['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(item['numero_nota']))
            self.table.setItem(row, 2, QTableWidgetItem(item['codigo_produto']))
            self.table.setItem(row, 3, QTableWidgetItem(item['descricao'] or ""))
            self.table.setItem(row, 4, QTableWidgetItem(item['data_fmt']))

    def carregar_item(self, item):
        row = item.row()
        self.txt_id.setText(self.table.item(row, 0).text())

    def salvar(self, status):
        if not self.txt_id.text(): return
        
        dados = {
            'serie': self.txt_serie.text(),
            'origem': self.cb_origem.currentText(),
            'fornecedor': self.txt_forn.text(),
            'cod_avaria': self.cb_avaria.currentData() or "000",
            'desc_avaria': self.txt_desc_avaria.text(),
            'status_resultado': status
        }
        try:
            self.controller.salvar_analise(self.txt_id.text(), dados)
            QMessageBox.information(self, "Salvo", f"Item finalizado como {status}")
            self.carregar_tabela()
            self.txt_id.clear()
            self.txt_serie.clear()
            self.txt_desc_avaria.clear()
        except Exception as e:
            QMessageBox.warning(self, "Erro", str(e))