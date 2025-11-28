import sys
import qtawesome as qta
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QStackedWidget, QFrame, QLabel)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize

# Importa as páginas
from views.lancamento_view import PageLancamento
from views.analise_view import PageAnalise
from views.relatorio_view import PageRelatorio
from views.dashboard_view import PageDashboard
from views.retorno_view import PageRetorno

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema Integrado de Gestão - Cardex")
        self.resize(1280, 800)
        self.setStyleSheet("QMainWindow { background-color: #12161f; }")

        # --- CONFIGURAÇÕES DO MENU ---
        self.menu_expanded = True
        self.sidebar_expanded_width = 200
        self.sidebar_collapsed_width = 60 

        # --- ESTILOS DOS BOTÕES ---
        # Aberto: Texto visível, alinhado à esquerda
        self.style_btn_expanded = """
            QPushButton {
                text-align: left; 
                padding: 12px 20px; 
                background-color: transparent; 
                color: #dce1e8; 
                border-radius: 5px;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover { background-color: #2c3545; color: white; }
        """
        # Fechado: Texto removido (via código), Ícone centralizado
        self.style_btn_collapsed = """
            QPushButton {
                text-align: center; 
                padding: 12px 0px; 
                background-color: transparent; 
                color: #dce1e8; 
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover { background-color: #2c3545; color: white; }
        """

        # Widget Central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- MENU LATERAL ---
        self.sidebar = QFrame()
        self.sidebar.setStyleSheet("background-color: #171c26; border-right: 1px solid #2c3545;")
        self.sidebar.setFixedWidth(self.sidebar_expanded_width)
        
        self.layout_sidebar = QVBoxLayout(self.sidebar)
        self.layout_sidebar.setContentsMargins(10, 20, 10, 20)
        self.layout_sidebar.setSpacing(10)

        # 1. CABEÇALHO (TOGGLE + LOGO)
        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(0, 0, 0, 10)

        self.btn_toggle = QPushButton()
        self.btn_toggle.setIcon(qta.icon('fa5s.bars', color='#8ab4f8'))
        self.btn_toggle.setIconSize(QSize(24, 24))
        self.btn_toggle.setCursor(Qt.PointingHandCursor)
        self.btn_toggle.setFixedSize(40, 40)
        self.btn_toggle.setStyleSheet("background: transparent; border: none;")
        self.btn_toggle.clicked.connect(self.toggle_menu)
        
        self.lbl_logo = QLabel("CARDEX")
        self.lbl_logo.setStyleSheet("color: #3a5f8a; font-size: 20px; font-weight: bold; margin-left: 10px;")
        
        self.header_layout.addWidget(self.btn_toggle)
        self.header_layout.addWidget(self.lbl_logo)
        self.header_layout.addStretch()

        self.layout_sidebar.addLayout(self.header_layout)

        # 2. BOTÕES DO MENU
        self.menu_buttons = []
        
        self.btn_dash = self.create_menu_btn(" Dashboard", "fa5s.chart-line")
        self.btn_lanc = self.create_menu_btn(" Lançamento", "fa5s.file-invoice-dollar")
        self.btn_ana = self.create_menu_btn(" Análise", "fa5s.microscope")
        self.btn_rel = self.create_menu_btn(" Relatório", "fa5s.table")
        self.btn_ret = self.create_menu_btn(" Retorno", "fa5s.boxes")

        self.layout_sidebar.addWidget(self.btn_dash)
        self.layout_sidebar.addWidget(self.btn_lanc)
        self.layout_sidebar.addWidget(self.btn_ana)
        self.layout_sidebar.addWidget(self.btn_rel)
        self.layout_sidebar.addWidget(self.btn_ret)
        
        self.layout_sidebar.addStretch()

        # Botão Sair
        self.btn_sair = QPushButton(" Sair")
        self.btn_sair.setProperty("original_text", " Sair") # Salva o texto original
        self.btn_sair.setIcon(qta.icon('fa5s.sign-out-alt', color='#e57373'))
        self.btn_sair.setIconSize(QSize(20, 20))
        self.btn_sair.clicked.connect(self.close)
        
        # Estilos específicos para o botão sair (cores avermelhadas)
        self.style_sair_expanded = """
            QPushButton { text-align: left; padding: 12px 15px; background-color: #2c1b1b; color: #e57373; border-radius: 5px; border: 1px solid #4a2b2b; }
            QPushButton:hover { background-color: #3b2424; }
        """
        self.style_sair_collapsed = """
            QPushButton { text-align: center; padding: 12px 0px; background-color: #2c1b1b; color: #e57373; border-radius: 5px; border: 1px solid #4a2b2b; }
            QPushButton:hover { background-color: #3b2424; }
        """
        self.btn_sair.setStyleSheet(self.style_sair_expanded)
        self.layout_sidebar.addWidget(self.btn_sair)

        # --- ÁREA DE CONTEÚDO ---
        self.pages = QStackedWidget()
        self.pages.addWidget(PageDashboard()) 
        self.pages.addWidget(PageLancamento()) 
        self.pages.addWidget(PageAnalise())   
        self.pages.addWidget(PageRelatorio())  
        self.pages.addWidget(PageRetorno())   

        self.btn_dash.clicked.connect(lambda: self.pages.setCurrentIndex(0))
        self.btn_lanc.clicked.connect(lambda: self.pages.setCurrentIndex(1))
        self.btn_ana.clicked.connect(lambda: self.pages.setCurrentIndex(2))
        self.btn_rel.clicked.connect(lambda: self.pages.setCurrentIndex(3))
        self.btn_ret.clicked.connect(lambda: self.pages.setCurrentIndex(4))

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.pages)

        # Animação
        self.animation = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)

    def create_menu_btn(self, text, icon_name):
        btn = QPushButton(text)
        # --- O TRUQUE ESTÁ AQUI ---
        # Salvamos o texto numa propriedade customizada para usar depois
        btn.setProperty("original_text", text) 
        
        btn.setIcon(qta.icon(icon_name, color='#dce1e8'))
        btn.setIconSize(QSize(20, 20))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(self.style_btn_expanded)
        self.menu_buttons.append(btn)
        return btn

    def toggle_menu(self):
        if self.menu_expanded:
            # --- FECHAR ---
            width_end = self.sidebar_collapsed_width
            self.lbl_logo.hide()
            
            # Loop nos botões normais
            for btn in self.menu_buttons:
                btn.setText("") # Remove o texto visualmente
                btn.setStyleSheet(self.style_btn_collapsed) # Centraliza o ícone
            
            # Botão Sair
            self.btn_sair.setText("")
            self.btn_sair.setStyleSheet(self.style_sair_collapsed)
            
        else:
            # --- ABRIR ---
            width_end = self.sidebar_expanded_width
            self.lbl_logo.show()
            
            # Loop nos botões normais
            for btn in self.menu_buttons:
                # Restaura o texto original salvo na propriedade
                btn.setText(btn.property("original_text")) 
                btn.setStyleSheet(self.style_btn_expanded) # Alinha à esquerda
            
            # Botão Sair
            self.btn_sair.setText(self.btn_sair.property("original_text"))
            self.btn_sair.setStyleSheet(self.style_sair_expanded)

        self.animation.setStartValue(self.sidebar.width())
        self.animation.setEndValue(width_end)
        self.animation.start()
        
        self.menu_expanded = not self.menu_expanded

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()    
    sys.exit(app.exec())