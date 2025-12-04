import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                               QLabel, QFrame, QPushButton, QSizePolicy)
from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView 
import plotly.graph_objects as go
import qtawesome as qta
from controllers import DashboardController

# --- ESTILO ORIGINAL ---
CARD_BG = "#1b212d"
TEXT_COLOR = "#dce1e8"
GRID_COLOR = "#2c3545"

STYLE_SHEET = """
QWidget { background-color: #12161f; color: #dce1e8; font-family: 'Segoe UI', sans-serif; }
QFrame#Card { background-color: #1b212d; border-radius: 8px; border: 1px solid #2c3545; }
QLabel#CardTitle { background-color: transparent; color: #a0aec0; font-size: 14px; font-weight: bold; padding-bottom: 5px; border-bottom: 1px solid #2c3545; }
QPushButton#btn_nav { background-color: #3a5f8a; color: white; border: 1px solid #2c3e50; padding: 8px 15px; border-radius: 4px; font-weight: bold; }
QPushButton#btn_nav:hover { background-color: #4b7bc0; }
"""

class PlotlyWidget(QWebEngineView):
    def __init__(self, fig):
        super().__init__()
        self.page().setBackgroundColor(Qt.transparent)
        self.settings().setAttribute(self.settings().WebAttribute.ShowScrollBars, False)
        config = {'scrollZoom': False, 'displayModeBar': False, 'responsive': True}
        html = fig.to_html(include_plotlyjs='cdn', full_html=False, config=config)
        full_html = f"""<html><head><style>
        body {{ background-color: {CARD_BG}; margin: 0; padding: 0; overflow: hidden; }}
        </style></head><body>{html}</body></html>"""
        self.setHtml(full_html)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

class PageDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = DashboardController()
        self.setWindowTitle("Dashboard Executivo")
        self.setStyleSheet(STYLE_SHEET)

        main_layout = QVBoxLayout(self) 
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # TOPO
        top_bar = QHBoxLayout()
        lbl_titulo = QLabel("Visão Geral")
        lbl_titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #8ab4f8; background: transparent;")
        
        btn_refresh = QPushButton(" Atualizar")
        btn_refresh.setObjectName("btn_nav")
        btn_refresh.setIcon(qta.icon('fa5s.sync-alt', color='white'))
        btn_refresh.clicked.connect(self.carregar_dados)

        top_bar.addWidget(lbl_titulo)
        top_bar.addStretch()
        top_bar.addWidget(btn_refresh)
        main_layout.addLayout(top_bar)

        # GRID
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(20)
        main_layout.addLayout(self.grid_layout)
        self.carregar_dados()

    def carregar_dados(self):
        # Limpar
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        kpis = self.controller.get_kpis()
        
        # Figuras
        fig_total = self.criar_indicador_unico("Valor em Análise", kpis.get('total_valor', 0))
        fig_pizza = self.criar_grafico_pizza(kpis.get('status_data', []))
        
        self.grid_layout.addWidget(self.criar_card("Indicador Financeiro", fig_total), 0, 0)
        self.grid_layout.addWidget(self.criar_card("Status dos Itens", fig_pizza), 0, 1)

    def criar_card(self, titulo, fig):
        card = QFrame(objectName="Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        lbl = QLabel(titulo)
        lbl.setObjectName("CardTitle")
        layout.addWidget(lbl)
        if fig: layout.addWidget(PlotlyWidget(fig))
        return card

    def criar_indicador_unico(self, titulo, valor):
        fig = go.Figure(go.Indicator(
            mode = "number",
            value = valor,
            number = {'prefix': "R$ "},
            title = {"text": titulo}
        ))
        self._apply_theme(fig)
        return fig

    def criar_grafico_pizza(self, dados):
        if not dados: return None
        labels = [d['status'] for d in dados]
        values = [d['qtd'] for d in dados]
        colors = ['#ecc94b', '#48bb78', '#f56565'] 
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.6, marker=dict(colors=colors))])
        self._apply_theme(fig)
        return fig

    def _apply_theme(self, fig):
        fig.update_layout(
            paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG, font_color=TEXT_COLOR,
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis=dict(showgrid=False, visible=False), yaxis=dict(showgrid=False, visible=False)
        )