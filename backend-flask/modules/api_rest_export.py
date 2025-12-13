"""
API REST para Export Manager - Exportação de documentos para PDF/DOCX
"""
from flask import Blueprint, jsonify, request, send_file
from main import db
from models import Documento, VersaoDocumento, AnaliseDocumento
import logging
from datetime import datetime
import io

logger = logging.getLogger(__name__)

export_api = Blueprint('export_api', __name__, url_prefix='/api/export')

@export_api.route('/pdf', methods=['POST'])
def exportar_pdf():
    """
    Exporta documento para PDF
    Body: { "documento_id": 1 } ou { "texto": "...", "titulo": "..." }
    """
    try:
        data = request.get_json()
        
        # Opção 1: Documento existente
        if 'documento_id' in data:
            doc_id = data['documento_id']
            documento = Documento.query.get_or_404(doc_id)
            versao = documento.versao_atual()
           
            if not versao:
                return jsonify({'error': 'Documento sem versões'}), 404
            
            titulo = documento.titulo
            conteudo = versao.conteudo
        
        # Opção 2: Texto direto
        elif 'texto' in data:
            titulo = data.get('titulo', 'Documento')
            conteudo = data['texto']
        else:
            return jsonify({'error': 'Forneça documento_id ou texto'}), 400
        
        # Mock: gerar "PDF"
        # TODO: Integrar com ReportLab ou biblioteca real
        pdf_content = f"""
%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >> endobj
trailer << /Root 1 0 R >>
%%EOF

[MOCKADO - Em produção seria um PDF real]

Título: {titulo}
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Conteúdo:
{conteudo[:500]}...

Gerado por Legal Pro SaaS
"""
        
        # Criar arquivo em memória
        buffer = io.BytesIO()
        buffer.write(pdf_content.encode('utf-8'))
        buffer.seek(0)
        
        return jsonify({
            'message': 'PDF gerado com sucesso (mockado)',
            'titulo': titulo,
            'formato': 'application/pdf',
            'tamanho_bytes': len(pdf_content),
            'download_url': f'/api/export/download/pdf/{titulo}.pdf',
            'nota': 'Em produção, retornaria um PDF real com formatação completa'
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao exportar PDF: {e}")
        return jsonify({'error': 'Erro ao exportar PDF'}), 500

@export_api.route('/docx', methods=['POST'])
def exportar_docx():
    """
    Exporta documento para DOCX
    Body: { "documento_id": 1 } ou { "texto": "...", "titulo": "..." }
    """
    try:
        data = request.get_json()
        
        # Opção 1: Documento existente
        if 'documento_id' in data:
            doc_id = data['documento_id']
            documento = Documento.query.get_or_404(doc_id)
            versao = documento.versao_atual()
            
            if not versao:
                return jsonify({'error': 'Documento sem versões'}), 404
            
            titulo = documento.titulo
            conteudo = versao.conteudo
        
        # Opção 2: Texto direto
        elif 'texto' in data:
            titulo = data.get('titulo', 'Documento')
            conteudo = data['texto']
        else:
            return jsonify({'error': 'Forneça documento_id ou texto'}), 400
        
        # Mock: gerar "DOCX"
        # TODO: Integrar com python-docx
        docx_info = {
            'message': 'DOCX gerado com sucesso (mockado)',
            'titulo': titulo,
            'formato': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'tamanho_bytes': len(conteudo) * 2,  # Estimativa
            'download_url': f'/api/export/download/docx/{titulo}.docx',
            'nota': 'Em produção, retornaria um DOCX real com formatação completa',
            'elementos': {
                'paragrafos': conteudo.count('\n\n') + 1,
                'caracteres': len(conteudo),
                'palavras': len(conteudo.split())
            }
        }
        
        return jsonify(docx_info), 200
        
    except Exception as e:
        logger.error(f"Erro ao exportar DOCX: {e}")
        return jsonify({'error': 'Erro ao exportar DOCX'}), 500

@export_api.route('/analise/pdf', methods=['POST'])
def exportar_analise_pdf():
    """
    Exporta análise jurídica para PDF
    Body: { "analise_id": 1 }
    """
    try:
        data = request.get_json()
        analise_id = data.get('analise_id')
        
        if not analise_id:
            return jsonify({'error': 'analise_id é obrigatório'}), 400
        
        analise = AnaliseDocumento.query.get_or_404(analise_id)
        
        # Mock: gerar relatório PDF da análise
        pdf_info = {
            'message': 'Relatório de análise gerado (mockado)',
            'analise_id': analise_id,
            'agente': analise.agente.nome if analise.agente else 'Sistema',
            'formato': 'application/pdf',
            'download_url': f'/api/export/download/analise-{analise_id}.pdf',
            'includes': [
                'Cabeçalho com dados da análise',
                'Conteúdo completo da análise',
                'Metadados e estatísticas',
                'Rodapé com assinatura digital'
            ]
        }
        
        return jsonify(pdf_info), 200
        
    except Exception as e:
        logger.error(f"Erro ao exportar análise PDF: {e}")
        return jsonify({'error': 'Erro ao exportar análise'}), 500

@export_api.route('/formatos', methods=['GET'])
def listar_formatos():
    """
    Lista formatos de exportação disponíveis
    """
    formatos = [
        {
            'formato': 'PDF',
            'mime_type': 'application/pdf',
            'extensao': '.pdf',
            'descricao': 'Portable Document Format - ideal para compartilhamento',
            'suporte': 'completo'
        },
        {
            'formato': 'DOCX',
            'mime_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'extensao': '.docx',
            'descricao': 'Microsoft Word - editável',
            'suporte': 'completo'
        },
        {
            'formato': 'TXT',
            'mime_type': 'text/plain',
            'extensao': '.txt',
            'descricao': 'Texto puro - sem formatação',
            'suporte': 'basico'
        }
    ]
    
    return jsonify({'formatos': formatos}), 200

def register_export_api(app):
    """Registra o blueprint de export no app"""
    app.register_blueprint(export_api)
    print("✅ API REST de Export Manager registrada")
    logger.info("✅ API REST de Export Manager registrada com sucesso")
