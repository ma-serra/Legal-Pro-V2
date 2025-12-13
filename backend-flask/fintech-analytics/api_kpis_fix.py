"""
CORREÇÃO TEMPORÁRIA PARA API KPIS
"""

# Adicionando rota KPIs que estava faltando
def create_kpis_route(fintech_bp):
    @fintech_bp.route('/api/kpis')
    def api_kpis():
        """API para KPIs do sistema - versão simplificada e funcional"""
        import os
        import json
        
        try:
            # Verificar se arquivo processado existe
            csv_path = "fintech-analytics/data/processed/dataset_fintech_limpo.csv"
            
            if os.path.exists(csv_path):
                try:
                    import pandas as pd
                    df = pd.read_csv(csv_path)
                    
                    result = {
                        'success': True,
                        'total_records': int(len(df)),
                        'unique_states': int(df['estado'].nunique()) if 'estado' in df.columns else 0,
                        'by_year': dict(df.groupby('ano').size()) if 'ano' in df.columns else {},
                        'by_result': dict(df.groupby('resultado').size()) if 'resultado' in df.columns else {}
                    }
                    
                    # Converter para tipos serializáveis
                    for key in result:
                        if isinstance(result[key], dict):
                            result[key] = {str(k): int(v) for k, v in result[key].items()}
                    
                    from flask import jsonify
                    return jsonify(result)
                    
                except Exception as e:
                    from flask import jsonify
                    return jsonify({
                        'success': False,
                        'error': f'Erro ao processar dados: {str(e)}'
                    })
            else:
                from flask import jsonify
                return jsonify({
                    'success': False,
                    'error': 'Dados não carregados - Execute o ETL primeiro'
                })
            
        except Exception as e:
            from flask import jsonify
            return jsonify({
                'success': False,
                'error': f'Erro interno: {str(e)}'
            })