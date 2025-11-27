import sys
# --- IMPORTAÇÃO DO QTAWESOME ADICIONADA ---
import qtawesome as qta 

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QTableWidget, QTableWidgetItem, QHeaderView, 
                               QLabel, QHBoxLayout, QPushButton, QFrame, QStyle)
from PySide6.QtCore import Qt, QSize

STYLE_SHEET = """
QWidget {
    background-color: #12161f; 
    color: #dce1e8;            
    font-family: 'Segoe UI', sans-serif;
}

QPushButton#btn_excel {
    background-color: #2e7d32; 
    color: white;
    border: 1px solid #1b5e20;
    padding: 6px 15px; 
    border-radius: 4px;
    font-weight: bold;
    font-size: 13px;
}
QPushButton#btn_excel:hover {
    background-color: #388e3c; 
    border: 1px solid #388e3c;
}
QPushButton#btn_excel:pressed {
    background-color: #1b5e20; 
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

/* --- PAGINAÇÃO --- */
QFrame#PagContainer {
    background-color: #171c26; 
    border-top: 1px solid #2c3545;
    border-bottom-left-radius: 8px;
    border-bottom-right-radius: 8px;
}

QPushButton#btn_pag {
    background-color: #3a5f8a; 
    color: white;
    border: 1px solid #2c3e50;
    padding: 8px 15px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 13px;
}
QPushButton#btn_pag:hover {
    background-color: #4b7bc0; 
    border: 1px solid #4b7bc0;
}
QPushButton#btn_pag:pressed {
    background-color: #2a4566; 
}
QPushButton#btn_pag:disabled {
    background-color: #252b38; 
    color: #4a5568;
    border: 1px solid #252b38;
}

QFrame#PagContainer QLabel {
    background-color: #171c26; 
    color: #a0aec0;            
}
"""

class PageRelatorio(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Relatório Dark Blue Neutro")
        self.resize(1000, 700)
        self.setStyleSheet(STYLE_SHEET)

        # Main Widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        # --- BARRA DE TOPO ---
        top_bar_layout = QHBoxLayout()
        
        lbl_titulo = QLabel("Relatório Geral de Estoque")
        lbl_titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #8ab4f8;")
        top_bar_layout.addWidget(lbl_titulo)
        
        top_bar_layout.addStretch()
        
        # Botão Excel (Também troquei o ícone nativo pelo qtawesome para ficar branco puro, opcional)
        self.btn_excel = QPushButton(" Exportar Excel")
        self.btn_excel.setCursor(Qt.PointingHandCursor)
        # Usei um ícone de "salvar" do FontAwesome na cor branca
        self.btn_excel.setIcon(qta.icon('fa5s.file-excel', color='white')) 
        self.btn_excel.setObjectName("btn_excel") 
        top_bar_layout.addWidget(self.btn_excel)

        layout.addLayout(top_bar_layout)
        layout.addSpacing(10) 

        # --- DADOS (Simulação) ---
        self.colunas = [
            "Data Recebimento", "Data Análise", "Cód. Produto", "Grupo Estoque", "Valor Produto", 
            "Ressarcimento", "Cód. Análise", "Cód. Avaría", "Desc. Avaría", "Status", "Num. Série", "Origem", "Forncedor"
        ]
        
        self.todos_dados = []
        for i in range(1, 1001):
            linha = [f"{i:04d}", f"P{i*5}", f"Peça Genérica {i}", "Bosch", "Distribuidora X",
                     "00.000.000/0001-99", "25/11/2023", "55032", "3523...",
                     "8708.99", "150.00", "10", "18", "195.00",
                     "40", "273.00", "50", "10", "A-12", "P-05"]
            self.todos_dados.append(linha)

        # Controle Paginação
        self.pagina_atual = 1
        self.itens_por_pagina = 20
        self.total_registros = len(self.todos_dados)
        self.total_paginas = (self.total_registros // self.itens_por_pagina) + 1

        # 1. TABELA
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.colunas))
        self.table.setHorizontalHeaderLabels(self.colunas)
        
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setDefaultSectionSize(120)
        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(2, 300)

        layout.addWidget(self.table)

        # 2. PAGINAÇÃO
        pag_container = QFrame()
        pag_container.setObjectName("PagContainer")
        
        pag_layout = QHBoxLayout(pag_container)
        pag_layout.setContentsMargins(15, 10, 15, 10)

        # --- MODIFICAÇÃO PRINCIPAL AQUI ---

        # Botão Anterior
        self.btn_prev = QPushButton(" Anterior")
        self.btn_prev.setObjectName("btn_pag")
        
        # Ícone Chevron Left (Seta Esquerda) - Cor Branca
        self.btn_prev.setIcon(qta.icon('fa5s.chevron-left', color='white')) 
        
        self.btn_prev.setCursor(Qt.PointingHandCursor)
        self.btn_prev.clicked.connect(self.voltar_pagina)

        # Label
        self.lbl_paginacao = QLabel(f"Página {self.pagina_atual} de {self.total_paginas}")
        self.lbl_paginacao.setAlignment(Qt.AlignCenter)
        self.lbl_paginacao.setStyleSheet("color: #a0aec0; font-weight: bold; font-size: 13px;")

        # Botão Próximo
        self.btn_next = QPushButton("Próximo ")
        self.btn_next.setObjectName("btn_pag")
        self.btn_next.setLayoutDirection(Qt.RightToLeft)
        
        # Ícone Chevron Right (Seta Direita) - Cor Branca
        self.btn_next.setIcon(qta.icon('fa5s.chevron-right', color='white'))
        
        self.btn_next.setCursor(Qt.PointingHandCursor)
        self.btn_next.clicked.connect(self.avancar_pagina)

        pag_layout.addWidget(self.btn_prev)
        pag_layout.addStretch()
        pag_layout.addWidget(self.lbl_paginacao)
        pag_layout.addStretch()
        pag_layout.addWidget(self.btn_next)

        layout.addWidget(pag_container)

        self.carregar_dados()

    def carregar_dados(self):
        inicio = (self.pagina_atual - 1) * self.itens_por_pagina
        fim = inicio + self.itens_por_pagina
        dados_da_pagina = self.todos_dados[inicio:fim]

        self.table.setRowCount(0)
        self.table.setRowCount(len(dados_da_pagina))

        for row_idx, row_data in enumerate(dados_da_pagina):
            for col_idx, valor in enumerate(row_data):
                item = QTableWidgetItem(valor)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)

        self.lbl_paginacao.setText(f"Página {self.pagina_atual} de {self.total_paginas}")
        self.btn_prev.setDisabled(self.pagina_atual == 1)
        self.btn_next.setDisabled(self.pagina_atual >= self.total_paginas)

    def avancar_pagina(self):
        if self.pagina_atual < self.total_paginas:
            self.pagina_atual += 1
            self.carregar_dados()

    def voltar_pagina(self):
        if self.pagina_atual > 1:
            self.pagina_atual -= 1
            self.carregar_dados()