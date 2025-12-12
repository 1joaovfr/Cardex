# models.py
from database import DatabaseConnection # Sua classe de conexão

class RetornoModel:
    def __init__(self):
        self.db = DatabaseConnection()

    def buscar_itens_pendentes(self, filtro_valor, tipo_filtro):
        """
        Busca itens que ainda têm saldo financeiro (dívida).
        tipo_filtro: 'CNPJ' ou 'GRUPO'
        """
        query = """
            SELECT 
                i.id, 
                nf.numero_nota, 
                nf.data_nota, 
                i.codigo_item, 
                i.valor_item, 
                i.saldo_financeiro,
                c.cliente as nome_cliente
            FROM itens_notas i
            JOIN notas_fiscais nf ON i.id_nota_fiscal = nf.id
            JOIN clientes c ON nf.cnpj_cliente = c.cnpj
            WHERE i.saldo_financeiro > 0
        """
        
        params = [filtro_valor]
        
        if tipo_filtro == 'CNPJ':
            query += " AND nf.cnpj_cliente = %s"
        elif tipo_filtro == 'GRUPO':
            query += " AND c.grupo = %s"
            
        query += " ORDER BY nf.data_nota ASC" # FIFO (Primeiro que entra, primeiro que sai)

        return self.db.execute_query(query, params, fetch=True)

    def salvar_retorno_com_transacao(self, dados_retorno, itens_selecionados):
        """
        Realiza a gravação atômica: Cria Retorno + Cria Conciliação + Baixa Saldo Entrada
        """
        conn_manager = self.db.get_connection()
        with conn_manager as conn:
            try:
                cursor = conn.cursor()
                
                # 1. Criar Cabeçalho do Retorno
                sql_retorno = """
                    INSERT INTO notas_retorno (numero_nota, data_emissao, tipo_retorno, cnpj_cliente, grupo_economico, valor_total_nota)
                    VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
                """
                cursor.execute(sql_retorno, (
                    dados_retorno['numero'],
                    dados_retorno['data'],
                    dados_retorno['tipo'],
                    dados_retorno.get('cnpj'),
                    dados_retorno.get('grupo'),
                    dados_retorno['valor_total']
                ))
                id_retorno = cursor.fetchone()[0]

                # 2. Processar cada item selecionado (abatimento)
                for item in itens_selecionados:
                    id_entrada = item['id']
                    valor_a_abater = item['valor_abatido'] # Quanto vamos usar deste item

                    # A. Atualiza Saldo na Entrada
                    sql_update = "UPDATE itens_notas SET saldo_financeiro = saldo_financeiro - %s WHERE id = %s"
                    cursor.execute(sql_update, (valor_a_abater, id_entrada))

                    # B. Cria vínculo na Conciliação
                    sql_conciliacao = """
                        INSERT INTO conciliacao (id_nota_retorno, id_item_entrada, valor_abatido)
                        VALUES (%s, %s, %s)
                    """
                    cursor.execute(sql_conciliacao, (id_retorno, id_entrada, valor_a_abater))

                conn.commit()
                return True, "Retorno processado com sucesso!"
            
            except Exception as e:
                conn.rollback()
                return False, f"Erro ao processar retorno: {str(e)}"