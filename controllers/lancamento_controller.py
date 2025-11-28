from datetime import datetime
from database.connection import DatabaseConnection

class LancamentoController:
    def __init__(self):
        self.db = DatabaseConnection()

    def buscar_cliente_por_cnpj(self, cnpj_sujo):
        cnpj = ''.join(filter(str.isdigit, cnpj_sujo))
        query = "SELECT cliente FROM Clientes WHERE cnpj = %s"
        result = self.db.execute_query(query, (cnpj,), fetch=True)
        return result[0]['cliente'] if result else None

    def salvar_nota_entrada(self, dados_nota, lista_itens):
        cnpj_limpo = ''.join(filter(str.isdigit, dados_nota['cnpj']))
        
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                # 1. Inserir Nota
                sql_nf = """
                    INSERT INTO NotasFiscais (numero_nota, data_nota, cnpj_cliente, data_lancamento)
                    VALUES (%s, %s, %s, %s) RETURNING id
                """
                cursor.execute(sql_nf, (
                    dados_nota['numero'], 
                    dados_nota['emissao'], 
                    cnpj_limpo, 
                    dados_nota['recebimento']
                ))
                id_nota = cursor.fetchone()[0]

                # 2. Inserir Itens (EXPLOSÃO DE ITENS)
                sql_item = """
                    INSERT INTO ItensGarantia 
                    (id_nota_fiscal, codigo_produto, valor_item, ressarcimento, codigo_analise, status)
                    VALUES (%s, %s, %s, %s, %s, 'Pendente')
                """
                
                ano_mes = datetime.now().strftime("%Y%m")
                
                for item in lista_itens:
                    qtd = int(item['qtd'])
                    # Loop para criar uma linha por unidade
                    for i in range(qtd):
                        # Gera código sequencial fake (em prod usar Sequence)
                        cursor.execute("SELECT count(*) + 1 FROM ItensGarantia") 
                        prox_id = cursor.fetchone()[0]
                        cod_analise = f"{ano_mes}-{prox_id}"

                        cursor.execute(sql_item, (
                            id_nota,
                            item['codigo'],
                            item['valor'],
                            item['ressarcimento'],
                            cod_analise
                        ))
            conn.commit()
        return True