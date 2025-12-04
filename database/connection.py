import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

# CONFIGURAÇÕES DO BANCO (Ajuste sua senha aqui)
DB_CONFIG = {
    'dbname': 'cardex_db',
    'user': 'dev',
    'password': 'indisa',  # <--- COLOQUE SUA SENHA DO DOCKER AQUI
    'host': 'localhost',
    'port': '5432'
}

class DatabaseConnection:
    @contextmanager
    def get_connection(self):
        conn = psycopg2.connect(**DB_CONFIG)
        try:
            yield conn
        finally:
            conn.close()

    def execute_query(self, query, params=None, fetch=False):
        """Executa query de forma segura e retorna dicts se fetch=True"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                if fetch:
                    return cursor.fetchall()
                conn.commit()

    def setup_database(self):
        """Cria as tabelas se não existirem"""
        queries = [
            '''CREATE TABLE IF NOT EXISTS Clientes (
                cnpj TEXT PRIMARY KEY,
                cliente TEXT,
                cidade TEXT, estado TEXT
            )''',
            '''CREATE TABLE IF NOT EXISTS Produtos (
                codigo_item TEXT PRIMARY KEY,
                descricao TEXT,
                grupo_estoque TEXT
            )''',
            '''CREATE TABLE IF NOT EXISTS CodigosAvaria (
                codigo_avaria TEXT PRIMARY KEY,
                descricao_tecnica TEXT,
                status_padrao TEXT -- Procedente/Improcedente
            )''',
            '''CREATE TABLE IF NOT EXISTS NotasFiscais (
                id SERIAL PRIMARY KEY,
                numero_nota TEXT,
                data_nota DATE,
                cnpj_cliente TEXT,
                data_lancamento DATE,
                FOREIGN KEY (cnpj_cliente) REFERENCES Clientes(cnpj)
            )''',
            '''CREATE TABLE IF NOT EXISTS ItensGarantia (
                id SERIAL PRIMARY KEY,
                id_nota_fiscal INTEGER,
                codigo_produto TEXT,
                valor_item REAL,
                ressarcimento REAL,
                status TEXT DEFAULT 'Pendente',
                codigo_analise TEXT,
                numero_serie TEXT,
                codigo_avaria TEXT,
                descricao_avaria TEXT,
                procedente_improcedente TEXT,
                produzido_revenda TEXT,
                fornecedor TEXT,
                FOREIGN KEY (id_nota_fiscal) REFERENCES NotasFiscais(id)
            )'''
        ]
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    for q in queries:
                        cursor.execute(q)
                conn.commit()
            print("Banco de dados verificado/criado com sucesso.")
            return True  # <--- ADICIONE ISSO: Avisa que deu certo!
            
        except Exception as e:
            print(f"Erro ao configurar banco: {e}")
            return False # <--- ADICIONE ISSO: Avisa que deu errado!