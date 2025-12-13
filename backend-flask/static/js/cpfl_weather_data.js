// =====================================================================
// DATASETS SIMULADOS - DADOS METEOROLÓGICOS E GEOLOCALIZAÇÃO CPFL
// Baseado nas comarcas reais dos processos RGE/CPFL
// =====================================================================

// 1. COORDENADAS GEOGRÁFICAS DAS PRINCIPAIS COMARCAS DO RS
// Baseado em dados reais do IBGE e Google Maps
export const comarcasGeolocalizacao = [
  // Região Metropolitana
  { comarca: 'Porto Alegre', lat: -30.0346, lon: -51.2177, regiao: 'Metropolitana', populacao: 1492000 },
  { comarca: 'Canoas', lat: -29.9177, lon: -51.1844, regiao: 'Metropolitana', populacao: 348000 },
  { comarca: 'Novo Hamburgo', lat: -29.6783, lon: -51.1306, regiao: 'Metropolitana', populacao: 247000 },
  { comarca: 'São Leopoldo', lat: -29.7604, lon: -51.1481, regiao: 'Metropolitana', populacao: 237000 },
  { comarca: 'Gravataí', lat: -29.9441, lon: -50.9911, regiao: 'Metropolitana', populacao: 281000 },
  { comarca: 'Viamão', lat: -30.0811, lon: -51.0233, regiao: 'Metropolitana', populacao: 255000 },
  { comarca: 'Alvorada', lat: -30.0011, lon: -51.0842, regiao: 'Metropolitana', populacao: 208000 },
  { comarca: 'Cachoeirinha', lat: -29.9508, lon: -51.0941, regiao: 'Metropolitana', populacao: 131000 },
  
  // Norte
  { comarca: 'Caxias do Sul', lat: -29.1634, lon: -51.1797, regiao: 'Norte', populacao: 517000 },
  { comarca: 'Passo Fundo', lat: -28.2622, lon: -52.4083, regiao: 'Norte', populacao: 204000 },
  { comarca: 'Erechim', lat: -27.6336, lon: -52.2736, regiao: 'Norte', populacao: 105000 },
  { comarca: 'Bento Gonçalves', lat: -29.1669, lon: -51.5189, regiao: 'Norte', populacao: 121000 },
  { comarca: 'Vacaria', lat: -28.5094, lon: -50.9344, regiao: 'Norte', populacao: 67000 },
  
  // Sul
  { comarca: 'Pelotas', lat: -31.7654, lon: -52.3376, regiao: 'Sul', populacao: 343000 },
  { comarca: 'Rio Grande', lat: -32.0350, lon: -52.0986, regiao: 'Sul', populacao: 211000 },
  { comarca: 'Santa Cruz do Sul', lat: -29.7172, lon: -52.4261, regiao: 'Sul', populacao: 131000 },
  { comarca: 'Uruguaiana', lat: -29.7544, lon: -57.0883, regiao: 'Sul', populacao: 126000 },
  { comarca: 'Bagé', lat: -31.3286, lon: -54.1072, regiao: 'Sul', populacao: 121000 },
  
  // Centro
  { comarca: 'Santa Maria', lat: -29.6842, lon: -53.8069, regiao: 'Centro', populacao: 283000 },
  { comarca: 'Cruz Alta', lat: -28.6389, lon: -53.6061, regiao: 'Centro', populacao: 63000 },
  { comarca: 'Santiago', lat: -29.1914, lon: -54.8658, regiao: 'Centro', populacao: 51000 },
  { comarca: 'Ijuí', lat: -28.3878, lon: -53.9147, regiao: 'Centro', populacao: 83000 },
  { comarca: 'Santo Ângelo', lat: -28.2989, lon: -54.2631, regiao: 'Centro', populacao: 78000 },
  
  // Litoral
  { comarca: 'Torres', lat: -29.3350, lon: -49.7269, regiao: 'Litoral', populacao: 38000 },
  { comarca: 'Tramandaí', lat: -30.0036, lon: -50.1328, regiao: 'Litoral', populacao: 49000 },
  { comarca: 'Capão da Canoa', lat: -29.7458, lon: -50.0128, regiao: 'Litoral', populacao: 53000 },
  { comarca: 'Osório', lat: -29.8878, lon: -50.2697, regiao: 'Litoral', populacao: 46000 },
  
  // Interior
  { comarca: 'Santa Rosa', lat: -27.8708, lon: -54.4811, regiao: 'Interior', populacao: 72000 },
  { comarca: 'Lajeado', lat: -29.4669, lon: -51.9614, regiao: 'Interior', populacao: 85000 },
  { comarca: 'Cachoeira do Sul', lat: -30.0392, lon: -52.8936, regiao: 'Interior', populacao: 83000 },
  { comarca: 'São Borja', lat: -28.6603, lon: -56.0044, regiao: 'Interior', populacao: 62000 },
  { comarca: 'Alegrete', lat: -29.7831, lon: -55.7917, regiao: 'Interior', populacao: 78000 },
  { comarca: 'Santana do Livramento', lat: -30.8908, lon: -55.5322, regiao: 'Interior', populacao: 82000 },
  { comarca: 'Santa Bárbara do Sul', lat: -28.3589, lon: -53.2553, regiao: 'Interior', populacao: 8000 },
  { comarca: 'Carazinho', lat: -28.2836, lon: -52.7864, regiao: 'Interior', populacao: 62000 }
];

// =====================================================================
// 2. DADOS METEOROLÓGICOS HISTÓRICOS SIMULADOS (2019-2025)
// Correlacionados com processos por comarca
// =====================================================================

function gerarDadosMeteorologicos(comarca, dataInicio, dataFim) {
  const dados = [];
  let dataAtual = new Date(dataInicio);
  const dataFinal = new Date(dataFim);
  
  // Características climáticas por região do RS
  const climaRegiao = {
    'Metropolitana': { temp_media: 19, chuva_media: 120, vento_medio: 12 },
    'Norte': { temp_media: 17, chuva_media: 140, vento_medio: 10 },
    'Sul': { temp_media: 18, chuva_media: 110, vento_medio: 15 },
    'Centro': { temp_media: 18, chuva_media: 130, vento_medio: 11 },
    'Litoral': { temp_media: 20, chuva_media: 100, vento_medio: 18 },
    'Interior': { temp_media: 19, chuva_media: 125, vento_medio: 13 }
  };
  
  const clima = climaRegiao[comarca.regiao] || climaRegiao['Centro'];
  
  while (dataAtual <= dataFinal) {
    const mes = dataAtual.getMonth();
    const hora = dataAtual.getHours();
    
    // Variação sazonal (verão mais quente e chuvoso)
    const fatorSazonal = Math.sin((mes - 2) * Math.PI / 6);
    
    // Temperatura (varia com estação e hora do dia)
    const temp_base = clima.temp_media + fatorSazonal * 5;
    const temp_hora = temp_base + Math.sin(hora * Math.PI / 12) * 3;
    const temperatura = temp_hora + (Math.random() - 0.5) * 4;
    
    // Chuva (mais comum no verão e em eventos extremos)
    const prob_chuva = 0.15 + fatorSazonal * 0.1;
    const esta_chovendo = Math.random() < prob_chuva;
    const intensidade_chuva = esta_chovendo ? 
      Math.pow(Math.random(), 2) * clima.chuva_media * (1 + Math.random() * 3) : 0;
    
    // Vento (mais forte em eventos de tempestade)
    const vento_base = clima.vento_medio + (Math.random() - 0.5) * 5;
    const vento_rajada = esta_chovendo && intensidade_chuva > 20 ?
      vento_base * (1.5 + Math.random() * 2) : vento_base * 1.2;
    
    // Umidade (maior quando chove)
    const umidade = esta_chovendo ? 
      75 + Math.random() * 20 : 
      55 + Math.random() * 25;
    
    // Pressão atmosférica (menor em tempestades)
    const pressao_base = 1013;
    const pressao = esta_chovendo && intensidade_chuva > 30 ?
      pressao_base - (10 + Math.random() * 15) :
      pressao_base + (Math.random() - 0.5) * 10;
    
    // Raios (apenas em tempestades fortes)
    const densidade_raios = intensidade_chuva > 40 && vento_rajada > 60 ?
      Math.random() * 15 : 0;
    
    // Índices compostos
    const storm_intensity = (intensidade_chuva * vento_rajada) / 100;
    const equipment_stress = Math.abs(temperatura - 25) + umidade / 10;
    
    // Classificar severidade
    let severidade;
    if (storm_intensity < 2) severidade = 'Baixa';
    else if (storm_intensity < 5) severidade = 'Moderada';
    else if (storm_intensity < 10) severidade = 'Alta';
    else if (storm_intensity < 20) severidade = 'Severa';
    else severidade = 'Extrema';
    
    dados.push({
      datetime: new Date(dataAtual),
      comarca: comarca.nome,
      lat: comarca.lat,
      lon: comarca.lon,
      temperatura: parseFloat(temperatura.toFixed(1)),
      temperatura_min: parseFloat((temperatura - 3).toFixed(1)),
      temperatura_max: parseFloat((temperatura + 3).toFixed(1)),
      precipitacao_mm: parseFloat(intensidade_chuva.toFixed(1)),
      vento_velocidade_ms: parseFloat(vento_base.toFixed(1)),
      vento_rajada_ms: parseFloat(vento_rajada.toFixed(1)),
      umidade_relativa: parseFloat(umidade.toFixed(1)),
      pressao_atmosferica: parseFloat(pressao.toFixed(1)),
      densidade_raios: parseFloat(densidade_raios.toFixed(2)),
      storm_intensity_index: parseFloat(storm_intensity.toFixed(2)),
      equipment_stress_index: parseFloat(equipment_stress.toFixed(2)),
      weather_severity: severidade
    });
    
    // Avançar 1 hora
    dataAtual.setHours(dataAtual.getHours() + 1);
  }
  
  return dados;
}

// Gerar dados para top 10 comarcas (exemplo com 30 dias de dados)
export const dadosMeteorologicosSimulados = comarcasGeolocalizacao
  .slice(0, 10)
  .map(comarca => ({
    comarca: comarca.nome,
    dados_historicos: gerarDadosMeteorologicos(
      comarca,
      '2024-08-01',
      '2024-08-30'
    )
  }));

// =====================================================================
// 3. EVENTOS CLIMÁTICOS EXTREMOS CORRELACIONADOS COM PROCESSOS
// =====================================================================

export const eventosClimaticosExtremos = [
  {
    id: 1,
    data: '2024-01-15',
    tipo: 'Temporal Severo',
    comarcas_afetadas: ['Porto Alegre', 'Canoas', 'Gravataí', 'Alvorada'],
    precipitacao_max: 142,
    vento_max: 98,
    duracao_horas: 6,
    processos_relacionados: 47,
    danos_estimados: 2400000,
    interrupcoes_energia: 1850,
    tempo_medio_restabelecimento: 14.5
  },
  {
    id: 2,
    data: '2024-03-22',
    tipo: 'Vendaval',
    comarcas_afetadas: ['Santa Maria', 'Santiago', 'Cruz Alta'],
    precipitacao_max: 35,
    vento_max: 115,
    duracao_horas: 4,
    processos_relacionados: 28,
    danos_estimados: 1800000,
    interrupcoes_energia: 980,
    tempo_medio_restabelecimento: 18.2
  },
  {
    id: 3,
    data: '2024-05-08',
    tipo: 'Chuva Intensa',
    comarcas_afetadas: ['Pelotas', 'Rio Grande', 'Santa Cruz do Sul'],
    precipitacao_max: 178,
    vento_max: 72,
    duracao_horas: 8,
    processos_relacionados: 35,
    danos_estimados: 2100000,
    interrupcoes_energia: 1420,
    tempo_medio_restabelecimento: 12.8
  },
  {
    id: 4,
    data: '2024-07-12',
    tipo: 'Geada Intensa',
    comarcas_afetadas: ['Vacaria', 'Caxias do Sul', 'Bento Gonçalves'],
    precipitacao_max: 0,
    vento_max: 45,
    duracao_horas: 12,
    processos_relacionados: 12,
    danos_estimados: 890000,
    interrupcoes_energia: 340,
    tempo_medio_restabelecimento: 8.5
  },
  {
    id: 5,
    data: '2024-08-20',
    tipo: 'Temporal com Granizo',
    comarcas_afetadas: ['Lajeado', 'Cachoeira do Sul', 'Santa Rosa'],
    precipitacao_max: 95,
    vento_max: 105,
    duracao_horas: 3,
    processos_relacionados: 31,
    danos_estimados: 1950000,
    interrupcoes_energia: 1120,
    tempo_medio_restabelecimento: 15.7
  }
];

// =====================================================================
// 4. CORRELAÇÃO ENTRE CLIMA E PROCESSOS POR COMARCA
// =====================================================================

export const correlacaoClimaProcessos = comarcasGeolocalizacao.map(comarca => {
  // Simular processos baseado em população e clima
  const fator_populacao = Math.log10(comarca.populacao) / 2;
  const processos_base = Math.floor(fator_populacao * (5 + Math.random() * 15));
  
  // Causas relacionadas ao clima
  const causas_climaticas = {
    'Demora no restabelecimento': Math.floor(processos_base * (0.3 + Math.random() * 0.2)),
    'Danos por temporal': Math.floor(processos_base * (0.15 + Math.random() * 0.15)),
    'Variação de consumo': Math.floor(processos_base * (0.1 + Math.random() * 0.1)),
    'Queima de equipamentos': Math.floor(processos_base * (0.08 + Math.random() * 0.07))
  };
  
  return {
    comarca: comarca.nome,
    lat: comarca.lat,
    lon: comarca.lon,
    regiao: comarca.regiao,
    total_processos: processos_base,
    causas_climaticas: causas_climaticas,
    eventos_extremos_12m: Math.floor(Math.random() * 8),
    tempo_medio_interrupcao: parseFloat((2 + Math.random() * 12).toFixed(1)),
    valor_medio_processos: parseFloat((15000 + Math.random() * 45000).toFixed(2)),
    taxa_sucesso_cpfl: parseFloat((0.55 + Math.random() * 0.25).toFixed(3))
  };
});

// =====================================================================
// 5. DADOS PARA MAPA DE CALOR (HEATMAP)
// =====================================================================

export const heatmapData = comarcasGeolocalizacao.map(comarca => {
  const intensidade = Math.random();
  
  return {
    lat: comarca.lat,
    lon: comarca.lon,
    comarca: comarca.nome,
    intensity: intensidade,
    processos: Math.floor(intensidade * 150),
    valor_risco: Math.floor(intensidade * 5000000),
    nivel_risco: intensidade > 0.7 ? 'Alto' : intensidade > 0.4 ? 'Médio' : 'Baixo'
  };
});

// =====================================================================
// 6. ESTAÇÕES METEOROLÓGICAS INMET NO RS
// =====================================================================

export const estacoesINMET = [
  { codigo: 'A801', nome: 'Porto Alegre', lat: -30.0531, lon: -51.1714 },
  { codigo: 'A802', nome: 'Caxias do Sul', lat: -29.1703, lon: -51.1789 },
  { codigo: 'A803', nome: 'Santa Maria', lat: -29.7103, lon: -53.7169 },
  { codigo: 'A804', nome: 'Pelotas', lat: -31.7833, lon: -52.4111 },
  { codigo: 'A805', nome: 'Uruguaiana', lat: -29.7500, lon: -57.0500 },
  { codigo: 'A806', nome: 'Passo Fundo', lat: -28.2333, lon: -52.4167 },
  { codigo: 'A807', nome: 'Rio Grande', lat: -32.0333, lon: -52.1000 },
  { codigo: 'A808', nome: 'Bagé', lat: -31.3333, lon: -54.1000 }
];

// =====================================================================
// 7. FUNÇÃO PARA ENCONTRAR ESTAÇÃO MAIS PRÓXIMA
// =====================================================================

export function encontrarEstacaoMaisProxima(lat, lon) {
  let menorDistancia = Infinity;
  let estacaoMaisProxima = null;
  
  estacoesINMET.forEach(estacao => {
    const distancia = Math.sqrt(
      Math.pow(lat - estacao.lat, 2) + 
      Math.pow(lon - estacao.lon, 2)
    );
    
    if (distancia < menorDistancia) {
      menorDistancia = distancia;
      estacaoMaisProxima = estacao;
    }
  });
  
  return {
    ...estacaoMaisProxima,
    distancia_km: parseFloat((menorDistancia * 111).toFixed(2)) // Conversão aproximada
  };
}

// =====================================================================
// 8. EXEMPLO DE USO - CORRELACIONAR PROCESSO COM CLIMA
// =====================================================================

export function correlacionarProcessoComClima(numeroProcesso, dataEvento, comarca) {
  // Encontrar dados da comarca
  const dadosComarca = comarcasGeolocalizacao.find(c => c.comarca === comarca);
  
  if (!dadosComarca) {
    return null;
  }
  
  // Encontrar estação meteorológica mais próxima
  const estacao = encontrarEstacaoMaisProxima(dadosComarca.lat, dadosComarca.lon);
  
  // Simular dados meteorológicos do dia do evento
  const data = new Date(dataEvento);
  const dadosMeteo = gerarDadosMeteorologicos(dadosComarca, dataEvento, dataEvento)[0];
  
  return {
    numero_processo: numeroProcesso,
    data_evento: dataEvento,
    comarca: {
      nome: comarca,
      lat: dadosComarca.lat,
      lon: dadosComarca.lon,
      regiao: dadosComarca.regiao
    },
    estacao_meteorologica: estacao,
    dados_climaticos: dadosMeteo,
    classificacao_evento: dadosMeteo.weather_severity,
    probabilidade_relacao_clima: dadosMeteo.storm_intensity_index > 5 ? 'Alta' : 
                                  dadosMeteo.storm_intensity_index > 2 ? 'Média' : 'Baixa'
  };
}

// =====================================================================
// EXPORTAR TUDO
// =====================================================================

export default {
  comarcasGeolocalizacao,
  dadosMeteorologicosSimulados,
  eventosClimaticosExtremos,
  correlacaoClimaProcessos,
  heatmapData,
  estacoesINMET,
  encontrarEstacaoMaisProxima,
  correlacionarProcessoComClima
};

console.log('✅ Datasets meteorológicos e geolocalização criados com sucesso!');
console.log(`📍 ${comarcasGeolocalizacao.length} comarcas mapeadas`);
console.log(`🌦️ ${dadosMeteorologicosSimulados.length} comarcas com dados meteorológicos`);
console.log(`⚡ ${eventosClimaticosExtremos.length} eventos extremos registrados`);
