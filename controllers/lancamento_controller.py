from datetime import datetime
from database.connection import DatabaseConnection

class LancamentoController:
    def __init__(self):
        self.db = DatabaseConnection()

    def buscar_cliente_por_cnpj(self, cnpj_sujo):
        cnpj = ''.join(filter(str.isdigit, cnpj_sujo))
        query = "SELECT cliente FROM clientes WHERE cnpj = %s"
        result = self.db.execute_query(query, (cnpj,), fetch=True)
        return result[0]['cliente'] if result else None
    
    def buscar_produto_por_codigo(self, codigo):
        query = "SELECT codigo_item FROM itens WHERE codigo_item = %s"
        result = self.db.execute_query(query, (codigo,), fetch=True)
        return True if result else False

    def salvar_nota_entrada(self, dados_nota, lista_itens):
        # 1. Validação prévia (MANTIDA)
        cliente_existente = self.buscar_cliente_por_cnpj(dados_nota['cnpj'])
        
        if not cliente_existente:
            raise Exception(f"Erro de Validação:\n\nO CNPJ {dados_nota['cnpj']} não está cadastrado...")

        cnpj_limpo = ''.join(filter(str.isdigit, dados_nota['cnpj']))
        
        # --- NOVO: Captura a data atual do sistema ---
        # Isso garante que a data seja HOJE, independente do que o usuário selecione
        data_lancamento_automatico = datetime.now().date() 
        
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                # -----------------------------------------------------------
                # 1. Inserir Nota Fiscal
                # -----------------------------------------------------------
                sql_nf = """
                    INSERT INTO notas_fiscais (numero_nota, data_nota, cnpj_cliente, data_lancamento)
                    VALUES (%s, %s, %s, %s) RETURNING id
                """
                cursor.execute(sql_nf, (
                    dados_nota['numero'], 
                    dados_nota['emissao'], 
                    cnpj_limpo, 
                    data_lancamento_automatico  # <--- AQUI MUDOU: Usamos a variável automática
                ))
                id_nota = cursor.fetchone()[0]

                # -----------------------------------------------------------
                # 2. Preparação para o Código de Análise (A0001...)
                # -----------------------------------------------------------
                data_atual = datetime.now()
                mes_atual = data_atual.month  # Retorna int (1 a 12)
                
                # Lógica: ASCII 'A' é 65. 
                # Se mês 1: 65 + 1 - 1 = 65 ('A')
                # Se mês 12: 65 + 12 - 1 = 76 ('L')
                letra_mes = chr(ord('A') + mes_atual - 1)

                # Busca o MAIOR código existente que começa com essa letra para continuar a sequência
                # Exemplo: Se existir A0005, retorna A0005. Se não existir, retorna None.
                sql_seq = "SELECT MAX(codigo_analise) FROM itens_notas WHERE codigo_analise LIKE %s"
                cursor.execute(sql_seq, (f"{letra_mes}%",))
                resultado = cursor.fetchone()
                
                ultimo_codigo = resultado[0] if resultado else None
                
                if ultimo_codigo:
                    # Se achou "A0005", pega o "0005", vira int 5 e soma 1 -> 6
                    sequencial_atual = int(ultimo_codigo[1:]) + 1
                else:
                    # Se é a primeira peça do mês
                    sequencial_atual = 1

                # -----------------------------------------------------------
                # 3. Inserir itens (Com loop do sequencial)
                # -----------------------------------------------------------
                sql_item = """
                    INSERT INTO itens_notas 
                    (id_nota_fiscal, codigo_item, valor_item, ressarcimento, codigo_analise, status)
                    VALUES (%s, %s, %s, %s, %s, 'Pendente')
                """
                
                for item in lista_itens:
                    qtd = int(item['qtd'])
                    
                    # Loop para criar uma linha por unidade (Explosão de itens)
                    for i in range(qtd):
                        # Formata o código: Letra + numero com 4 casas preenchidas com zero
                        # Ex: A + 0001 = A0001
                        cod_analise = f"{letra_mes}{sequencial_atual:04d}"

                        cursor.execute(sql_item, (
                            id_nota,
                            item['codigo'],
                            item['valor'],
                            item['ressarcimento'],
                            cod_analise
                        ))
                        
                        # Incrementa para a próxima volta do loop (A0002, A0003...)
                        sequencial_atual += 1

            conn.commit()
        return True