import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                               QComboBox, QPushButton, QFrame, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QDoubleSpinBox, QMessageBox, QRadioButton, QButtonGroup, QDateEdit)
from PySide6.QtCore import Qt, QDate
from controllers.retorno_controller import RetornoController

STYLE_SHEET = """
QWidget { background-color: #12161f; color: #dce1e8; font-family: 'Segoe UI', sans-serif; font-size: 13px; }
QFrame#Card { background-color: #1b212d; border-radius: 8px; border: 1px solid #2c3545; }
QLineEdit, QComboBox, QDoubleSpinBox, QDateEdit { background-color: #171c26; border: 1px solid #2c3545; padding: 8px; color: white; }
QTableWidget { background-color: #171c26; border: 1px solid #2c3545; }
QHeaderView::section { background-color: #283042; color: white; padding: 4px; }
QPushButton { background-color: #3a5f8a; color: white; border: none; padding: 8px; border-radius: 4px; }
QPushButton:hover { background-color: #4a6f9a; }
QPushButton#btn_success { background-color: #2e7d32; }
QPushButton#btn_danger { background-color: #c62828; }
QLabel#TotalOk { color: #4caf50; font-weight: bold; font-size: 14px; }
QLabel#TotalErro { color: #f44336; font-weight: bold; font-size: 14px; }
"""

class PageRetorno(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = RetornoController()
        self.setStyleSheet(STYLE_SHEET)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # --- ÁREA 1: CABEÇALHO DO RETORNO (Input do Analista) ---
        self.frame_header = QFrame(objectName="Card")
        layout_header = QHBoxLayout(self.frame_header)
        
        # Seleção de Modo (CNPJ ou Grupo)
        self.group_tipo_cliente = QButtonGroup(self)
        self.radio_cnpj = QRadioButton("Por CNPJ")
        self.radio_grupo = QRadioButton("Por Grupo Econômico")
        self.radio_cnpj.setChecked(True)
        self.group_tipo_cliente.addButton(self.radio_cnpj)
        self.group_tipo_cliente.addButton(self.radio_grupo)
        
        layout_header.addWidget(QLabel("Busca:"))
        layout_header.addWidget(self.radio_cnpj)
        layout_header.addWidget(self.radio_grupo)
        
        self.txt_busca = QLineEdit(placeholderText="Digite CNPJ ou Nome do Grupo...")
        self.btn_buscar = QPushButton("Buscar Pendências")
        self.btn_buscar.clicked.connect(self.buscar_notas)
        
        layout_header.addWidget(self.txt_busca)
        layout_header.addWidget(self.btn_buscar)
        
        # Dados da Nota de Retorno
        self.combo_tipo_retorno = QComboBox()
        self.combo_tipo_retorno.addItems(["GIRO", "SIMPLES"])
        
        self.txt_num_nota = QLineEdit(placeholderText="Nº Nota Retorno")
        self.date_emissao = QDateEdit()
        self.date_emissao.setDate(QDate.currentDate())
        self.date_emissao.setCalendarPopup(True)
        
        self.spin_valor_retorno = QDoubleSpinBox()
        self.spin_valor_retorno.setPrefix("R$ ")
        self.spin_valor_retorno.setRange(0, 10000000) # Aumentei o range
        # REMOVIDO: self.spin_valor_retorno.setPlaceholderText(...) <- Causava o erro
        self.spin_valor_retorno.setToolTip("Digite o Valor Total da Nota de Retorno")
        self.spin_valor_retorno.valueChanged.connect(self.atualizar_totais) 

        layout_header.addWidget(QLabel("|  Dados Retorno:"))
        layout_header.addWidget(self.combo_tipo_retorno)
        layout_header.addWidget(self.txt_num_nota)
        layout_header.addWidget(self.date_emissao)
        layout_header.addWidget(self.spin_valor_retorno)

        main_layout.addWidget(self.frame_header)

        # --- ÁREA 2: AS TABELAS (Dual List Box) ---
        layout_tables = QHBoxLayout()
        
        # Tabela Esquerda: Itens Disponíveis (Dívidas)
        self.table_origem = self.criar_tabela(["ID", "NF Origem", "Item", "Saldo (R$)", "Cliente"])
        
        # Botões de Ação no Meio
        layout_btns = QVBoxLayout()
        self.btn_add = QPushButton(">>")
        self.btn_remove = QPushButton("<<")
        self.btn_add.clicked.connect(self.adicionar_item)
        self.btn_remove.clicked.connect(self.remover_item)
        layout_btns.addStretch()
        layout_btns.addWidget(self.btn_add)
        layout_btns.addWidget(self.btn_remove)
        layout_btns.addStretch()

        # Tabela Direita: Itens Selecionados para Abatimento
        self.table_destino = self.criar_tabela(["ID", "NF Origem", "Item", "Valor Abatido (R$)", "Cliente"])

        layout_tables.addWidget(self.table_origem, stretch=1)
        layout_tables.addLayout(layout_btns)
        layout_tables.addWidget(self.table_destino, stretch=1)
        
        main_layout.addLayout(layout_tables)

        # --- ÁREA 3: RODAPÉ E TOTAIS ---
        self.frame_footer = QFrame(objectName="Card")
        layout_footer = QHBoxLayout(self.frame_footer)
        
        self.lbl_status = QLabel("Aguardando seleção...")
        self.lbl_status.setObjectName("TotalOk") 
        
        self.btn_confirmar = QPushButton("CONFIRMAR RETORNO")
        self.btn_confirmar.setObjectName("btn_success")
        self.btn_confirmar.setMinimumHeight(40)
        self.btn_confirmar.clicked.connect(self.salvar_final)
        self.btn_confirmar.setEnabled(False)

        layout_footer.addWidget(self.lbl_status)
        layout_footer.addStretch()
        layout_footer.addWidget(self.btn_confirmar)

        main_layout.addWidget(self.frame_footer)

    def criar_tabela(self, colunas):
        table = QTableWidget()
        table.setColumnCount(len(colunas))
        table.setHorizontalHeaderLabels(colunas)
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        return table

    def buscar_notas(self):
        modo = "CNPJ" if self.radio_cnpj.isChecked() else "GRUPO"
        termo = self.txt_busca.text()
        
        itens = self.controller.buscar_pendencias(termo, modo)
        
        self.table_origem.setRowCount(0)
        self.table_destino.setRowCount(0) 
        
        for row, item in enumerate(itens):
            self.table_origem.insertRow(row)
            self.table_origem.setItem(row, 0, QTableWidgetItem(str(item['id'])))
            self.table_origem.setItem(row, 1, QTableWidgetItem(str(item['numero_nota'])))
            self.table_origem.setItem(row, 2, QTableWidgetItem(f"{item['codigo_item']}"))
            self.table_origem.setItem(row, 3, QTableWidgetItem(f"{item['saldo_financeiro']:.2f}"))
            self.table_origem.setItem(row, 4, QTableWidgetItem(item['nome_cliente']))

    def adicionar_item(self):
        row = self.table_origem.currentRow()
        if row < 0: return

        # Pega os dados
        id_item = self.table_origem.item(row, 0).text()
        nf = self.table_origem.item(row, 1).text()
        sku = self.table_origem.item(row, 2).text()
        saldo = self.table_origem.item(row, 3).text()
        cliente = self.table_origem.item(row, 4).text()

        # Adiciona na direita
        dest_row = self.table_destino.rowCount()
        self.table_destino.insertRow(dest_row)
        self.table_destino.setItem(dest_row, 0, QTableWidgetItem(id_item))
        self.table_destino.setItem(dest_row, 1, QTableWidgetItem(nf))
        self.table_destino.setItem(dest_row, 2, QTableWidgetItem(sku))
        self.table_destino.setItem(dest_row, 3, QTableWidgetItem(saldo))
        self.table_destino.setItem(dest_row, 4, QTableWidgetItem(cliente))

        # Remove da origem visualmente
        self.table_origem.removeRow(row)
        self.atualizar_totais()

    def remover_item(self):
        row = self.table_destino.currentRow()
        if row < 0: return

        # Remove da direita e "força" usuário a buscar novamente se quiser o item de volta
        # (Para simplificar a lógica visual sem cache local complexo)
        self.table_destino.removeRow(row)
        self.atualizar_totais()

    def atualizar_totais(self):
        valor_nota_retorno = self.spin_valor_retorno.value()
        
        total_selecionado = 0.0
        for i in range(self.table_destino.rowCount()):
            val_str = self.table_destino.item(i, 3).text().replace(",", ".")
            total_selecionado += float(val_str)

        diferenca = valor_nota_retorno - total_selecionado
        
        if total_selecionado == 0:
            self.lbl_status.setText("Selecione itens para abater.")
            self.lbl_status.setObjectName("TotalOk")
            self.btn_confirmar.setEnabled(False)
        elif total_selecionado > valor_nota_retorno:
            # Caso especial: Se o usuário digitou zero no valor da nota, avisar
            if valor_nota_retorno == 0:
                 self.lbl_status.setText(f"Digite o valor da Nota de Retorno acima.")
            else:
                 self.lbl_status.setText(f"ERRO: Itens (R$ {total_selecionado:.2f}) excedem Nota Retorno (R$ {valor_nota_retorno:.2f})")
            
            self.lbl_status.setObjectName("TotalErro")
            self.btn_confirmar.setEnabled(False)
        else:
            self.lbl_status.setText(f"OK. Crédito Restante/Sobra: R$ {diferenca:.2f}")
            self.lbl_status.setObjectName("TotalOk")
            self.btn_confirmar.setEnabled(True)
        
        self.lbl_status.style().unpolish(self.lbl_status)
        self.lbl_status.style().polish(self.lbl_status)

    def salvar_final(self):
        cabecalho = {
            "numero": self.txt_num_nota.text(),
            "data": self.date_emissao.date().toString("yyyy-MM-dd"),
            "tipo": self.combo_tipo_retorno.currentText(),
            "valor_total": self.spin_valor_retorno.value(),
            "cnpj": self.txt_busca.text() if self.radio_cnpj.isChecked() else None,
            "grupo": self.txt_busca.text() if self.radio_grupo.isChecked() else None
        }

        itens = []
        for i in range(self.table_destino.rowCount()):
            itens.append({
                "id": self.table_destino.item(i, 0).text(),
                "valor_abatido": float(self.table_destino.item(i, 3).text())
            })

        sucesso, msg = self.controller.processar_retorno(cabecalho, itens)
        
        if sucesso:
            QMessageBox.information(self, "Sucesso", msg)
            self.resetar_tela()
        else:
            QMessageBox.warning(self, "Erro", msg)

    def resetar_tela(self):
        self.table_destino.setRowCount(0)
        self.table_origem.setRowCount(0)
        self.spin_valor_retorno.setValue(0)
        self.txt_num_nota.clear()
        self.lbl_status.setText("Aguardando seleção...")