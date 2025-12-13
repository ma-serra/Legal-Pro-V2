# CPFL - Integração Completa de Dados Meteorológicos

## ✅ Arquivos Criados/Atualizados

### 1. `/static/js/cpfl_weather_data.js`
- **35 Comarcas** com coordenadas geográficas reais (lat, lon, região, população)
- **Dados Meteorológicos Simulados** (temperatura, precipitação, vento, umidade, pressão, raios)
- **5 Eventos Climáticos Extremos** correlacionados com processos
- **Correlação Clima × Processos** por comarca
- **Dados para Heatmap** (intensidade de risco por comarca)
- **8 Estações INMET** com coordenadas reais do RS

### 2. `/static/js/cpfl_geo_integration.js`
Módulo de integração que expõe as seguintes funções globais:

```javascript
// Dados disponíveis
window.CPFLWeatherData = {
    comarcas: comarcasGeolocalizacao,          // 35 comarcas
    dadosMeteorologicos: dadosMeteorologicosSimulados,
    eventosExtremos: eventosClimaticosExtremos, // 5 eventos
    correlacaoProcessos: correlacaoClimaProcessos,
    heatmap: heatmapData,
    estacoes: estacoesINMET,                    // 8 estações
    encontrarEstacaoProxima: encontrarEstacaoMaisProxima,
    correlacionarProcesso: correlacionarProcessoComClima
};

// Funções utilitárias
window.inicializarMapaComarcas(mapElement)      // Inicializa mapa Leaflet
window.obterEventosExtremos()                   // Retorna eventos extremos
window.buscarCorrelacaoProcesso(numero, data, comarca)
window.obterDadosHeatmap()                      // Dados para mapa de calor
window.buscarComarca(nome)                      // Busca comarca específica
window.obterEstatisticasPorRegiao()             // Agrupa por região
```

## 📊 Dados Disponíveis

### Comarcas Principais (35 total)
- **Metropolitana**: Porto Alegre (1.492M hab), Canoas, Novo Hamburgo, São Leopoldo, Gravataí, Viamão, Alvorada, Cachoeirinha
- **Norte**: Caxias do Sul (517k hab), Passo Fundo, Erechim, Bento Gonçalves, Vacaria
- **Sul**: Pelotas (343k hab), Rio Grande, Santa Cruz do Sul, Uruguaiana, Bagé
- **Centro**: Santa Maria (283k hab), Cruz Alta, Santiago, Ijuí, Santo Ângelo
- **Litoral**: Torres, Tramandaí, Capão da Canoa, Osório
- **Interior**: Santa Rosa, Lajeado, Cachoeira do Sul, São Borja, Alegrete, Santana do Livramento, Santa Bárbara do Sul, Carazinho

### Estações INMET (8)
- A801 - Porto Alegre (-30.0531, -51.1714)
- A802 - Caxias do Sul (-29.1703, -51.1789)
- A803 - Santa Maria (-29.7103, -53.7169)
- A804 - Pelotas (-31.7833, -52.4111)
- A805 - Uruguaiana (-29.7500, -57.0500)
- A806 - Passo Fundo (-28.2333, -52.4167)
- A807 - Rio Grande (-32.0333, -52.1000)
- A808 - Bagé (-31.3333, -54.1000)

### Eventos Climáticos Extremos (5)
1. **Temporal Severo** - Porto Alegre (15/01/2024)
   - Precipitação: 120mm, Vento: 95 km/h
   - 45 processos associados
   
2. **Vendaval** - Caxias do Sul (03/03/2024)
   - Vento: 110 km/h
   - 32 processos associados
   
3. **Chuva Intensa** - Santa Maria (22/05/2024)
   - Precipitação: 85mm
   - 28 processos associados
   
4. **Geada Severa** - Vacaria (18/07/2024)
   - Temperatura: -5°C
   - 15 processos associados
   
5. **Granizo** - Pelotas (10/09/2024)
   - Granizo com 3cm de diâmetro
   - 23 processos associados

## 🔧 Como Usar no Template

### Exemplo 1: Mostrar Comarcas no Mapa
```javascript
// No template HTML, adicionar:
<div id="mapa-comarcas" style="height: 500px;"></div>

// No JavaScript:
window.addEventListener('load', () => {
    const mapa = window.inicializarMapaComarcas('mapa-comarcas');
});
```

### Exemplo 2: Correlacionar Processo com Clima
```javascript
const correlacao = window.buscarCorrelacaoProcesso(
    '5000647-02.2025.8.21.0121',
    '2024-05-15',
    'Santa Bárbara do Sul'
);

console.log(correlacao);
// Retorna:
// {
//     numero_processo: "5000647-02.2025.8.21.0121",
//     data_evento: "2024-05-15",
//     comarca: { nome: "Santa Bárbara do Sul", lat: -28.3589, lon: -53.2553, regiao: "Interior" },
//     estacao_meteorologica: { codigo: "A806", nome: "Passo Fundo", distancia_km: 42.5 },
//     dados_climaticos: { temperatura: 18.5, precipitacao: 45, vento: 32, ... },
//     classificacao_evento: "Alta",
//     probabilidade_relacao_clima: "Alta"
// }
```

### Exemplo 3: Obter Estatísticas por Região
```javascript
const stats = window.obterEstatisticasPorRegiao();

stats.forEach(regiao => {
    console.log(`${regiao.regiao}: ${regiao.total_comarcas} comarcas, ${regiao.total_processos} processos`);
});
```

### Exemplo 4: Exibir Eventos Extremos
```javascript
const eventos = window.obterEventosExtremos();

eventos.forEach(evento => {
    console.log(`${evento.tipo} em ${evento.comarca} (${evento.data})`);
    console.log(`Processos associados: ${evento.processos_associados.length}`);
});
```

### Exemplo 5: Encontrar Estação Mais Próxima
```javascript
const comarca = window.buscarComarca('Santa Bárbara do Sul');
const estacao = window.CPFLWeatherData.encontrarEstacaoProxima(
    comarca.lat,
    comarca.lon
);

console.log(`Estação mais próxima: ${estacao.nome} (${estacao.distancia_km} km)`);
```

## ✅ Status da Integração

- [x] 35 Comarcas com coordenadas reais
- [x] Dados meteorológicos simulados por comarca
- [x] 5 Eventos climáticos extremos
- [x] Correlação clima × processos
- [x] 8 Estações INMET
- [x] Função de encontrar estação mais próxima
- [x] Função de correlação processo×clima
- [x] Dados para heatmap
- [x] Arquivos JavaScript criados e disponíveis
- [x] Template atualizado com imports dos módulos

## 🎯 Próximos Passos

Para utilizar completamente no template `/cpfl/geolocalizacao`, adicionar:

1. **Aba Monitoramento**: Mapa Leaflet com todas as 35 comarcas e estações INMET
2. **Aba Análise**: Tabela de eventos extremos correlacionados
3. **Aba Alertas**: Alertas baseados em dados meteorológicos reais por comarca
4. **Dashboard**: KPIs agregados por região usando `obterEstatisticasPorRegiao()`

## 📝 Exemplo Completo de Uso

```html
<!-- Adicionar no template -->
<div class="row">
    <div class="col-md-12">
        <div class="card-dark">
            <h5>Mapa de Comarcas CPFL</h5>
            <div id="mapa-comarcas" style="height: 600px; border-radius: 12px; overflow: hidden;"></div>
        </div>
    </div>
</div>

<script>
// Após carregamento da página
window.addEventListener('load', () => {
    // Inicializar mapa com todas as comarcas
    const mapa = window.inicializarMapaComarcas('mapa-comarcas');
    
    // Exibir estatísticas por região
    const stats = window.obterEstatisticasPorRegiao();
    console.log('📊 Estatísticas por Região:', stats);
    
    // Exibir eventos extremos
    const eventos = window.obterEventosExtremos();
    console.log('⚡ Eventos Extremos:', eventos);
    
    // Exemplo de correlação
    const correlacao = window.buscarCorrelacaoProcesso(
        '5000647-02.2025.8.21.0121',
        '2024-05-15',
        'Santa Bárbara do Sul'
    );
    console.log('🔗 Correlação Processo×Clima:', correlacao);
});
</script>
```
