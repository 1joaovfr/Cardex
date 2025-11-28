from database.connection import DatabaseConnection

class DashboardController:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_kpis(self):
        kpis = {}
        # Total Valor
        res = self.db.execute_query("SELECT SUM(valor_item) as total FROM ItensGarantia", fetch=True)
        kpis['total_valor'] = res[0]['total'] or 0.0
        
        # Status Chart
        res = self.db.execute_query("SELECT status, COUNT(*) as qtd FROM ItensGarantia GROUP BY status", fetch=True)
        kpis['status_data'] = res
        return kpis