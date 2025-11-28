from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QMessageBox)
import qtawesome as qta
from controllers import RetornoController

STYLE = """
QWidget { background-color: #12161f; color: #dce1e8; font-family: 'Segoe UI'; }
QFrame { background-color: #1b212d; border-radius: 8px; border: 1px solid #2c3545; }
QPushButton { background-color: #3a5f8a; color: white; border: none; padding: 10px; border-radius: 4px; }
"""

class PageRetorno(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = RetornoController()
        self.setStyleSheet(STYLE)
        
        layout = QHBoxLayout(self)
        
        frame = QFrame()
        v_layout = QVBoxLayout(frame)
        
        lbl = QLabel("Módulo de Retorno / Estoque")
        lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #8ab4f8;")
        v_layout.addWidget(lbl)
        
        self.btn_teste = QPushButton(" Teste de Conexão DB")
        self.btn_teste.setIcon(qta.icon('fa5s.database', color='white'))
        self.btn_teste.clicked.connect(self.teste_db)
        v_layout.addWidget(self.btn_teste)
        v_layout.addStretch()
        
        layout.addWidget(frame)
        
    def teste_db(self):
        if self.controller.salvar_produto("TESTE-AUTO", "Produto Teste", "Geral", 1.0):
            QMessageBox.information(self, "OK", "Produto Teste inserido no banco!")
        else:
            QMessageBox.warning(self, "Erro", "Falha ao inserir.")