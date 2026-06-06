"""
Gerenciamento de Contexto da Aplicação via ContextVars.
Isso permite injetar a configuração da instância atual
sem precisar passar 'instance: dict' por todas as funções.
"""
from contextvars import ContextVar

# A variável de contexto armazena o dicionário da instância atual
# proveniente do banco de dados (tabela bots.instances).
current_instance: ContextVar[dict] = ContextVar("current_instance", default={})

def get_current_instance() -> dict:
    """Retorna a instância atual (ou vazio se não setado)."""
    return current_instance.get()
