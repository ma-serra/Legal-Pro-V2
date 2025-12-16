"""
Script para remover null bytes de models.py
"""

# Ler arquivo binário
with open('backend-flask/models.py', 'rb') as f:
    content = f.read()

# Contar null bytes
null_count = content.count(b'\x00')
print(f'Null bytes encontrados: {null_count}')
print(f'Tamanho original: {len(content)} bytes')

# Remover null bytes
cleaned = content.replace(b'\x00', b'')
print(f'Tamanho limpo: {len(cleaned)} bytes')
print(f'Bytes removidos: {len(content) - len(cleaned)}')

# Salvar arquivo limpo
with open('backend-flask/models.py', 'wb') as f:
    f.write(cleaned)

print('✅ Arquivo limpo salvo!')

# Validar que é Python válido
try:
    with open('backend-flask/models.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        print(f'✅ Arquivo válido: {len(lines)} linhas')
except Exception as e:
    print(f'❌ Erro: {e}')
