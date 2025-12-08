from styles.common import COMMON_STYLES, get_date_edit_style
from styles.theme import *

# Se você tiver um caminho de ícone, passe aqui. Se não, deixe vazio.
DATE_EDIT_CSS = get_date_edit_style("assets/icons/arrow_down.png") # Exemplo

LANCAMENTO_STYLES = COMMON_STYLES + DATE_EDIT_CSS + f"""
/* ESPECÍFICO DE LANÇAMENTO */

QCheckBox {{ color: {COLOR_TEXT}; spacing: 8px; }}
QCheckBox::indicator {{ width: 18px; height: 18px; border-radius: 3px; border: 1px solid {COLOR_INPUT_BORDER}; background: {COLOR_INPUT_BG}; }}
QCheckBox::indicator:checked {{ background-color: {COLOR_FOCUS}; border: 1px solid {COLOR_FOCUS}; }}

QPushButton#btn_add {{
    background-color: {COLOR_FOCUS}; color: white; border: none; padding: 8px 15px; border-radius: 4px; font-weight: bold;
}}
QPushButton#btn_add:hover {{ background-color: {COLOR_INFO}; }}
"""