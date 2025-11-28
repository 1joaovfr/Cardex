from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QTableWidget, 
                               QTableWidgetItem, QHeaderView, QMessageBox, QFileDialog, QLabel, QHBoxLayout)
import qtawesome as qta
from controllers import RelatorioController

STYLE = """
QWidget { background-color: #12161f; color: #dce1e8; font-family: 'Segoe UI'; }
QTableWidget { background-color: #171c26; border: none; alternate-background-color: #202736; gridline-color: #2c3545; }
QHeaderView::section { background-color: #283042; color: #e0e6ed; padding: 6px; border: 1px solid #2c3545; font-weight: bold; }
QPushButton#btn_excel { background-color: #2e7d32; color: white; border: 1px solid #1b5e20; padding: 8px 15px; border-radius: 4px; font-weight: bold; }
QPushButton#btn_excel:hover { background-color: #388e3c; }
"""

class PageRelatorio(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = RelatorioController()
        self.setStyleSheet(STYLE)
        
        layout = QVBoxLayout(self)
        
        top_bar = QHBoxLayout()
        lbl_tit = QLabel("Relatório Geral")
        lbl_tit.setStyleSheet("font-size: 18px; font-weight: bold; color: #8ab4f8;")
        
        self.btn_excel = QPushButton(" Exportar Excel")
        self.btn_excel.setObjectName("btn_excel")
        self.btn_excel.setIcon(qta.icon('fa5s.file-excel', color='white'))
        self.btn_excel.clicked.connect(self.exportar)
        
        top_bar.addWidget(lbl_tit)
        top_bar.addStretch()
        top_bar.addWidget(self.btn_excel)
        layout.addLayout(top_bar)
        
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(["Status", "Cod. Analise", "Nota", "Cliente", "Produto", "Defeito", "Valor", "Ressarc."])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)
        
        self.carregar()

    def carregar(self):
        dados = self.controller.buscar_dados()
        self.table.setRowCount(0)
        for row, d in enumerate(dados):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(d['status']))
            self.table.setItem(row, 1, QTableWidgetItem(d['codigo_analise']))
            self.table.setItem(row, 2, QTableWidgetItem(d['numero_nota']))
            self.table.setItem(row, 3, QTableWidgetItem(d['razao_social']))
            self.table.setItem(row, 4, QTableWidgetItem(d['codigo_produto']))
            self.table.setItem(row, 5, QTableWidgetItem(d['codigo_avaria']))
            self.table.setItem(row, 6, QTableWidgetItem(str(d['valor_item'])))
            self.table.setItem(row, 7, QTableWidgetItem(str(d['ressarcimento'])))

    def exportar(self):
        path, _ = QFileDialog.getSaveFileName(self, "Salvar Excel", "", "Excel Files (*.xlsx)")
        if path:
            if self.controller.exportar_excel(path):
                QMessageBox.information(self, "Sucesso", "Exportado com sucesso!")