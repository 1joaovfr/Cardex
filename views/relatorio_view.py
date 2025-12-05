import sys
import math
import os 
from datetime import date, datetime, timedelta
import qtawesome as qta
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                               QFrame, QTableWidget, QTableWidgetItem, QHeaderView, 
                               QFileDialog, QMessageBox, QAbstractItemView,
                               QDialog, QDateEdit, QFormLayout)
from PySide6.QtCore import Qt, QDate, QPoint
from controllers import RelatorioController

# --- CSS BASE ---
STYLE_SHEET_BASE = """
QWidget { background-color: #12161f; color: #dce1e8; font-family: 'Segoe UI', sans-serif; font-size: 13px; }

/* POPUP PEQUENO */
QDialog { 
    background-color: #1b212d; 
    border: 1px solid #3a5f8a; 
    border-radius: 4px; 
}

/* CALENDÁRIO */
QCalendarWidget QWidget { alternate-background-color: #202736; }
QCalendarWidget QAbstractItemView:enabled { color: #dce1e8; background-color: #171c26; selection-background-color: #3a5f8a; selection-color: white; }
QCalendarWidget QToolButton { color: #dce1e8; icon-size: 20px; background-color: #1b212d; }
QCalendarWidget QMenu { background-color: #1b212d; color: #dce1e8; }
QCalendarWidget QSpinBox { background-color: #171c26; color: #dce1e8; }
QCalendarWidget QAbstractItemView:disabled { color: #4a5568; }

/* BOTÃO CONFIRMAR (Compacto) */
QPushButton#btn_confirmar { 
    background-color: #2e7d32; 
    color: white; 
    border: none; 
    padding: 6px; 
    border-radius: 3px; 
    font-weight: bold; 
    font-size: 12px;
}
QPushButton#btn_confirmar:hover { background-color: #388e3c; }

/* ESTILOS DA TELA PRINCIPAL */
QFrame#FormCard { background-color: #1b212d; border-radius: 8px; border: 1px solid #2c3545; }
QLabel#SectionTitle { color: #8ab4f8; background-color: #1b212d; font-size: 15px; font-weight: bold; padding-bottom: 5px; border-bottom: 1px solid #2c3545; }

/* TABELA */
QTableWidget { background-color: #171c26; alternate-background-color: #202736; gridline-color: #2c3545; border: none; font-size: 13px; }
QHeaderView::section { background-color: #283042; color: #e0e6ed; padding: 6px; border: 1px solid #2c3545; font-weight: bold; text-transform: uppercase; }
QTableWidget::item:selected { background-color: #3a5f8a; color: white; }

/* SCROLLBARS */
QScrollBar:vertical { background: #171c26; width: 8px; margin: 0px; }
QScrollBar::handle:vertical { background-color: #3a5f8a; min-height: 30px; border-radius: 4px; }
QScrollBar::handle:vertical:hover { background-color: #4b7bc0; }
QScrollBar:horizontal { background: #171c26; height: 8px; margin: 0px; }
QScrollBar::handle:horizontal { background-color: #3a5f8a; min-width: 30px; border-radius: 4px; }
QScrollBar::handle:horizontal:hover { background-color: #4b7bc0; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical, QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; height: 0px; background: none; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical, QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: none; }

/* BOTÕES GERAIS */
QPushButton { padding: 8px 15px; border-radius: 4px; font-weight: bold; }

/* Botão Excel Header */
QPushButton#btn_excel { background-color: transparent; border: none; padding: 5px; }
QPushButton#btn_excel:hover { background-color: #2c3545; border-radius: 4px; }

/* Paginação */
QPushButton#btn_pag { background-color: #3a5f8a; color: white; border: 1px solid #2c3e50; }
QPushButton#btn_pag:hover { background-color: #4b7bc0; }
QPushButton#btn_pag:disabled { background-color: #252b38; color: #4a5568; border: 1px solid #252b38; }
QLabel#lbl_pag { color: #a0aec0; background-color: #1b212d; font-weight: bold; font-size: 13px; }
"""

class ExportarPopup(QDialog):
    def __init__(self, target_widget, parent=None):
        super().__init__(parent)
        self.target_widget = target_widget 
        
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setFixedWidth(200) 
        
        self.icon_path = self.gerar_icone_calendario()
        self.setStyleSheet(STYLE_SHEET_BASE + self.get_date_edit_style())
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        lbl_style = "color: #a0aec0; font-size: 11px; font-weight: bold;"
        
        lbl_ini = QLabel("De:")
        lbl_ini.setStyleSheet(lbl_style)
        self.dt_inicio = QDateEdit()
        self.dt_inicio.setCalendarPopup(True) 
        self.dt_inicio.setDisplayFormat("dd/MM/yyyy")
        hoje = date.today()
        self.dt_inicio.setDate(date(hoje.year, hoje.month, 1))
        
        lbl_fim = QLabel("Até:")
        lbl_fim.setStyleSheet(lbl_style)
        self.dt_fim = QDateEdit()
        self.dt_fim.setCalendarPopup(True)
        self.dt_fim.setDisplayFormat("dd/MM/yyyy")
        self.dt_fim.setDate(hoje)

        layout.addWidget(lbl_ini)
        layout.addWidget(self.dt_inicio)
        layout.addWidget(lbl_fim)
        layout.addWidget(self.dt_fim)
        
        self.btn_confirmar = QPushButton("Exportar")
        self.btn_confirmar.setObjectName("btn_confirmar")
        self.btn_confirmar.setCursor(Qt.PointingHandCursor)
        self.btn_confirmar.clicked.connect(self.accept) 
        
        layout.addSpacing(5)
        layout.addWidget(self.btn_confirmar)
        
        self.posicionar_janela()

    def posicionar_janela(self):
        # 1. Pega a posição absoluta do botão na tela
        pos_global = self.target_widget.mapToGlobal(QPoint(0, 0))
        
        # 2. Calcula o X: Alinha à direita do botão
        x = pos_global.x() + self.target_widget.width() - self.width()
        
        # 3. Calcula o Y: Logo abaixo do botão
        y = pos_global.y() + self.target_widget.height()
        
        self.move(x, y)

    def gerar_icone_calendario(self):
        icon = qta.icon('fa5s.calendar-alt', color='#8ab4f8') 
        caminho_arquivo = "temp_calendar_icon.png"
        icon.pixmap(16, 16).save(caminho_arquivo)
        return os.path.abspath(caminho_arquivo).replace("\\", "/")

    def get_date_edit_style(self):
        return f"""
        QDateEdit {{
            background-color: #171c26; border: 1px solid #2c3545; border-radius: 3px; 
            padding: 4px; color: #dce1e8; font-size: 12px; padding-right: 25px;
        }}
        QDateEdit:hover {{ border: 1px solid #3a5f8a; }}
        QDateEdit::drop-down {{
            subcontrol-origin: padding; subcontrol-position: top right; width: 25px;
            border-left: 1px solid #2c3545; background-color: #1b212d;
        }}
        QDateEdit::down-arrow {{ image: url("{self.icon_path}"); width: 14px; height: 14px; }}
        """

class PageRelatorio(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("PageRelatorio")
        self.controller = RelatorioController()
        self.setWindowTitle("Relatório Geral de Garantias")
        self.setStyleSheet(STYLE_SHEET_BASE)
        
        self.todos_dados = []    
        self.pagina_atual = 1
        self.itens_por_pagina = 50 
        self.total_paginas = 1

        self.setup_ui()
        self.carregar_dados() 

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self.card = QFrame()
        self.card.setObjectName("FormCard")
        card_layout = QVBoxLayout(self.card)

        # --- CABEÇALHO ---
        header_layout = QHBoxLayout()
        lbl_titulo = QLabel("Relatório Analítico de Garantias")
        lbl_titulo.setObjectName("SectionTitle")
        header_layout.addWidget(lbl_titulo, 1)
        
        self.btn_excel = QPushButton()
        self.btn_excel.setCursor(Qt.PointingHandCursor)
        self.btn_excel.setIcon(qta.icon('fa5s.file-excel', color='#8ab4f8', scale_factor=1.2)) 
        self.btn_excel.setIconSize(qta.QtCore.QSize(20, 20)) 
        self.btn_excel.setObjectName("btn_excel") 
        self.btn_excel.setToolTip("Exportar para Excel")
        self.btn_excel.clicked.connect(self.abrir_formulario_exportacao) 
        header_layout.addWidget(self.btn_excel)
        
        card_layout.addLayout(header_layout)

        # --- DEFINIÇÃO DE COLUNAS ---
        # ADICIONADO "Data Lanç."
        self.colunas = [
            "Status", "Cód. Análise", "Data Lanç.", "Recebimento", "Data Análise", 
            "CNPJ", "Cliente", "Grupo Cli.", "Cidade", "UF", "Região",
            "NF Entrada", "Cód. Item", "Grupo Item", "N. Série",
            "Cód. Avaria", "Desc. Avaria",
            "Valor", "Ressarc.",
            "NF Retorno", "Tipo Ret.", "Data Ret."
        ]
        
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
        header.setDefaultSectionSize(100)
        # Ajustes de largura
        header.resizeSection(0, 80)  # Status
        header.resizeSection(2, 90)  # Data Lanç (Novo)
        header.resizeSection(6, 200) # Nome Cliente (Índice mudou pois entrou coluna nova)
        header.resizeSection(16, 200) # Descrição Avaria
        
        card_layout.addWidget(self.table)

        # --- PAGINAÇÃO ---
        pag_layout = QHBoxLayout()
        self.btn_prev = QPushButton(" Anterior")
        self.btn_prev.setObjectName("btn_pag")
        self.btn_prev.setIcon(qta.icon('fa5s.chevron-left', color='white')) 
        self.btn_prev.clicked.connect(self.voltar_pagina)

        self.lbl_paginacao = QLabel(f"Página 0 de 0")
        self.lbl_paginacao.setObjectName("lbl_pag")
        self.lbl_paginacao.setAlignment(Qt.AlignCenter)

        self.btn_next = QPushButton("Próximo ")
        self.btn_next.setObjectName("btn_pag")
        self.btn_next.setLayoutDirection(Qt.RightToLeft)
        self.btn_next.setIcon(qta.icon('fa5s.chevron-right', color='white'))
        self.btn_next.clicked.connect(self.avancar_pagina)

        pag_layout.addWidget(self.btn_prev)
        pag_layout.addStretch()
        pag_layout.addWidget(self.lbl_paginacao)
        pag_layout.addStretch()
        pag_layout.addWidget(self.btn_next)

        card_layout.addLayout(pag_layout)
        main_layout.addWidget(self.card)

    def carregar_dados(self):
        try:
            raw_data = self.controller.buscar_dados()
            self.todos_dados = []
            
            for d in raw_data:
                # Funções auxiliares internas
                def safe_str(val, default=''):
                    return str(val) if val is not None else default

                def fmt_moeda(val):
                    try:
                        return f"R$ {float(val):.2f}"
                    except:
                        return "R$ 0.00"

                linha = [
                    safe_str(d.get('status')),
                    safe_str(d.get('codigo_analise')),
                    
                    # --- ADICIONADO AQUI ---
                    safe_str(d.get('data_lancamento')),
                    
                    safe_str(d.get('data_recebimento')),
                    safe_str(d.get('data_analise')),
                    
                    safe_str(d.get('cnpj')),
                    safe_str(d.get('nome_cliente')),
                    safe_str(d.get('grupo_cliente')),
                    safe_str(d.get('cidade')),
                    safe_str(d.get('estado')),
                    safe_str(d.get('regiao')),
                    
                    safe_str(d.get('nf_entrada')),
                    safe_str(d.get('codigo_item')),
                    safe_str(d.get('grupo_item')),
                    safe_str(d.get('numero_serie')),
                    
                    safe_str(d.get('codigo_avaria')),
                    safe_str(d.get('descricao_avaria')),
                    
                    fmt_moeda(d.get('valor_item')),
                    fmt_moeda(d.get('ressarcimento')),
                    
                    safe_str(d.get('nf_retorno')),   # Futuro
                    safe_str(d.get('tipo_retorno')), # Futuro
                    safe_str(d.get('data_retorno'))  # Futuro
                ]
                self.todos_dados.append(linha)
            
            total_itens = len(self.todos_dados)
            self.total_paginas = math.ceil(total_itens / self.itens_por_pagina)
            if self.total_paginas < 1: self.total_paginas = 1
            self.pagina_atual = 1
            self.atualizar_tabela()
            
        except Exception as e:
            print(f"Erro ao carregar dados na View: {e}")
            import traceback
            traceback.print_exc()

    def atualizar_tabela(self):
        inicio = (self.pagina_atual - 1) * self.itens_por_pagina
        fim = inicio + self.itens_por_pagina
        dados_da_pagina = self.todos_dados[inicio:fim]
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

    def abrir_formulario_exportacao(self):
        dialog = ExportarPopup(target_widget=self.btn_excel, parent=self)
        if dialog.exec(): 
            data_ini = dialog.dt_inicio.date().toPython()
            data_fim = dialog.dt_fim.date().toPython()
            
            if data_fim < data_ini:
                QMessageBox.warning(self, "Erro", "A data final não pode ser menor que a inicial.")
                return

            nome_arq = f"Relatorio_Geral_{data_ini}_{data_fim}.xlsx"
            path, _ = QFileDialog.getSaveFileName(self, "Salvar Excel", nome_arq, "Excel Files (*.xlsx)")
            
            if path:
                sucesso = self.controller.exportar_excel(path, data_ini, data_fim)
                if sucesso:
                    QMessageBox.information(self, "Sucesso", "Arquivo gerado com sucesso!")
                else:
                    QMessageBox.warning(self, "Aviso", "Não foram encontrados dados neste período.")