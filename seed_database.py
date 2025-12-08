from database.connection import DatabaseConnection

class DatabaseSeeder:
    def __init__(self):
        self.db = DatabaseConnection()
        
    def limpar_banco(self):
        """
        Apaga as tabelas antigas e recria a estrutura nova vazia.
        """
        print("Recriando estrutura do banco de dados...")
        
        # 1. DROP: Apaga as tabelas existentes
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

        # 2. RECRIAR: Chama o método setup_database da sua classe de conexão
        sucesso = self.db.setup_database()
        
        if sucesso:
            print("✅ Tabelas recriadas e limpas!")
        else:
            print("❌ Erro ao recriar tabelas. Verifique o console.")
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
            VALUES (%s, %s, %s, %s, %s, %s) 
            ON CONFLICT DO NOTHING
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
            VALUES (%s, %s, %s) 
            ON CONFLICT DO NOTHING
        """
        
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                for p in produtos:
                    cursor.execute(sql, p)
            conn.commit()

    def seed_avarias(self):
        print("Inserindo Códigos de Avaria padrão...")
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

    def run(self):
        try:
            # 1. Limpa tudo e cria tabelas vazias
            self.limpar_banco()
            
            # 2. Insere apenas os cadastros básicos
            self.seed_clientes()
            self.seed_itens()
            self.seed_avarias()
            
            print("\n✅ Banco de dados pronto! (Tabelas de notas estão vazias)")
        except Exception as e:
            print(f"\n❌ Erro ao popular banco: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    seeder = DatabaseSeeder()
    seeder.run()