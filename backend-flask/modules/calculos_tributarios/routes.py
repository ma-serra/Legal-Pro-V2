
from flask import Blueprint, jsonify, request, send_file
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

    # === NOVAS ROTAS (Persistência) ===

    @calc_bp.route('/simulacoes', methods=['POST'])
    def salvar_simulacao():
        data = request.json
        try:
            nova_sim = CalculadoraTributariaService.salvar_simulacao(
                cliente_nome=data.get('cliente_nome'),
                tipo=data.get('tipo_simulacao'),
                parametros=data.get('parametros_input'),
                resultado=data.get('resultado_output')
            )
            return jsonify({'success': True, 'id': str(nova_sim.id)}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @calc_bp.route('/simulacoes', methods=['GET'])
    def listar_simulacoes():
        cliente = request.args.get('cliente')
        simulacoes = CalculadoraTributariaService.listar_simulacoes(cliente)
        return jsonify([s.to_dict() for s in simulacoes])

    @calc_bp.route('/simulacoes/<id>/pdf', methods=['GET'])
    def baixar_pdf(id):
        try:
            pdf_buffer = CalculadoraTributariaService.gerar_pdf_simulacao(id)
            return send_file(
                pdf_buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'simulacao_tributaria_{id}.pdf'
            )
        except Exception as e:
            return jsonify({'error': str(e)}), 404

    app.register_blueprint(calc_bp)
