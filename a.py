import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QFrame, QLabel
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import Qt

class PlotlyCard(QFrame):
    def __init__(self, title):
        super().__init__()
        
        # Estilização do Card (CSS no PySide)
        self.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-radius: 12px;
                border: 1px solid #3d3d3d;
            }
            QLabel {
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                border: none;
                padding: 10px;
                background-color: transparent;
            }
        """)
        
        # Layout interno do Card
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5) # Margem interna pequena
        
        # Título
        self.lbl_title = QLabel(title)
        self.lbl_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_title)
        
        # O "Navegador" que vai mostrar o gráfico
        self.browser = QWebEngineView()
        # Hack para deixar o fundo do webview transparente/igual ao tema
        self.browser.page().setBackgroundColor(Qt.transparent)
        
        layout.addWidget(self.browser)
        self.setLayout(layout)

    def set_chart(self, fig):
        """Recebe uma figura do Plotly e renderiza no WebEngine"""
        
        # Atualiza o layout do Plotly para Dark Mode e margens zero
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)', # Fundo transparente
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=20, l=20, r=20, b=20),
            font=dict(color='#e0e0e0')
        )
        
        # Converte o gráfico para HTML
        html = fig.to_html(include_plotlyjs='cdn', full_html=False)
        
        # CSS extra para injetar na página HTML do gráfico (garante scroll oculto)
        custom_css = """
        <style>
            body { margin: 0; padding: 0; overflow: hidden; background-color: transparent; }
        </style>
        """
        
        self.browser.setHtml(custom_css + html)

class DashboardGarantia(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GARANTIA_APP - Interactive Dashboard")
        self.resize(1100, 750)
        self.setStyleSheet("background-color: #1e1e1e;") # Fundo da janela

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout Principal
        main_layout = QVBoxLayout(central_widget)
        
        # Cabeçalho
        header = QLabel("Monitoramento de Garantias (Tempo Real)")
        header.setStyleSheet("color: white; font-size: 24px; font-weight: bold; margin: 10px;")
        main_layout.addWidget(header)

        # Grid 2x2
        grid = QGridLayout()
        grid.setSpacing(20) # Espaço entre os cards
        main_layout.addLayout(grid)

        # --- CRIANDO OS 4 GRÁFICOS DIFERENTES ---

        # 1. Gráfico de Barras (Peças com mais defeito)
        card1 = PlotlyCard("Top Peças Defeituosas")
        df_pecas = pd.DataFrame({
            'Peça': ['Amortecedor', 'Bomba Água', 'Embreagem', 'Disco Freio', 'Bobina'],
            'Qtd': [45, 30, 25, 20, 15]
        })
        fig1 = px.bar(df_pecas, x='Peça', y='Qtd', color='Qtd', color_continuous_scale='Blues')
        card1.set_chart(fig1)
        grid.addWidget(card1, 0, 0)

        # 2. Gráfico de Rosca/Donut (Status das Garantias)
        card2 = PlotlyCard("Distribuição de Status")
        df_status = pd.DataFrame({
            'Status': ['Aprovado', 'Rejeitado', 'Em Análise', 'Pendente DOC'],
            'Qtd': [150, 40, 35, 10]
        })
        # Hole=.5 cria o efeito de Rosca
        fig2 = px.pie(df_status, values='Qtd', names='Status', hole=0.5, 
                      color_discrete_sequence=['#00cc96', '#ef553b', '#fca311', '#ab63fa'])
        card2.set_chart(fig2)
        grid.addWidget(card2, 0, 1)

        # 3. Gráfico de Área/Linha (Evolução de Custos R$)
        card3 = PlotlyCard("Custo Mensal de Garantias (R$)")
        df_custo = pd.DataFrame({
            'Mês': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
            'Valor': [12000, 15000, 11000, 18000, 22000, 20000]
        })
        fig3 = px.area(df_custo, x='Mês', y='Valor', markers=True)
        fig3.update_traces(line_color='#636efa', fillcolor='rgba(99, 110, 250, 0.3)')
        card3.set_chart(fig3)
        grid.addWidget(card3, 1, 0)

        # 4. Gráfico de Indicador/Gauge (Tempo Médio de Resposta)
        card4 = PlotlyCard("Tempo Médio de Análise (Dias)")
        fig4 = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = 4.2,
            delta = {'reference': 7}, # Meta era 7 dias
            title = {'text': "Meta: 7 Dias"},
            gauge = {
                'axis': {'range': [0, 10]},
                'bar': {'color': "#00cc96"},
                'steps': [
                    {'range': [0, 5], 'color': "rgba(0, 204, 150, 0.1)"},
                    {'range': [5, 8], 'color': "rgba(255, 255, 0, 0.1)"},
                    {'range': [8, 10], 'color': "rgba(239, 85, 59, 0.1)"}],
            }
        ))
        card4.set_chart(fig4)
        grid.addWidget(card4, 1, 1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DashboardGarantia()
    window.show()
    sys.exit(app.exec())