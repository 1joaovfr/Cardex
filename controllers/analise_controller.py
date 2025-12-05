from datetime import datetime
from database.connection import DatabaseConnection

class AnaliseController:
    def __init__(self):
        self.db = DatabaseConnection()

    def listar_pendentes(self):
        sql = """
            SELECT i.id, 
                   nf.numero_nota, 
                   i.codigo_item, 
                   p.descricao_item as descricao, 
                   to_char(nf.data_lancamento, 'DD/MM/YYYY') as data_fmt, 
                   i.codigo_analise,
                   i.ressarcimento
            FROM itens_notas i
            JOIN notas_fiscais nf ON i.id_nota_fiscal = nf.id
            LEFT JOIN itens p ON i.codigo_item = p.codigo_item
            WHERE i.status = 'Pendente'
            ORDER BY nf.data_lancamento ASC
        """
        return self.db.execute_query(sql, fetch=True)

    def get_codigos_avaria(self):
        return self.db.execute_query("SELECT * FROM avarias", fetch=True)

    def salvar_analise(self, id_item, dados):
        # --- NOVO: Captura a data de hoje automaticamente ---
        data_hoje = datetime.now().date()

        sql = """
            UPDATE itens_notas
            SET numero_serie = %s, 
                produzido_revenda = %s, 
                fornecedor = %s,
                codigo_avaria = %s, 
                descricao_avaria = %s, 
                status = %s,
                procedente_improcedente = %s,
                data_analise = %s  -- <--- CAMPO NOVO NO UPDATE
            WHERE id = %s
        """
        
        self.db.execute_query(sql, (
            dados['serie'], 
            dados['origem'], 
            dados['fornecedor'],
            dados['cod_avaria'], 
            dados['desc_avaria'],
            dados['status_resultado'], # Define o status (Procedente/Improcedente) na coluna status geral também? 
            # Dica: Geralmente 'status' é 'Finalizado' e 'procedente_improcedente' é o resultado.
            # Mas mantive como você fez (usando o resultado nos dois campos)
            dados['status_resultado'], 
            data_hoje,  # <--- AQUI ENTRA A DATA AUTOMÁTICA
            id_item
        ))