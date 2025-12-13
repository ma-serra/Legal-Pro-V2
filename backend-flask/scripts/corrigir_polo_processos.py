#!/usr/bin/env python3
"""
Script para corrigir o campo 'polo' dos processos jurídicos baseado na regra de negócio:

REGRA:
- Polo PASSIVO: Cliente é pessoa jurídica AND Autor é pessoa física
- EXCEÇÃO Direito Tributário: Autor é instituição pública = Polo PASSIVO  
- Polo ATIVO: Todos os outros casos

"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

def conectar_banco():
    """Conecta ao banco PostgreSQL"""
    try:
        conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar banco: {e}")
        return None

def e_pessoa_juridica(nome):
    """Identifica se é pessoa jurídica baseado no nome - LÓGICA SIMPLES"""
    if not nome:
        return False
    
    nome_upper = nome.upper()
    
    # Lista de sufixos que CLARAMENTE indicam PJ - SOMENTE SUFIXOS EXATOS
    sufixos_pj_claros = [
        'S.A.', 'S/A', 'LTDA', 'EIRELI', 'ME', 'EPP', 
        'CORP', 'CORPORATION', 'HOLDINGS', 'HOLDING',
        'INDÚSTRIA', 'INDUSTRIA', 'COMÉRCIO', 'COMERCIO',
        'SERVIÇOS', 'SERVICOS', 'COOPERATIVA', 'BANCO',
        'COMPANHIA', 'COMERCIAL'
    ]
    
    # Palavras que indicam empresas (mais cuidadosas)
    palavras_empresa = [
        'STEELWORKS', 'TECNOIL', 'FOODINDUSTRIES', 'BEVERAGECORP',
        'ELECTRICSUL', 'CHEMICALPLUS', 'PAPERCORP', 'PACKAGEPRO',
        'CREDITOCORP', 'SHOPCENTER', 'COMMERCEHUB', 'MEGASTORE',
        'POWERENERGY', 'MINERALCORP', 'BEAUTYCORP', 'ENERGIANORTE',
        'AEROTECH', 'SIDERÚRGICA'
    ]
    
    # Verificar sufixos EXATOS de PJ (no final ou separados por espaço)
    for sufixo in sufixos_pj_claros:
        if (nome_upper.endswith(f' {sufixo}') or 
            nome_upper.endswith(sufixo) or
            f' {sufixo} ' in nome_upper):
            return True
    
    # Se tem palavras típicas de empresa (nomes completos), É PESSOA JURÍDICA
    for palavra in palavras_empresa:
        if palavra in nome_upper:
            return True
    
    # Se não tem sufixo de PJ nem palavra de empresa, É PESSOA FÍSICA
    return False

def e_instituicao_publica(nome):
    """Identifica se é instituição pública"""
    if not nome:
        return False
        
    nome_upper = nome.upper()
    
    # Termos que indicam instituição pública
    termos_publicos = [
        'FAZENDA NACIONAL', 'FAZENDA PÚBLICA', 'UNIÃO', 'ESTADO',
        'MUNICÍPIO', 'PREFEITURA', 'PGFN', 'PROCURADORIA',
        'RECEITA FEDERAL', 'SEFAZ', 'INSS', 'GOVERNO',
        'MINISTÉRIO', 'MINISTERIO', 'FEDERAL', 'MUNICIPAL',
        'ESTADUAL', 'PÚBLICA', 'PUBLICA'
    ]
    
    for termo in termos_publicos:
        if termo in nome_upper:
            return True
    
    return False

def e_direito_tributario(area):
    """Identifica se é área de Direito Tributário"""
    if not area:
        return False
    
    return 'Tributário' in area or 'Fiscal' in area

def calcular_polo(cliente, autor, area_juridica):
    """
    Calcula o polo baseado na regra de negócio:
    
    PASSIVO: 
    - Cliente é PJ AND Autor é PF, OU
    - Direito Tributário AND Autor é instituição pública
    
    ATIVO: Todos os outros casos
    """
    
    cliente_e_pj = e_pessoa_juridica(cliente)
    autor_e_pf = not e_pessoa_juridica(autor) and not e_instituicao_publica(autor)
    autor_e_publico = e_instituicao_publica(autor)
    e_tributario = e_direito_tributario(area_juridica)
    
    # Regra principal: Cliente PJ + Autor PF = PASSIVO
    if cliente_e_pj and autor_e_pf:
        return 'Passivo', f"Cliente PJ ({cliente}) + Autor PF ({autor})"
    
    # Exceção Tributário: Autor público = PASSIVO
    if e_tributario and autor_e_publico:
        return 'Passivo', f"Direito Tributário + Autor Público ({autor})"
    
    # Todos os outros casos = ATIVO
    return 'Ativo', f"Caso padrão - Cliente: {cliente} / Autor: {autor}"

def executar_dry_run():
    """Executa análise sem alterar dados"""
    print("🔍 EXECUTANDO DRY RUN - Analisando 163 processos...")
    print("=" * 60)
    
    conn = conectar_banco()
    if not conn:
        return
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Buscar todos os processos
        cursor.execute("""
            SELECT id, cliente, autor, area_juridica, polo 
            FROM processo_juridico 
            ORDER BY id
        """)
        
        processos = cursor.fetchall()
        
        alteracoes = []
        estatisticas = {
            'total': len(processos),
            'para_ativo': 0,
            'para_passivo': 0,
            'sem_alteracao': 0,
            'tributario_publico': 0,
            'cliente_pj_autor_pf': 0
        }
        
        for processo in processos:
            polo_atual = processo['polo']
            polo_novo, motivo = calcular_polo(
                processo['cliente'], 
                processo['autor'], 
                processo['area_juridica']
            )
            
            if polo_atual != polo_novo:
                alteracoes.append({
                    'id': processo['id'],
                    'cliente': processo['cliente'],
                    'autor': processo['autor'],
                    'area': processo['area_juridica'],
                    'polo_atual': polo_atual,
                    'polo_novo': polo_novo,
                    'motivo': motivo
                })
                
                if polo_novo == 'Ativo':
                    estatisticas['para_ativo'] += 1
                else:
                    estatisticas['para_passivo'] += 1
                    
                if 'Tributário' in motivo and 'Público' in motivo:
                    estatisticas['tributario_publico'] += 1
                elif 'Cliente PJ' in motivo:
                    estatisticas['cliente_pj_autor_pf'] += 1
            else:
                estatisticas['sem_alteracao'] += 1
        
        # Relatório
        print(f"📊 ESTATÍSTICAS:")
        print(f"Total de processos: {estatisticas['total']}")
        print(f"Alterações para ATIVO: {estatisticas['para_ativo']}")
        print(f"Alterações para PASSIVO: {estatisticas['para_passivo']}")
        print(f"Sem alteração: {estatisticas['sem_alteracao']}")
        print(f"Tributário + Público: {estatisticas['tributario_publico']}")
        print(f"Cliente PJ + Autor PF: {estatisticas['cliente_pj_autor_pf']}")
        print("=" * 60)
        
        if alteracoes:
            print(f"🔄 ALTERAÇÕES NECESSÁRIAS ({len(alteracoes)} processos):")
            print("-" * 60)
            for alt in alteracoes[:10]:  # Mostrar apenas primeiras 10
                print(f"ID {alt['id']}: {alt['polo_atual']} → {alt['polo_novo']}")
                print(f"   Cliente: {alt['cliente']}")
                print(f"   Autor: {alt['autor']}")
                print(f"   Área: {alt['area']}")
                print(f"   Motivo: {alt['motivo']}")
                print("-" * 60)
            
            if len(alteracoes) > 10:
                print(f"... e mais {len(alteracoes) - 10} alterações")
        else:
            print("✅ Nenhuma alteração necessária!")
        
        return alteracoes
        
    except Exception as e:
        print(f"❌ Erro no dry run: {e}")
        return []
    finally:
        conn.close()

def aplicar_alteracoes():
    """Aplica as alterações no banco de dados"""
    print("⚠️  APLICANDO ALTERAÇÕES NO BANCO...")
    print("=" * 60)
    
    conn = conectar_banco()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Buscar todos os processos
        cursor.execute("""
            SELECT id, cliente, autor, area_juridica, polo 
            FROM processo_juridico 
            ORDER BY id
        """)
        
        processos = cursor.fetchall()
        
        alteracoes_aplicadas = 0
        
        for processo in processos:
            polo_atual = processo['polo']
            polo_novo, motivo = calcular_polo(
                processo['cliente'], 
                processo['autor'], 
                processo['area_juridica']
            )
            
            if polo_atual != polo_novo:
                # Aplicar alteração
                cursor.execute("""
                    UPDATE processo_juridico 
                    SET polo = %s 
                    WHERE id = %s
                """, (polo_novo, processo['id']))
                
                alteracoes_aplicadas += 1
                print(f"✅ ID {processo['id']}: {polo_atual} → {polo_novo}")
        
        # Confirmar transação
        conn.commit()
        
        print("=" * 60)
        print(f"🎉 CONCLUÍDO! {alteracoes_aplicadas} processos atualizados.")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao aplicar alterações: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("🏛️  CORREÇÃO DO POLO DOS PROCESSOS JURÍDICOS")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--aplicar":
        print("⚠️  MODO APLICAÇÃO - Alterações serão salvas no banco!")
        input("Pressione ENTER para continuar ou Ctrl+C para cancelar...")
        aplicar_alteracoes()
    else:
        print("🔍 MODO DRY RUN - Apenas análise, sem alterações")
        print("Para aplicar as alterações, execute: python corrigir_polo_processos.py --aplicar")
        print()
        executar_dry_run()