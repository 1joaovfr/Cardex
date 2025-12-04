import random
from datetime import datetime, timedelta
from database.connection import DatabaseConnection

class DatabaseSeeder:
    def __init__(self):
        self.db = DatabaseConnection()
        
    def limpar_banco(self):
        """Limpa dados antigos para evitar duplicidade (Opcional)"""
        print("Limpando tabelas antigas...")
        cmds = [
            "TRUNCATE TABLE ItensGarantia RESTART IDENTITY CASCADE;",
            "TRUNCATE TABLE NotasFiscais RESTART IDENTITY CASCADE;",
            "TRUNCATE TABLE Produtos RESTART IDENTITY CASCADE;",
            "TRUNCATE TABLE Clientes RESTART IDENTITY CASCADE;",
            "TRUNCATE TABLE CodigosAvaria RESTART IDENTITY CASCADE;"
        ]
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                for cmd in cmds:
                    try:
                        cursor.execute(cmd)
                    except Exception as e:
                        print(f"Aviso ao limpar (pode ser a primeira vez): {e}")
                conn.commit()

    def seed_clientes(self):
        print("Gerando Clientes...")
        clientes = [
            ("12345678000199", "AUTO PEÇAS SILVA", "São Paulo", "SP"),
            ("98765432000155", "OFICINA DO ZÉ", "Rio de Janeiro", "RJ"),
            ("11222333000188", "DISTRIBUIDORA NORTE", "Manaus", "AM"),
            ("44555666000177", "SUL PEÇAS LTDA", "Porto Alegre", "RS"),
            ("99888777000122", "CENTRO AUTOMOTIVO MINAS", "Belo Horizonte", "MG"),
        ]
        sql = "INSERT INTO Clientes (cnpj, cliente, cidade, estado) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING"
        
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                for c in clientes:
                    cursor.execute(sql, c)
            conn.commit()
            
    def seed_produtos(self):
        print("Gerando Produtos...")
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
        sql = "INSERT INTO Produtos (codigo_item, descricao, grupo_estoque) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING"
        
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                for p in produtos:
                    cursor.execute(sql, p)
            conn.commit()

    def seed_avarias(self):
        print("Gerando Códigos de Avaria...")
        avarias = [
            ("001", "Quebra Física / Mau Uso", "Improcedente"),
            ("002", "Defeito de Fabricação (Vazamento)", "Procedente"),
            ("003", "Ruído Excessivo", "Procedente"),
            ("004", "Instalação Incorreta", "Improcedente"),
            ("005", "Desgaste Natural", "Improcedente"),
            ("006", "Falha Elétrica Interna", "Procedente"),
        ]
        sql = "INSERT INTO CodigosAvaria (codigo_avaria, descricao_tecnica, status_padrao) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING"
        
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                for a in avarias:
                    cursor.execute(sql, a)
            conn.commit()

    def seed_movimentacao(self, qtd_notas=20):
        print(f"Gerando {qtd_notas} Notas Fiscais com Itens...")
        
        # Recuperar dados base para gerar relacionamentos válidos
        clientes = self.db.execute_query("SELECT cnpj FROM Clientes", fetch=True)
        produtos = self.db.execute_query("SELECT * FROM Produtos", fetch=True)
        avarias = self.db.execute_query("SELECT * FROM CodigosAvaria", fetch=True)
        
        cnjps = [c['cnpj'] for c in clientes]
        
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                for i in range(qtd_notas):
                    # 1. Criar Nota
                    num_nota = f"{random.randint(1000, 99999)}"
                    cnpj = random.choice(cnjps)
                    # Data aleatória nos últimos 60 dias
                    dias_atras = random.randint(0, 365)
                    data_lanc = datetime.now() - timedelta(days=dias_atras)
                    data_nota = data_lanc - timedelta(days=random.randint(1, 10))
                    
                    sql_nf = """
                        INSERT INTO NotasFiscais (numero_nota, data_nota, cnpj_cliente, data_lancamento)
                        VALUES (%s, %s, %s, %s) RETURNING id
                    """
                    cursor.execute(sql_nf, (num_nota, data_nota.date(), cnpj, data_lanc.date()))
                    id_nota = cursor.fetchone()[0]
                    
                    # 2. Criar Itens para essa nota (1 a 5 itens)
                    qtd_itens = random.randint(1, 5)
                    for _ in range(qtd_itens):
                        prod = random.choice(produtos)
                        valor = round(random.uniform(50.0, 500.0), 2)
                        ressarc = 0.0
                        if random.random() > 0.8: # 20% chance de ter ressarcimento
                            ressarc = round(random.uniform(10.0, 50.0), 2)
                        
                        # Definir Status Aleatório
                        status_choice = random.choice(['Pendente', 'Pendente', 'Procedente', 'Improcedente'])
                        
                        cod_analise = f"{data_lanc.strftime('%Y%m')}-{random.randint(10000, 99999)}"
                        
                        # Se não for pendente, precisa de laudo
                        cod_avaria = None
                        desc_avaria = None
                        proc_imp = None
                        serie = None
                        origem = None
                        forn = None
                        
                        if status_choice != 'Pendente':
                            avaria = random.choice(avarias)
                            cod_avaria = avaria['codigo_avaria']
                            desc_avaria = f"Análise técnica: {avaria['descricao_tecnica']}"
                            proc_imp = status_choice # Procedente ou Improcedente
                            serie = f"SN{random.randint(100000, 999999)}"
                            origem = random.choice(['Produzido', 'Revenda'])
                            if origem == 'Revenda':
                                forn = "Fabricante Original X"

                        sql_item = """
                            INSERT INTO ItensGarantia 
                            (id_nota_fiscal, codigo_produto, valor_item, ressarcimento, status, 
                             codigo_analise, numero_serie, codigo_avaria, descricao_avaria,
                             procedente_improcedente, produzido_revenda, fornecedor)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        cursor.execute(sql_item, (
                            id_nota, prod['codigo_item'], valor, ressarc, status_choice,
                            cod_analise, serie, cod_avaria, desc_avaria,
                            proc_imp, origem, forn
                        ))
                
                conn.commit()

    def run(self):
        try:
            self.limpar_banco()
            self.seed_clientes()
            self.seed_produtos()
            self.seed_avarias()
            self.seed_movimentacao(qtd_notas=30) # Gera 30 notas
            print("\n✅ Banco de dados populado com sucesso!")
            print("Agora você pode rodar 'python main.py' e ver os dados no Dashboard e Relatórios.")
        except Exception as e:
            print(f"\n❌ Erro ao popular banco: {e}")

if __name__ == "__main__":
    seeder = DatabaseSeeder()
    seeder.run()