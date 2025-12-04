import sys
import qtawesome as qta
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                               QComboBox, QPushButton, QFrame, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QMessageBox)
from PySide6.QtCore import Qt
from controllers import AnaliseController

# --- ESTILO ORIGINAL (MANTIDO) ---
STYLE_SHEET = """
QWidget { background-color: #12161f; color: #dce1e8; font-family: 'Segoe UI', sans-serif; font-size: 13px; }
QFrame#FormCard { background-color: #1b212d; border-radius: 8px; border: 1px solid #2c3545; }
QLineEdit, QComboBox { background-color: #171c26; border: 1px solid #2c3545; border-radius: 4px; padding: 6px; color: #e0e6ed; }
QLineEdit:focus, QComboBox:focus { border: 1px solid #3a5f8a; background-color: #1a202c; }
QLineEdit:read-only { background-color: #141820; color: #718096; border: 1px solid #252b38; }
QLabel { background-color: transparent; color: #a0aec0; font-weight: 500; }
QLabel#SectionTitle { color: #8ab4f8; font-size: 15px; font-weight: bold; padding-bottom: 5px; border-bottom: 1px solid #2c3545; }
QLabel#StatusProcedente { color: #48bb78; font-weight: bold; background-color: #1b212d; border: 1px solid #2f855a; }
QLabel#StatusImprocedente { color: #f56565; font-weight: bold; background-color: #1b212d; border: 1px solid #c53030; }
QLabel#StatusNeutro { color: #a0aec0; background-color: #1b212d; border: 1px solid #2c3545; }
QTableWidget { background-color: #171c26; alternate-background-color: #202736; gridline-color: #2c3545; border: none; font-size: 13px; }
QHeaderView::section { background-color: #283042; color: #e0e6ed; padding: 6px; border: 1px solid #2c3545; font-weight: bold; text-transform: uppercase; }
QTableWidget::item:selected { background-color: #3a5f8a; color: white; }
QScrollBar:horizontal, QScrollBar:vertical { background-color: #1b212d; border: none; }
QScrollBar:horizontal { height: 12px; }
QScrollBar:vertical   { width: 12px; }
QScrollBar::handle:horizontal, QScrollBar::handle:vertical { background-color: #3a5f8a; border-radius: 6px; min-height: 20px; }
QPushButton#btn_primary { background-color: #2e7d32; color: white; border: 1px solid #1b5e20; padding: 8px 20px; border-radius: 4px; font-weight: bold; }
QPushButton#btn_primary:hover { background-color: #388e3c; }
QPushButton#btn_secondary { background-color: #1b212d; color: #a0aec0; border: 1px solid #2c3e50; padding: 8px 20px; border-radius: 4px; }
QPushButton#btn_secondary:hover { background-color: #2c3545; color: white; }
"""

class PageAnalise(QWidget):
    def __init__(self):
        super().__init__()
        # --- INTEGRAÇÃO CONTROLLER ---
        self.controller = AnaliseController()
        
        self.setWindowTitle("Análise Técnica de Itens")
        self.setStyleSheet(STYLE_SHEET)

        # Mock Códigos Avaria (Idealmente viria do banco, mas mantive sua estrutura original)
        self.codigos_avaria = {
            "001": {"desc": "Dano Físico / Quebra", "status": "Improcedente"},
            "002": {"desc": "Defeito de Fabricação", "status": "Procedente"},
            "003": {"desc": "Instalação Incorreta", "status": "Improcedente"},
            "004": {"desc": "Ruído Excessivo", "status": "Procedente"},
        }
        self.item_atual = None

        layout = QVBoxLayout(self) 
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # PARTE 1: TABELA
        card_tabela = QFrame(objectName="FormCard")
        layout_tabela = QVBoxLayout(card_tabela)
        
        lbl_lista = QLabel("Itens Aguardando Análise")
        lbl_lista.setObjectName("SectionTitle")
        layout_tabela.addWidget(lbl_lista)

        self.table = QTableWidget()
        colunas = ["ID", "Nota Fiscal", "Cód. Peça", "Descrição", "Data Entrada"]
        self.table.setColumnCount(len(colunas))
        self.table.setHorizontalHeaderLabels(colunas)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setShowGrid(True) 
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        self.table.itemClicked.connect(self.carregar_item_para_analise)

        layout_tabela.addWidget(self.table)
        layout.addWidget(card_tabela, stretch=1)

        # PARTE 2: FORMULÁRIO
        card_form = QFrame(objectName="FormCard")
        layout_form = QVBoxLayout(card_form)
        
        lbl_analise = QLabel("Dados da Análise Técnica")
        lbl_analise.setObjectName("SectionTitle")
        layout_form.addWidget(lbl_analise)

        # Linha 1
        row1 = QHBoxLayout()
        self.txt_id_item = QLineEdit(placeholderText="ID", readOnly=True)
        self.txt_id_item.setFixedWidth(50) 
        
        self.txt_peca_nome = QLineEdit(placeholderText="Selecione um item...", readOnly=True)
        
        self.txt_serie = QLineEdit(placeholderText="Nº Série")
        self.txt_serie.setFixedWidth(110)
        
        self.combo_origem = QComboBox()
        self.combo_origem.addItems(["Nacional", "Importado", "Reindustrializado"])
        self.combo_origem.setFixedWidth(110)

        self.txt_fornecedor = QLineEdit(placeholderText="Fabricante / Distribuidor")

        row1.addWidget(QLabel("ID:"))
        row1.addWidget(self.txt_id_item)
        row1.addWidget(QLabel("Peça:"))
        row1.addWidget(self.txt_peca_nome, stretch=1) 
        row1.addWidget(QLabel("Série:"))
        row1.addWidget(self.txt_serie)
        row1.addWidget(QLabel("Origem:"))
        row1.addWidget(self.combo_origem)
        row1.addWidget(QLabel("Forn.:"))
        row1.addWidget(self.txt_fornecedor, stretch=1) 

        layout_form.addLayout(row1)

        # Linha 2
        row_diag = QHBoxLayout()

        self.combo_cod_avaria = QComboBox()
        self.combo_cod_avaria.addItem("Selecione...", None)
        for cod in self.codigos_avaria:
            self.combo_cod_avaria.addItem(f"{cod}", cod)
        self.combo_cod_avaria.setFixedWidth(120)
        self.combo_cod_avaria.currentTextChanged.connect(self.atualizar_detalhes_avaria)

        self.txt_desc_avaria = QLineEdit(readOnly=True, placeholderText="Descrição da avaria...")

        self.lbl_status_resultado = QLabel("AGUARDANDO")
        self.lbl_status_resultado.setObjectName("StatusNeutro")
        self.lbl_status_resultado.setAlignment(Qt.AlignCenter)
        self.lbl_status_resultado.setFixedSize(130, 32)
        self.lbl_status_resultado.setStyleSheet("border-radius: 4px;")

        self.btn_cancelar = QPushButton(" Cancelar")
        self.btn_cancelar.setObjectName("btn_secondary")
        self.btn_cancelar.setIcon(qta.icon('fa5s.times', color='#a0aec0'))
        
        self.btn_concluir = QPushButton(" Concluir")
        self.btn_concluir.setObjectName("btn_primary")
        self.btn_concluir.setIcon(qta.icon('fa5s.check-double', color='white'))
        self.btn_concluir.clicked.connect(self.salvar_analise)

        row_diag.addWidget(QLabel("Cód. Avaria:"))
        row_diag.addWidget(self.combo_cod_avaria)
        row_diag.addWidget(self.txt_desc_avaria, stretch=1) 
        row_diag.addWidget(self.lbl_status_resultado)
        row_diag.addSpacing(10)
        row_diag.addWidget(self.btn_cancelar)
        row_diag.addWidget(self.btn_concluir)

        layout_form.addLayout(row_diag)
        layout.addWidget(card_form)

        # Inicialização
        self.carregar_dados_tabela()
        self.bloquear_form(True)

    # --- LÓGICA ATUALIZADA ---
    def carregar_dados_tabela(self):
        # Busca real do banco
        itens_db = self.controller.listar_pendentes()
        
        self.table.setRowCount(0)
        for item in itens_db:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(item['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(item['numero_nota']))
            self.table.setItem(row, 2, QTableWidgetItem(item['codigo_produto']))
            self.table.setItem(row, 3, QTableWidgetItem(item['descricao'] or ""))
            self.table.setItem(row, 4, QTableWidgetItem(item['data_fmt']))

    def carregar_item_para_analise(self, item):
        row = item.row()
        id_item = self.table.item(row, 0).text()
        desc_item = self.table.item(row, 3).text()

        self.bloquear_form(False)
        self.item_atual = id_item
        self.txt_id_item.setText(id_item)
        self.txt_peca_nome.setText(desc_item)
        
        self.txt_serie.clear()
        self.txt_fornecedor.clear()
        self.combo_origem.setCurrentIndex(0)
        self.combo_cod_avaria.setCurrentIndex(0)
        self.txt_serie.setFocus()

    def atualizar_detalhes_avaria(self, text):
        codigo_puro = text.split(" ")[0]
        dados = self.codigos_avaria.get(codigo_puro)
        
        if dados:
            self.txt_desc_avaria.setText(dados['desc'])
            status = dados['status']
            self.lbl_status_resultado.setText(status.upper())
            
            if status == "Procedente":
                self.lbl_status_resultado.setObjectName("StatusProcedente")
            else:
                self.lbl_status_resultado.setObjectName("StatusImprocedente")
        else:
            self.txt_desc_avaria.clear()
            self.lbl_status_resultado.setText("AGUARDANDO")
            self.lbl_status_resultado.setObjectName("StatusNeutro")
        
        self.lbl_status_resultado.style().unpolish(self.lbl_status_resultado)
        self.lbl_status_resultado.style().polish(self.lbl_status_resultado)

    def bloquear_form(self, bloquear):
        inputs = [self.txt_serie, self.combo_origem, self.txt_fornecedor, self.combo_cod_avaria, self.btn_concluir]
        for widget in inputs:
            widget.setEnabled(not bloquear)

    def salvar_analise(self):
        if not self.item_atual: return
        if self.combo_cod_avaria.currentIndex() == 0:
            QMessageBox.warning(self, "Aviso", "Selecione um código de avaria.")
            return

        dados = {
            'serie': self.txt_serie.text(),
            'origem': self.combo_origem.currentText(),
            'fornecedor': self.txt_fornecedor.text(),
            'cod_avaria': self.combo_cod_avaria.currentText().split(" ")[0],
            'desc_avaria': self.txt_desc_avaria.text(),
            'status_resultado': self.lbl_status_resultado.text().capitalize()
        }

        try:
            self.controller.salvar_analise(self.item_atual, dados)
            QMessageBox.information(self, "Sucesso", "Análise salva!")
            self.bloquear_form(True)
            self.txt_id_item.clear()
            self.txt_peca_nome.clear()
            self.txt_desc_avaria.clear()
            self.lbl_status_resultado.setText("AGUARDANDO")
            self.lbl_status_resultado.setObjectName("StatusNeutro")
            self.carregar_dados_tabela()
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))