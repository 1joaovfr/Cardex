import sys
import qtawesome as qta
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                               QPushButton, QFrame, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QMessageBox, QDateEdit, QCheckBox, 
                               QDoubleSpinBox, QSpinBox)
from PySide6.QtCore import Qt, QDate
from controllers import LancamentoController

# --- ESTILO ORIGINAL (MANTIDO) ---
STYLE_SHEET = """
QWidget {
    background-color: #12161f;
    color: #dce1e8;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}
QFrame#FormCard {
    background-color: #1b212d;
    border-radius: 8px;
    border: 1px solid #2c3545;
}
QLineEdit, QDateEdit, QDoubleSpinBox, QSpinBox {
    background-color: #171c26;
    border: 1px solid #2c3545;
    border-radius: 4px;
    padding: 6px;
    color: #e0e6ed;
}
QLineEdit:focus, QDateEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus {
    border: 1px solid #3a5f8a;
    background-color: #1a202c;
}
QLineEdit:read-only {
    background-color: #141820;
    color: #718096;
    border: 1px solid #252b38;
}
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button,
QSpinBox::up-button, QSpinBox::down-button {
    width: 0px; height: 0px; border: none; background: transparent;
}
QLabel { 
    background-color: transparent; 
    color: #a0aec0; 
    font-weight: 500; 
}
QLabel#SectionTitle {
    color: #8ab4f8; 
    font-size: 15px; 
    font-weight: bold;
    padding-bottom: 5px; 
    border-bottom: 1px solid #2c3545;
}
QTableWidget {
    background-color: #171c26; 
    alternate-background-color: #202736; 
    gridline-color: #2c3545;
    border: none; 
    font-size: 13px;
}
QHeaderView::section {
    background-color: #283042; 
    color: #e0e6ed;
    padding: 6px;
    border: 1px solid #2c3545;
    font-weight: bold;
    text-transform: uppercase; 
}
QTableWidget::item:selected {
    background-color: #3a5f8a; 
    color: white;
}
QScrollBar:horizontal, QScrollBar:vertical { background-color: #1b212d; border: none; }
QScrollBar:horizontal { height: 12px; }
QScrollBar:vertical   { width: 12px; }
QScrollBar::handle:horizontal, QScrollBar::handle:vertical {
    background-color: #3a5f8a; border-radius: 6px; min-height: 20px;
}
QCheckBox { color: #dce1e8; spacing: 8px; }
QCheckBox::indicator { width: 18px; height: 18px; border-radius: 3px; border: 1px solid #2c3545; background: #171c26; }
QCheckBox::indicator:checked { background-color: #3a5f8a; border: 1px solid #3a5f8a; }

QPushButton#btn_add {
    background-color: #3a5f8a; color: white; border: none; padding: 8px 15px; border-radius: 4px; font-weight: bold;
}
QPushButton#btn_add:hover { background-color: #4b7bc0; }
QPushButton#btn_primary {
    background-color: #2e7d32; color: white; border: 1px solid #1b5e20; padding: 10px 20px; border-radius: 4px; font-weight: bold;
}
QPushButton#btn_primary:hover { background-color: #388e3c; }
QPushButton#btn_secondary {
    background-color: #1b212d; color: #a0aec0; border: 1px solid #2c3e50; padding: 10px 20px; border-radius: 4px;
}
QPushButton#btn_secondary:hover { background-color: #2c3545; color: white; }
"""

class PageLancamento(QWidget):
    def __init__(self):
        super().__init__()
        # --- INTEGRAÇÃO CONTROLLER ---
        self.controller = LancamentoController()
        
        self.setWindowTitle("Lançamento de NF-e")
        self.setStyleSheet(STYLE_SHEET)

        # Layout Principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # CARD 1: CABEÇALHO
        card_header = QFrame(objectName="FormCard")
        layout_header = QVBoxLayout(card_header)
        
        lbl_header = QLabel("Entrada de Nota Fiscal")
        lbl_header.setObjectName("SectionTitle")
        layout_header.addWidget(lbl_header)
        
        row1 = QHBoxLayout()
        
        # Inputs
        self.txt_cnpj = QLineEdit(placeholderText="CNPJ Emitente")
        self.txt_cnpj.setInputMask("99.999.999/9999-99;_")
        self.txt_cnpj.setFixedWidth(140)
        self.txt_cnpj.textChanged.connect(self.buscar_emitente)
        
        self.txt_emitente = QLineEdit(placeholderText="Razão Social", readOnly=True)
        
        self.txt_num_nf = QLineEdit(placeholderText="Nº Nota")
        self.txt_num_nf.setFixedWidth(100)

        self.dt_emissao = QDateEdit(calendarPopup=True, date=QDate.currentDate())
        self.dt_emissao.setFixedWidth(110)
        
        # --- NOVO CAMPO: RECEBIMENTO ---
        self.dt_recebimento = QDateEdit(calendarPopup=True, date=QDate.currentDate())
        self.dt_recebimento.setFixedWidth(110)

        # Helper layouts
        def v_box(lbl, widget):
            l = QVBoxLayout()
            l.addWidget(QLabel(lbl))
            l.addWidget(widget)
            return l

        row1.addLayout(v_box("CNPJ Emitente", self.txt_cnpj))
        row1.addLayout(v_box("Nome do Emitente", self.txt_emitente))
        row1.addLayout(v_box("Nº NF-e", self.txt_num_nf))
        row1.addLayout(v_box("Emissão", self.dt_emissao))
        row1.addLayout(v_box("Recebimento", self.dt_recebimento))
        
        layout_header.addLayout(row1)
        main_layout.addWidget(card_header)

        # CARD 2: ITENS
        card_itens = QFrame(objectName="FormCard")
        layout_itens = QVBoxLayout(card_itens)
        
        lbl_sec_itens = QLabel("Itens da Nota")
        lbl_sec_itens.setObjectName("SectionTitle")
        layout_itens.addWidget(lbl_sec_itens)

        # Inputs Item
        input_item_layout = QHBoxLayout()
        
        self.txt_cod_item = QLineEdit(placeholderText="Cód.")
        self.txt_cod_item.setFixedWidth(80)

        self.spin_qtd = QSpinBox(minimum=1, maximum=9999)
        self.spin_qtd.setFixedWidth(70)

        self.spin_valor = QDoubleSpinBox(minimum=0.00, maximum=999999.99)
        self.spin_valor.setPrefix("R$ ")
        self.spin_valor.setFixedWidth(100)

        self.chk_ressarcimento = QCheckBox("Ressarcimento?")
        self.chk_ressarcimento.setCursor(Qt.PointingHandCursor)
        self.chk_ressarcimento.toggled.connect(self.toggle_ressarcimento)

        self.lbl_vlr_ressarc = QLabel("Vl. Ressarc:")
        self.lbl_vlr_ressarc.setVisible(False)
        
        self.spin_vlr_ressarc = QDoubleSpinBox(minimum=0.00, maximum=999999.99)
        self.spin_vlr_ressarc.setPrefix("R$ ")
        self.spin_vlr_ressarc.setFixedWidth(100)
        self.spin_vlr_ressarc.setVisible(False)

        self.btn_add_item = QPushButton(" Adicionar")
        self.btn_add_item.setObjectName("btn_add")
        self.btn_add_item.setIcon(qta.icon('fa5s.plus', color='white'))
        self.btn_add_item.setCursor(Qt.PointingHandCursor)
        self.btn_add_item.clicked.connect(self.adicionar_item_tabela)

        input_item_layout.addWidget(QLabel("Item:"))
        input_item_layout.addWidget(self.txt_cod_item)
        input_item_layout.addWidget(QLabel("Qtd:"))
        input_item_layout.addWidget(self.spin_qtd)
        input_item_layout.addWidget(QLabel("Valor:"))
        input_item_layout.addWidget(self.spin_valor)
        input_item_layout.addSpacing(15)
        input_item_layout.addWidget(self.chk_ressarcimento)
        input_item_layout.addWidget(self.lbl_vlr_ressarc)
        input_item_layout.addWidget(self.spin_vlr_ressarc)
        input_item_layout.addStretch()
        input_item_layout.addWidget(self.btn_add_item)

        layout_itens.addLayout(input_item_layout)

        # Tabela
        self.table_itens = QTableWidget()
        self.colunas = ["Cód. Item", "Quantidade", "Valor", "Valor Total", "Ressarcimento", "Vlr Ressarc"]
        self.table_itens.setColumnCount(len(self.colunas))
        self.table_itens.setHorizontalHeaderLabels(self.colunas)
        self.table_itens.verticalHeader().setVisible(False)
        self.table_itens.setAlternatingRowColors(True)
        self.table_itens.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_itens.setEditTriggers(QTableWidget.NoEditTriggers)
        
        header = self.table_itens.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)

        layout_itens.addWidget(self.table_itens)

        # Botões Ação
        action_buttons_layout = QHBoxLayout()
        action_buttons_layout.setContentsMargins(0, 10, 0, 0)
        
        self.btn_cancelar = QPushButton(" Cancelar")
        self.btn_cancelar.setObjectName("btn_secondary")
        self.btn_cancelar.setIcon(qta.icon('fa5s.times', color='#a0aec0'))
        
        self.btn_salvar = QPushButton(" Salvar Nota Fiscal")
        self.btn_salvar.setObjectName("btn_primary")
        self.btn_salvar.setIcon(qta.icon('fa5s.check', color='white'))
        self.btn_salvar.clicked.connect(self.salvar_tudo)

        action_buttons_layout.addStretch()
        action_buttons_layout.addWidget(self.btn_cancelar)
        action_buttons_layout.addWidget(self.btn_salvar)

        layout_itens.addLayout(action_buttons_layout)
        main_layout.addWidget(card_itens)

    # --- LÓGICA MANTIDA ---
    def toggle_ressarcimento(self, checked):
        self.lbl_vlr_ressarc.setVisible(checked)
        self.spin_vlr_ressarc.setVisible(checked)
        if checked:
            self.spin_vlr_ressarc.setFocus()
        else:
            self.spin_vlr_ressarc.setValue(0.0)

    def adicionar_item_tabela(self):
        codigo = self.txt_cod_item.text()
        if not codigo:
            QMessageBox.warning(self, "Aviso", "Preencha o código do item.")
            return

        qtd = self.spin_qtd.value()
        vlr_unit = self.spin_valor.value()
        total = qtd * vlr_unit
        
        tem_ressarc = self.chk_ressarcimento.isChecked()
        vlr_ressarc = self.spin_vlr_ressarc.value() if tem_ressarc else 0.0

        row = self.table_itens.rowCount()
        self.table_itens.insertRow(row)

        self.table_itens.setItem(row, 0, QTableWidgetItem(codigo))
        self.table_itens.setItem(row, 1, QTableWidgetItem(str(qtd)))
        self.table_itens.setItem(row, 2, QTableWidgetItem(f"R$ {vlr_unit:.2f}"))
        self.table_itens.setItem(row, 3, QTableWidgetItem(f"R$ {total:.2f}"))
        
        status_ressarc = "SIM" if tem_ressarc else "NÃO"
        item_status = QTableWidgetItem(status_ressarc)
        item_status.setForeground(Qt.green if tem_ressarc else Qt.gray)
        self.table_itens.setItem(row, 4, item_status)
        
        self.table_itens.setItem(row, 5, QTableWidgetItem(f"R$ {vlr_ressarc:.2f}"))

        self.txt_cod_item.clear()
        self.spin_qtd.setValue(1)
        self.spin_valor.setValue(0.00)
        self.chk_ressarcimento.setChecked(False)
        self.txt_cod_item.setFocus()

    def buscar_emitente(self):
        # Lógica conectada ao controller
        cnpj_sujo = self.txt_cnpj.text()
        if len(cnpj_sujo) >= 14: # Simples verificação visual
            nome = self.controller.buscar_cliente_por_cnpj(cnpj_sujo)
            if nome:
                self.txt_emitente.setText(nome)
            else:
                self.txt_emitente.setText("NÃO CADASTRADO")

    def salvar_tudo(self):
        qtd_itens = self.table_itens.rowCount()
        if qtd_itens == 0:
            QMessageBox.warning(self, "Erro", "Adicione pelo menos um item à nota.")
            return
            
        # Preparar dados para o controller
        dados_nota = {
            'cnpj': self.txt_cnpj.text(),
            'numero': self.txt_num_nf.text(),
            'emissao': self.dt_emissao.date().toPython(),
            'recebimento': self.dt_recebimento.date().toPython()
        }
        
        lista_itens = []
        for row in range(qtd_itens):
            # Extrair valores limpos da tabela
            lista_itens.append({
                'codigo': self.table_itens.item(row, 0).text(),
                'qtd': self.table_itens.item(row, 1).text(),
                'valor': float(self.table_itens.item(row, 2).text().replace("R$ ", "")),
                'ressarcimento': float(self.table_itens.item(row, 5).text().replace("R$ ", ""))
            })
            
        try:
            self.controller.salvar_nota_entrada(dados_nota, lista_itens)
            QMessageBox.information(self, "Sucesso", "Nota lançada com sucesso!")
            self.table_itens.setRowCount(0)
            self.txt_num_nf.clear()
            self.txt_cod_item.clear()
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))