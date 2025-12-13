// Dados jurídicos completos do Brasil - Estados, Comarcas e Varas
const dadosJuridicos = {
    estados: [
        {codigo: 'SP', nome: 'São Paulo', regiao: 'Sudeste'},
        {codigo: 'RJ', nome: 'Rio de Janeiro', regiao: 'Sudeste'},
        {codigo: 'MG', nome: 'Minas Gerais', regiao: 'Sudeste'},
        {codigo: 'ES', nome: 'Espírito Santo', regiao: 'Sudeste'},
        {codigo: 'RS', nome: 'Rio Grande do Sul', regiao: 'Sul'},
        {codigo: 'PR', nome: 'Paraná', regiao: 'Sul'},
        {codigo: 'SC', nome: 'Santa Catarina', regiao: 'Sul'},
        {codigo: 'DF', nome: 'Distrito Federal', regiao: 'Centro-Oeste'},
        {codigo: 'GO', nome: 'Goiás', regiao: 'Centro-Oeste'},
        {codigo: 'MT', nome: 'Mato Grosso', regiao: 'Centro-Oeste'},
        {codigo: 'MS', nome: 'Mato Grosso do Sul', regiao: 'Centro-Oeste'},
        {codigo: 'BA', nome: 'Bahia', regiao: 'Nordeste'},
        {codigo: 'PE', nome: 'Pernambuco', regiao: 'Nordeste'},
        {codigo: 'CE', nome: 'Ceará', regiao: 'Nordeste'},
        {codigo: 'MA', nome: 'Maranhão', regiao: 'Nordeste'},
        {codigo: 'PB', nome: 'Paraíba', regiao: 'Nordeste'},
        {codigo: 'PI', nome: 'Piauí', regiao: 'Nordeste'},
        {codigo: 'AL', nome: 'Alagoas', regiao: 'Nordeste'},
        {codigo: 'SE', nome: 'Sergipe', regiao: 'Nordeste'},
        {codigo: 'RN', nome: 'Rio Grande do Norte', regiao: 'Nordeste'},
        {codigo: 'AM', nome: 'Amazonas', regiao: 'Norte'},
        {codigo: 'PA', nome: 'Pará', regiao: 'Norte'},
        {codigo: 'AC', nome: 'Acre', regiao: 'Norte'},
        {codigo: 'RO', nome: 'Rondônia', regiao: 'Norte'},
        {codigo: 'RR', nome: 'Roraima', regiao: 'Norte'},
        {codigo: 'AP', nome: 'Amapá', regiao: 'Norte'},
        {codigo: 'TO', nome: 'Tocantins', regiao: 'Norte'}
    ],

    comarcas: {
        'SP': [
            'São Paulo', 'Guarulhos', 'Santo André', 'São Bernardo do Campo', 'Osasco', 'Campinas',
            'Ribeirão Preto', 'Sorocaba', 'Santos', 'São José dos Campos', 'Bauru', 'Socorro',
            'Piracicaba', 'Jundiaí', 'Taubaté', 'Franca', 'Araraquara', 'Presidente Prudente',
            'Marília', 'Americana', 'Araçatuba', 'Assis', 'Barretos', 'Botucatu', 'Bragança Paulista',
            'Caraguatatuba', 'Catanduva', 'Cruzeiro', 'Dracena', 'Fernandópolis', 'Guaratinguetá',
            'Itapetininga', 'Itapeva', 'Jaú', 'Limeira', 'Lins', 'Matão', 'Mococa', 'Ourinhos',
            'Registro', 'Rio Claro', 'São Carlos', 'São João da Boa Vista', 'Tupã', 'Votuporanga'
        ],
        'RJ': [
            'Rio de Janeiro', 'Niterói', 'Duque de Caxias', 'São Gonçalo', 'Nova Iguaçu', 'Belford Roxo',
            'Campos dos Goytacazes', 'Volta Redonda', 'Petrópolis', 'Nova Friburgo', 'Angra dos Reis',
            'Barra Mansa', 'Cabo Frio', 'Itaperuna', 'Macaé', 'Magé', 'Maricá', 'Nilópolis',
            'Resende', 'Rio das Ostras', 'Teresópolis'
        ],
        'MG': [
            'Belo Horizonte', 'Contagem', 'Betim', 'Ribeirão das Neves', 'Santa Luzia', 'Juiz de Fora',
            'Uberlândia', 'Montes Claros', 'Uberaba', 'Divinópolis', 'Ipatinga', 'Governador Valadares',
            'Poços de Caldas', 'Varginha', 'Patos de Minas', 'Barbacena', 'Pouso Alegre', 'Teófilo Otoni',
            'Sete Lagoas', 'Conselheiro Lafaiete', 'Itajubá'
        ],
        'ES': [
            'Vitória', 'Vila Velha', 'Serra', 'Cariacica', 'Viana', 'Cachoeiro de Itapemirim',
            'Linhares', 'Colatina', 'São Mateus', 'Aracruz', 'Guarapari', 'Nova Venécia',
            'Alegre', 'Afonso Cláudio', 'Baixo Guandu', 'Barra de São Francisco', 'Conceição da Barra',
            'Domingos Martins', 'Ecoporanga', 'Guaçuí', 'Iúna', 'Itapemirim', 'Marataízes',
            'Montanha', 'Piúma', 'Santa Teresa', 'São Gabriel da Palha', 'Venda Nova do Imigrante'
        ],
        'DF': [
            'Brasília', 'Taguatinga', 'Ceilândia', 'Águas Claras', 'Gama', 'Planaltina',
            'Sobradinho', 'Brazlândia', 'Santa Maria', 'São Sebastião', 'Paranoá',
            'Núcleo Bandeirante', 'Guará', 'Samambaia', 'Recanto das Emas', 'Riacho Fundo'
        ],
        'RS': [
            'Porto Alegre', 'Canoas', 'Novo Hamburgo', 'São Leopoldo', 'Viamão', 'Alvorada',
            'Cachoeirinha', 'Gravataí', 'Sapucaia do Sul', 'Caxias do Sul', 'Pelotas',
            'Santa Maria', 'Passo Fundo', 'Rio Grande', 'Bagé', 'Uruguaiana', 'Santa Cruz do Sul',
            'Lajeado', 'Bento Gonçalves', 'Ijuí', 'Cruz Alta', 'Santana do Livramento', 'Cachoeira do Sul'
        ],
        'PR': [
            'Curitiba', 'Londrina', 'Maringá', 'Ponta Grossa', 'Cascavel', 'Foz do Iguaçu',
            'São José dos Pinhais', 'Colombo', 'Araucária', 'Paranaguá', 'Guarapuava',
            'Umuarama', 'Toledo', 'Apucarana', 'Arapongas', 'Campo Mourão'
        ],
        'SC': [
            'Florianópolis', 'Joinville', 'Blumenau', 'Chapecó', 'Criciúma', 'Itajaí',
            'São José', 'Lages', 'Tubarão', 'Balneário Camboriú', 'Caçador', 'Concórdia',
            'Brusque', 'São Bento do Sul', 'Videira', 'Joaçaba'
        ]
    },

    varas: {
        // São Paulo
        'São Paulo': [
            '1ª Vara Cível São Paulo SP', '2ª Vara Cível São Paulo SP', '3ª Vara Cível São Paulo SP',
            '4ª Vara Cível São Paulo SP', '5ª Vara Cível São Paulo SP', '6ª Vara Cível São Paulo SP',
            '7ª Vara Cível São Paulo SP', '8ª Vara Cível São Paulo SP', '9ª Vara Cível São Paulo SP',
            '10ª Vara Cível São Paulo SP', '11ª Vara Cível São Paulo SP', '12ª Vara Cível São Paulo SP',
            '13ª Vara Cível São Paulo SP', '14ª Vara Cível São Paulo SP', '15ª Vara Cível São Paulo SP',
            '16ª Vara Cível São Paulo SP', '17ª Vara Cível São Paulo SP', '18ª Vara Cível São Paulo SP',
            '19ª Vara Cível São Paulo SP', '20ª Vara Cível São Paulo SP', '21ª Vara Cível São Paulo SP',
            '22ª Vara Cível São Paulo SP', '23ª Vara Cível São Paulo SP', '24ª Vara Cível São Paulo SP',
            '25ª Vara Cível São Paulo SP', '26ª Vara Cível São Paulo SP', '27ª Vara Cível São Paulo SP',
            '28ª Vara Cível São Paulo SP', '29ª Vara Cível São Paulo SP', '30ª Vara Cível São Paulo SP',
            '31ª Vara Cível São Paulo SP', '32ª Vara Cível São Paulo SP', '33ª Vara Cível São Paulo SP',
            '34ª Vara Cível São Paulo SP', '35ª Vara Cível São Paulo SP', '36ª Vara Cível São Paulo SP',
            '37ª Vara Cível São Paulo SP', '38ª Vara Cível São Paulo SP', '39ª Vara Cível São Paulo SP',
            '40ª Vara Cível São Paulo SP', '41ª Vara Cível São Paulo SP', '42ª Vara Cível São Paulo SP'
        ],
        'Guarulhos': [
            '1ª Vara Cível Guarulhos SP', '2ª Vara Cível Guarulhos SP', '3ª Vara Cível Guarulhos SP',
            '4ª Vara Cível Guarulhos SP', '5ª Vara Cível Guarulhos SP', '6ª Vara Cível Guarulhos SP'
        ],
        'Santo André': [
            '1ª Vara Cível Santo André SP', '2ª Vara Cível Santo André SP', '3ª Vara Cível Santo André SP', '4ª Vara Cível Santo André SP'
        ],
        'São Bernardo do Campo': [
            '1ª Vara Cível São Bernardo do Campo SP', '2ª Vara Cível São Bernardo do Campo SP',
            '3ª Vara Cível São Bernardo do Campo SP', '4ª Vara Cível São Bernardo do Campo SP'
        ],
        'Osasco': [
            '1ª Vara Cível Osasco SP', '2ª Vara Cível Osasco SP', '3ª Vara Cível Osasco SP'
        ],
        'Campinas': [
            '1ª Vara Cível Campinas SP', '2ª Vara Cível Campinas SP', '3ª Vara Cível Campinas SP',
            '4ª Vara Cível Campinas SP', '5ª Vara Cível Campinas SP', '6ª Vara Cível Campinas SP', '7ª Vara Cível Campinas SP'
        ],
        'Ribeirão Preto': [
            '1ª Vara Cível Ribeirão Preto SP', '2ª Vara Cível Ribeirão Preto SP', '3ª Vara Cível Ribeirão Preto SP'
        ],
        'Sorocaba': [
            '1ª Vara Cível Sorocaba SP', '2ª Vara Cível Sorocaba SP', '3ª Vara Cível Sorocaba SP'
        ],
        'Santos': [
            '1ª Vara Cível Santos SP', '2ª Vara Cível Santos SP', '3ª Vara Cível Santos SP'
        ],

        // Rio de Janeiro
        'Rio de Janeiro': [
            '1ª Vara Cível Rio de Janeiro RJ', '2ª Vara Cível Rio de Janeiro RJ', '3ª Vara Cível Rio de Janeiro RJ',
            '4ª Vara Cível Rio de Janeiro RJ', '5ª Vara Cível Rio de Janeiro RJ', '6ª Vara Cível Rio de Janeiro RJ',
            '7ª Vara Cível Rio de Janeiro RJ', '8ª Vara Cível Rio de Janeiro RJ', '9ª Vara Cível Rio de Janeiro RJ',
            '10ª Vara Cível Rio de Janeiro RJ', '11ª Vara Cível Rio de Janeiro RJ', '12ª Vara Cível Rio de Janeiro RJ',
            '13ª Vara Cível Rio de Janeiro RJ', '14ª Vara Cível Rio de Janeiro RJ', '15ª Vara Cível Rio de Janeiro RJ',
            '16ª Vara Cível Rio de Janeiro RJ', '17ª Vara Cível Rio de Janeiro RJ', '18ª Vara Cível Rio de Janeiro RJ',
            '19ª Vara Cível Rio de Janeiro RJ', '20ª Vara Cível Rio de Janeiro RJ', '21ª Vara Cível Rio de Janeiro RJ',
            '22ª Vara Cível Rio de Janeiro RJ', '23ª Vara Cível Rio de Janeiro RJ', '24ª Vara Cível Rio de Janeiro RJ',
            '25ª Vara Cível Rio de Janeiro RJ', '26ª Vara Cível Rio de Janeiro RJ', '27ª Vara Cível Rio de Janeiro RJ',
            '28ª Vara Cível Rio de Janeiro RJ', '29ª Vara Cível Rio de Janeiro RJ', '30ª Vara Cível Rio de Janeiro RJ',
            '31ª Vara Cível Rio de Janeiro RJ', '32ª Vara Cível Rio de Janeiro RJ', '33ª Vara Cível Rio de Janeiro RJ',
            '34ª Vara Cível Rio de Janeiro RJ', '35ª Vara Cível Rio de Janeiro RJ', '36ª Vara Cível Rio de Janeiro RJ',
            '37ª Vara Cível Rio de Janeiro RJ', '38ª Vara Cível Rio de Janeiro RJ', '39ª Vara Cível Rio de Janeiro RJ', '40ª Vara Cível Rio de Janeiro RJ'
        ],
        'Niterói': [
            '1ª Vara Cível Niterói RJ', '2ª Vara Cível Niterói RJ', '3ª Vara Cível Niterói RJ', '4ª Vara Cível Niterói RJ'
        ],
        'Duque de Caxias': [
            '1ª Vara Cível Duque de Caxias RJ', '2ª Vara Cível Duque de Caxias RJ', '3ª Vara Cível Duque de Caxias RJ'
        ],

        // Minas Gerais
        'Belo Horizonte': [
            '1ª Vara Cível Belo Horizonte MG', '2ª Vara Cível Belo Horizonte MG', '3ª Vara Cível Belo Horizonte MG',
            '4ª Vara Cível Belo Horizonte MG', '5ª Vara Cível Belo Horizonte MG', '6ª Vara Cível Belo Horizonte MG',
            '7ª Vara Cível Belo Horizonte MG', '8ª Vara Cível Belo Horizonte MG', '9ª Vara Cível Belo Horizonte MG',
            '10ª Vara Cível Belo Horizonte MG', '11ª Vara Cível Belo Horizonte MG', '12ª Vara Cível Belo Horizonte MG',
            '13ª Vara Cível Belo Horizonte MG', '14ª Vara Cível Belo Horizonte MG', '15ª Vara Cível Belo Horizonte MG',
            '16ª Vara Cível Belo Horizonte MG', '17ª Vara Cível Belo Horizonte MG', '18ª Vara Cível Belo Horizonte MG',
            '19ª Vara Cível Belo Horizonte MG', '20ª Vara Cível Belo Horizonte MG', '21ª Vara Cível Belo Horizonte MG',
            '22ª Vara Cível Belo Horizonte MG', '23ª Vara Cível Belo Horizonte MG', '24ª Vara Cível Belo Horizonte MG',
            '25ª Vara Cível Belo Horizonte MG', '26ª Vara Cível Belo Horizonte MG', '27ª Vara Cível Belo Horizonte MG',
            '28ª Vara Cível Belo Horizonte MG', '29ª Vara Cível Belo Horizonte MG', '30ª Vara Cível Belo Horizonte MG'
        ],
        'Contagem': [
            '1ª Vara Cível Contagem MG', '2ª Vara Cível Contagem MG', '3ª Vara Cível Contagem MG', '4ª Vara Cível Contagem MG'
        ],

        // Espírito Santo
        'Vitória': [
            '1ª Vara Cível Vitória ES', '2ª Vara Cível Vitória ES', '3ª Vara Cível Vitória ES',
            '4ª Vara Cível Vitória ES', '5ª Vara Cível Vitória ES', '6ª Vara Cível Vitória ES',
            '7ª Vara Cível Vitória ES', '8ª Vara Cível Vitória ES', '9ª Vara Cível Vitória ES'
        ],
        'Vila Velha': [
            '1ª Vara Cível Vila Velha ES', '2ª Vara Cível Vila Velha ES', '3ª Vara Cível Vila Velha ES'
        ],

        // Distrito Federal
        'Brasília': [
            '1ª Vara Cível Brasília DF', '2ª Vara Cível Brasília DF', '3ª Vara Cível Brasília DF',
            '4ª Vara Cível Brasília DF', '5ª Vara Cível Brasília DF', '6ª Vara Cível Brasília DF',
            '7ª Vara Cível Brasília DF', '8ª Vara Cível Brasília DF', '9ª Vara Cível Brasília DF',
            '10ª Vara Cível Brasília DF', '11ª Vara Cível Brasília DF', '12ª Vara Cível Brasília DF',
            '13ª Vara Cível Brasília DF', '14ª Vara Cível Brasília DF', '15ª Vara Cível Brasília DF',
            '16ª Vara Cível Brasília DF', '17ª Vara Cível Brasília DF', '18ª Vara Cível Brasília DF',
            '19ª Vara Cível Brasília DF', '20ª Vara Cível Brasília DF'
        ],
        'Taguatinga': [
            '1ª Vara Cível Taguatinga DF', '2ª Vara Cível Taguatinga DF', '3ª Vara Cível Taguatinga DF'
        ],

        // Rio Grande do Sul
        'Porto Alegre': [
            '1ª Vara Cível Porto Alegre RS', '2ª Vara Cível Porto Alegre RS', '3ª Vara Cível Porto Alegre RS',
            '4ª Vara Cível Porto Alegre RS', '5ª Vara Cível Porto Alegre RS', '6ª Vara Cível Porto Alegre RS',
            '7ª Vara Cível Porto Alegre RS', '8ª Vara Cível Porto Alegre RS', '9ª Vara Cível Porto Alegre RS',
            '10ª Vara Cível Porto Alegre RS', '11ª Vara Cível Porto Alegre RS', '12ª Vara Cível Porto Alegre RS',
            '13ª Vara Cível Porto Alegre RS', '14ª Vara Cível Porto Alegre RS', '15ª Vara Cível Porto Alegre RS',
            '16ª Vara Cível Porto Alegre RS', '17ª Vara Cível Porto Alegre RS', '18ª Vara Cível Porto Alegre RS',
            '19ª Vara Cível Porto Alegre RS', '20ª Vara Cível Porto Alegre RS'
        ],

        // Paraná
        'Curitiba': [
            '1ª Vara Cível Curitiba PR', '2ª Vara Cível Curitiba PR', '3ª Vara Cível Curitiba PR',
            '4ª Vara Cível Curitiba PR', '5ª Vara Cível Curitiba PR', '6ª Vara Cível Curitiba PR',
            '7ª Vara Cível Curitiba PR', '8ª Vara Cível Curitiba PR', '9ª Vara Cível Curitiba PR',
            '10ª Vara Cível Curitiba PR', '11ª Vara Cível Curitiba PR', '12ª Vara Cível Curitiba PR',
            '13ª Vara Cível Curitiba PR', '14ª Vara Cível Curitiba PR', '15ª Vara Cível Curitiba PR',
            '16ª Vara Cível Curitiba PR', '17ª Vara Cível Curitiba PR', '18ª Vara Cível Curitiba PR',
            '19ª Vara Cível Curitiba PR', '20ª Vara Cível Curitiba PR'
        ],

        // Santa Catarina
        'Florianópolis': [
            '1ª Vara Cível Florianópolis SC', '2ª Vara Cível Florianópolis SC', '3ª Vara Cível Florianópolis SC',
            '4ª Vara Cível Florianópolis SC', '5ª Vara Cível Florianópolis SC', '6ª Vara Cível Florianópolis SC'
        ]
    }
};

// Função para obter comarcas por estado
function obterComarcasPorEstado(uf) {
    return dadosJuridicos.comarcas[uf] || [];
}

// Função para obter varas por comarca
function obterVarasPorComarca(comarca) {
    return dadosJuridicos.varas[comarca] || [];
}

// Função para obter estado por comarca
function obterEstadoPorComarca(comarca) {
    for (const [uf, comarcas] of Object.entries(dadosJuridicos.comarcas)) {
        if (comarcas.includes(comarca)) {
            return uf;
        }
    }
    return null;
}