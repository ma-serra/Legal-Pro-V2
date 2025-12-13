@echo off
REM Script Windows para migrar banco de dados PostgreSQL
REM De: 147.93.68.169:5433/hublegalpro_db
REM Para: gondola.proxy.rlwy.net:11843/railway

echo ========================================
echo MIGRACAO DE BANCO DE DADOS
echo ========================================
echo.

REM Configuracoes
set SOURCE_HOST=147.93.68.169
set SOURCE_PORT=5433
set SOURCE_DB=hublegalpro_db
set SOURCE_USER=arsdatascience
set SOURCE_PASS=xJ^>rh}zv?jU;21?t

set DEST_HOST=gondola.proxy.rlwy.net
set DEST_PORT=11843
set DEST_DB=railway
set DEST_USER=postgres
set DEST_PASS=XKtolNYAChqKElojyEfgzUdfpExZmBtM

set DUMP_FILE=backup_hublegalpro_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%.sql
set DUMP_FILE=%DUMP_FILE: =0%

echo ORIGEM: %SOURCE_HOST%:%SOURCE_PORT%/%SOURCE_DB%
echo DESTINO: %DEST_HOST%:%DEST_PORT%/%DEST_DB%
echo.
echo ATENCAO: Esta operacao ira SUBSTITUIR os dados no Railway!
echo.
pause

echo.
echo ========================================
echo PASSO 1: Fazendo backup do banco origem
echo ========================================
echo.

set PGPASSWORD=%SOURCE_PASS%
pg_dump -h %SOURCE_HOST% -p %SOURCE_PORT% -U %SOURCE_USER% -d %SOURCE_DB% -F c -f %DUMP_FILE% --verbose

if errorlevel 1 (
    echo.
    echo ERRO ao criar backup!
    echo.
    echo Verifique se:
    echo 1. PostgreSQL client tools estao instalados
    echo 2. Pode conectar no banco origem
    echo 3. Usuario e senha estao corretos
    pause
    exit /b 1
)

echo.
echo Backup criado com sucesso: %DUMP_FILE%
pause

echo.
echo ========================================
echo PASSO 2: Restaurando no banco Railway
echo ========================================
echo.

set PGPASSWORD=%DEST_PASS%
pg_restore -h %DEST_HOST% -p %DEST_PORT% -U %DEST_USER% -d %DEST_DB% --clean --if-exists --no-owner --no-acl --verbose %DUMP_FILE%

if errorlevel 1 (
    echo.
    echo AVISO: Alguns erros podem ser normais durante restore
    echo Continue apenas se os dados principais foram migrados
    echo.
)

echo.
echo ========================================
echo PASSO 3: Verificando migracao
echo ========================================
echo.

set PGPASSWORD=%DEST_PASS%
psql -h %DEST_HOST% -p %DEST_PORT% -U %DEST_USER% -d %DEST_DB% -c "SELECT COUNT(*) as total_tabelas FROM information_schema.tables WHERE table_schema = 'public';"

echo.
echo ========================================
echo MIGRACAO CONCLUIDA!
echo ========================================
echo.
echo Proximos passos:
echo 1. Verifique os dados no Railway
echo 2. Teste as funcionalidades do sistema
echo 3. Atualize DATABASE_URL no Railway:
echo    postgresql://%DEST_USER%:%DEST_PASS%@%DEST_HOST%:%DEST_PORT%/%DEST_DB%
echo.

REM Perguntar se deve deletar o arquivo de backup
echo.
set /p DELETE_BACKUP="Deseja deletar o arquivo de backup? (S/N): "
if /i "%DELETE_BACKUP%"=="S" (
    del %DUMP_FILE%
    echo Backup deletado.
) else (
    echo Backup mantido: %DUMP_FILE%
)

echo.
pause
