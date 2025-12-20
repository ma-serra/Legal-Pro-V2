
from flask import Blueprint, jsonify, request
from .service import CalculadoraTributariaService

def registrar_rotas_calculos(app):
    calc_bp = Blueprint('calculos_tributarios', __name__, url_prefix='/api/calculos-tributarios')

    @calc_bp.route('/simular/presumido', methods=['POST'])
    def simular_presumido():
        data = request.json
        receita = float(data.get('receita_trimestral', 0))
        atividade = data.get('atividade', 'servicos')
        folha = float(data.get('folha_pagamento', 0))
        
        resultado = CalculadoraTributariaService.calcular_lucro_presumido(receita, atividade, folha)
        return jsonify(resultado)

    @calc_bp.route('/simular/simples', methods=['POST'])
    def simular_simples():
        data = request.json
        receita_mes = float(data.get('receita_mensal', 0))
        rbt12 = float(data.get('receita_bruta_12_meses', 0))
        folha12 = float(data.get('folha_12_meses', 0))
        anexo = data.get('anexo', 'ANEXO_III')
        
        resultado = CalculadoraTributariaService.calcular_simples_nacional(receita_mes, rbt12, folha12, anexo)
        return jsonify(resultado)

    @calc_bp.route('/simular/tese-icms', methods=['POST'])
    def simular_tese_icms():
        data = request.json
        faturamento = float(data.get('faturamento_mensal', 0))
        icms = float(data.get('aliquota_icms', 18))
        meses = int(data.get('meses', 60))
        
        resultado = CalculadoraTributariaService.simular_tese_exclusao_icms(faturamento, icms, meses)
        return jsonify(resultado)

    @calc_bp.route('/referencias', methods=['GET'])
    def referencias():
        return jsonify({
            'atividades_presumido': list(CalculadoraTributariaService.PRESUNCAO_IRPJ.keys()),
            'anexos_simples': list(CalculadoraTributariaService.TABELAS_SIMPLES.keys())
        })

    app.register_blueprint(calc_bp)
