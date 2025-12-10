import random
from datetime import datetime, timedelta
from database.connection import DatabaseConnection

class DatabaseSeeder:
    def __init__(self):
        self.db = DatabaseConnection()
        
    def limpar_banco(self):
        """Apaga as tabelas antigas e recria a estrutura nova vazia."""
        print("Recriando estrutura do banco de dados...")
        
        # Ordem importa por causa das Foreign Keys
        cmds_drop = [
            "DROP TABLE IF EXISTS itens_notas CASCADE;",
            "DROP TABLE IF EXISTS notas_fiscais CASCADE;",
            "DROP TABLE IF EXISTS itens CASCADE;",
            "DROP TABLE IF EXISTS clientes CASCADE;",
            "DROP TABLE IF EXISTS avarias CASCADE;",
        ]
        
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                for cmd in cmds_drop:
                    try:
                        cursor.execute(cmd)
                    except Exception as e:
                        print(f"Aviso ao dropar tabela: {e}")
                conn.commit()

        # Chama o setup do banco real
        sucesso = self.db.setup_database()
        
        if sucesso:
            print("✅ Tabelas recriadas e limpas!")
        else:
            raise Exception("Falha ao recriar schema do banco.")

    def seed_clientes(self):
        print("Inserindo Clientes padrão...")
        clientes = [
            ("12345678000199", "AUTO PEÇAS SILVA", "Varejo", "São Paulo", "SP", "Sudeste"),
            ("98765432000155", "OFICINA DO ZÉ", "Oficina", "Rio de Janeiro", "RJ", "Sudeste"),
            ("11222333000188", "DISTRIBUIDORA NORTE", "Distribuidor", "Manaus", "AM", "Norte"),
            ("44555666000177", "SUL PEÇAS LTDA", "Varejo", "Porto Alegre", "RS", "Sul"),
            ("99888777000122", "CENTRO AUTO MINAS", "Oficina", "Belo Horizonte", "MG", "Sudeste"),
        ]
        sql = """
            INSERT INTO clientes (cnpj, cliente, grupo, cidade, estado, regiao) 
            VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING
        """
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                for c in clientes:
                    cursor.execute(sql, c)
            conn.commit()
            
    def seed_itens(self):
        print("Inserindo Produtos padrão...")
        produtos = [
            ("P001", "Bomba de Combustível", "Motor"),
            ("P002", "Pastilha de Freio Diant.", "Freios"),
            ("P003", "Alternador 12V", "Elétrica"),
            ("P004", "Amortecedor Traseiro", "Suspensão"),
            ("P005", "Kit Embreagem", "Transmissão"),
            ("P006", "Sensor Lambda", "Injeção"),
            ("P007", "Radiador", "Arrefecimento"),
            ("P008", "Vela de Ignição", "Ignição"),
        ]
        sql = """
            INSERT INTO itens (codigo_item, descricao_item, grupo_item) 
            VALUES (%s, %s, %s) ON CONFLICT DO NOTHING
        """
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                for p in produtos:
                    cursor.execute(sql, p)
            conn.commit()

    def seed_avarias(self):
        print("Inserindo Avarias padrão...")
        avarias = [
            ("001", "Quebra Física / Mau Uso", "Improcedente"),
            ("002", "Defeito de Fabricação (Vazamento)", "Procedente"),
            ("003", "Ruído Excessivo", "Procedente"),
            ("004", "Instalação Incorreta", "Improcedente"),
            ("005", "Desgaste Natural", "Improcedente"),
            ("006", "Falha Elétrica Interna", "Procedente"),
        ]
        sql = """
            INSERT INTO avarias (codigo_avaria, descricao_avaria, status_avaria) 
            VALUES (%s, %s, %s) ON CONFLICT DO NOTHING
        """
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                for a in avarias:
                    cursor.execute(sql, a)
            conn.commit()

    def seed_movimentacao(self):
        """
        Gera Notas Fiscais e Itens de Notas aleatórios para teste.
        """
        print("Gerando Movimentação (Notas e Itens)...")
        
        # 1. Recuperar dados base para fazer relacionamentos válidos
        lista_cnpjs = []
        lista_produtos = [] # Tupla (codigo, preco_base)
        lista_avarias = []  # Tupla (codigo, descricao, status)

        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT cnpj FROM clientes")
                lista_cnpjs = [row[0] for row in cursor.fetchall()]
                
                cursor.execute("SELECT codigo_item FROM itens")
                # Preços simulados baseados no ID só para variar
                lista_produtos = [(row[0], random.randint(50, 500)) for row in cursor.fetchall()]
                
                cursor.execute("SELECT codigo_avaria, descricao_avaria, status_avaria FROM avarias")
                lista_avarias = cursor.fetchall()

        if not lista_cnpjs or not lista_produtos:
            print("❌ Erro: Não há clientes ou produtos para gerar movimentação.")
            return

        # Lógica para o Sequencial do Código de Análise (Simulação local)
        data_atual = datetime.now()
        letra_mes = chr(ord('A') + data_atual.month - 1)
        contador_analise = 1

        # Vamos criar 10 Notas Fiscais
        for i in range(10):
            cnpj_escolhido = random.choice(lista_cnpjs)
            num_nota = f"{random.randint(1000, 9999)}"
            data_emissao = data_atual - timedelta(days=random.randint(5, 30))
            data_entrada = data_emissao + timedelta(days=random.randint(1, 5))

            with self.db.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 1. Inserir Nota Fiscal (Assumindo estrutura básica, ajuste conforme seu DB real)
                    sql_nota = """
                        INSERT INTO notas_fiscais (numero_nota, cnpj_cliente, data_emissao, data_entrada)
                        VALUES (%s, %s, %s, %s) RETURNING id
                    """
                    # Se sua tabela notas_fiscais tiver colunas diferentes, ajuste aqui
                    try:
                        cursor.execute(sql_nota, (num_nota, cnpj_escolhido, data_emissao, data_entrada))
                        id_nota = cursor.fetchone()[0]
                    except Exception as e:
                        print(f"Erro ao criar nota simulada: {e}")
                        continue # Pula para a próxima se der erro na nota

                    # 2. Inserir Itens para essa Nota (1 a 4 itens por nota)
                    qtd_itens = random.randint(1, 4)
                    for _ in range(qtd_itens):
                        produto = random.choice(lista_produtos) # (cod, preco)
                        cod_prod = produto[0]
                        valor = float(produto[1])
                        
                        # Decide aleatoriamente se o item já foi analisado ou está pendente
                        status = random.choice(['Pendente', 'Finalizado', 'Finalizado']) # Peso maior para finalizado
                        
                        cod_analise = None
                        data_analise_item = None
                        avaria_escolhida = (None, None, None)
                        procedente = None
                        ressarcimento = 0.0
                        
                        if status == 'Finalizado':
                            # Aplica sua lógica de Código de Análise
                            cod_analise = f"{letra_mes}{contador_analise:04d}" # Ex: L0001
                            contador_analise += 1
                            
                            data_analise_item = data_entrada + timedelta(days=random.randint(1, 3))
                            avaria_escolhida = random.choice(lista_avarias)
                            procedente = avaria_escolhida[2] # Procedente/Improcedente vindo da tabela avarias
                            
                            if procedente == 'Procedente':
                                ressarcimento = valor # Reembolsa o valor total
                            else:
                                ressarcimento = 0.0

                        # SQL de inserção do Item
                        sql_item = """
                            INSERT INTO itens_notas (
                                id_nota_fiscal, codigo_item, valor_item, ressarcimento, 
                                status, codigo_analise, data_analise, numero_serie,
                                codigo_avaria, descricao_avaria, procedente_improcedente,
                                produzido_revenda, fornecedor
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        
                        valores_item = (
                            id_nota,
                            cod_prod,
                            valor,
                            ressarcimento,
                            status,
                            cod_analise,
                            data_analise_item,
                            f"NS{random.randint(10000,99999)}", # Num Serie Fake
                            avaria_escolhida[0], # Cod Avaria
                            avaria_escolhida[1], # Desc Avaria
                            procedente,
                            random.choice(['Produzido', 'Revenda']),
                            "Fornecedor Padrão LTDA"
                        )
                        
                        cursor.execute(sql_item, valores_item)
                
                conn.commit() # Commit a cada nota completa (nota + itens)

    def run(self):
        try:
            self.limpar_banco()
            
            self.seed_clientes()
            self.seed_itens()
            self.seed_avarias()
            
            # Nova chamada
            self.seed_movimentacao()
            
            print("\n✅ Banco de dados populado com sucesso!")
        except Exception as e:
            print(f"\n❌ Erro ao popular banco: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    seeder = DatabaseSeeder()
    seeder.run()