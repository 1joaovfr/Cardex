import pandas as pd
from database.connection import DatabaseConnection

class RelatorioController:
    def __init__(self):
        self.db = DatabaseConnection()

    def buscar_dados(self):
        # SQL ajustado para incluir data_lancamento
        sql = """
            SELECT 
                l.status, 
                l.codigo_analise, 
                to_char(n.data_lancamento, 'DD/MM/YYYY') as data_lancamento, -- <--- ADICIONADO AQUI
                to_char(n.data_recebimento, 'DD/MM/YYYY') as data_recebimento,
                to_char(l.data_analise, 'DD/MM/YYYY') as data_analise,
                c.cnpj,
                c.cliente as nome_cliente,
                c.grupo as grupo_cliente,
                c.cidade,
                c.estado,
                c.regiao,
                n.numero_nota as nf_entrada,
                l.codigo_item,
                i.grupo_item,
                l.numero_serie,
                l.codigo_avaria,
                a.descricao_avaria,
                l.valor_item,
                l.ressarcimento,
                NULL as nf_retorno,
                NULL as tipo_retorno,
                NULL as data_retorno
            FROM itens_notas l
            JOIN notas_fiscais n ON l.id_nota_fiscal = n.id
            LEFT JOIN clientes c ON n.cnpj_cliente = c.cnpj
            LEFT JOIN itens i ON l.codigo_item = i.codigo_item
            LEFT JOIN avarias a ON l.codigo_avaria = a.codigo_avaria
            ORDER BY l.id DESC
        """
        return self.db.execute_query(sql, fetch=True)

    def exportar_excel(self, caminho, data_inicio, data_fim):
        # SQL ajustado para incluir data_lancamento no Excel também
        sql = """
            SELECT 
                l.status, 
                l.codigo_analise, 
                to_char(n.data_lancamento, 'DD/MM/YYYY') as data_lancamento, -- <--- ADICIONADO AQUI
                to_char(n.data_recebimento, 'DD/MM/YYYY') as data_recebimento,
                to_char(l.data_analise, 'DD/MM/YYYY') as data_analise,
                c.cliente as nome_cliente, 
                n.numero_nota as nf_entrada, 
                l.codigo_item, 
                l.numero_serie, 
                a.descricao_avaria, 
                l.valor_item, 
                l.ressarcimento
            FROM itens_notas l
            JOIN notas_fiscais n ON l.id_nota_fiscal = n.id
            LEFT JOIN clientes c ON n.cnpj_cliente = c.cnpj
            LEFT JOIN itens i ON l.codigo_item = i.codigo_item
            LEFT JOIN avarias a ON l.codigo_avaria = a.codigo_avaria
            WHERE n.data_lancamento BETWEEN %s AND %s
            ORDER BY n.data_lancamento ASC
        """
        try:
            dados = self.db.execute_query(sql, (data_inicio, data_fim), fetch=True)
            if not dados: return False
            
            df = pd.DataFrame(dados)
            
            # Renomear colunas para ficar bonito no Excel
            df.rename(columns={
                'status': 'Status',
                'codigo_analise': 'Cód. Análise',
                'data_lancamento': 'Data Lançamento',
                'data_recebimento': 'Data Recebimento',
                'data_analise': 'Data Análise',
                'nome_cliente': 'Cliente',
                'nf_entrada': 'NF Entrada',
                'codigo_item': 'Item',
                'numero_serie': 'Nº Série',
                'descricao_avaria': 'Defeito',
                'valor_item': 'Valor',
                'ressarcimento': 'Ressarcimento'
            }, inplace=True)

            df.to_excel(caminho, index=False)
            return True
        except Exception as e:
            print(f"Erro Excel: {e}")
            return False