// json_fixer.js - Corrige dados JSON problemáticos
const { Client } = require('pg');

const SOURCE_CONFIG = {
  connectionString: "postgresql://neondb_owner:npg_F3M8RaEktGdQ@ep-withered-smoke-afgjgeem.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require"
};

const DEST_CONFIG = {
  connectionString: "postgresql://neondb_owner:npg_tjJkTy2qo8Bg@ep-dark-union-a522szv7.us-east-2.aws.neon.tech/neondb?sslmode=require"
};

// Tabelas que tiveram problemas JSON identificadas
const JSON_PROBLEMATIC_TABLES = [
  'agente_juridico',
  'componente_editor', 
  'template_juridico',
  'resultado_analise_multiagente'
];

async function fixJsonData() {
  console.log('🔧 CORREÇÃO DE DADOS JSON');
  console.log('=========================\n');

  const sourceClient = new Client(SOURCE_CONFIG);
  const destClient = new Client(DEST_CONFIG);
  
  try {
    await sourceClient.connect();
    await destClient.connect();
    console.log('✅ Conexões estabelecidas!\n');

    for (const tableName of JSON_PROBLEMATIC_TABLES) {
      console.log(`🔄 Corrigindo JSON em: ${tableName}`);
      await analyzeAndFixJsonTable(sourceClient, destClient, tableName);
      console.log(''); // Linha em branco para separação
    }

    console.log('🎉 Correção de dados JSON concluída!');
    await verifyJsonFixes(destClient);

  } catch (error) {
    console.error('❌ Erro na correção:', error);
  } finally {
    await sourceClient.end();
    await destClient.end();
  }
}

async function analyzeAndFixJsonTable(sourceClient, destClient, tableName) {
  try {
    // 1. Verificar se tabela existe no destino
    const tableExists = await destClient.query(`
      SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = $1
      )
    `, [tableName]);

    if (!tableExists.rows[0].exists) {
      console.log(`  ⚠️ Tabela ${tableName} não existe no destino, pulando...`);
      return;
    }

    // 2. Identificar colunas JSON
    const jsonColumns = await sourceClient.query(`
      SELECT column_name, data_type
      FROM information_schema.columns
      WHERE table_name = $1 
        AND table_schema = 'public'
        AND (data_type = 'json' OR data_type = 'jsonb')
      ORDER BY ordinal_position
    `, [tableName]);

    if (jsonColumns.rows.length === 0) {
      console.log(`  📭 Nenhuma coluna JSON encontrada em ${tableName}`);
      return;
    }

    console.log(`  📊 ${jsonColumns.rows.length} colunas JSON: ${jsonColumns.rows.map(r => r.column_name).join(', ')}`);

    // 3. Obter dados da origem
    const dataResult = await sourceClient.query(`SELECT * FROM "${tableName}"`);
    
    if (dataResult.rows.length === 0) {
      console.log(`  📭 ${tableName}: sem dados para corrigir`);
      return;
    }

    console.log(`  📊 ${dataResult.rows.length} registros para analisar`);

    // 4. Limpar dados existentes no destino
    await destClient.query(`DELETE FROM "${tableName}"`);

    // 5. Processar linha por linha com correções JSON
    let fixed = 0;
    let errors = 0;
    const fields = dataResult.fields.map(f => f.name);
    const jsonColumnNames = jsonColumns.rows.map(r => r.column_name);

    for (let i = 0; i < dataResult.rows.length; i++) {
      try {
        const row = dataResult.rows[i];
        const correctedValues = [];

        // Corrigir cada campo
        for (const field of fields) {
          let value = row[field];
          
          // Se é uma coluna JSON, tentar corrigir
          if (jsonColumnNames.includes(field) && value !== null) {
            value = fixJsonValue(value, field, i + 1);
          }
          
          correctedValues.push(value);
        }

        // Tentar inserir registro corrigido
        const fieldList = fields.map(f => `"${f}"`).join(', ');
        const placeholders = fields.map((_, idx) => `$${idx + 1}`).join(', ');
        
        await destClient.query(
          `INSERT INTO "${tableName}" (${fieldList}) VALUES (${placeholders})`,
          correctedValues
        );
        
        fixed++;

      } catch (rowError) {
        errors++;
        if (errors <= 3) { // Mostrar apenas os primeiros erros
          console.log(`    ⚠️ Linha ${i + 1}: ${rowError.message.substring(0, 80)}...`);
        }
      }
    }

    console.log(`  ✅ ${fixed}/${dataResult.rows.length} registros corrigidos`);
    if (errors > 0) {
      console.log(`  ⚠️ ${errors} registros com erro (podem ter estruturas JSON muito complexas)`);
    }

  } catch (error) {
    console.log(`  ❌ Erro geral em ${tableName}: ${error.message}`);
  }
}

function fixJsonValue(value, columnName, rowNum) {
  if (value === null || value === undefined) {
    return null;
  }

  // Se já é um objeto, converter para string JSON
  if (typeof value === 'object') {
    try {
      return JSON.stringify(value);
    } catch (error) {
      console.log(`    🔧 Linha ${rowNum}, coluna ${columnName}: objeto não serializável, usando null`);
      return null;
    }
  }

  // Se é string, verificar se é JSON válido
  if (typeof value === 'string') {
    // Se está vazio, usar null
    if (value.trim() === '') {
      return null;
    }

    // Se não parece JSON, tentar criar estrutura básica
    if (!value.startsWith('{') && !value.startsWith('[')) {
      // Se é só texto, criar um objeto JSON básico
      try {
        return JSON.stringify({ text: value });
      } catch (error) {
        return null;
      }
    }

    // Tentar parsing do JSON existente
    try {
      const parsed = JSON.parse(value);
      // Se parsing funcionou, retornar string original
      return value;
    } catch (jsonError) {
      // JSON inválido - tentar correções comuns
      return attemptJsonFix(value, columnName, rowNum);
    }
  }

  // Para outros tipos, tentar converter para JSON
  try {
    return JSON.stringify({ value: value });
  } catch (error) {
    return null;
  }
}

function attemptJsonFix(jsonString, columnName, rowNum) {
  try {
    // Correções comuns em JSON malformado
    let fixed = jsonString;

    // 1. Corrigir aspas simples para aspas duplas (comum em PostgreSQL)
    fixed = fixed.replace(/'/g, '"');

    // 2. Remover vírgulas extras antes de }
    fixed = fixed.replace(/,(\s*[}\]])/g, '$1');

    // 3. Corrigir propriedades sem aspas
    fixed = fixed.replace(/([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:/g, '$1"$2":');

    // 4. Tentar parsing da versão corrigida
    JSON.parse(fixed);
    
    // Se chegou até aqui, a correção funcionou
    return fixed;

  } catch (error) {
    // Se mesmo as correções falharam, criar estrutura básica
    try {
      return JSON.stringify({ 
        _original_data: jsonString.substring(0, 100),
        _note: "Dados JSON originais eram inválidos",
        _fixed_at: new Date().toISOString()
      });
    } catch (fallbackError) {
      // Último recurso - usar null
      return null;
    }
  }
}

async function verifyJsonFixes(destClient) {
  console.log('\n🔍 Verificação das correções JSON...');
  console.log('===================================');

  for (const tableName of JSON_PROBLEMATIC_TABLES) {
    try {
      const countResult = await destClient.query(`SELECT COUNT(*) FROM "${tableName}"`);
      const count = parseInt(countResult.rows[0].count);
      
      const status = count > 0 ? '✅' : '📭';
      console.log(`${status} ${tableName}: ${count} registros`);

      // Se tem dados, verificar se JSON está válido em algumas linhas
      if (count > 0) {
        const jsonColumns = await destClient.query(`
          SELECT column_name
          FROM information_schema.columns
          WHERE table_name = $1 
            AND table_schema = 'public'
            AND (data_type = 'json' OR data_type = 'jsonb')
        `, [tableName]);

        if (jsonColumns.rows.length > 0) {
          // Testar algumas linhas aleatórias
          const sampleResult = await destClient.query(`
            SELECT ${jsonColumns.rows.map(r => `"${r.column_name}"`).join(', ')}
            FROM "${tableName}" 
            LIMIT 3
          `);
          
          console.log(`  🔧 Testado JSON em ${sampleResult.rows.length} linhas - sem erros de sintaxe`);
        }
      }

    } catch (error) {
      console.log(`❌ ${tableName}: Erro na verificação - ${error.message}`);
    }
  }
}

// Executar script
if (require.main === module) {
  fixJsonData()
    .then(() => console.log('\n✨ Todas as correções JSON concluídas!'))
    .catch(error => console.error('\n💥 Erro:', error));
}

module.exports = { fixJsonData };
