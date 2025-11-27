import sys
import qtawesome as qta
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QLineEdit, QDateEdit, 
                               QPushButton, QFrame, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QCheckBox, QDoubleSpinBox, QSpinBox, QMessageBox)
from PySide6.QtCore import Qt, QDate

# --- ESTILO ATUALIZADO ---
STYLE_SHEET = """
QMainWindow {
    background-color: #12161f;
}
QWidget {
    background-color: #12161f;
    color: #dce1e8;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}

/* --- CARDS --- */
QFrame#FormCard {
    background-color: #1b212d;
    border-radius: 8px;
    border: 1px solid #2c3545;
}

/* --- INPUTS --- */
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

/* --- REMOVENDO OS BOTÕES +/- (NOVO CÓDIGO AQUI) --- */
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button,
QSpinBox::up-button, QSpinBox::down-button {
    width: 0px;
    height: 0px;
    border: none;
    background: transparent;
}

/* --- LABELS --- */
QLabel { 
    background-color: #1b212d; 
    color: #a0aec0; 
    font-weight: 500; 
}

/* Label do Título Principal (Fora do Card) */
QLabel#MainTitle {
    background-color: #12161f; 
    color: #dce1e8;
    font-size: 20px; 
    font-weight: bold;
}

/* Títulos das Seções (Dentro do Card) */
QLabel#SectionTitle {
    background-color: #1b212d; 
    color: #8ab4f8; 
    font-size: 15px; 
    font-weight: bold;
    padding-bottom: 5px; 
    border-bottom: 1px solid #2c3545;
}

/* --- TABELA --- */
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

/* --- SCROLLBARS --- */
QScrollBar:horizontal, QScrollBar:vertical {
    background-color: #1b212d; 
    border: none;
}
QScrollBar:horizontal { height: 12px; }
QScrollBar:vertical   { width: 12px; }

QScrollBar::handle:horizontal, QScrollBar::handle:vertical {
    background-color: #3a5f8a; 
    border-radius: 6px;
    min-height: 20px;
    min-width: 20px;
}
QScrollBar::handle:horizontal:hover, QScrollBar::handle:vertical:hover {
    background-color: #4b7bc0; 
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
QScrollBar::add-line:vertical,   QScrollBar::sub-line:vertical {
    width: 0px; height: 0px;
}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal,
QScrollBar::add-page:vertical,   QScrollBar::sub-page:vertical {
    background: none;
}

/* --- CHECKBOX --- */
QCheckBox { 
    background-color: #1b212d; 
    color: #dce1e8; 
    spacing: 8px; 
}
QCheckBox::indicator { width: 18px; height: 18px; border-radius: 3px; border: 1px solid #2c3545; background: #171c26; }
QCheckBox::indicator:checked { background-color: #3a5f8a; border: 1px solid #3a5f8a; }

/* --- BOTÕES --- */
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
        self.setWindowTitle("Lançamento de NF-e com Itens")
        self.resize(1000, 750)
        self.setStyleSheet(STYLE_SHEET)

        # Main Scroll Area
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # =================================================================
        # CARD 1: CABEÇALHO DA NOTA (Sem alterações)
        # =================================================================
        card_header = QFrame()
        card_header.setObjectName("FormCard")
        layout_header = QVBoxLayout(card_header)
        
        lbl_header = QLabel("Entrada de Nota Fiscal")
        lbl_header.setObjectName("SectionTitle")
        layout_header.addWidget(lbl_header)
        
        # Linha 1: Emitente e NF
        row1 = QHBoxLayout()
        
        self.txt_cnpj = QLineEdit()
        self.txt_cnpj.setPlaceholderText("CNPJ Emitente")
        self.txt_cnpj.setInputMask("99.999.999/9999-99;_")
        self.txt_cnpj.setFixedWidth(140)
        self.txt_cnpj.textChanged.connect(self.buscar_emitente)
        
        self.txt_emitente = QLineEdit()
        self.txt_emitente.setPlaceholderText("Razão Social")
        self.txt_emitente.setReadOnly(True)

        self.txt_num_nf = QLineEdit()
        self.txt_num_nf.setPlaceholderText("Nº Nota")
        self.txt_num_nf.setFixedWidth(100)

        self.dt_emissao = QDateEdit()
        self.dt_emissao.setCalendarPopup(True)
        self.dt_emissao.setDate(QDate.currentDate())
        self.dt_emissao.setFixedWidth(110)

        # Layouts Verticais para Label + Input
        box_cnpj = QVBoxLayout()
        box_cnpj.addWidget(QLabel("CNPJ Emitente"))
        box_cnpj.addWidget(self.txt_cnpj)
        
        box_nome = QVBoxLayout()
        box_nome.addWidget(QLabel("Nome do Emitente"))
        box_nome.addWidget(self.txt_emitente)

        box_nf = QVBoxLayout()
        box_nf.addWidget(QLabel("Nº NF-e"))
        box_nf.addWidget(self.txt_num_nf)

        box_dt = QVBoxLayout()
        box_dt.addWidget(QLabel("Emissão"))
        box_dt.addWidget(self.dt_emissao)

        row1.addLayout(box_cnpj)
        row1.addLayout(box_nome)
        row1.addLayout(box_nf)
        row1.addLayout(box_dt)
        
        layout_header.addLayout(row1)
        main_layout.addWidget(card_header)

        # =================================================================
        # CARD 2: INSERÇÃO DE ITENS + TABELA + BOTÕES DE AÇÃO
        # =================================================================
        card_itens = QFrame()
        card_itens.setObjectName("FormCard")
        layout_itens = QVBoxLayout(card_itens)
        
        lbl_sec_itens = QLabel("Itens da Nota")
        lbl_sec_itens.setObjectName("SectionTitle")
        layout_itens.addWidget(lbl_sec_itens)

        # --- Linha de Inputs do Item ---
        input_item_layout = QHBoxLayout()
        
        # Código
        self.txt_cod_item = QLineEdit()
        self.txt_cod_item.setPlaceholderText("Cód.")
        self.txt_cod_item.setFixedWidth(80)

        # Quantidade
        self.spin_qtd = QSpinBox()
        self.spin_qtd.setRange(1, 9999)
        self.spin_qtd.setFixedWidth(70)

        # Valor Unitário
        self.spin_valor = QDoubleSpinBox()
        self.spin_valor.setRange(0.00, 999999.99)
        self.spin_valor.setPrefix("R$ ")
        self.spin_valor.setFixedWidth(100)

        # Checkbox Ressarcimento
        self.chk_ressarcimento = QCheckBox("Ressarcimento?")
        self.chk_ressarcimento.setCursor(Qt.PointingHandCursor)
        self.chk_ressarcimento.toggled.connect(self.toggle_ressarcimento)

        # Valor Ressarcimento
        self.lbl_vlr_ressarc = QLabel("Vl. Ressarc:")
        self.lbl_vlr_ressarc.setVisible(False)
        
        self.spin_vlr_ressarc = QDoubleSpinBox()
        self.spin_vlr_ressarc.setRange(0.00, 999999.99)
        self.spin_vlr_ressarc.setPrefix("R$ ")
        self.spin_vlr_ressarc.setFixedWidth(100)
        self.spin_vlr_ressarc.setVisible(False)

        # Botão Adicionar Item
        self.btn_add_item = QPushButton(" Adicionar")
        self.btn_add_item.setObjectName("btn_add")
        self.btn_add_item.setIcon(qta.icon('fa5s.plus', color='white'))
        self.btn_add_item.setCursor(Qt.PointingHandCursor)
        self.btn_add_item.clicked.connect(self.adicionar_item_tabela)

        # Montando a linha de inputs
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

        # --- Tabela de Itens ---
        self.table_itens = QTableWidget()
        self.colunas = ["Cód. Item", "Quantidade", "Valor", "Valor Total", "Ressarcimento"]
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

        # --- BOTÕES DE AÇÃO (MOVIDOS PARA CÁ) ---
        # Cria um layout horizontal para os botões ficarem no fundo do Card
        action_buttons_layout = QHBoxLayout()
        action_buttons_layout.setContentsMargins(0, 10, 0, 0) # Margem superior para separar da tabela
        
        self.btn_cancelar = QPushButton(" Cancelar")
        self.btn_cancelar.setObjectName("btn_secondary")
        self.btn_cancelar.setIcon(qta.icon('fa5s.times', color='#a0aec0'))
        
        self.btn_salvar = QPushButton(" Salvar Nota Fiscal")
        self.btn_salvar.setObjectName("btn_primary")
        self.btn_salvar.setIcon(qta.icon('fa5s.check', color='white'))
        self.btn_salvar.clicked.connect(self.salvar_tudo)

        # Adiciona Stretch primeiro para empurrar os botões para a DIREITA
        action_buttons_layout.addStretch()
        action_buttons_layout.addWidget(self.btn_cancelar)
        action_buttons_layout.addWidget(self.btn_salvar)

        # Adiciona o layout dos botões dentro do layout do card de itens
        layout_itens.addLayout(action_buttons_layout)

        # Adiciona o card ao layout principal
        main_layout.addWidget(card_itens)
        
        # O antigo footer_layout foi removido

    # ... Restante dos métodos (toggle_ressarcimento, adicionar_item_tabela, etc) continua igual ...
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

        def create_item(text):
            it = QTableWidgetItem(str(text))
            it.setTextAlignment(Qt.AlignCenter)
            return it

        self.table_itens.setItem(row, 0, create_item(codigo))
        self.table_itens.setItem(row, 1, create_item(qtd))
        self.table_itens.setItem(row, 2, create_item(f"R$ {vlr_unit:.2f}"))
        self.table_itens.setItem(row, 3, create_item(f"R$ {total:.2f}"))
        
        status_ressarc = "SIM" if tem_ressarc else "NÃO"
        item_status = create_item(status_ressarc)
        if tem_ressarc:
            item_status.setForeground(Qt.green)
        else:
            item_status.setForeground(Qt.gray)
            
        self.table_itens.setItem(row, 4, item_status)
        
        txt_vlr_ressarc = f"R$ {vlr_ressarc:.2f}" if tem_ressarc else "-"
        self.table_itens.setItem(row, 5, create_item(txt_vlr_ressarc))

        self.txt_cod_item.clear()
        self.spin_qtd.setValue(1)
        self.spin_valor.setValue(0.00)
        self.chk_ressarcimento.setChecked(False)
        self.txt_cod_item.setFocus()

    def buscar_emitente(self):
        cnpj = self.txt_cnpj.text().replace(".", "").replace("/", "").replace("-", "").strip()
        if len(cnpj) == 14:
            self.txt_emitente.setText("AUTO PEÇAS DISTRIBUIDORA LTDA")
        else:
            self.txt_emitente.clear()

    def salvar_tudo(self):
        qtd_itens = self.table_itens.rowCount()
        if qtd_itens == 0:
            QMessageBox.warning(self, "Erro", "Adicione pelo menos um item à nota.")
            return
        print(f"Salvando NF {self.txt_num_nf.text()} com {qtd_itens} itens.")