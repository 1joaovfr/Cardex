from styles.common import COMMON_STYLES
from styles.theme import *

ANALISE_STYLES = COMMON_STYLES + f"""
/* LABELS DE STATUS (Só existem na Análise) */
QLabel#StatusProcedente {{ 
    color: {COLOR_SUCCESS}; font-weight: bold; background-color: {COLOR_CARD_BG}; border: 1px solid #2f855a; 
}}
QLabel#StatusImprocedente {{ 
    color: {COLOR_DANGER}; font-weight: bold; background-color: {COLOR_CARD_BG}; border: 1px solid #c53030; 
}}
QLabel#StatusNeutro {{ 
    color: {COLOR_TEXT_DIM}; background-color: {COLOR_CARD_BG}; border: 1px solid {COLOR_CARD_BORDER}; 
}}
"""