import sys
import qtawesome as qta
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QLineEdit, QComboBox, 
                               QPushButton, QFrame, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QDoubleSpinBox, QMessageBox)
from PySide6.QtCore import Qt

# --- ESTILO DARK BLUE ---
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

/* --- CARDS (Onde ficam os widgets) --- */
QFrame#Card {
    background-color: #1b212d;
    border-radius: 8px;
    border: 1px solid #2c3545;
}

/* --- TÍTULOS --- */
QLabel#SectionTitle {
    background-color: #1b212d; 
    color: #8ab4f8; 
    font-size: 16px; 
    font-weight: bold;
    padding-bottom: 8px; 
    border-bottom: 1px solid #2c3545;
    margin-bottom: 10px;
}

/* --- INPUTS --- */
QLineEdit, QComboBox, QDoubleSpinBox {
    background-color: #171c26;
    border: 1px solid #2c3545;
    border-radius: 4px;
    padding: 8px;
    color: #e0e6ed;
}
QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #3a5f8a;
    background-color: #1a202c;
}

/* Remove setas do SpinBox */
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    width: 0px; height: 0px; border: none; background: transparent;
}

/* --- LABELS --- */
QLabel { 
    background-color: #1b212d; 
    color: #a0aec0; 
    font-weight: 500; 
    margin-top: 5px;
}

/* --- TABELA --- */
QTableWidget {
    background-color: #171c26; 
    gridline-color: #2c3545;   
    border: 1px solid #2c3545;
    border-radius: 4px;
}
QHeaderView::section {
    background-color: #283042; 
    color: #e0e6ed;
    padding: 6px;
    border: 1px solid #2c3545;
    font-weight: bold;
}
QTableWidget::item { padding: 5px; }
QTableWidget::item:selected {
    background-color: #3a5f8a;
    color: white;
}

/* --- BOTÕES --- */
QPushButton#btn_primary {
    background-color: #2e7d32; color: white; border: 1px solid #1b5e20; padding: 10px 20px; border-radius: 4px; font-weight: bold; margin-top: 10px;
}
QPushButton#btn_primary:hover { background-color: #388e3c; }

QPushButton#btn_danger {
    background-color: #c62828; color: white; border: 1px solid #b71c1c; padding: 10px 20px; border-radius: 4px; font-weight: bold; margin-top: 10px;
}
QPushButton#btn_danger:hover { background-color: #d32f2f; }
"""

class PageRetorno(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerenciamento de Estoque - Layout Dividido")
        self.resize(1100, 700)
        self.setStyleSheet(STYLE_SHEET)

        main_layout = QHBoxLayout(self) 
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        # =========================================================
        # LADO ESQUERDO: FORMULÁRIO (Card)
        # =========================================================
        self.frame_form = QFrame()
        self.frame_form.setObjectName("Card")
        # Tamanho mínimo para o formulário não ficar espremido
        self.frame_form.setMinimumWidth(300) 
        
        layout_form = QVBoxLayout(self.frame_form)
        layout_form.setContentsMargins(20, 20, 20, 20)

        # Título do Form
        lbl_titulo_form = QLabel("Novo Produto")
        lbl_titulo_form.setObjectName("SectionTitle")
        layout_form.addWidget(lbl_titulo_form)

        # Campos
        self.txt_codigo = QLineEdit()
        self.txt_codigo.setPlaceholderText("Ex: P005")
        
        self.txt_descricao = QLineEdit()
        self.txt_descricao.setPlaceholderText("Nome do produto...")

        self.combo_categoria = QComboBox()
        self.combo_categoria.addItems(["Peças Motor", "Freios", "Elétrica", "Suspensão", "Acessórios"])

        self.spin_preco = QDoubleSpinBox()
        self.spin_preco.setPrefix("R$ ")
        self.spin_preco.setRange(0, 99999)
        self.spin_preco.setAlignment(Qt.AlignRight)

        # Adicionando ao layout vertical do form
        layout_form.addWidget(QLabel("Código:"))
        layout_form.addWidget(self.txt_codigo)
        
        layout_form.addWidget(QLabel("Descrição:"))
        layout_form.addWidget(self.txt_descricao)
        
        layout_form.addWidget(QLabel("Categoria:"))
        layout_form.addWidget(self.combo_categoria)
        
        layout_form.addWidget(QLabel("Preço Venda:"))
        layout_form.addWidget(self.spin_preco)

        layout_form.addStretch() # Empurra botões para baixo

        # Botões
        self.btn_salvar = QPushButton(" Adicionar")
        self.btn_salvar.setObjectName("btn_primary")
        self.btn_salvar.setIcon(qta.icon('fa5s.plus', color='white'))
        self.btn_salvar.setCursor(Qt.PointingHandCursor)
        self.btn_salvar.clicked.connect(self.adicionar_na_tabela)

        self.btn_limpar = QPushButton(" Limpar Campos")
        self.btn_limpar.setObjectName("btn_danger")
        self.btn_limpar.setIcon(qta.icon('fa5s.eraser', color='white'))
        self.btn_limpar.setCursor(Qt.PointingHandCursor)
        self.btn_limpar.clicked.connect(self.limpar_campos)

        layout_form.addWidget(self.btn_salvar)
        layout_form.addWidget(self.btn_limpar)

        # =========================================================
        # LADO DIREITO: TABELA (Card)
        # =========================================================
        self.frame_table = QFrame()
        self.frame_table.setObjectName("Card")
        
        layout_table = QVBoxLayout(self.frame_table)
        layout_table.setContentsMargins(20, 20, 20, 20)

        # Título da Tabela
        lbl_titulo_table = QLabel("Produtos Cadastrados")
        lbl_titulo_table.setObjectName("SectionTitle")
        layout_table.addWidget(lbl_titulo_table)

        # Tabela
        self.table = QTableWidget()
        colunas = ["Código", "Descrição", "Categoria", "Preço"]
        self.table.setColumnCount(len(colunas))
        self.table.setHorizontalHeaderLabels(colunas)
        
        # Estilo Tabela
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Headers
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch) # Distribui espaço
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents) # Codigo pequeno

        layout_table.addWidget(self.table)

        # =========================================================
        # ADICIONANDO AO LAYOUT PRINCIPAL (DIVISÃO)
        # =========================================================
        # stretch=1 : O Formulário ocupa 1 parte
        main_layout.addWidget(self.frame_form, stretch=1)
        
        # stretch=2 : A Tabela ocupa 2 partes (é mais larga)
        main_layout.addWidget(self.frame_table, stretch=2)

        # Dados iniciais para exemplo
        self.adicionar_linha("P001", "Filtro de Óleo", "Peças Motor", 45.90)
        self.adicionar_linha("P002", "Pastilha Freio Diant.", "Freios", 120.00)

    # --- LÓGICA ---
    def adicionar_na_tabela(self):
        cod = self.txt_codigo.text()
        desc = self.txt_descricao.text()
        cat = self.combo_categoria.currentText()
        preco = self.spin_preco.value()

        if not cod or not desc:
            QMessageBox.warning(self, "Aviso", "Preencha Código e Descrição.")
            return

        self.adicionar_linha(cod, desc, cat, preco)
        self.limpar_campos()
        self.txt_codigo.setFocus()

    def adicionar_linha(self, cod, desc, cat, preco):
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        def make_item(text, center=True):
            it = QTableWidgetItem(str(text))
            if center: it.setTextAlignment(Qt.AlignCenter)
            return it

        self.table.setItem(row, 0, make_item(cod))
        self.table.setItem(row, 1, make_item(desc, center=False))
        self.table.setItem(row, 2, make_item(cat))
        self.table.setItem(row, 3, make_item(f"R$ {preco:.2f}"))

    def limpar_campos(self):
        self.txt_codigo.clear()
        self.txt_descricao.clear()
        self.spin_preco.setValue(0)
        self.combo_categoria.setCurrentIndex(0)