import sys
import qtawesome as qta
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                               QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt
from controllers import RelatorioController

# --- ESTILO ORIGINAL ---
STYLE_SHEET = """
QWidget { background-color: #12161f; color: #dce1e8; font-family: 'Segoe UI', sans-serif; }
QPushButton#btn_excel { background-color: #2e7d32; color: white; border: 1px solid #1b5e20; padding: 6px 15px; border-radius: 4px; font-weight: bold; }
QPushButton#btn_excel:hover { background-color: #388e3c; }
QTableWidget { background-color: #171c26; alternate-background-color: #202736; gridline-color: #2c3545; border: none; font-size: 13px; }
QHeaderView::section { background-color: #283042; color: #e0e6ed; padding: 6px; border: 1px solid #2c3545; font-weight: bold; text-transform: uppercase; }
QTableWidget::item:selected { background-color: #3a5f8a; color: white; }
QFrame#PagContainer { background-color: #171c26; border-top: 1px solid #2c3545; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px; }
QPushButton#btn_pag { background-color: #3a5f8a; color: white; border: 1px solid #2c3e50; padding: 8px 15px; border-radius: 4px; font-weight: bold; }
QPushButton#btn_pag:hover { background-color: #4b7bc0; }
QPushButton#btn_pag:disabled { background-color: #252b38; color: #4a5568; }
"""

class PageRelatorio(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = RelatorioController()
        self.setWindowTitle("Relatório Geral de Estoque")
        self.setStyleSheet(STYLE_SHEET)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # BARRA DE TOPO
        top_bar = QHBoxLayout()
        lbl_titulo = QLabel("Relatório Geral de Estoque")
        lbl_titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #8ab4f8;")
        
        self.btn_excel = QPushButton(" Exportar Excel")
        self.btn_excel.setCursor(Qt.PointingHandCursor)
        self.btn_excel.setIcon(qta.icon('fa5s.file-excel', color='white')) 
        self.btn_excel.setObjectName("btn_excel") 
        self.btn_excel.clicked.connect(self.exportar)
        
        top_bar.addWidget(lbl_titulo)
        top_bar.addStretch()
        top_bar.addWidget(self.btn_excel)
        layout.addLayout(top_bar)
        layout.addSpacing(10) 

        # TABELA
        self.colunas = ["Status", "Cód. Análise", "Recebimento", "Cód. Cliente", "Razão Social", 
                        "Nota Fiscal", "Produto", "Num. Série", "Cód. Avaría", "Valor", "Ressarc."]
        
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
        
        layout.addWidget(self.table)
        self.carregar_dados()

    def carregar_dados(self):
        dados = self.controller.buscar_dados()
        self.table.setRowCount(0)
        for row, d in enumerate(dados):
            self.table.insertRow(row)
            # Mapeia as chaves do dict retornado pelo controller para a ordem das colunas
            valores = [
                d['status'], d['codigo_analise'], d['recebimento'], 
                d.get('codigo_cliente', '-'), d['razao_social'], d['numero_nota'],
                d['codigo_produto'], d['numero_serie'], d['codigo_avaria'],
                f"{d['valor_item']:.2f}", f"{d['ressarcimento']:.2f}"
            ]
            for col, val in enumerate(valores):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

    def exportar(self):
        path, _ = QFileDialog.getSaveFileName(self, "Salvar Excel", "", "Excel Files (*.xlsx)")
        if path:
            if self.controller.exportar_excel(path):
                QMessageBox.information(self, "Sucesso", "Exportado com sucesso!")