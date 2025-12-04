import sys
import qtawesome as qta
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                               QComboBox, QPushButton, QFrame, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QDoubleSpinBox, QMessageBox)
from PySide6.QtCore import Qt
from controllers import RetornoController

STYLE_SHEET = """
QWidget { background-color: #12161f; color: #dce1e8; font-family: 'Segoe UI', sans-serif; font-size: 13px; }
QFrame#Card { background-color: #1b212d; border-radius: 8px; border: 1px solid #2c3545; }
QLabel#SectionTitle { background-color: #1b212d; color: #8ab4f8; font-size: 16px; font-weight: bold; padding-bottom: 8px; border-bottom: 1px solid #2c3545; margin-bottom: 10px; }
QLineEdit, QComboBox, QDoubleSpinBox { background-color: #171c26; border: 1px solid #2c3545; border-radius: 4px; padding: 8px; color: #e0e6ed; }
QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus { border: 1px solid #3a5f8a; background-color: #1a202c; }
QTableWidget { background-color: #171c26; gridline-color: #2c3545; border: 1px solid #2c3545; border-radius: 4px; }
QHeaderView::section { background-color: #283042; color: #e0e6ed; padding: 6px; border: 1px solid #2c3545; font-weight: bold; }
QPushButton#btn_primary { background-color: #2e7d32; color: white; border: 1px solid #1b5e20; padding: 10px 20px; border-radius: 4px; font-weight: bold; margin-top: 10px; }
QPushButton#btn_primary:hover { background-color: #388e3c; }
"""

class PageRetorno(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = RetornoController()
        self.setWindowTitle("Gerenciamento de Estoque")
        self.setStyleSheet(STYLE_SHEET)

        main_layout = QHBoxLayout(self) 
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # LADO ESQUERDO: FORM
        self.frame_form = QFrame(objectName="Card")
        self.frame_form.setMinimumWidth(300) 
        layout_form = QVBoxLayout(self.frame_form)
        layout_form.setContentsMargins(20, 20, 20, 20)

        lbl_titulo_form = QLabel("Novo Produto")
        lbl_titulo_form.setObjectName("SectionTitle")
        layout_form.addWidget(lbl_titulo_form)

        self.txt_codigo = QLineEdit(placeholderText="Ex: P005")
        self.txt_descricao = QLineEdit(placeholderText="Nome do produto...")
        self.combo_categoria = QComboBox()
        self.combo_categoria.addItems(["Peças Motor", "Freios", "Elétrica", "Suspensão"])
        self.spin_preco = QDoubleSpinBox()
        self.spin_preco.setPrefix("R$ ")
        self.spin_preco.setRange(0, 99999)

        layout_form.addWidget(QLabel("Código:"))
        layout_form.addWidget(self.txt_codigo)
        layout_form.addWidget(QLabel("Descrição:"))
        layout_form.addWidget(self.txt_descricao)
        layout_form.addWidget(QLabel("Categoria:"))
        layout_form.addWidget(self.combo_categoria)
        layout_form.addWidget(QLabel("Preço Venda:"))
        layout_form.addWidget(self.spin_preco)
        layout_form.addStretch() 

        self.btn_salvar = QPushButton(" Adicionar")
        self.btn_salvar.setObjectName("btn_primary")
        self.btn_salvar.setIcon(qta.icon('fa5s.plus', color='white'))
        self.btn_salvar.clicked.connect(self.salvar_produto)
        layout_form.addWidget(self.btn_salvar)

        # LADO DIREITO: TABELA
        self.frame_table = QFrame(objectName="Card")
        layout_table = QVBoxLayout(self.frame_table)
        layout_table.setContentsMargins(20, 20, 20, 20)

        lbl_titulo_table = QLabel("Produtos Cadastrados")
        lbl_titulo_table.setObjectName("SectionTitle")
        layout_table.addWidget(lbl_titulo_table)

        self.table = QTableWidget()
        colunas = ["Código", "Descrição", "Categoria", "Preço"]
        self.table.setColumnCount(len(colunas))
        self.table.setHorizontalHeaderLabels(colunas)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        layout_table.addWidget(self.table)

        main_layout.addWidget(self.frame_form, stretch=1)
        main_layout.addWidget(self.frame_table, stretch=2)

    def salvar_produto(self):
        cod = self.txt_codigo.text()
        desc = self.txt_descricao.text()
        cat = self.combo_categoria.currentText()
        preco = self.spin_preco.value()

        if self.controller.salvar_produto(cod, desc, cat, preco):
            QMessageBox.information(self, "Sucesso", "Produto adicionado!")
            # Adiciona visualmente só para feedback imediato
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(cod))
            self.table.setItem(row, 1, QTableWidgetItem(desc))
            self.table.setItem(row, 2, QTableWidgetItem(cat))
            self.table.setItem(row, 3, QTableWidgetItem(f"R$ {preco:.2f}"))
        else:
            QMessageBox.warning(self, "Erro", "Erro ao salvar (Código duplicado?)")