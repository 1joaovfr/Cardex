import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                               QLabel, QFrame, QPushButton, QSizePolicy)
from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView 
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import qtawesome as qta
from controllers import DashboardController

# --- PALETA DE CORES DARK BLUE ---
CARD_BG = "#1b212d"
TEXT_COLOR = "#dce1e8"

# Cores Harmônicas
COLOR_BLUE_PRIMARY = "#3182ce"   # Azul para barras principais
COLOR_CYAN_TEAL = "#38b2ac"      # Verde água para rankings
COLOR_INDIGO = "#5a67d8"         # Roxo azulado para barras secundárias
COLOR_NEON_BLUE = "#63b3ed"      # Azul claro para destaques
COLOR_LINE_HIGHLIGHT = "#00b5d8" # Ciano brilhante para linhas

# Cores de Status
COLOR_SUCCESS = "#48bb78"
COLOR_DANGER = "#f56565"
COLOR_WARNING = "#ecc94b"
COLOR_NEUTRAL = "#a0aec0"

STYLE_SHEET = """
QWidget { background-color: #12161f; color: #dce1e8; font-family: 'Segoe UI', sans-serif; }
QFrame#Card { background-color: #1b212d; border-radius: 8px; border: 1px solid #2c3545; }
QLabel#CardTitle { background-color: transparent; color: #a0aec0; font-size: 14px; font-weight: bold; padding-bottom: 5px; border-bottom: 1px solid #2c3545; }
QPushButton#btn_nav { background-color: #2c5282; color: white; border: 1px solid #2a4365; padding: 8px 15px; border-radius: 4px; font-weight: bold; }
QPushButton#btn_nav:hover { background-color: #3182ce; }
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
        lbl_titulo = QLabel("Visão Geral - Executivo")
        lbl_titulo.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {COLOR_NEON_BLUE}; background: transparent;")
        
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
        self.grid_layout.setColumnStretch(0, 1)
        self.grid_layout.setColumnStretch(1, 1)
        self.grid_layout.setRowStretch(0, 1)
        self.grid_layout.setRowStretch(1, 1)

        main_layout.addLayout(self.grid_layout)
        self.carregar_dados()

    def carregar_dados(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        kpis = self.controller.get_kpis()
        
        # 1. Crescimento (AGORA DUAL AXIS)
        fig_cresc = self.criar_grafico_crescimento(kpis.get('crescimento', []))
        self.grid_layout.addWidget(self.criar_card("Evolução Mensal (Qtd vs R$)", fig_cresc), 0, 0)

        # 2. Top 5 Produtos (AGORA COM VALOR E QTD)
        fig_top5 = self.criar_grafico_top5(kpis.get('top5', []))
        self.grid_layout.addWidget(self.criar_card("Top 5 Procedência (Qtd e Valor)", fig_top5), 0, 1)

        # 3. Status (Rosca)
        fig_rosca = self.criar_grafico_rosca(kpis.get('status_data', []))
        self.grid_layout.addWidget(self.criar_card("Distribuição de Status", fig_rosca), 1, 0)

        # 4. Pendentes (Eixo Duplo)
        fig_dual = self.criar_grafico_dual(kpis.get('pendentes', []))
        self.grid_layout.addWidget(self.criar_card("Análise de Pendências (Valor vs Qtd)", fig_dual), 1, 1)

    def criar_card(self, titulo, fig):
        card = QFrame(objectName="Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        lbl = QLabel(titulo)
        lbl.setObjectName("CardTitle")
        layout.addWidget(lbl)
        if fig: layout.addWidget(PlotlyWidget(fig))
        else: layout.addWidget(QLabel("Sem dados", styleSheet="color: #666; font-style: italic;"))
        return card

    # --- ATUALIZAÇÕES NOS GRÁFICOS ---

    def criar_grafico_crescimento(self, dados):
        if not dados: return None
        meses = [d['mes'] for d in dados]
        valores = [d['total'] for d in dados]
        qtds = [d['qtd'] for d in dados]

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Barras = Quantidade (Volume)
        fig.add_trace(
            go.Bar(
                x=meses, 
                y=qtds, 
                name="Qtd", 
                marker_color=COLOR_BLUE_PRIMARY, 
                opacity=0.8,
                hovertemplate='%{y} itens'
            ),
            secondary_y=False
        )

        # Linha = Valor Financeiro
        fig.add_trace(
            go.Scatter(
                x=meses, 
                y=valores, 
                name="Total (R$)", 
                # ALTERADO: Removido '+text' do mode
                mode='lines+markers', 
                # REMOVIDO: text=[...], textposition="..."
                line=dict(color=COLOR_NEON_BLUE, width=3),
                marker=dict(size=6, color='white', line=dict(width=2, color=COLOR_NEON_BLUE)),
                # O hovertemplate garante que o valor apareça ao passar o mouse
                hovertemplate='R$ %{y:,.2f}'
            ),
            secondary_y=True
        )

        self._apply_theme(fig)

        # Mantendo a legenda igual ao de Pendências
        fig.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        fig.update_yaxes(showgrid=False, secondary_y=False)
        fig.update_yaxes(showgrid=False, secondary_y=True)
        
        return fig

    def criar_grafico_top5(self, dados):
        if not dados: return None
        dados_inv = dados[::-1] 
        produtos = [d['produto'] for d in dados_inv]
        qtds = [d['qtd'] for d in dados_inv]
        valores = [d['valor'] for d in dados_inv] # Novo campo

        # Criamos o texto que vai aparecer na barra: "15 un. | R$ 1.500,00"
        textos_barra = [f"{q} un.   <span style='color:#a0aec0'>|</span>   R$ {v:,.2f}" for q, v in zip(qtds, valores)]

        fig = go.Figure(data=[
            go.Bar(
                x=qtds, 
                y=produtos,
                orientation='h',
                marker_color=COLOR_CYAN_TEAL,
                # Usamos o texto customizado
                text=textos_barra,
                textposition='auto', # Plotly tenta colocar dentro, se não der, põe fora
                hovertemplate='<b>%{y}</b><br>Quantidade: %{x}<br>Valor Total: R$ %{customdata:,.2f}<extra></extra>',
                customdata=valores # Passa o valor para usar no tooltip
            )
        ])
        
        # Aumentar margem esquerda se os nomes dos produtos forem longos
        fig.update_layout(margin=dict(l=10, r=20, t=30, b=10))
        self._apply_theme(fig)
        return fig

    def criar_grafico_rosca(self, dados):
        if not dados: return None
        labels = [d['status'] for d in dados]
        values = [d['qtd'] for d in dados]
        total = sum(values)

        colors_map = {
            'Procedente': COLOR_SUCCESS, 'Concluído': COLOR_SUCCESS,
            'Improcedente': COLOR_DANGER, 'Reprovado': COLOR_DANGER,
            'Pendente': COLOR_WARNING, 'Em Análise': COLOR_NEON_BLUE
        }
        lista_cores = [colors_map.get(l, COLOR_NEUTRAL) for l in labels]

        fig = go.Figure(data=[
            go.Pie(
                labels=labels, values=values, hole=.6, 
                marker=dict(colors=lista_cores),
                textinfo='percent', hoverinfo='label+value',
                textfont=dict(color='#ffffff')
            )
        ])
        fig.add_annotation(text=f"{total}", x=0.5, y=0.5, font_size=22, showarrow=False, font_color="white")
        self._apply_theme(fig)
        return fig

    def criar_grafico_dual(self, dados):
        # Pendentes (Valor vs Qtd)
        if not dados: return None
        meses = [d['mes'] for d in dados]
        qtds = [d['qtd'] for d in dados]
        valores = [d['valor'] for d in dados]

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Barras = Qtd
        fig.add_trace(
            go.Bar(x=meses, y=qtds, name="Qtd", marker_color=COLOR_INDIGO, opacity=0.8),
            secondary_y=False
        )

        # Linha = Valor
        fig.add_trace(
            go.Scatter(
                x=meses, y=valores, name="Valor (R$)", 
                mode='lines+markers', 
                line=dict(color=COLOR_LINE_HIGHLIGHT, width=3),
                marker=dict(size=6, color='white', line=dict(width=2, color=COLOR_LINE_HIGHLIGHT))
            ),
            secondary_y=True
        )

        self._apply_theme(fig)
        fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig.update_yaxes(showgrid=False, secondary_y=False)
        fig.update_yaxes(showgrid=False, secondary_y=True)
        return fig

    def _apply_theme(self, fig):
        fig.update_layout(
            paper_bgcolor=CARD_BG, 
            plot_bgcolor=CARD_BG, 
            font_color=TEXT_COLOR,
            font_family="Segoe UI",
            margin=dict(l=10, r=10, t=30, b=10),
            xaxis=dict(showgrid=False, zeroline=False, showline=True, linecolor='#2c3545'), 
            yaxis=dict(showgrid=False, zeroline=False),
            hovermode="x unified",
            hoverlabel=dict(
                bgcolor="#2d3748", font_size=12, font_family="Segoe UI",
                font_color="white", bordercolor="#2c3545"
            )
        )