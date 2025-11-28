from database.connection import DatabaseConnection

class RetornoController:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def salvar_produto(self, cod, desc, cat, preco):
        # Exemplo simples para a tela de Retorno/Estoque
        # Adapte conforme sua necessidade real da tela de retorno
        sql = "INSERT INTO Produtos (codigo_item, descricao, grupo_estoque) VALUES (%s, %s, %s)"
        try:
            self.db.execute_query(sql, (cod, desc, cat))
            return True
        except:
            return False