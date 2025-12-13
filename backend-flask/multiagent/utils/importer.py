import importlib

def import_from_path(caminho_completo):
    """
    Importa uma classe a partir do caminho completo.
    Exemplo: 'multiagent.agents.extrator.ExtratorAgent'
    """
    modulo_caminho, classe_nome = caminho_completo.rsplit('.', 1)
    modulo = importlib.import_module(modulo_caminho)
    return getattr(modulo, classe_nome)
