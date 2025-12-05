import random
from datetime import datetime, timedelta
from database.connection import DatabaseConnection

class DatabaseSeeder:
    def __init__(self):
        self.db = DatabaseConnection()
        
    def limpar_banco(self):
        """
        Apaga as tabelas antigas e recria a estrutura nova.
        Isso garante que novas colunas (como 'grupo' e 'regiao') sejam criadas.
        """
        print("Recriando estrutura do banco de dados...")
        
        # 1. DROP: Apaga as tabelas existentes (Cuidado: apaga todos os dados!)
        cmds_drop = [
            "DROP TABLE IF EXISTS itens_notas CASCADE;",
            "DROP TABLE IF EXISTS notas_fiscais CASCADE;", # Se sua tabela chama notas_fiscais, ajuste aqui
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

        # 2. RECRIAR: Chama o método setup_database da sua classe de conexão
        # Isso vai rodar os CREATE TABLE novos que você definiu no Passo 1
        sucesso = self.db.setup_database()
        
        if sucesso:
            print("✅ Tabelas recriadas com a nova estrutura!")
        else:
            print("❌ Erro ao recriar tabelas. Verifique o console.")
            raise Exception("Falha ao recriar schema do banco.")
        
    def seed_clientes(self):
        print("Gerando clientes...")
        # Adicionei 'Grupo' e 'Região' aos dados
        clientes = [
            ("12345678000199", "AUTO PEÇAS SILVA", "Varejo", "São Paulo", "SP", "Sudeste"),
            ("98765432000155", "OFICINA DO ZÉ", "Oficina", "Rio de Janeiro", "RJ", "Sudeste"),
            ("11222333000188", "DISTRIBUIDORA NORTE", "Distribuidor", "Manaus", "AM", "Norte"),
            ("44555666000177", "SUL PEÇAS LTDA", "Varejo", "Porto Alegre", "RS", "Sul"),
            ("99888777000122", "CENTRO AUTO MINAS", "Oficina", "Belo Horizonte", "MG", "Sudeste"),
        ]
        # Query atualizada para a tabela clientes
        sql = """
            INSERT INTO clientes (cnpj, cliente, grupo, cidade, estado, regiao) 
            VALUES (%s, %s, %s, %s, %s, %s) 
            ON CONFLICT DO NOTHING
        """
        
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                for c in clientes:
                    cursor.execute(sql, c)
            conn.commit()
            
    def seed_itens(self):
        print("Gerando itens...")
        # Atualizado para tabela itens
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
            VALUES (%s, %s, %s) 
            ON CONFLICT DO NOTHING
        """
        
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                for p in produtos:
                    cursor.execute(sql, p)
            conn.commit()

    def seed_avarias(self):
        print("Gerando avarias...")
        # Atualizado para tabela avarias
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
            VALUES (%s, %s, %s) 
            ON CONFLICT DO NOTHING
        """
        
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                for a in avarias:
                    cursor.execute(sql, a)
            conn.commit()

    def seed_movimentacao(self, qtd_notas=20):
        print(f"Gerando {qtd_notas} notas_fiscais com Lançamentos...")
        
        # Recupera dados usando os NOMES NOVOS das tabelas
        clientes = self.db.execute_query("SELECT cnpj FROM clientes", fetch=True)
        itens = self.db.execute_query("SELECT * FROM itens", fetch=True)
        avarias = self.db.execute_query("SELECT * FROM avarias", fetch=True)
        
        if not clientes or not itens or not avarias:
            print("Erro: Tabelas base vazias. Rode os seeds anteriores primeiro.")
            return

        cnjps = [c['cnpj'] for c in clientes]
        sequencia_por_letra = {}
        
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                for i in range(qtd_notas):
                    # 1. CRIAR NOTA (Tabela notas_fiscais)
                    num_nota = f"{random.randint(1000, 99999)}"
                    cnpj = random.choice(cnjps)
                    
                    # Datas
                    dias_atras = random.randint(0, 365)
                    data_lanc = datetime.now() - timedelta(days=dias_atras)
                    data_receb = data_lanc - timedelta(days=random.randint(0, 2)) # Recebido 0-2 dias antes do lançamento
                    data_nota = data_receb - timedelta(days=random.randint(1, 10)) # Nota emitida 1-10 dias antes de chegar
                    
                    sql_nf = """
                        INSERT INTO notas_fiscais (numero_nota, data_nota, cnpj_cliente, data_recebimento, data_lancamento)
                        VALUES (%s, %s, %s, %s, %s) RETURNING id
                    """
                    cursor.execute(sql_nf, (num_nota, data_nota.date(), cnpj, data_receb.date(), data_lanc.date()))
                    id_nota = cursor.fetchone()[0]
                    
                    # Lógica da Letra (Janeiro=A, Fevereiro=B...)
                    mes_lancamento = data_lanc.month
                    letra_mes = chr(ord('A') + mes_lancamento - 1)

                    # 2. CRIAR LANÇAMENTOS (Tabela itens_notas)
                    qtd_itens = random.randint(1, 5)
                    
                    for _ in range(qtd_itens):
                        item = random.choice(itens)
                        valor = round(random.uniform(50.0, 500.0), 2)
                        
                        ressarc = 0.0
                        if random.random() > 0.8: 
                            ressarc = round(random.uniform(10.0, 50.0), 2)
                        
                        status_choice = random.choice(['Pendente', 'Pendente', 'Procedente', 'Improcedente'])
                        
                        # GERAÇÃO DO CÓDIGO DE ANÁLISE (A0001, A0002...)
                        if letra_mes not in sequencia_por_letra:
                            sequencia_por_letra[letra_mes] = 0
                        
                        sequencia_por_letra[letra_mes] += 1
                        seq_atual = sequencia_por_letra[letra_mes]
                        cod_analise = f"{letra_mes}{seq_atual:04d}"
                        
                        # Dados da Avaria
                        cod_avaria = None
                        desc_avaria = None
                        proc_imp = None
                        serie = None
                        origem = None
                        forn = None
                        
                        if status_choice != 'Pendente':
                            avaria = random.choice(avarias)
                            cod_avaria = avaria['codigo_avaria']
                            desc_avaria = avaria['descricao_avaria'] # Coluna nova
                            proc_imp = status_choice 
                            serie = f"SN{random.randint(100000, 999999)}"
                            origem = random.choice(['Produzido', 'Revenda'])
                            if origem == 'Revenda':
                                forn = "Fabricante Original X"

                        sql_lanc = """
                            INSERT INTO itens_notas 
                            (id_nota_fiscal, codigo_item, valor_item, ressarcimento, status, 
                             codigo_analise, numero_serie, codigo_avaria, descricao_avaria,
                             procedente_improcedente, produzido_revenda, fornecedor)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        cursor.execute(sql_lanc, (
                            id_nota, item['codigo_item'], valor, ressarc, status_choice,
                            cod_analise, serie, cod_avaria, desc_avaria,
                            proc_imp, origem, forn
                        ))
                
                conn.commit()

    def run(self):
        try:
            self.limpar_banco()
            self.seed_clientes()
            self.seed_itens()
            self.seed_avarias()
            self.seed_movimentacao(qtd_notas=100) 
            print("\n✅ Banco de dados populado com sucesso (Novo Schema)!")
        except Exception as e:
            print(f"\n❌ Erro ao popular banco: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    seeder = DatabaseSeeder()
    seeder.run()