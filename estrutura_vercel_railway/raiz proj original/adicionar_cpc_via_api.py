"""
Adiciona artigos do CPC via API do sistema
Usa endpoints existentes para inserção na base vetorial
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def adicionar_artigos_cpc_via_api():
    """Adiciona artigos fundamentais do CPC via API"""
    
    artigos_cpc = [
        {
            "titulo": "Art. 1º - Normas Fundamentais",
            "conteudo": "O processo civil será ordenado, disciplinado e interpretado conforme os valores e as normas fundamentais estabelecidos na Constituição da República Federativa do Brasil, observando-se as disposições deste Código.",
            "area": "direito_civil",
            "tipo": "processo_civil"
        },
        {
            "titulo": "Art. 3º - Acesso à Justiça",
            "conteudo": "Não se excluirá da apreciação jurisdicional ameaça ou lesão a direito. É permitida a arbitragem, na forma da lei. O Estado promoverá, sempre que possível, a solução consensual dos conflitos. A conciliação, a mediação e outros métodos de solução consensual de conflitos deverão ser estimulados por juízes, advogados, defensores públicos e membros do Ministério Público.",
            "area": "direito_civil",
            "tipo": "processo_civil"
        },
        {
            "titulo": "Art. 5º - Boa-fé Processual",
            "conteudo": "Aquele que de qualquer forma participa do processo deve comportar-se de acordo com a boa-fé.",
            "area": "direito_civil",
            "tipo": "processo_civil"
        },
        {
            "titulo": "Art. 6º - Cooperação Processual",
            "conteudo": "Todos os sujeitos do processo devem cooperar entre si para que se obtenha, em tempo razoável, decisão de mérito justa e efetiva.",
            "area": "direito_civil",
            "tipo": "processo_civil"
        },
        {
            "titulo": "Art. 7º - Paridade de Tratamento",
            "conteudo": "É assegurada às partes paridade de tratamento em relação ao exercício de direitos e faculdades processuais, aos meios de defesa, aos ônus, aos deveres e à aplicação de sanções processuais, competindo ao juiz zelar pelo efetivo contraditório.",
            "area": "direito_civil",
            "tipo": "processo_civil"
        }
    ]
    
    print("Adicionando artigos do CPC via API...")
    
    for artigo in artigos_cpc:
        try:
            # Simular upload de documento
            response = requests.post(
                f"{BASE_URL}/api/chat_juridico",
                json={
                    "pergunta": f"Processar documento: {artigo['titulo']}",
                    "texto_documento": artigo['conteudo'],
                    "area_juridica": artigo['area'],
                    "tipo_documento": artigo['tipo']
                },
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✓ {artigo['titulo']} processado com sucesso")
            else:
                print(f"✗ Erro ao processar {artigo['titulo']}: {response.status_code}")
                
            time.sleep(2)  # Evitar sobrecarga
            
        except Exception as e:
            print(f"✗ Erro ao processar {artigo['titulo']}: {e}")

def testar_busca_cpc():
    """Testa busca de artigos do CPC"""
    print("\nTestando busca de artigos do CPC...")
    
    consultas = [
        "código de processo civil",
        "normas fundamentais processo",
        "boa-fé processual",
        "cooperação entre partes"
    ]
    
    for consulta in consultas:
        try:
            response = requests.post(
                f"{BASE_URL}/api/qdrant/buscar",
                json={
                    "area": "direito_civil",
                    "consulta": consulta,
                    "limite": 3
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                total = data.get('total_resultados', 0)
                print(f"✓ '{consulta}': {total} resultados encontrados")
                
                for resultado in data.get('resultados', []):
                    ref = resultado.get('referencia', '')
                    if 'Processo Civil' in ref or 'CPC' in ref:
                        print(f"  → {ref}: {resultado.get('conteudo', '')[:80]}...")
                        
            else:
                print(f"✗ Erro na busca '{consulta}': {response.status_code}")
                
        except Exception as e:
            print(f"✗ Erro ao buscar '{consulta}': {e}")

def main():
    # Adicionar artigos
    adicionar_artigos_cpc_via_api()
    
    # Aguardar processamento
    time.sleep(5)
    
    # Testar busca
    testar_busca_cpc()

if __name__ == "__main__":
    main()