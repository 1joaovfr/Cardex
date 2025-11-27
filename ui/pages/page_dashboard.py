import sys
import qtawesome as qta
import plotly.graph_objects as go
# import plotly.express as px # Não estamos usando neste exemplo
# from plotly.subplots import make_subplots # Não estamos usando neste exemplo

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QGridLayout, QLabel, QHBoxLayout, QFrame, QPushButton)
from PySide6.QtCore import Qt
# IMPORTANTE: Necessário para renderizar HTML/JS do Plotly
from PySide6.QtWebEngineWidgets import QWebEngineView 

# --- CORES DO TEMA ---
THEME_BG = "#12161f"       
CARD_BG = "#1b212d"        
TEXT_COLOR = "#dce1e8"     
ACCENT_COLOR = "#3a5f8a"   
GRID_COLOR = "#2c3545"     

STYLE_SHEET = """
QMainWindow { background-color: #12161f; }
QWidget { background-color: #12161f; color: #dce1e8; font-family: 'Segoe UI', sans-serif; }
QFrame#Card { background-color: #1b212d; border-radius: 8px; border: 1px solid #2c3545; }
QLabel#CardTitle { background-color: transparent; color: #a0aec0; font-size: 14px; font-weight: bold; padding-bottom: 5px; border-bottom: 1px solid #2c3545; }
QPushButton#btn_nav { background-color: #3a5f8a; color: white; border: 1px solid #2c3e50; padding: 8px 15px; border-radius: 4px; font-weight: bold; }
QPushButton#btn_nav:hover { background-color: #4b7bc0; }
"""

# --- MODIFICAÇÃO 1: Atualização na PlotlyWidget para incluir Config ---
class PlotlyWidget(QWebEngineView):
    """ Widget personalizado para renderizar gráficos Plotly """
    def __init__(self, fig):
        super().__init__()
        self.page().setBackgroundColor(Qt.transparent)
        
        # --- Configurações para travar a interação do usuário ---
        config_plot = {
            'scrollZoom': False,       # Desabilita zoom com o scroll do mouse
            'displayModeBar': False,   # Esconde a barra de ferramentas do topo (zoom, pan, etc)
            'editable': False,         # Impede edição de títulos/textos ao clicar
            'showLink': False,         # Remove link do Plotly
            'displaylogo': False,      # Remove logo do Plotly
            'responsive': True         # Mantém responsividade ao redimensionar a janela
        }
        
        # Adicionamos o parâmetro 'config' aqui
        html = fig.to_html(include_plotlyjs='cdn', full_html=False, config=config_plot)
        
        full_html = f"""
        <html>
        <head>
            <style>
                body {{ background-color: {CARD_BG}; margin: 0; padding: 0; overflow: hidden; }}
                /* Esconde a barra de scroll do WebEngineView se aparecer */
                ::-webkit-scrollbar {{ display: none; }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        self.setHtml(full_html)

class PageDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard Executivo - Travado")
        self.resize(1100, 800)
        self.setStyleSheet(STYLE_SHEET)

        main_layout = QVBoxLayout(self) 
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        # --- TOPO ---
        top_bar = QHBoxLayout()
        lbl_titulo = QLabel("Visão Geral (Hover Ativo / Zoom Bloqueado)")
        lbl_titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #8ab4f8; background: transparent;")
        
        btn_refresh = QPushButton(" Atualizar")
        btn_refresh.setObjectName("btn_nav")
        btn_refresh.setIcon(qta.icon('fa5s.sync-alt', color='white'))
        btn_refresh.setCursor(Qt.PointingHandCursor)

        top_bar.addWidget(lbl_titulo)
        top_bar.addStretch()
        top_bar.addWidget(btn_refresh)
        main_layout.addLayout(top_bar)

        # --- GRID DOS 4 CARDS ---
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)

        # Criar os 4 gráficos
        fig1 = self.criar_grafico_vendas()
        fig2 = self.criar_grafico_estoque()
        fig3 = self.criar_grafico_categoria()
        fig4 = self.criar_grafico_performance()

        # Adicionar Cards ao Grid
        grid_layout.addWidget(self.criar_card("Vendas Mensais (R$)", fig1), 0, 0)
        grid_layout.addWidget(self.criar_card("Evolução do Estoque", fig2), 0, 1)
        grid_layout.addWidget(self.criar_card("Mix de Categorias", fig3), 1, 0)
        grid_layout.addWidget(self.criar_card("Top 5 Fornecedores", fig4), 1, 1)

        main_layout.addLayout(grid_layout)

    def criar_card(self, titulo, fig):
        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        lbl = QLabel(titulo)
        lbl.setObjectName("CardTitle")
        
        # Widget do Plotly (que agora aplica as configs de bloqueio)
        plotly_view = PlotlyWidget(fig)
        
        layout.addWidget(lbl)
        layout.addWidget(plotly_view)
        return card

    # --- MÉTODOS DE GERAÇÃO DOS GRÁFICOS ---
    
    # --- MODIFICAÇÃO 2: Atualização no tema para travar os eixos ---
    def _apply_theme(self, fig):
        """ Aplica o tema e trava os eixos """
        fig.update_layout(
            paper_bgcolor=CARD_BG,
            plot_bgcolor=CARD_BG,
            font_color=TEXT_COLOR,
            margin=dict(l=20, r=20, t=30, b=20),
            # Configura os eixos para não serem arrastáveis (fixedrange=True)
            xaxis=dict(
                showgrid=True, 
                gridcolor=GRID_COLOR, 
                zerolinecolor=GRID_COLOR,
                fixedrange=True # <--- IMPEDE ARRASTAR EIXO X
            ),
            yaxis=dict(
                showgrid=True, 
                gridcolor=GRID_COLOR, 
                zerolinecolor=GRID_COLOR,
                fixedrange=True # <--- IMPEDE ARRASTAR EIXO Y
            ),
            hovermode="x unified",
            dragmode=False # Desativa o modo de arrastar padrão
        )
        return fig

    def criar_grafico_vendas(self):
        meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun']
        vendas = [120, 150, 140, 180, 220, 250]
        
        fig = go.Figure(data=[
            go.Bar(x=meses, y=vendas, marker_color='#3a5f8a', name='Vendas')
        ])
        fig.update_traces(marker_color='#4299e1', marker_line_color='#2b6cb0',
                          marker_line_width=1, opacity=0.8)
        return self._apply_theme(fig)

    def criar_grafico_estoque(self):
        dias = [1, 5, 10, 15, 20, 25, 30]
        qtd = [500, 480, 510, 450, 470, 420, 400]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dias, y=qtd, 
            mode='lines+markers',
            fill='tozeroy',
            line=dict(color='#48bb78', width=3, shape='spline'),
            name='Itens'
        ))
        return self._apply_theme(fig)

    def criar_grafico_categoria(self):
        labels = ['Peças Motor', 'Freios', 'Suspensão', 'Elétrica']
        values = [450, 250, 150, 150]
        colors = ['#4299e1', '#48bb78', '#ecc94b', '#f56565']

        fig = go.Figure(data=[go.Pie(
            labels=labels, values=values, hole=.6,
            marker=dict(colors=colors, line=dict(color=CARD_BG, width=2))
        )])
        # Gráficos de pizza não usam eixos X/Y da mesma forma, 
        # mas a config na PlotlyWidget já resolve o bloqueio.
        fig.update_layout(showlegend=True, legend=dict(orientation="v"))
        return self._apply_theme(fig)

    def criar_grafico_performance(self):
        fornecedores = ['Bosch', 'Magneti', 'Valeo', 'Continental', 'Delphi']
        score = [98, 85, 90, 78, 92]

        fig = go.Figure(go.Bar(
            x=score, y=fornecedores, orientation='h',
            marker=dict(color=score, colorscale='Viridis')
        ))
        return self._apply_theme(fig)