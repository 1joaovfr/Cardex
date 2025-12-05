from database.connection import DatabaseConnection

class DashboardController:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_kpis(self):
        kpis = {}
        
        # --- 0. KPI Total (Valor em Análise) ---
        # CORREÇÃO: Tabela 'itens_notas' (Plural)
        sql_total = "SELECT SUM(valor_item) as total FROM itens_notas WHERE status != 'Concluído'"
        res_total = self.db.execute_query(sql_total, fetch=True)
        kpis['total_valor'] = res_total[0]['total'] if res_total and res_total[0]['total'] else 0.0

        # --- 1. Crescimento / Evolução Mensal ---
        # CORREÇÃO: Join com tabela 'notas_fiscais'
        sql_crescimento = """
            SELECT TO_CHAR(N.data_lancamento, 'YYYY-MM') as mes, 
                   SUM(L.valor_item) as total,
                   COUNT(*) as qtd 
            FROM itens_notas L
            INNER JOIN notas_fiscais N ON L.id_nota_fiscal = N.id
            GROUP BY mes 
            ORDER BY mes DESC
            LIMIT 6
        """
        kpis['crescimento'] = self.db.execute_query(sql_crescimento, fetch=True)

        # --- 2. Top 5 Produtos ---
        # CORREÇÃO: 
        # Tabela 'Produtos' virou 'itens'
        # Coluna 'descricao' virou 'descricao_item'
        # Coluna 'codigo_produto' virou 'codigo_item'
        sql_top5 = """
            SELECT I.descricao_item as produto, 
                   COUNT(*) as qtd,
                   SUM(L.valor_item) as valor
            FROM itens_notas L
            INNER JOIN itens I ON L.codigo_item = I.codigo_item
            WHERE L.procedente_improcedente = 'Procedente' 
            GROUP BY I.descricao_item 
            ORDER BY qtd DESC 
            LIMIT 5
        """
        kpis['top5'] = self.db.execute_query(sql_top5, fetch=True)

        # --- 3. Status ---
        # CORREÇÃO: Tabela 'itens_notas'
        sql_status = "SELECT status, COUNT(*) as qtd FROM itens_notas GROUP BY status"
        kpis['status_data'] = self.db.execute_query(sql_status, fetch=True)

        # --- 4. Pendentes ---
        # CORREÇÃO: Tabela 'itens_notas' e 'notas_fiscais' (não notas_fiscaisF)
        sql_pendentes = """
            SELECT TO_CHAR(N.data_lancamento, 'YYYY-MM') as mes, 
                   COUNT(*) as qtd, 
                   SUM(L.valor_item) as valor
            FROM itens_notas L
            INNER JOIN notas_fiscais N ON L.id_nota_fiscal = N.id
            WHERE L.status = 'Pendente'
            GROUP BY mes
            ORDER BY mes DESC
            LIMIT 6
        """
        kpis['pendentes'] = self.db.execute_query(sql_pendentes, fetch=True)

        return kpis