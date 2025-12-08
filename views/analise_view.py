import sys
import qtawesome as qta
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                               QComboBox, QPushButton, QFrame, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QMessageBox)
from PySide6.QtCore import Qt

# --- Importação do Controller ---
from controllers.analise_controller import AnaliseController

# --- Importação do Estilo Padronizado ---
# Certifique-se de ter criado o arquivo styles/analise_styles.py
from styles.analise_styles import ANALISE_STYLES

class PageAnalise(QWidget):
    def __init__(self):
        super().__init__()
        # --- INTEGRAÇÃO CONTROLLER ---
        self.controller = AnaliseController()
        
        self.setWindowTitle("Análise Técnica de Itens")
        
        # --- APLICAÇÃO DO ESTILO ---
        self.setStyleSheet(ANALISE_STYLES)

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
        
        # Colunas Solicitadas
        colunas = ["ENTRADA", "ITEM", "CÓD. ANÁLISE", "NOTA FISCAL", "RESSARCIMENTO"]
        self.table.setColumnCount(len(colunas))
        self.table.setHorizontalHeaderLabels(colunas)
        
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setShowGrid(True) 
        
        # Todas as colunas com mesmo tamanho (Stretch)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
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
        self.txt_id_item = QLineEdit(placeholderText="Cód. análise", readOnly=True)
        self.txt_id_item.setFixedWidth(100) 
        
        self.txt_peca_nome = QLineEdit(placeholderText="Selecione um item...", readOnly=True)
        
        self.txt_serie = QLineEdit(placeholderText="Nº Série")
        self.txt_serie.setFixedWidth(110)
        
        self.combo_origem = QComboBox()
        self.combo_origem.addItems(["Nacional", "Importado", "Reindustrializado"])
        self.combo_origem.setFixedWidth(110)

        self.txt_fornecedor = QLineEdit(placeholderText="Fabricante / Distribuidor")

        row1.addWidget(QLabel("Cód.:"))
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
        # O estilo (borda/cor) virá do stylesheet agora, baseado no ID

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

    def criar_item_tabela(self, texto):
        """Helper para criar item centralizado"""
        item = QTableWidgetItem(str(texto) if texto else "")
        item.setTextAlignment(Qt.AlignCenter)
        return item

    def carregar_dados_tabela(self):
        # Busca a lista de OBJETOS DTO do controller
        itens_dto = self.controller.listar_pendentes()
        
        self.table.setRowCount(0)
        
        # Agora 'item' é um objeto ItemPendenteDTO
        for item in itens_dto:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # 1. ENTRADA (Acessando atributo .data_fmt e .id)
            val_entrada = self.criar_item_tabela(item.data_fmt)
            val_entrada.setData(Qt.UserRole, item.id) 
            self.table.setItem(row, 0, val_entrada)

            # 2. ITEM (Acessando .codigo_item)
            self.table.setItem(row, 1, self.criar_item_tabela(item.codigo_item))

            # 3. CÓD. ANÁLISE (Acessando .codigo_analise)
            self.table.setItem(row, 2, self.criar_item_tabela(item.codigo_analise))

            # 4. NOTA FISCAL (Acessando .numero_nota)
            self.table.setItem(row, 3, self.criar_item_tabela(item.numero_nota))

            # 5. RESSARCIMENTO (Acessando .ressarcimento)
            if item.ressarcimento is not None:
                valor_fmt = f"{item.ressarcimento:.2f}".replace('.', ',')
            else:
                valor_fmt = "0,00"

            self.table.setItem(row, 4, self.criar_item_tabela(valor_fmt))
            
    def carregar_item_para_analise(self, item):
        row = item.row()
        
        # Recupera o ID oculto na coluna 0 (ENTRADA)
        id_item = str(self.table.item(row, 0).data(Qt.UserRole))

        codigo_analise_visual = self.table.item(row, 2).text()
        
        # Recupera a descrição na coluna 1 (ITEM)
        desc_item = self.table.item(row, 1).text()

        self.bloquear_form(False)
        self.item_atual = id_item
        self.txt_id_item.setText(codigo_analise_visual)
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
        
        # Força a atualização do estilo (necessário ao mudar o objectName dinamicamente)
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
            
            # Atualiza estilo do status para neutro
            self.lbl_status_resultado.style().unpolish(self.lbl_status_resultado)
            self.lbl_status_resultado.style().polish(self.lbl_status_resultado)
            
            self.carregar_dados_tabela()
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))