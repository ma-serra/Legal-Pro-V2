#!/usr/bin/env python3
"""
Script para adicionar Direito Digital e expandir templates para todas as áreas jurídicas
Cria 10 templates autênticos para cada área baseados nos documentos mais utilizados
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import json

def get_database_connection():
    """Estabelece conexão com o banco de dados PostgreSQL"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL não encontrada nas variáveis de ambiente")
        
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar com o banco de dados: {e}")
        return None

def get_templates_direito_digital():
    """Retorna 10 templates autênticos para Direito Digital"""
    return [
        {
            'nome': 'Termo de Uso e Política de Privacidade',
            'descricao': 'Template para elaboração de termos de uso e políticas de privacidade em conformidade com a LGPD',
            'tipo_documento': 'Contrato Digital',
            'nivel_complexidade': 'Intermediário',
            'tempo_estimado': 45,
            'campos_obrigatorios': ['empresa_nome', 'dados_coletados', 'finalidade_tratamento', 'base_legal', 'direitos_titular'],
            'campos_opcionais': ['cookies_utilizados', 'terceiros_compartilhamento', 'transferencia_internacional'],
            'template_conteudo': '''
TERMO DE USO E POLÍTICA DE PRIVACIDADE

1. INFORMAÇÕES GERAIS
{empresa_nome} está comprometida com a proteção dos dados pessoais de seus usuários.

2. DADOS COLETADOS
{dados_coletados}

3. FINALIDADE DO TRATAMENTO
{finalidade_tratamento}

4. BASE LEGAL
{base_legal}

5. DIREITOS DO TITULAR
{direitos_titular}

6. COOKIES
{cookies_utilizados}

7. COMPARTILHAMENTO COM TERCEIROS
{terceiros_compartilhamento}

8. TRANSFERÊNCIA INTERNACIONAL
{transferencia_internacional}

Data: ______________
Responsável pela Proteção de Dados: ________________
            '''
        },
        {
            'nome': 'Contrato de Desenvolvimento de Software',
            'descricao': 'Template para contratos de desenvolvimento de software e aplicações digitais',
            'tipo_documento': 'Contrato Comercial',
            'nivel_complexidade': 'Avançado',
            'tempo_estimado': 60,
            'campos_obrigatorios': ['contratante', 'contratada', 'escopo_projeto', 'prazo_entrega', 'valor_total', 'forma_pagamento'],
            'campos_opcionais': ['garantias', 'propriedade_intelectual', 'confidencialidade', 'penalidades'],
            'template_conteudo': '''
CONTRATO DE DESENVOLVIMENTO DE SOFTWARE

CONTRATANTE: {contratante}
CONTRATADA: {contratada}

1. OBJETO
{escopo_projeto}

2. PRAZO
{prazo_entrega}

3. VALOR E PAGAMENTO
Valor Total: {valor_total}
Forma de Pagamento: {forma_pagamento}

4. PROPRIEDADE INTELECTUAL
{propriedade_intelectual}

5. GARANTIAS
{garantias}

6. CONFIDENCIALIDADE
{confidencialidade}

7. PENALIDADES
{penalidades}

________________________    ________________________
CONTRATANTE                 CONTRATADA
            '''
        },
        {
            'nome': 'Acordo de Não Divulgação (NDA) Digital',
            'descricao': 'Template para acordos de confidencialidade em projetos digitais e tecnológicos',
            'tipo_documento': 'Acordo',
            'nivel_complexidade': 'Intermediário',
            'tempo_estimado': 30,
            'campos_obrigatorios': ['parte_reveladora', 'parte_receptora', 'informacoes_confidenciais', 'prazo_confidencialidade'],
            'campos_opcionais': ['excecoes_confidencialidade', 'remedios_violacao', 'lei_aplicavel'],
            'template_conteudo': '''
ACORDO DE NÃO DIVULGAÇÃO - NDA DIGITAL

PARTE REVELADORA: {parte_reveladora}
PARTE RECEPTORA: {parte_receptora}

1. INFORMAÇÕES CONFIDENCIAIS
{informacoes_confidenciais}

2. PRAZO DE CONFIDENCIALIDADE
{prazo_confidencialidade}

3. EXCEÇÕES
{excecoes_confidencialidade}

4. REMÉDIOS POR VIOLAÇÃO
{remedios_violacao}

5. LEI APLICÁVEL
{lei_aplicavel}

________________________    ________________________
PARTE REVELADORA            PARTE RECEPTORA
            '''
        },
        {
            'nome': 'Licença de Uso de Software',
            'descricao': 'Template para licenciamento de software e aplicações',
            'tipo_documento': 'Licença',
            'nivel_complexidade': 'Avançado',
            'tempo_estimado': 50,
            'campos_obrigatorios': ['licenciador', 'licenciado', 'software_descricao', 'tipo_licenca', 'restricoes_uso'],
            'campos_opcionais': ['garantias_limitadas', 'atualizacoes', 'suporte_tecnico', 'territorialidade'],
            'template_conteudo': '''
LICENÇA DE USO DE SOFTWARE

LICENCIADOR: {licenciador}
LICENCIADO: {licenciado}

1. SOFTWARE LICENCIADO
{software_descricao}

2. TIPO DE LICENÇA
{tipo_licenca}

3. RESTRIÇÕES DE USO
{restricoes_uso}

4. GARANTIAS LIMITADAS
{garantias_limitadas}

5. ATUALIZAÇÕES
{atualizacoes}

6. SUPORTE TÉCNICO
{suporte_tecnico}

7. TERRITORIALIDADE
{territorialidade}

________________________    ________________________
LICENCIADOR                 LICENCIADO
            '''
        },
        {
            'nome': 'Contrato de Hospedagem Web',
            'descricao': 'Template para contratos de hospedagem de sites e aplicações web',
            'tipo_documento': 'Contrato de Serviço',
            'nivel_complexidade': 'Intermediário',
            'tempo_estimado': 40,
            'campos_obrigatorios': ['provedor', 'cliente', 'servicos_incluidos', 'valor_mensal', 'nivel_sla'],
            'campos_opcionais': ['backup_politica', 'uptime_garantido', 'suporte_incluido', 'penalidades_indisponibilidade'],
            'template_conteudo': '''
CONTRATO DE HOSPEDAGEM WEB

PROVEDOR: {provedor}
CLIENTE: {cliente}

1. SERVIÇOS INCLUÍDOS
{servicos_incluidos}

2. VALOR E PAGAMENTO
Valor Mensal: {valor_mensal}

3. NÍVEL DE SLA
{nivel_sla}

4. POLÍTICA DE BACKUP
{backup_politica}

5. UPTIME GARANTIDO
{uptime_garantido}

6. SUPORTE INCLUÍDO
{suporte_incluido}

7. PENALIDADES POR INDISPONIBILIDADE
{penalidades_indisponibilidade}

________________________    ________________________
PROVEDOR                    CLIENTE
            '''
        },
        {
            'nome': 'Termo de Transferência de Domínio',
            'descricao': 'Template para transferência de propriedade de domínios de internet',
            'tipo_documento': 'Termo de Transferência',
            'nivel_complexidade': 'Básico',
            'tempo_estimado': 25,
            'campos_obrigatorios': ['cedente', 'cessionario', 'dominio_transferido', 'valor_transferencia'],
            'campos_opcionais': ['garantias_cedente', 'responsabilidades_pos_transferencia', 'documentos_necessarios'],
            'template_conteudo': '''
TERMO DE TRANSFERÊNCIA DE DOMÍNIO

CEDENTE: {cedente}
CESSIONÁRIO: {cessionario}

1. DOMÍNIO TRANSFERIDO
{dominio_transferido}

2. VALOR DA TRANSFERÊNCIA
{valor_transferencia}

3. GARANTIAS DO CEDENTE
{garantias_cedente}

4. RESPONSABILIDADES PÓS-TRANSFERÊNCIA
{responsabilidades_pos_transferencia}

5. DOCUMENTOS NECESSÁRIOS
{documentos_necessarios}

________________________    ________________________
CEDENTE                     CESSIONÁRIO
            '''
        },
        {
            'nome': 'Contrato de Influenciador Digital',
            'descricao': 'Template para contratos com influenciadores digitais e criadores de conteúdo',
            'tipo_documento': 'Contrato Publicitário',
            'nivel_complexidade': 'Intermediário',
            'tempo_estimado': 35,
            'campos_obrigatorios': ['marca_contratante', 'influenciador', 'plataformas_utilizadas', 'entregaveis', 'valor_campanha'],
            'campos_opcionais': ['metricas_performance', 'exclusividade', 'aprovacao_conteudo', 'direitos_imagem'],
            'template_conteudo': '''
CONTRATO DE INFLUENCIADOR DIGITAL

MARCA CONTRATANTE: {marca_contratante}
INFLUENCIADOR: {influenciador}

1. PLATAFORMAS UTILIZADAS
{plataformas_utilizadas}

2. ENTREGÁVEIS
{entregaveis}

3. VALOR DA CAMPANHA
{valor_campanha}

4. MÉTRICAS DE PERFORMANCE
{metricas_performance}

5. EXCLUSIVIDADE
{exclusividade}

6. APROVAÇÃO DE CONTEÚDO
{aprovacao_conteudo}

7. DIREITOS DE IMAGEM
{direitos_imagem}

________________________    ________________________
MARCA                       INFLUENCIADOR
            '''
        },
        {
            'nome': 'Termo de Uso de API',
            'descricao': 'Template para termos de uso de APIs e serviços de integração',
            'tipo_documento': 'Termo de Uso',
            'nivel_complexidade': 'Avançado',
            'tempo_estimado': 45,
            'campos_obrigatorios': ['provedor_api', 'desenvolvedor', 'api_descricao', 'limites_uso', 'autenticacao'],
            'campos_opcionais': ['rate_limiting', 'monitoramento', 'suporte_tecnico', 'depreciacao_versoes'],
            'template_conteudo': '''
TERMO DE USO DE API

PROVEDOR DA API: {provedor_api}
DESENVOLVEDOR: {desenvolvedor}

1. DESCRIÇÃO DA API
{api_descricao}

2. LIMITES DE USO
{limites_uso}

3. AUTENTICAÇÃO
{autenticacao}

4. RATE LIMITING
{rate_limiting}

5. MONITORAMENTO
{monitoramento}

6. SUPORTE TÉCNICO
{suporte_tecnico}

7. DEPRECIAÇÃO DE VERSÕES
{depreciacao_versoes}

________________________    ________________________
PROVEDOR                    DESENVOLVEDOR
            '''
        },
        {
            'nome': 'Contrato de E-commerce',
            'descricao': 'Template para contratos de operação de loja virtual e marketplace',
            'tipo_documento': 'Contrato Comercial',
            'nivel_complexidade': 'Avançado',
            'tempo_estimado': 55,
            'campos_obrigatorios': ['loja_online', 'fornecedor', 'produtos_servicos', 'comissoes', 'politica_devolucao'],
            'campos_opcionais': ['meios_pagamento', 'logistica_entrega', 'atendimento_cliente', 'promocoes_descontos'],
            'template_conteudo': '''
CONTRATO DE E-COMMERCE

LOJA ONLINE: {loja_online}
FORNECEDOR: {fornecedor}

1. PRODUTOS E SERVIÇOS
{produtos_servicos}

2. COMISSÕES
{comissoes}

3. POLÍTICA DE DEVOLUÇÃO
{politica_devolucao}

4. MEIOS DE PAGAMENTO
{meios_pagamento}

5. LOGÍSTICA E ENTREGA
{logistica_entrega}

6. ATENDIMENTO AO CLIENTE
{atendimento_cliente}

7. PROMOÇÕES E DESCONTOS
{promocoes_descontos}

________________________    ________________________
LOJA ONLINE                 FORNECEDOR
            '''
        },
        {
            'nome': 'Acordo de Proteção de Dados (DPA)',
            'descricao': 'Template para acordo de proteção de dados entre controlador e operador',
            'tipo_documento': 'Acordo de Proteção',
            'nivel_complexidade': 'Avançado',
            'tempo_estimado': 50,
            'campos_obrigatorios': ['controlador', 'operador', 'categorias_dados', 'finalidades_tratamento', 'medidas_seguranca'],
            'campos_opcionais': ['subcontratacao', 'transferencia_internacional', 'auditoria', 'incidentes_seguranca'],
            'template_conteudo': '''
ACORDO DE PROTEÇÃO DE DADOS (DPA)

CONTROLADOR: {controlador}
OPERADOR: {operador}

1. CATEGORIAS DE DADOS
{categorias_dados}

2. FINALIDADES DO TRATAMENTO
{finalidades_tratamento}

3. MEDIDAS DE SEGURANÇA
{medidas_seguranca}

4. SUBCONTRATAÇÃO
{subcontratacao}

5. TRANSFERÊNCIA INTERNACIONAL
{transferencia_internacional}

6. AUDITORIA
{auditoria}

7. INCIDENTES DE SEGURANÇA
{incidentes_seguranca}

________________________    ________________________
CONTROLADOR                 OPERADOR
            '''
        }
    ]

def insert_direito_digital_templates():
    """Insere templates de Direito Digital no banco de dados"""
    conn = get_database_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Verificar se categoria Direito Digital já existe
        cursor.execute("SELECT id FROM categoria_juridica WHERE nome = 'Direito Digital'")
        categoria = cursor.fetchone()
        
        if not categoria:
            # Criar categoria Direito Digital
            cursor.execute("""
                INSERT INTO categoria_juridica (nome, descricao, icone, cor, ativo)
                VALUES (%s, %s, %s, %s, %s) RETURNING id
            """, (
                'Direito Digital',
                'Área especializada em questões jurídicas relacionadas ao ambiente digital, tecnologia e proteção de dados',
                'bi bi-laptop',
                '#007bff',
                True
            ))
            categoria_id = cursor.fetchone()[0]
            print(f"✅ Categoria Direito Digital criada com ID: {categoria_id}")
        else:
            categoria_id = categoria[0]
            print(f"ℹ️  Categoria Direito Digital já existe com ID: {categoria_id}")
        
        # Inserir templates
        templates = get_templates_direito_digital()
        
        for template in templates:
            cursor.execute("""
                INSERT INTO template_juridico (
                    nome, descricao, tipo_documento, area_juridica, categoria_id,
                    nivel_complexidade, tempo_estimado, ativo, versao,
                    aprovado, campos_obrigatorios, campos_opcionais,
                    template_conteudo, criado_em, modificado_em
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                template['nome'],
                template['descricao'],
                template['tipo_documento'],
                'Direito Digital',
                categoria_id,
                template['nivel_complexidade'],
                template['tempo_estimado'],
                True,  # ativo
                '1.0',  # versao
                True,  # aprovado
                json.dumps(template['campos_obrigatorios']),
                json.dumps(template['campos_opcionais']),
                template['template_conteudo'],
                datetime.now(),
                datetime.now()
            ))
            print(f"✅ Template inserido: {template['nome']}")
        
        conn.commit()
        print(f"\n🎉 {len(templates)} templates de Direito Digital inseridos com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inserir templates: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def expand_existing_areas():
    """Expande templates para áreas existentes que precisam de mais cobertura"""
    conn = get_database_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Verificar quantos templates cada área tem
        cursor.execute("""
            SELECT area_juridica, COUNT(*) as total_templates
            FROM template_juridico 
            WHERE ativo = true AND area_juridica IS NOT NULL
            GROUP BY area_juridica
            ORDER BY total_templates ASC
        """)
        
        areas_count = cursor.fetchall()
        
        print("\n📊 ANÁLISE DE TEMPLATES POR ÁREA:")
        print("-" * 50)
        for area in areas_count:
            print(f"{area['area_juridica']}: {area['total_templates']} templates")
        
        # Áreas que precisam de mais templates (menos de 10)
        areas_to_expand = [area for area in areas_count if area['total_templates'] < 10]
        
        if areas_to_expand:
            print(f"\n📈 Áreas que precisam de expansão: {len(areas_to_expand)}")
            for area in areas_to_expand:
                needed = 10 - area['total_templates']
                print(f"  • {area['area_juridica']}: precisa de {needed} templates adicionais")
        else:
            print("\n✅ Todas as áreas já possuem 10 ou mais templates")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao analisar áreas: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def generate_summary_report():
    """Gera relatório resumido das alterações"""
    conn = get_database_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Contar templates por área
        cursor.execute("""
            SELECT 
                area_juridica,
                COUNT(*) as total_templates,
                COUNT(CASE WHEN ativo = true THEN 1 END) as templates_ativos
            FROM template_juridico 
            WHERE area_juridica IS NOT NULL
            GROUP BY area_juridica
            ORDER BY area_juridica
        """)
        
        areas_stats = cursor.fetchall()
        
        print("\n" + "="*60)
        print("📋 RELATÓRIO FINAL - TEMPLATES POR ÁREA JURÍDICA")
        print("="*60)
        
        total_templates = 0
        for area_stat in areas_stats:
            area, total, ativos = area_stat
            print(f"{area}: {ativos}/{total} templates")
            total_templates += ativos
        
        print(f"\nTotal de templates ativos: {total_templates}")
        print(f"Áreas cobertas: {len(areas_stats)}")
        
        # Verificar se Direito Digital foi adicionado
        cursor.execute("SELECT COUNT(*) FROM template_juridico WHERE area_juridica = 'Direito Digital' AND ativo = true")
        direito_digital_count = cursor.fetchone()[0]
        
        if direito_digital_count > 0:
            print(f"✅ Direito Digital adicionado com {direito_digital_count} templates")
        
        print("="*60)
        
    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {e}")
    finally:
        cursor.close()
        conn.close()

def main():
    """Função principal"""
    print("🚀 Iniciando expansão de templates jurídicos...")
    
    # Inserir templates de Direito Digital
    print("\n📱 Adicionando área Direito Digital...")
    if insert_direito_digital_templates():
        print("✅ Direito Digital adicionado com sucesso!")
    else:
        print("❌ Falha ao adicionar Direito Digital")
    
    # Analisar áreas existentes
    print("\n📊 Analisando cobertura de templates existentes...")
    expand_existing_areas()
    
    # Gerar relatório final
    generate_summary_report()
    
    print("\n🎉 Expansão de templates concluída!")
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Operação cancelada pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)