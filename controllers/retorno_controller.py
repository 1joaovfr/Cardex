from models import RetornoModel

class RetornoController:
    def __init__(self):
        self.model = RetornoModel()

    def buscar_pendencias(self, termo, modo):
        # modo = "CNPJ" ou "GRUPO"
        # termo = O número do CNPJ ou Nome do Grupo
        if not termo:
            return []
        return self.model.buscar_itens_pendentes(termo, modo)

    def processar_retorno(self, cabecalho, itens_grid):
        """
        cabecalho: dict com dados da NF de Retorno
        itens_grid: lista de dicts com os itens que o usuário selecionou na tela
        """
        
        valor_nota_retorno = float(cabecalho['valor_total'])
        soma_itens_selecionados = sum(item['valor_abatido'] for item in itens_grid)
        tipo = cabecalho['tipo']

        # REGRA 1: Validação de Valores (Crucial para Giro)
        # O valor dos itens selecionados (dívida) NÃO pode ser maior que o valor da Nota de Retorno (pagamento).
        # Mas o valor da Nota de Retorno PODE ser maior (sobra crédito/brinde).
        if soma_itens_selecionados > valor_nota_retorno:
            return False, f"A soma dos itens (R$ {soma_itens_selecionados:.2f}) excede o valor da Nota de Retorno (R$ {valor_nota_retorno:.2f})."

        # REGRA 2: Validação de Simples
        if tipo == 'SIMPLES':
            # No simples, geralmente o valor deve bater exato, ou validamos SKU
            # Para simplificar aqui, vamos focar no financeiro, mas você pode adicionar check de SKU
            if abs(soma_itens_selecionados - valor_nota_retorno) > 0.01:
                return False, "No Retorno Simples, o valor dos itens deve ser igual ao da Nota."

        # Se passou nas regras, chama o model
        return self.model.salvar_retorno_com_transacao(cabecalho, itens_grid)