import pandas as pd
from database.connection import DatabaseConnection

class RelatorioController:
    def __init__(self):
        self.db = DatabaseConnection()

    def buscar_dados(self):
        sql = """
            SELECT 
                i.status, i.codigo_analise, to_char(nf.data_lancamento, 'DD/MM/YYYY') as recebimento,
                c.cliente as razao_social, c.estado, nf.numero_nota,
                i.codigo_produto, i.numero_serie, i.codigo_avaria,
                i.valor_item, i.ressarcimento
            FROM ItensGarantia i
            JOIN NotasFiscais nf ON i.id_nota_fiscal = nf.id
            LEFT JOIN Clientes c ON nf.cnpj_cliente = c.cnpj
            ORDER BY i.id DESC
        """
        return self.db.execute_query(sql, fetch=True)

    def exportar_excel(self, caminho):
        dados = self.buscar_dados()
        if not dados: return False
        df = pd.DataFrame(dados)
        df.to_excel(caminho, index=False)
        return True