#!/usr/bin/env python3
"""
Script para verificar e corrigir agentes que devem estar na área Direito Agrário
e analisar a distribuição dos 135 agentes pelas áreas jurídicas
"""

import os
import sys
sys.path.append('.')

from models import AgenteJuridico, db
from main import app

def verificar_e_corrigir_agentes():
    """Verifica e corrige os agentes que devem estar na área Direito Agrário"""
    
    with app.app_context():
        print("=== VERIFICANDO AGENTES RURAIS/AGRÁRIOS ===")
        
        # Buscar os agentes mencionados pelo usuário
        agentes_para_corrigir = []
        
        # Buscar por palavras-chave relacionadas ao direito agrário
        keywords = [
            'Contratos Rurais',
            'Crédito Rural', 
            'Regularização Fundiária',
            'Agrário',
            'Rural',
            'Fundiária'
        ]
        
        for keyword in keywords:
            agentes = AgenteJuridico.query.filter(
                AgenteJuridico.nome.like(f'%{keyword}%')
            ).all()
            
            for agente in agentes:
                if agente not in agentes_para_corrigir:
                    agentes_para_corrigir.append(agente)
        
        print(f"Encontrados {len(agentes_para_corrigir)} agentes relacionados ao Direito Agrário:")
        
        for agente in agentes_para_corrigir:
            print(f"ID: {agente.id}, Nome: {agente.nome}, Área Atual: {agente.area}")
            
            # Corrigir área se não estiver em "agrario"
            if agente.area != 'agrario':
                print(f"  → Corrigindo área de '{agente.area}' para 'agrario'")
                agente.area = 'agrario'
        
        # Salvar alterações
        try:
            db.session.commit()
            print(f"\n✅ {len(agentes_para_corrigir)} agentes corrigidos com sucesso!")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Erro ao salvar: {e}")
        
        print("\n=== DISTRIBUIÇÃO ATUAL POR ÁREA ===")
        areas = db.session.query(
            AgenteJuridico.area, 
            db.func.count(AgenteJuridico.id)
        ).group_by(AgenteJuridico.area).order_by(AgenteJuridico.area).all()
        
        total = 0
        areas_existentes = []
        
        for area, count in areas:
            print(f"{area}: {count} agentes")
            total += count
            areas_existentes.append(area)
        
        print(f"\nTOTAL: {total} agentes")
        
        # Verificar se temos todas as 13 áreas
        areas_esperadas = [
            'criminal',
            'agrario', 
            'bancario',
            'empresarial',
            'recuperacao',
            'trabalhista',
            'consumidor',
            'digital',
            'previdenciario',
            'tributario',
            'imobiliario',
            'securitario',
            'negociacao'
        ]
        
        print("\n=== VERIFICAÇÃO DAS 13 ÁREAS JURÍDICAS ===")
        areas_faltando = []
        for area in areas_esperadas:
            if area in areas_existentes:
                print(f"✅ {area}")
            else:
                print(f"❌ {area} - FALTANDO")
                areas_faltando.append(area)
        
        if areas_faltando:
            print(f"\n⚠️  Áreas faltando: {len(areas_faltando)}")
            print(f"Áreas sem agentes: {', '.join(areas_faltando)}")
        else:
            print(f"\n✅ Todas as 13 áreas jurídicas têm agentes!")
        
        return agentes_para_corrigir, areas, areas_faltando

if __name__ == "__main__":
    verificar_e_corrigir_agentes()