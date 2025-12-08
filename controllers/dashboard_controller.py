from models.dashboard_model import DashboardModel
from dtos.dashboard_dto import (
    DashboardDTO, ComparativoFinDTO, StatusDTO, 
    EntradaMensalDTO
)

class DashboardController:
    def __init__(self):
        self.model = DashboardModel()

    def get_kpis(self) -> DashboardDTO:
        # 1. Busca dados do Model
        # Removemos a chamada de 'get_evolucao_lead_time' pois ela não existe mais no Model
        val_lead_time_geral = self.model.get_lead_time_geral()
        
        raw_fin = self.model.get_comparativo_financeiro()
        raw_status = self.model.get_status_geral()
        raw_entrada = self.model.get_entrada_mensal()

        # 2. Converte para DTOs (Listas)
        list_fin = [
            ComparativoFinDTO(
                mes=d['mes'], 
                valor_recebido=float(d['val_recebido']), 
                valor_retornado=float(d['val_retornado'])
            ) for d in raw_fin
        ]

        list_status = [
            StatusDTO(status=d['status_final'], qtd=int(d['qtd']))
            for d in raw_status
        ]

        list_entrada = [
            EntradaMensalDTO(
                mes=d['mes'], 
                qtd=int(d['qtd']), 
                valor=float(d['valor'])
            ) for d in raw_entrada
        ]

        # 3. Retorna o DTO
        # Note que não passamos mais 'evolucao_lead_time' (lista), apenas 'lead_time_geral' (float)
        return DashboardDTO(
            comparativo_financeiro=list_fin,
            status_data=list_status,
            entrada_mensal=list_entrada,
            lead_time_geral=val_lead_time_geral 
        )