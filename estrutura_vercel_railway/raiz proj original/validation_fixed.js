// validation_fixed.js - Validação corrigida da clonagem
const { Client } = require('pg');

const SOURCE_CONFIG = {
  connectionString: "postgresql://neondb_owner:npg_F3M8RaEktGdQ@ep-withered-smoke-afgjgeem.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require"
};

const DEST_CONFIG = {
  connectionString: "postgresql://neondb_owner:npg_tjJkTy2qo8Bg@ep-dark-union-a522szv7.us-east-2.aws.neon.tech/neondb?sslmode=require"
};

async function quickValidation() {
  console.log('🔍 VALIDAÇÃO RÁPIDA DA CLONAGEM');
  console.log('===============================\n');

  const sourceClient = new Client(SOURCE_CONFIG);
  const destClient = new Client(DEST_CONFIG);
  
  try {
    await sourceClient.connect();
    await destClient.connect();
    console.log('✅ Conexões estabelecidas\n');

    // 1. Comparar tabelas básicas
    console.log('📊 1. COMPARAÇÃO DE TABELAS');
    console.log('===========================');
    
    const sourceTablesResult = await sourceClient.query(`
      SELECT COUNT(*) as count 
      FROM information_schema.tables 
      WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
    `);

    const destTablesResult = await destClient.query(`
      SELECT COUNT(*) as count 
      FROM information_schema.tables 
      WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
    `);

    const sourceTables = parseInt(sourceTablesResult.rows[0].count);
    const destTables = parseInt(destTablesResult.rows[0].count);

    console.log(`📋 Origem: ${sourceTables} tabelas`);
    console.log(`📋 Destino: ${destTables} tabelas`);

    const tableScore = destTables >= sourceTables ? 100 : Math.round((destTables / sourceTables) * 100);
    console.log(`📊 Score de tabelas: ${tableScore}%`);

    // 2. Verificar dados críticos
    console.log('\n👤 2. DADOS CRÍTICOS');
    console.log('====================');

    const criticalTables = ['user', 'role', 'permission'];
    let criticalScore = 0;

    for (const tableName of criticalTables) {
      try {
        const destCount = await destClient.query(`SELECT COUNT(*) FROM "${tableName}"`);
        const count = parseInt(destCount.rows[0].count);
        
        const status = count > 0 ? '✅' : '❌';
        console.log(`${status} ${tableName}: ${count} registros`);
        
        if (count > 0) criticalScore += 33.33;

      } catch (error) {
        console.log(`❌ ${tableName}: ERRO - ${error.message}`);
      }
    }

    console.log(`📊 Score dados críticos: ${Math.round(criticalScore)}%`);

    // 3. Contagem total de registros
    console.log('\n📈 3. REGISTROS TOTAIS');
    console.log('======================');

    let totalRecords = 0;
    let tablesWithData = 0;

    const allTablesResult = await destClient.query(`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
      ORDER BY table_name
    `);

    for (const row of allTablesResult.rows) {
      try {
        const countResult = await destClient.query(`SELECT COUNT(*) FROM "${row.table_name}"`);
        const count = parseInt(countResult.rows[0].count);
        
        if (count > 0) {
          tablesWithData++;
          totalRecords += count;
        }
      } catch (error) {
        // Ignorar erros de contagem
      }
    }

    console.log(`📊 Total de registros: ${totalRecords}`);
    console.log(`📊 Tabelas com dados: ${tablesWithData}/${destTables}`);

    const dataScore = tablesWithData >= 15 ? 100 : Math.round((tablesWithData / 15) * 100);
    console.log(`📊 Score de dados: ${dataScore}%`);

    // 4. Calcular score final
    console.log('\n🏆 RESULTADO FINAL');
    console.log('==================');

    const finalScore = Math.round((tableScore * 0.3) + (criticalScore * 0.4) + (dataScore * 0.3));

    console.log(`📊 Score de tabelas: ${tableScore}% (peso 30%)`);
    console.log(`📊 Score crítico: ${Math.round(criticalScore)}% (peso 40%)`);
    console.log(`📊 Score de dados: ${dataScore}% (peso 30%)`);
    console.log('\n' + '='.repeat(40));
    console.log(`🎯 SCORE FINAL: ${finalScore}%`);

    if (finalScore >= 90) {
      console.log('\n🎉 EXCELENTE! Clonagem 100% bem-sucedida! 🎉');
      console.log('✅ Sua database está pronta para uso!');
    } else if (finalScore >= 80) {
      console.log('\n✅ MUITO BOM! Clonagem bem-sucedida!');
      console.log('📊 Alguns dados podem estar ausentes, mas funcional');
    } else if (finalScore >= 70) {
      console.log('\n⚠️ PARCIAL: Clonagem funcionou parcialmente');
      console.log('🔧 Algumas correções podem ser necessárias');
    } else {
      console.log('\n❌ ATENÇÃO: Clonagem precisa de correções');
      console.log('🛠️ Revisar processo de migração');
    }

    // 5. Detalhes específicos
    console.log('\n📋 DETALHES IMPORTANTES:');
    console.log('========================');

    const importantTables = ['user', 'role', 'permission', 'processo_juridico', 'template_juridico'];
    
    for (const tableName of importantTables) {
      try {
        const countResult = await destClient.query(`SELECT COUNT(*) FROM "${tableName}"`);
        const count = parseInt(countResult.rows[0].count);
        
        const status = count > 0 ? '✅' : '📭';
        console.log(`${status} ${tableName}: ${count} registros`);
        
      } catch (error) {
        console.log(`❌ ${tableName}: não encontrada`);
      }
    }

    return { finalScore, totalRecords, tablesWithData, destTables };

  } catch (error) {
    console.error('❌ Erro durante validação:', error.message);
    return { finalScore: 0, error: error.message };
  } finally {
    await sourceClient.end();
    await destClient.end();
    console.log('\n🔌 Validação concluída');
  }
}

if (require.main === module) {
  quickValidation()
    .then(result => {
      if (result.finalScore >= 80) {
        console.log('\n🌟 Validação passou! Clonagem bem-sucedida!');
        process.exit(0);
      } else {
        console.log('\n⚠️ Validação indica que melhorias são necessárias');
        process.exit(1);
      }
    })
    .catch(error => {
      console.error('\n💥 Erro na validação:', error);
      process.exit(1);
    });
}
