from database.connection import DatabaseConnection

class DashboardController:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_kpis(self):
        kpis = {}
        
        # --- 0. KPI Total (Valor em Análise) ---
        sql_total = "SELECT SUM(valor_item) as total FROM ItensGarantia WHERE status != 'Concluído'"
        res_total = self.db.execute_query(sql_total, fetch=True)
        kpis['total_valor'] = res_total[0]['total'] if res_total and res_total[0]['total'] else 0.0

        # --- 1. Crescimento / Evolução Mensal (Valor vs Qtd) ---
        # ADICIONADO: COUNT(*) as qtd
        sql_crescimento = """
            SELECT TO_CHAR(N.data_lancamento, 'YYYY-MM') as mes, 
                   SUM(I.valor_item) as total,
                   COUNT(*) as qtd 
            FROM ItensGarantia I
            INNER JOIN NotasFiscais N ON I.id_nota_fiscal = N.id
            GROUP BY mes 
            ORDER BY mes DESC
            LIMIT 6
        """
        # Nota: O ORDER BY DESC pega os meses mais recentes. 
        # Se o gráfico ficar invertido (da direita para esquerda), 
        # você pode inverter a lista no Python com .reverse() ou ajustar aqui.
        kpis['crescimento'] = self.db.execute_query(sql_crescimento, fetch=True)

        # --- 2. Top 5 Produtos (Valor vs Qtd) ---
        # ADICIONADO: SUM(I.valor_item) as valor
        sql_top5 = """
            SELECT P.descricao as produto, 
                   COUNT(*) as qtd,
                   SUM(I.valor_item) as valor
            FROM ItensGarantia I
            INNER JOIN Produtos P ON I.codigo_produto = P.codigo_item
            WHERE I.procedente_improcedente = 'Procedente' 
            GROUP BY P.descricao 
            ORDER BY qtd DESC 
            LIMIT 5
        """
        kpis['top5'] = self.db.execute_query(sql_top5, fetch=True)

        # --- 3. Status (Rosca/Pizza) ---
        sql_status = "SELECT status, COUNT(*) as qtd FROM ItensGarantia GROUP BY status"
        kpis['status_data'] = self.db.execute_query(sql_status, fetch=True)

        # --- 4. Pendentes (Eixo Duplo - Já estava correto) ---
        sql_pendentes = """
            SELECT TO_CHAR(N.data_lancamento, 'YYYY-MM') as mes, 
                   COUNT(*) as qtd, 
                   SUM(I.valor_item) as valor
            FROM ItensGarantia I
            INNER JOIN NotasFiscais N ON I.id_nota_fiscal = N.id
            WHERE I.status = 'Pendente'
            GROUP BY mes
            ORDER BY mes DESC
            LIMIT 6
        """
        kpis['pendentes'] = self.db.execute_query(sql_pendentes, fetch=True)

        return kpis