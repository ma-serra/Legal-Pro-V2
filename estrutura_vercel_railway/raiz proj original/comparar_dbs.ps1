# Script para comparar estruturas de dois bancos PostgreSQL
# Executa no PowerShell do Replit

param(
    [switch]$DetalhesCompletos,
    [switch]$SomenteResumo
)

Write-Host "=== COMPARAÇÃO DE BANCOS DE DADOS POSTGRESQL ===" -ForegroundColor Cyan
Write-Host ""

# Configurações dos bancos
$DB1 = @{
    Name = "DB1 (us-east-2)"
    Host = "ep-late-tree-aectaew7.c-2.us-east-2.aws.neon.tech"
    Port = "5432"
    Database = "neondb"
    User = "neondb_owner"
    Password = "npg_YDKTIQge3i4o"
}

$DB2 = @{
    Name = "DB2 (us-west-2)"
    Host = "ep-withered-smoke-afgjgeem.c-2.us-west-2.aws.neon.tech"
    Port = "5432"
    Database = "neondb"
    User = "neondb_owner"
    Password = "npg_F3M8RaEktGdQ"
}

# Função para executar query PostgreSQL
function Invoke-PostgreSQLQuery {
    param(
        [hashtable]$Database,
        [string]$Query
    )

    $env:PGPASSWORD = $Database.Password

    try {
        $result = psql -h $Database.Host -p $Database.Port -U $Database.User -d $Database.Database -t -c $Query 2>$null
        if ($LASTEXITCODE -eq 0) {
            return $result
        } else {
            Write-Warning "Erro ao executar query no $($Database.Name)"
            return $null
        }
    }
    catch {
        Write-Warning "Erro de conexão com $($Database.Name): $($_.Exception.Message)"
        return $null
    }
}

# Função para testar conectividade
function Test-DatabaseConnection {
    param([hashtable]$Database)

    Write-Host "Testando conexão com $($Database.Name)..." -NoNewline

    $result = Invoke-PostgreSQLQuery -Database $Database -Query "SELECT version();"

    if ($result) {
        Write-Host " ✓ CONECTADO" -ForegroundColor Green
        return $true
    } else {
        Write-Host " ✗ FALHA" -ForegroundColor Red
        return $false
    }
}

# Função para obter lista de tabelas
function Get-DatabaseTables {
    param([hashtable]$Database)

    $query = @"
SELECT schemaname, tablename, hasindexes, hasrules, hastriggers
FROM pg_tables 
WHERE schemaname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
ORDER BY schemaname, tablename;
"@

    $result = Invoke-PostgreSQLQuery -Database $Database -Query $query
    return $result
}

# Função para obter estrutura de uma tabela
function Get-TableStructure {
    param(
        [hashtable]$Database,
        [string]$TableName,
        [string]$SchemaName = "public"
    )

    $query = @"
SELECT 
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = '$SchemaName' AND table_name = '$TableName'
ORDER BY ordinal_position;
"@

    $result = Invoke-PostgreSQLQuery -Database $Database -Query $query
    return $result
}

# Função para obter índices de uma tabela
function Get-TableIndexes {
    param(
        [hashtable]$Database,
        [string]$TableName,
        [string]$SchemaName = "public"
    )

    $query = @"
SELECT 
    indexname,
    indexdef
FROM pg_indexes 
WHERE schemaname = '$SchemaName' AND tablename = '$TableName'
ORDER BY indexname;
"@

    $result = Invoke-PostgreSQLQuery -Database $Database -Query $query
    return $result
}

# Verificar se psql está disponível
if (-not (Get-Command psql -ErrorAction SilentlyContinue)) {
    Write-Error "psql não encontrado. Para instalar no Replit:"
    Write-Host "1. Abra o painel 'Tools' > 'Packages' ou use Ctrl+Shift+P" -ForegroundColor Yellow
    Write-Host "2. Procure por 'postgresql' e adicione como dependência" -ForegroundColor Yellow
    Write-Host "3. Ou adicione 'pkgs.postgresql' no arquivo replit.nix" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Exemplo de replit.nix:" -ForegroundColor Cyan
    Write-Host "{ pkgs }: { deps = [ pkgs.postgresql ]; }" -ForegroundColor Gray
    exit 1
}

# Testar conectividade
Write-Host "=== TESTE DE CONECTIVIDADE ===" -ForegroundColor Yellow
$db1Connected = Test-DatabaseConnection -Database $DB1
$db2Connected = Test-DatabaseConnection -Database $DB2

if (-not $db1Connected -or -not $db2Connected) {
    Write-Error "Não foi possível conectar aos bancos de dados. Verifique as credenciais."
    exit 1
}

Write-Host ""

# Obter tabelas de ambos os bancos
Write-Host "=== OBTENDO ESTRUTURAS DAS TABELAS ===" -ForegroundColor Yellow
Write-Host "Analisando $($DB1.Name)..." -NoNewline
$tables1 = Get-DatabaseTables -Database $DB1
Write-Host " ✓" -ForegroundColor Green

Write-Host "Analisando $($DB2.Name)..." -NoNewline
$tables2 = Get-DatabaseTables -Database $DB2
Write-Host " ✓" -ForegroundColor Green

Write-Host ""

# Processar listas de tabelas
$tableList1 = @()
$tableList2 = @()

if ($tables1) {
    foreach ($line in $tables1) {
        if ($line.Trim()) {
            $parts = $line.Trim() -split '\|'
            if ($parts.Length -ge 2) {
                $tableList1 += "$($parts[0].Trim()).$($parts[1].Trim())"
            }
        }
    }
}

if ($tables2) {
    foreach ($line in $tables2) {
        if ($line.Trim()) {
            $parts = $line.Trim() -split '\|'
            if ($parts.Length -ge 2) {
                $tableList2 += "$($parts[0].Trim()).$($parts[1].Trim())"
            }
        }
    }
}

# Comparar tabelas
Write-Host "=== COMPARAÇÃO DE TABELAS ===" -ForegroundColor Yellow
Write-Host "Total de tabelas em $($DB1.Name): $($tableList1.Count)" -ForegroundColor Cyan
Write-Host "Total de tabelas em $($DB2.Name): $($tableList2.Count)" -ForegroundColor Cyan
Write-Host ""

# Tabelas em DB1 mas não em DB2
$onlyInDB1 = $tableList1 | Where-Object { $_ -notin $tableList2 }
if ($onlyInDB1.Count -gt 0) {
    Write-Host "❌ Tabelas apenas em $($DB1.Name):" -ForegroundColor Red
    foreach ($table in $onlyInDB1) {
        Write-Host "   - $table" -ForegroundColor Red
    }
    Write-Host ""
}

# Tabelas em DB2 mas não em DB1
$onlyInDB2 = $tableList2 | Where-Object { $_ -notin $tableList1 }
if ($onlyInDB2.Count -gt 0) {
    Write-Host "❌ Tabelas apenas em $($DB2.Name):" -ForegroundColor Red
    foreach ($table in $onlyInDB2) {
        Write-Host "   - $table" -ForegroundColor Red
    }
    Write-Host ""
}

# Tabelas comuns
$commonTables = $tableList1 | Where-Object { $_ -in $tableList2 }
if ($commonTables.Count -gt 0) {
    Write-Host "✅ Tabelas presentes em ambos os bancos:" -ForegroundColor Green
    foreach ($table in $commonTables) {
        Write-Host "   - $table" -ForegroundColor Green
    }
    Write-Host ""
}

# Análise detalhada das estruturas (se solicitado)
if ($DetalhesCompletos -and $commonTables.Count -gt 0) {
    Write-Host "=== ANÁLISE DETALHADA DAS ESTRUTURAS ===" -ForegroundColor Yellow

    foreach ($fullTableName in $commonTables) {
        $parts = $fullTableName -split '\.'
        $schema = $parts[0]
        $table = $parts[1]

        Write-Host ""
        Write-Host "--- Analisando tabela: $fullTableName ---" -ForegroundColor Cyan

        # Obter estrutura de ambas as tabelas
        $struct1 = Get-TableStructure -Database $DB1 -TableName $table -SchemaName $schema
        $struct2 = Get-TableStructure -Database $DB2 -TableName $table -SchemaName $schema

        if ($struct1 -and $struct2) {
            # Comparar colunas (simplificado)
            $columns1 = ($struct1 | ForEach-Object { ($_ -split '\|')[0].Trim() }) | Where-Object { $_ }
            $columns2 = ($struct2 | ForEach-Object { ($_ -split '\|')[0].Trim() }) | Where-Object { $_ }

            $colDiff1 = $columns1 | Where-Object { $_ -notin $columns2 }
            $colDiff2 = $columns2 | Where-Object { $_ -notin $columns1 }

            if ($colDiff1.Count -eq 0 -and $colDiff2.Count -eq 0) {
                Write-Host "   ✅ Estrutura idêntica" -ForegroundColor Green
            } else {
                Write-Host "   ❌ Diferenças encontradas:" -ForegroundColor Red
                if ($colDiff1.Count -gt 0) {
                    Write-Host "      Colunas apenas em $($DB1.Name): $($colDiff1 -join ', ')" -ForegroundColor Red
                }
                if ($colDiff2.Count -gt 0) {
                    Write-Host "      Colunas apenas em $($DB2.Name): $($colDiff2 -join ', ')" -ForegroundColor Red
                }
            }
        }
    }
}

# Resumo final
Write-Host ""
Write-Host "=== RESUMO FINAL ===" -ForegroundColor Yellow

$totalIssues = $onlyInDB1.Count + $onlyInDB2.Count

if ($totalIssues -eq 0) {
    Write-Host "✅ ESTRUTURAS IDÊNTICAS" -ForegroundColor Green
    Write-Host "Ambos os bancos possuem exatamente as mesmas tabelas." -ForegroundColor Green
} else {
    Write-Host "❌ DIFERENÇAS ENCONTRADAS" -ForegroundColor Red
    Write-Host "Total de discrepâncias: $totalIssues" -ForegroundColor Red

    if ($onlyInDB1.Count -gt 0) {
        Write-Host "- $($onlyInDB1.Count) tabela(s) apenas em $($DB1.Name)" -ForegroundColor Red
    }
    if ($onlyInDB2.Count -gt 0) {
        Write-Host "- $($onlyInDB2.Count) tabela(s) apenas em $($DB2.Name)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Tabelas comuns: $($commonTables.Count)" -ForegroundColor Cyan
Write-Host ""

# Comandos úteis
Write-Host "=== COMANDOS ÚTEIS ===" -ForegroundColor Yellow
Write-Host "Para análise detalhada: ./script.ps1 -DetalhesCompletos" -ForegroundColor Gray
Write-Host "Para conectar ao DB1: psql -h $($DB1.Host) -p $($DB1.Port) -U $($DB1.User) -d $($DB1.Database)" -ForegroundColor Gray
Write-Host "Para conectar ao DB2: psql -h $($DB2.Host) -p $($DB2.Port) -U $($DB2.User) -d $($DB2.Database)" -ForegroundColor Gray

Write-Host ""
Write-Host "=== SCRIPT CONCLUÍDO ===" -ForegroundColor Cyan
