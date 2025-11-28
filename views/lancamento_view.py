import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                               QDateEdit, QPushButton, QFrame, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QCheckBox, QDoubleSpinBox, QSpinBox, QMessageBox)
from PySide6.QtCore import Qt, QDate
import qtawesome as qta
from controllers import LancamentoController

# --- SEU ESTILO ORIGINAL ---
STYLE_SHEET = """
QWidget { background-color: #12161f; color: #dce1e8; font-family: 'Segoe UI', sans-serif; font-size: 13px; }
QFrame#FormCard { background-color: #1b212d; border-radius: 8px; border: 1px solid #2c3545; }
QLineEdit, QDateEdit, QDoubleSpinBox, QSpinBox { background-color: #171c26; border: 1px solid #2c3545; border-radius: 4px; padding: 6px; color: #e0e6ed; }
QLineEdit:focus, QDateEdit:focus { border: 1px solid #3a5f8a; background-color: #1a202c; }
QLabel { color: #a0aec0; font-weight: 500; background: transparent; }
QLabel#SectionTitle { color: #8ab4f8; font-size: 15px; font-weight: bold; padding-bottom: 5px; border-bottom: 1px solid #2c3545; }
QTableWidget { background-color: #171c26; alternate-background-color: #202736; gridline-color: #2c3545; border: none; }
QHeaderView::section { background-color: #283042; color: #e0e6ed; padding: 6px; border: 1px solid #2c3545; font-weight: bold; }
QPushButton#btn_primary { background-color: #2e7d32; color: white; border: 1px solid #1b5e20; padding: 8px 20px; border-radius: 4px; font-weight: bold; }
QPushButton#btn_primary:hover { background-color: #388e3c; }
QPushButton#btn_add { background-color: #3a5f8a; color: white; border: none; padding: 8px 15px; border-radius: 4px; }
"""

class PageLancamento(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = LancamentoController()
        self.setWindowTitle("Lançamento de NF-e")
        self.setStyleSheet(STYLE_SHEET)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        
        # --- HEADER ---
        card_header = QFrame(objectName="FormCard")
        layout_header = QVBoxLayout(card_header)
        
        lbl_title = QLabel("Entrada de Nota Fiscal")
        lbl_title.setObjectName("SectionTitle")
        layout_header.addWidget(lbl_title)
        
        row1 = QHBoxLayout()
        
        self.txt_cnpj = QLineEdit(placeholderText="CNPJ Emitente")
        self.txt_cnpj.setFixedWidth(140)
        self.txt_cnpj.textChanged.connect(self.buscar_emitente)
        
        self.txt_emitente = QLineEdit(readOnly=True, placeholderText="Razão Social")
        self.txt_num_nf = QLineEdit(placeholderText="Nº Nota")
        self.txt_num_nf.setFixedWidth(100)
        
        self.dt_emissao = QDateEdit(calendarPopup=True, date=QDate.currentDate())
        self.dt_emissao.setFixedWidth(110)
        
        self.dt_recebimento = QDateEdit(calendarPopup=True, date=QDate.currentDate())
        self.dt_recebimento.setFixedWidth(110)
        
        # Layouts verticais pequenos para labels
        def create_field(label, widget):
            l = QVBoxLayout()
            l.addWidget(QLabel(label))
            l.addWidget(widget)
            return l

        row1.addLayout(create_field("CNPJ", self.txt_cnpj))
        row1.addLayout(create_field("Emitente", self.txt_emitente))
        row1.addLayout(create_field("Nº NF", self.txt_num_nf))
        row1.addLayout(create_field("Emissão", self.dt_emissao))
        row1.addLayout(create_field("Recebimento", self.dt_recebimento))
        
        layout_header.addLayout(row1)
        main_layout.addWidget(card_header)

        # --- ITENS ---
        card_itens = QFrame(objectName="FormCard")
        layout_itens = QVBoxLayout(card_itens)
        
        lbl_itens = QLabel("Itens da Nota")
        lbl_itens.setObjectName("SectionTitle")
        layout_itens.addWidget(lbl_itens)
        
        input_layout = QHBoxLayout()
        self.txt_cod_item = QLineEdit(placeholderText="Cód.")
        self.txt_cod_item.setFixedWidth(100)
        
        self.spin_qtd = QSpinBox(minimum=1, maximum=999)
        self.spin_qtd.setFixedWidth(80)
        
        self.spin_valor = QDoubleSpinBox(maximum=999999, prefix="R$ ")
        self.spin_valor.setFixedWidth(100)
        
        self.chk_ressarc = QCheckBox("Ressarcimento?")
        self.spin_ressarc = QDoubleSpinBox(maximum=99999, prefix="R$ ")
        self.spin_ressarc.setFixedWidth(100)
        self.spin_ressarc.setVisible(False)
        self.chk_ressarc.toggled.connect(lambda c: self.spin_ressarc.setVisible(c))
        
        self.btn_add = QPushButton(" Adicionar")
        self.btn_add.setObjectName("btn_add")
        self.btn_add.setIcon(qta.icon('fa5s.plus', color='white'))
        self.btn_add.clicked.connect(self.add_item)
        
        input_layout.addWidget(QLabel("Item:"))
        input_layout.addWidget(self.txt_cod_item)
        input_layout.addWidget(QLabel("Qtd:"))
        input_layout.addWidget(self.spin_qtd)
        input_layout.addWidget(QLabel("Valor:"))
        input_layout.addWidget(self.spin_valor)
        input_layout.addWidget(self.chk_ressarc)
        input_layout.addWidget(self.spin_ressarc)
        input_layout.addStretch()
        input_layout.addWidget(self.btn_add)
        layout_itens.addLayout(input_layout)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Código", "Qtd", "Valor Unit.", "Ressarc.", "Total"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        layout_itens.addWidget(self.table)
        
        # Botão Salvar Principal
        btn_layout = QHBoxLayout()
        self.btn_salvar = QPushButton(" Salvar Nota Fiscal")
        self.btn_salvar.setObjectName("btn_primary")
        self.btn_salvar.setIcon(qta.icon('fa5s.check-double', color='white'))
        self.btn_salvar.clicked.connect(self.salvar_tudo)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_salvar)
        layout_itens.addLayout(btn_layout)
        
        main_layout.addWidget(card_itens)

    def buscar_emitente(self):
        t = self.txt_cnpj.text()
        if len(t) >= 14:
            nome = self.controller.buscar_cliente_por_cnpj(t)
            self.txt_emitente.setText(nome if nome else "NÃO ENCONTRADO")

    def add_item(self):
        if not self.txt_cod_item.text(): return
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        val = self.spin_valor.value()
        qtd = self.spin_qtd.value()
        res = self.spin_ressarc.value() if self.chk_ressarc.isChecked() else 0.0
        
        self.table.setItem(row, 0, QTableWidgetItem(self.txt_cod_item.text()))
        self.table.setItem(row, 1, QTableWidgetItem(str(qtd)))
        self.table.setItem(row, 2, QTableWidgetItem(f"{val:.2f}"))
        self.table.setItem(row, 3, QTableWidgetItem(f"{res:.2f}"))
        self.table.setItem(row, 4, QTableWidgetItem(f"{(val * qtd):.2f}"))
        
        self.txt_cod_item.clear()
        self.spin_qtd.setValue(1)
        self.txt_cod_item.setFocus()

    def salvar_tudo(self):
        if self.table.rowCount() == 0: 
            QMessageBox.warning(self, "Aviso", "Adicione itens.")
            return
        
        dados_nota = {
            'cnpj': self.txt_cnpj.text(),
            'numero': self.txt_num_nf.text(),
            'emissao': self.dt_emissao.date().toPython(),
            'recebimento': self.dt_recebimento.date().toPython()
        }
        
        itens = []
        for i in range(self.table.rowCount()):
            itens.append({
                'codigo': self.table.item(i, 0).text(),
                'qtd': self.table.item(i, 1).text(),
                'valor': float(self.table.item(i, 2).text()),
                'ressarcimento': float(self.table.item(i, 3).text())
            })
            
        try:
            if self.controller.salvar_nota_entrada(dados_nota, itens):
                QMessageBox.information(self, "Sucesso", "Nota lançada!")
                self.table.setRowCount(0)
                self.txt_num_nf.clear()
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))