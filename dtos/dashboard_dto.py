from dataclasses import dataclass
from typing import List

# --- DTOs AUXILIARES ---

@dataclass
class ComparativoFinDTO:
    mes: str
    valor_recebido: float  # Total entrada (R$)
    valor_retornado: float # Total pago em garantia (R$)

@dataclass
class EvolucaoLeadTimeDTO:
    mes: str
    media_dias: float

@dataclass
class StatusDTO:
    status: str
    qtd: int

@dataclass
class EntradaMensalDTO:
    mes: str
    qtd: int
    valor: float

# --- DTO PRINCIPAL ---
@dataclass
class DashboardDTO:
    comparativo_financeiro: List
    status_data: List
    entrada_mensal: List
    # Adicione esta linha:
    evolucao_lead_time: Optional[float] = 0.0