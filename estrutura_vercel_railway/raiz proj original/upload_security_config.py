
# Configurações de Segurança para Upload
UPLOAD_SECURITY = {
    'MAX_FILE_SIZE': 50 * 1024 * 1024,  # 50MB
    'ALLOWED_EXTENSIONS': {
        'audio': ['mp3', 'wav', 'ogg', 'm4a', 'flac'],
        'document': ['pdf', 'doc', 'docx', 'txt'],
        'image': ['jpg', 'jpeg', 'png', 'gif']
    },
    'QUARANTINE_DIR': 'uploads/quarantine',
    'SCAN_UPLOADS': True,
    'MAX_UPLOADS_PER_HOUR': 10
}

def validate_upload_file(file):
    '''Valida arquivo de upload com verificações de segurança'''
    if not file or not file.filename:
        return False, "Nenhum arquivo selecionado"
    
    # Verificar extensão
    ext = file.filename.rsplit('.', 1)[1].lower()
    allowed_exts = []
    for exts in UPLOAD_SECURITY['ALLOWED_EXTENSIONS'].values():
        allowed_exts.extend(exts)
    
    if ext not in allowed_exts:
        return False, f"Tipo de arquivo não permitido: {ext}"
    
    # Verificar tamanho
    file.seek(0, 2)  # Ir para o final
    size = file.tell()
    file.seek(0)     # Voltar ao início
    
    if size > UPLOAD_SECURITY['MAX_FILE_SIZE']:
        return False, "Arquivo muito grande"
    
    return True, "Arquivo válido"
