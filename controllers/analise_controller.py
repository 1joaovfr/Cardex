from database.connection import DatabaseConnection

class AnaliseController:
    def __init__(self):
        self.db = DatabaseConnection()

    def listar_pendentes(self):
        sql = """
            SELECT i.id, nf.numero_nota, i.codigo_produto, p.descricao, 
                   to_char(nf.data_lancamento, 'DD/MM/YYYY') as data_fmt, i.codigo_analise
            FROM ItensGarantia i
            JOIN NotasFiscais nf ON i.id_nota_fiscal = nf.id
            LEFT JOIN Produtos p ON i.codigo_produto = p.codigo_item
            WHERE i.status = 'Pendente'
            ORDER BY nf.data_lancamento ASC
        """
        return self.db.execute_query(sql, fetch=True)

    def get_codigos_avaria(self):
        return self.db.execute_query("SELECT * FROM CodigosAvaria", fetch=True)

    def salvar_analise(self, id_item, dados):
        sql = """
            UPDATE ItensGarantia
            SET numero_serie = %s, produzido_revenda = %s, fornecedor = %s,
                codigo_avaria = %s, descricao_avaria = %s, status = %s,
                procedente_improcedente = %s
            WHERE id = %s
        """
        self.db.execute_query(sql, (
            dados['serie'], dados['origem'], dados['fornecedor'],
            dados['cod_avaria'], dados['desc_avaria'],
            dados['status_resultado'], dados['status_resultado'],
            id_item
        ))