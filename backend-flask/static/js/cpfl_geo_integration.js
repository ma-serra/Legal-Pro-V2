// =====================================================================
// INTEGRAÇÃO COMPLETA DOS DADOS METEOROLÓGICOS CPFL
// Utiliza os dados reais do arquivo cpfl_weather_geolocation_datasets
// =====================================================================

import {
    comarcasGeolocalizacao,
    dadosMeteorologicosSimulados,
    eventosClimaticosExtremos,
    correlacaoClimaProcessos,
    heatmapData,
    estacoesINMET,
    encontrarEstacaoMaisProxima,
    correlacionarProcessoComClima
} from './cpfl_weather_data.js';

// Tornar dados disponíveis globalmente para uso no template
window.CPFLWeatherData = {
    comarcas: comarcasGeolocalizacao,
    dadosMeteorologicos: dadosMeteorologicosSimulados,
    eventosExtremos: eventosClimaticosExtremos,
    correlacaoProcessos: correlacaoClimaProcessos,
    heatmap: heatmapData,
    estacoes: estacoesINMET,
    encontrarEstacaoProxima: encontrarEstacaoMaisProxima,
    correlacionarProcesso: correlacionarProcessoComClima
};

// Função para inicializar mapa com todas as comarcas
window.inicializarMapaComarcas = function(mapElement) {
    if (typeof L === 'undefined') {
        console.error('Leaflet não está carregado');
        return null;
    }
    
    // Centro do RS
    const map = L.map(mapElement).setView([-29.6842, -53.8069], 7);
    
    // Adicionar camada base
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap'
    }).addTo(map);
    
    // Adicionar marcadores para cada comarca
    comarcasGeolocalizacao.forEach(comarca => {
        const correlacao = correlacaoClimaProcessos.find(c => c.comarca === comarca.comarca);
        const totalProcessos = correlacao ? correlacao.total_processos : 0;
        const valorMedio = correlacao ? correlacao.valor_medio : 0;
        
        // Determinar cor do marcador baseado no número de processos
        let markerColor = totalProcessos > 100 ? 'red' : 
                         totalProcessos > 50 ? 'orange' : 'green';
        
        const marker = L.circleMarker([comarca.lat, comarca.lon], {
            radius: Math.sqrt(totalProcessos) * 2,
            fillColor: markerColor,
            color: '#fff',
            weight: 1,
            opacity: 1,
            fillOpacity: 0.6
        });
        
        marker.bindPopup(`
            <div style="color: #000; font-family: Arial;">
                <h6 style="margin: 0 0 8px 0; color: #003366;"><strong>${comarca.comarca}</strong></h6>
                <p style="margin: 4px 0; font-size: 0.9rem;"><strong>Região:</strong> ${comarca.regiao}</p>
                <p style="margin: 4px 0; font-size: 0.9rem;"><strong>População:</strong> ${comarca.populacao.toLocaleString('pt-BR')}</p>
                <p style="margin: 4px 0; font-size: 0.9rem;"><strong>Processos:</strong> ${totalProcessos}</p>
                <p style="margin: 4px 0; font-size: 0.9rem;"><strong>Valor Médio:</strong> R$ ${valorMedio.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</p>
                <p style="margin: 4px 0; font-size: 0.9rem;"><strong>Coordenadas:</strong> ${comarca.lat.toFixed(4)}, ${comarca.lon.toFixed(4)}</p>
            </div>
        `);
        
        marker.addTo(map);
    });
    
    // Adicionar estações INMET
    estacoesINMET.forEach(estacao => {
        const marker = L.marker([estacao.lat, estacao.lon], {
            icon: L.divIcon({
                className: 'estacao-inmet-marker',
                html: '<i class="fas fa-broadcast-tower" style="color: #0089CF; font-size: 20px;"></i>'
            })
        });
        
        marker.bindPopup(`
            <div style="color: #000;">
                <h6 style="color: #003366;"><strong>Estação INMET</strong></h6>
                <p style="margin: 4px 0;"><strong>Código:</strong> ${estacao.codigo}</p>
                <p style="margin: 4px 0;"><strong>Nome:</strong> ${estacao.nome}</p>
            </div>
        `);
        
        marker.addTo(map);
    });
    
    return map;
};

// Função para obter eventos climáticos extremos
window.obterEventosExtremos = function() {
    return eventosClimaticosExtremos;
};

// Função para correlacionar processo específico
window.buscarCorrelacaoProcesso = function(numeroProcesso, dataEvento, comarca) {
    return correlacionarProcessoComClima(numeroProcesso, dataEvento, comarca);
};

// Função para obter dados de heatmap
window.obterDadosHeatmap = function() {
    return heatmapData;
};

// Função para encontrar comarca por nome
window.buscarComarca = function(nomeComarca) {
    return comarcasGeolocalizacao.find(c => c.comarca === nomeComarca);
};

// Função para obter estatísticas por região
window.obterEstatisticasPorRegiao = function() {
    const estatisticas = {};
    
    comarcasGeolocalizacao.forEach(comarca => {
        if (!estatisticas[comarca.regiao]) {
            estatisticas[comarca.regiao] = {
                regiao: comarca.regiao,
                total_comarcas: 0,
                populacao_total: 0,
                total_processos: 0,
                comarcas: []
            };
        }
        
        const correlacao = correlacaoClimaProcessos.find(c => c.comarca === comarca.comarca);
        const totalProcessos = correlacao ? correlacao.total_processos : 0;
        
        estatisticas[comarca.regiao].total_comarcas++;
        estatisticas[comarca.regiao].populacao_total += comarca.populacao;
        estatisticas[comarca.regiao].total_processos += totalProcessos;
        estatisticas[comarca.regiao].comarcas.push(comarca.comarca);
    });
    
    return Object.values(estatisticas);
};

console.log('✅ Integração CPFL Weather Data carregada');
console.log(`📍 ${comarcasGeolocalizacao.length} comarcas disponíveis`);
console.log(`⚡ ${eventosClimaticosExtremos.length} eventos extremos registrados`);
console.log(`🌡️ ${estacoesINMET.length} estações INMET mapeadas`);
