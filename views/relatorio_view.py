import sys
import math
import qtawesome as qta
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                               QFrame, QTableWidget, QTableWidgetItem, QHeaderView, 
                               QFileDialog, QMessageBox, QAbstractItemView)
from PySide6.QtCore import Qt
from controllers import RelatorioController

# --- ESTILO ATUALIZADO ---
STYLE_SHEET = """
QWidget { background-color: #12161f; color: #dce1e8; font-family: 'Segoe UI', sans-serif; font-size: 13px; }

/* CARD PRINCIPAL */
QFrame#FormCard { background-color: #1b212d; border-radius: 8px; border: 1px solid #2c3545; }

/* TÍTULO DA SEÇÃO */
QLabel#SectionTitle { color: #8ab4f8; background-color: #1b212d; font-size: 15px; font-weight: bold; padding-bottom: 5px; border-bottom: 1px solid #2c3545; }

/* TABELA */
QTableWidget { background-color: #171c26; alternate-background-color: #202736; gridline-color: #2c3545; border: none; font-size: 13px; }
QHeaderView::section { background-color: #283042; color: #e0e6ed; padding: 6px; border: 1px solid #2c3545; font-weight: bold; text-transform: uppercase; }
QTableWidget::item:selected { background-color: #3a5f8a; color: white; }

/* --- SCROLLBARS (Fina e Arredondada) --- */

/* Vertical */
QScrollBar:vertical {
    background: #171c26;      /* Cor do fundo do trilho */
    width: 8px;               /* <--- LARGURA MAIS FINA */
    margin: 0px;
}
QScrollBar::handle:vertical {
    background-color: #3a5f8a;
    min-height: 30px;
    border-radius: 4px;       /* <--- ARREDONDAMENTO (Metade da largura) */
}
QScrollBar::handle:vertical:hover {
    background-color: #4b7bc0;
}

/* Horizontal */
QScrollBar:horizontal {
    background: #171c26;
    height: 8px;              /* <--- ALTURA MAIS FINA */
    margin: 0px;
}
QScrollBar::handle:horizontal {
    background-color: #3a5f8a;
    min-width: 30px;
    border-radius: 4px;       /* <--- ARREDONDAMENTO */
}
QScrollBar::handle:horizontal:hover {
    background-color: #4b7bc0;
}

/* Esconde as setas (cima/baixo/esquerda/direita) */
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical, 
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px; height: 0px;
    background: none;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
}

/* BOTÕES GERAIS */
QPushButton { padding: 8px 15px; border-radius: 4px; font-weight: bold; }

/* Botão Excel */
QPushButton#btn_excel { background-color: #2e7d32; color: white; border: 1px solid #1b5e20; }
QPushButton#btn_excel:hover { background-color: #388e3c; }

/* Botões de Paginação */
QPushButton#btn_pag { background-color: #3a5f8a; color: white; border: 1px solid #2c3e50; }
QPushButton#btn_pag:hover { background-color: #4b7bc0; }
QPushButton#btn_pag:disabled { background-color: #252b38; color: #4a5568; border: 1px solid #252b38; }

/* Label Paginação */
QLabel#lbl_pag { color: #a0aec0; background-color: #1b212d; font-weight: bold; font-size: 13px; }
"""

class PageRelatorio(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("PageRelatorio")
        self.controller = RelatorioController()
        self.setWindowTitle("Relatório Geral de Estoque")
        self.setStyleSheet(STYLE_SHEET)
        
        # Variáveis de Dados e Paginação
        self.todos_dados = []    
        self.pagina_atual = 1
        self.itens_por_pagina = 50 
        self.total_paginas = 1

        self.setup_ui()
        self.carregar_dados() # Busca inicial

    def setup_ui(self):
        # 1. Layout Principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 2. CARD
        self.card = QFrame()
        self.card.setObjectName("FormCard")
        
        card_layout = QVBoxLayout(self.card)

        # 3. CABEÇALHO
        header_layout = QHBoxLayout()
        
        lbl_titulo = QLabel("Relatório Geral de Estoque")
        lbl_titulo.setObjectName("SectionTitle")
        
        self.btn_excel = QPushButton(" Exportar Excel")
        self.btn_excel.setCursor(Qt.PointingHandCursor)
        self.btn_excel.setIcon(qta.icon('fa5s.file-excel', color='white')) 
        self.btn_excel.setObjectName("btn_excel") 
        self.btn_excel.clicked.connect(self.exportar)
        
        header_layout.addWidget(lbl_titulo, stretch=1) 
        header_layout.addWidget(self.btn_excel)
        
        card_layout.addLayout(header_layout)

        # 4. TABELA
        self.colunas = ["Status", "Cód. Análise", "Recebimento", "Cód. Cliente", "Razão Social", 
                        "Nota Fiscal", "Produto", "Num. Série", "Cód. Avaría", "Valor", "Ressarc."]
        
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.colunas))
        self.table.setHorizontalHeaderLabels(self.colunas)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setFocusPolicy(Qt.NoFocus)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)
        header.setDefaultSectionSize(110)
        
        card_layout.addWidget(self.table)

        # 5. PAGINAÇÃO
        pag_layout = QHBoxLayout()
        
        self.btn_prev = QPushButton(" Anterior")
        self.btn_prev.setObjectName("btn_pag")
        self.btn_prev.setIcon(qta.icon('fa5s.chevron-left', color='white')) 
        self.btn_prev.setCursor(Qt.PointingHandCursor)
        self.btn_prev.clicked.connect(self.voltar_pagina)

        self.lbl_paginacao = QLabel(f"Página 0 de 0")
        self.lbl_paginacao.setObjectName("lbl_pag")
        self.lbl_paginacao.setAlignment(Qt.AlignCenter)

        self.btn_next = QPushButton("Próximo ")
        self.btn_next.setObjectName("btn_pag")
        self.btn_next.setLayoutDirection(Qt.RightToLeft)
        self.btn_next.setIcon(qta.icon('fa5s.chevron-right', color='white'))
        self.btn_next.setCursor(Qt.PointingHandCursor)
        self.btn_next.clicked.connect(self.avancar_pagina)

        pag_layout.addWidget(self.btn_prev)
        pag_layout.addStretch()
        pag_layout.addWidget(self.lbl_paginacao)
        pag_layout.addStretch()
        pag_layout.addWidget(self.btn_next)

        card_layout.addLayout(pag_layout)

        # Adiciona o card ao layout principal
        main_layout.addWidget(self.card)

    def carregar_dados(self):
        try:
            raw_data = self.controller.buscar_dados()
            
            self.todos_dados = []
            for d in raw_data:
                linha = [
                    str(d.get('status', '')), 
                    str(d.get('codigo_analise', '')), 
                    str(d.get('recebimento', '')), 
                    str(d.get('codigo_cliente', '-')), 
                    str(d.get('razao_social', '')), 
                    str(d.get('numero_nota', '')),
                    str(d.get('codigo_produto', '')), 
                    str(d.get('numero_serie', '')), 
                    str(d.get('codigo_avaria', '')),
                    f"R$ {float(d.get('valor_item', 0)):.2f}", 
                    f"R$ {float(d.get('ressarcimento', 0)):.2f}"
                ]
                self.todos_dados.append(linha)

            total_itens = len(self.todos_dados)
            self.total_paginas = math.ceil(total_itens / self.itens_por_pagina)
            if self.total_paginas < 1: self.total_paginas = 1

            self.pagina_atual = 1
            self.atualizar_tabela()
            
        except Exception as e:
            print(f"Erro ao buscar dados: {e}")
            QMessageBox.critical(self, "Erro", f"Falha ao carregar dados: {str(e)}")

    def atualizar_tabela(self):
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
            self.atualizar_tabela()

    def voltar_pagina(self):
        if self.pagina_atual > 1:
            self.pagina_atual -= 1
            self.atualizar_tabela()

    def exportar(self):
        path, _ = QFileDialog.getSaveFileName(self, "Salvar Excel", "", "Excel Files (*.xlsx)")
        if path:
            if self.controller.exportar_excel(path):
                QMessageBox.information(self, "Sucesso", "Exportado com sucesso!")