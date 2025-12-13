#!/usr/bin/env python3
"""
Script para corrigir todas as rotas de templates que estão causando erro 404
"""

import re

def corrigir_rotas_templates():
    """Corrige as rotas dos templates no app.py"""
    
    # Ler arquivo atual
    with open('app.py', 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Encontrar e corrigir a estrutura dos templates_juridicos
    pattern = r"(templates_juridicos = \[[\s\S]*?\])"
    
    def substituir_template(match):
        # Estrutura corrigida com campos necessários para as rotas
        nova_estrutura = """templates_juridicos = [
            # CRIMINAL (12 templates)
            {'id': 1, 'nome': 'Denúncia Criminal', 'categoria': 'Criminal', 'area': 'criminal', 'nivel': '5/5', 'icone': 'fas fa-exclamation-triangle', 'descricao': 'Template para denúncia criminal'},
            {'id': 2, 'nome': 'Defesa Prévia', 'categoria': 'Criminal', 'area': 'criminal', 'nivel': '5/5', 'icone': 'fas fa-shield-alt', 'descricao': 'Template para defesa prévia'},
            {'id': 3, 'nome': 'Alegações Finais', 'categoria': 'Criminal', 'area': 'criminal', 'nivel': '5/5', 'icone': 'fas fa-gavel', 'descricao': 'Template para alegações finais'},
            {'id': 4, 'nome': 'Habeas Corpus', 'categoria': 'Criminal', 'area': 'criminal', 'nivel': '5/5', 'icone': 'fas fa-key', 'descricao': 'Template para habeas corpus'},
            {'id': 5, 'nome': 'Recurso de Apelação', 'categoria': 'Criminal', 'area': 'criminal', 'nivel': '5/5', 'icone': 'fas fa-arrow-up', 'descricao': 'Template para recurso de apelação'},
            {'id': 6, 'nome': 'Petição de Liberdade Provisória', 'categoria': 'Criminal', 'area': 'criminal', 'nivel': '4/5', 'icone': 'fas fa-unlock', 'descricao': 'Template para liberdade provisória'},
            {'id': 7, 'nome': 'Memoriais do Júri', 'categoria': 'Criminal', 'area': 'criminal', 'nivel': '5/5', 'icone': 'fas fa-users', 'descricao': 'Template para memoriais do júri'},
            {'id': 8, 'nome': 'Embargos de Declaração', 'categoria': 'Criminal', 'area': 'criminal', 'nivel': '4/5', 'icone': 'fas fa-question', 'descricao': 'Template para embargos de declaração'},
            {'id': 9, 'nome': 'Recurso Especial', 'categoria': 'Criminal', 'area': 'criminal', 'nivel': '5/5', 'icone': 'fas fa-star', 'descricao': 'Template para recurso especial'},
            {'id': 10, 'nome': 'Recurso Extraordinário', 'categoria': 'Criminal', 'area': 'criminal', 'nivel': '5/5', 'icone': 'fas fa-trophy', 'descricao': 'Template para recurso extraordinário'},
            {'id': 11, 'nome': 'Mandado de Segurança', 'categoria': 'Criminal', 'area': 'criminal', 'nivel': '4/5', 'icone': 'fas fa-shield', 'descricao': 'Template para mandado de segurança'},
            {'id': 12, 'nome': 'Queixa-Crime', 'categoria': 'Criminal', 'area': 'criminal', 'nivel': '4/5', 'icone': 'fas fa-file-signature', 'descricao': 'Template para queixa-crime'},
            
            # EMPRESARIAL (8 templates)
            {'id': 13, 'nome': 'Contrato Social', 'categoria': 'Empresarial', 'area': 'empresarial', 'nivel': '4/5', 'icone': 'fas fa-building', 'descricao': 'Template para contrato social'},
            {'id': 14, 'nome': 'Ata de Assembleia', 'categoria': 'Empresarial', 'area': 'empresarial', 'nivel': '4/5', 'icone': 'fas fa-users', 'descricao': 'Template para ata de assembleia'},
            {'id': 15, 'nome': 'Distrato Social', 'categoria': 'Empresarial', 'area': 'empresarial', 'nivel': '4/5', 'icone': 'fas fa-times-circle', 'descricao': 'Template para distrato social'},
            {'id': 16, 'nome': 'Acordo de Acionistas', 'categoria': 'Empresarial', 'area': 'empresarial', 'nivel': '5/5', 'icone': 'fas fa-handshake', 'descricao': 'Template para acordo de acionistas'},
            {'id': 17, 'nome': 'Due Diligence', 'categoria': 'Empresarial', 'area': 'empresarial', 'nivel': '5/5', 'icone': 'fas fa-search', 'descricao': 'Template para due diligence'},
            {'id': 18, 'nome': 'Plano de Recuperação', 'categoria': 'Empresarial', 'area': 'empresarial', 'nivel': '5/5', 'icone': 'fas fa-chart-line', 'descricao': 'Template para plano de recuperação'},
            {'id': 19, 'nome': 'Contrato de Joint Venture', 'categoria': 'Empresarial', 'area': 'empresarial', 'nivel': '5/5', 'icone': 'fas fa-network-wired', 'descricao': 'Template para joint venture'},
            {'id': 20, 'nome': 'Termo de Confidencialidade', 'categoria': 'Empresarial', 'area': 'empresarial', 'nivel': '3/5', 'icone': 'fas fa-lock', 'descricao': 'Template para termo de confidencialidade'},
            
            # BANCÁRIO (6 templates)
            {'id': 21, 'nome': 'Revisão de Contrato Bancário', 'categoria': 'Bancário', 'area': 'bancario', 'nivel': '4/5', 'icone': 'fas fa-university', 'descricao': 'Template para revisão de contrato bancário'},
            {'id': 22, 'nome': 'Defesa em Execução', 'categoria': 'Bancário', 'area': 'bancario', 'nivel': '4/5', 'icone': 'fas fa-shield-alt', 'descricao': 'Template para defesa em execução'},
            {'id': 23, 'nome': 'Embargos à Execução', 'categoria': 'Bancário', 'area': 'bancario', 'nivel': '4/5', 'icone': 'fas fa-ban', 'descricao': 'Template para embargos à execução'},
            {'id': 24, 'nome': 'Impugnação ao Cumprimento', 'categoria': 'Bancário', 'area': 'bancario', 'nivel': '4/5', 'icone': 'fas fa-times', 'descricao': 'Template para impugnação ao cumprimento'},
            {'id': 25, 'nome': 'Consignação em Pagamento', 'categoria': 'Bancário', 'area': 'bancario', 'nivel': '4/5', 'icone': 'fas fa-money-check', 'descricao': 'Template para consignação em pagamento'},
            {'id': 26, 'nome': 'Ação de Cobrança', 'categoria': 'Bancário', 'area': 'bancario', 'nivel': '4/5', 'icone': 'fas fa-hand-holding-usd', 'descricao': 'Template para ação de cobrança'},
            
            # RECUPERAÇÃO (6 templates)
            {'id': 27, 'nome': 'Execução Civil', 'categoria': 'Recuperação', 'area': 'recuperacao', 'nivel': '4/5', 'icone': 'fas fa-gavel', 'descricao': 'Template para execução civil'},
            {'id': 28, 'nome': 'Busca e Apreensão', 'categoria': 'Recuperação', 'area': 'recuperacao', 'nivel': '4/5', 'icone': 'fas fa-search-plus', 'descricao': 'Template para busca e apreensão'},
            {'id': 29, 'nome': 'Penhora de Bens', 'categoria': 'Recuperação', 'area': 'recuperacao', 'nivel': '4/5', 'icone': 'fas fa-hammer', 'descricao': 'Template para penhora de bens'},
            {'id': 30, 'nome': 'Leilão Judicial', 'categoria': 'Recuperação', 'area': 'recuperacao', 'nivel': '4/5', 'icone': 'fas fa-auction', 'descricao': 'Template para leilão judicial'},
            {'id': 31, 'nome': 'Acordo Extrajudicial', 'categoria': 'Recuperação', 'area': 'recuperacao', 'nivel': '3/5', 'icone': 'fas fa-handshake', 'descricao': 'Template para acordo extrajudicial'},
            {'id': 32, 'nome': 'Negativação', 'categoria': 'Recuperação', 'area': 'recuperacao', 'nivel': '3/5', 'icone': 'fas fa-exclamation-triangle', 'descricao': 'Template para negativação'},
            
            # TRABALHISTA (5 templates)
            {'id': 33, 'nome': 'Reclamação Trabalhista', 'categoria': 'Trabalhista', 'area': 'trabalhista', 'nivel': '4/5', 'icone': 'fas fa-hard-hat', 'descricao': 'Template para reclamação trabalhista'},
            {'id': 34, 'nome': 'Defesa Trabalhista', 'categoria': 'Trabalhista', 'area': 'trabalhista', 'nivel': '4/5', 'icone': 'fas fa-shield-alt', 'descricao': 'Template para defesa trabalhista'},
            {'id': 35, 'nome': 'Acordo Trabalhista', 'categoria': 'Trabalhista', 'area': 'trabalhista', 'nivel': '3/5', 'icone': 'fas fa-handshake', 'descricao': 'Template para acordo trabalhista'},
            {'id': 36, 'nome': 'Recurso Ordinário', 'categoria': 'Trabalhista', 'area': 'trabalhista', 'nivel': '4/5', 'icone': 'fas fa-arrow-up', 'descricao': 'Template para recurso ordinário'},
            {'id': 37, 'nome': 'Execução Trabalhista', 'categoria': 'Trabalhista', 'area': 'trabalhista', 'nivel': '4/5', 'icone': 'fas fa-gavel', 'descricao': 'Template para execução trabalhista'},
            
            # CONSUMIDOR (5 templates)
            {'id': 38, 'nome': 'Ação de Indenização', 'categoria': 'Consumidor', 'area': 'consumidor', 'nivel': '4/5', 'icone': 'fas fa-shopping-cart', 'descricao': 'Template para ação de indenização'},
            {'id': 39, 'nome': 'Reclamação no PROCON', 'categoria': 'Consumidor', 'area': 'consumidor', 'nivel': '3/5', 'icone': 'fas fa-exclamation-circle', 'descricao': 'Template para reclamação no PROCON'},
            {'id': 40, 'nome': 'Ação Coletiva', 'categoria': 'Consumidor', 'area': 'consumidor', 'nivel': '5/5', 'icone': 'fas fa-users', 'descricao': 'Template para ação coletiva'},
            {'id': 41, 'nome': 'Defesa do Consumidor', 'categoria': 'Consumidor', 'area': 'consumidor', 'nivel': '4/5', 'icone': 'fas fa-shield-alt', 'descricao': 'Template para defesa do consumidor'},
            {'id': 42, 'nome': 'Tutela de Urgência', 'categoria': 'Consumidor', 'area': 'consumidor', 'nivel': '4/5', 'icone': 'fas fa-clock', 'descricao': 'Template para tutela de urgência'}
        ]"""
        return nova_estrutura
    
    # Substituir a estrutura de templates
    conteudo_corrigido = re.sub(pattern, substituir_template, conteudo, flags=re.MULTILINE)
    
    # Escrever arquivo corrigido
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(conteudo_corrigido)
    
    print("✅ Estrutura de templates corrigida")
    return True

if __name__ == "__main__":
    corrigir_rotas_templates()