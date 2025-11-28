import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                               QLabel, QFrame, QPushButton, QSizePolicy)
from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView # Necessário instalar: pip install PySide6-WebEngine
import plotly.graph_objects as go
import qtawesome as qta
from controllers import DashboardController

# --- CORES E ESTILO ---
CARD_BG = "#1b212d"
TEXT_COLOR = "#dce1e8"
GRID_COLOR = "#2c3545"

STYLE_SHEET = """
QWidget { background-color: #12161f; color: #dce1e8; font-family: 'Segoe UI', sans-serif; }
QFrame#Card { background-color: #1b212d; border-radius: 8px; border: 1px solid #2c3545; }
QLabel#CardTitle { color: #8ab4f8; font-size: 14px; font-weight: bold; padding-bottom: 5px; border-bottom: 1px solid #2c3545; }
QLabel#KpiValue { font-size: 28px; font-weight: bold; color: #48bb78; }
QLabel#KpiLabel { font-size: 12px; color: #a0aec0; }
QPushButton#btn_refresh { background-color: #3a5f8a; color: white; border: 1px solid #2c3e50; padding: 6px 15px; border-radius: 4px; }
QPushButton#btn_refresh:hover { background-color: #4b7bc0; }
"""

class PlotlyWidget(QWebEngineView):
    """ Widget auxiliar para renderizar HTML do Plotly com fundo transparente """
    def __init__(self, fig):
        super().__init__()
        self.page().setBackgroundColor(Qt.transparent)
        self.settings().setAttribute(self.settings().WebAttribute.ShowScrollBars, False)
        
        # Configurações para travar zoom e deixar visual limpo
        config = {'scrollZoom': False, 'displayModeBar': False, 'responsive': True}
        
        html = fig.to_html(include_plotlyjs='cdn', full_html=False, config=config)
        
        # Injeção de CSS para garantir fundo escuro no HTML
        full_html = f"""
        <html>
        <head>
            <style>
                body {{ background-color: {CARD_BG}; margin: 0; padding: 0; overflow: hidden; }}
            </style>
        </head>
        <body>{html}</body>
        </html>
        """
        self.setHtml(full_html)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

class PageDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = DashboardController()
        self.setWindowTitle("Dashboard Executivo")
        self.setStyleSheet(STYLE_SHEET)

        # Layout Principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # --- TOPO ---
        top_bar = QHBoxLayout()
        lbl_titulo = QLabel("Visão Geral da Garantia")
        lbl_titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #dce1e8;")
        
        self.btn_refresh = QPushButton(" Atualizar Dados")
        self.btn_refresh.setObjectName("btn_refresh")
        self.btn_refresh.setIcon(qta.icon('fa5s.sync-alt', color='white'))
        self.btn_refresh.clicked.connect(self.carregar_dados)
        
        top_bar.addWidget(lbl_titulo)
        top_bar.addStretch()
        top_bar.addWidget(self.btn_refresh)
        main_layout.addLayout(top_bar)

        # --- GRID DE CARDS ---
        self.grid = QGridLayout()
        self.grid.setSpacing(20)
        main_layout.addLayout(self.grid)

        # Inicializa a UI (Placeholders) e carrega dados
        self.carregar_dados()

    def carregar_dados(self):
        # Limpar grid atual (se houver refresh)
        while self.grid.count():
            child = self.grid.takeAt(0)
            if child.widget(): child.widget().deleteLater()

        # Buscar dados do Controller
        kpis = self.controller.get_kpis()
        
        # 1. KPI: Valor Total em Garantia
        card_total = self.criar_card_kpi("Valor Total em Análise", f"R$ {kpis.get('total_valor', 0):.2f}")
        self.grid.addWidget(card_total, 0, 0)

        # 2. Gráfico: Distribuição de Status (Pizza)
        fig_status = self.gerar_grafico_pizza(kpis.get('status_data', []))
        card_status = self.criar_card_grafico("Status dos Itens", fig_status)
        self.grid.addWidget(card_status, 0, 1)

        # 3. Gráfico (Exemplo): Evolução (Mock - pois controller atual foca em status)
        # Se quiser implementar "Top 5", precisaria atualizar o controller. 
        # Aqui coloquei um gráfico vazio estilizado para manter o layout 2x2.
        fig_dummy = self.gerar_grafico_barra_dummy()
        self.grid.addWidget(self.criar_card_grafico("Indicador de Performance (Demo)", fig_dummy), 1, 0, 1, 2)

    def criar_card_kpi(self, titulo, valor):
        frame = QFrame(objectName="Card")
        layout = QVBoxLayout(frame)
        
        lbl_tit = QLabel(titulo)
        lbl_tit.setObjectName("CardTitle")
        
        lbl_val = QLabel(valor)
        lbl_val.setObjectName("KpiValue")
        lbl_val.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(lbl_tit)
        layout.addStretch()
        layout.addWidget(lbl_val)
        layout.addStretch()
        return frame

    def criar_card_grafico(self, titulo, fig):
        frame = QFrame(objectName="Card")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)
        
        lbl = QLabel(titulo)
        lbl.setObjectName("CardTitle")
        layout.addWidget(lbl)
        
        # Widget Plotly
        if fig:
            layout.addWidget(PlotlyWidget(fig))
        else:
            layout.addWidget(QLabel("Sem dados", alignment=Qt.AlignCenter))
            
        return frame

    def gerar_grafico_pizza(self, dados_banco):
        # dados_banco = [{'status': 'Pendente', 'qtd': 5}, ...]
        if not dados_banco:
            return None

        labels = [d['status'] for d in dados_banco]
        values = [d['qtd'] for d in dados_banco]
        colors = ['#ecc94b', '#48bb78', '#f56565'] # Amarelo, Verde, Vermelho (Ajuste conforme ordem)

        fig = go.Figure(data=[go.Pie(
            labels=labels, 
            values=values, 
            hole=.6,
            marker=dict(colors=colors, line=dict(color=CARD_BG, width=2))
        )])

        self._aplicar_tema(fig)
        return fig

    def gerar_grafico_barra_dummy(self):
        # Exemplo visual para preencher o dashboard
        fig = go.Figure(go.Bar(
            x=['Jan', 'Fev', 'Mar'], 
            y=[10, 14, 12],
            marker_color='#3a5f8a'
        ))
        self._aplicar_tema(fig)
        return fig

    def _aplicar_tema(self, fig):
        """ Aplica o tema Dark Blue do sistema ao gráfico Plotly """
        fig.update_layout(
            paper_bgcolor=CARD_BG,
            plot_bgcolor=CARD_BG,
            font_color=TEXT_COLOR,
            margin=dict(l=20, r=20, t=20, b=20),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
        )
        # Remove eixos e grades desnecessários para visual limpo
        fig.update_xaxes(showgrid=False, zeroline=False, fixedrange=True)
        fig.update_yaxes(showgrid=True, gridcolor=GRID_COLOR, zeroline=False, fixedrange=True)