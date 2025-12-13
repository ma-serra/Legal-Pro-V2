"""
Módulo de Geração de Dados Sintéticos para Sistema Jurídico
Alternativa ao SDV com foco em dados jurídicos brasileiros realistas
"""

import random
import datetime
from typing import List, Dict, Any
import json
import re


class LegalSyntheticDataGenerator:
    """Gerador de dados sintéticos para processos jurídicos brasileiros"""
    
    def __init__(self):
        self.setup_data_pools()
    
    def setup_data_pools(self):
        """Configura pools de dados para geração sintética"""
        
        # Nomes realistas
        self.nomes_masculinos = [
            "Carlos", "José", "João", "Antonio", "Francisco", "Paulo", "Rafael", "Lucas", 
            "Pedro", "Gabriel", "Daniel", "Marcos", "Bruno", "Eduardo", "Roberto",
            "Felipe", "Henrique", "Alexandre", "Gustavo", "Diego", "Leonardo", "Rodrigo"
        ]
        
        self.nomes_femininos = [
            "Maria", "Ana", "Francisca", "Antonia", "Adriana", "Juliana", "Marcia", 
            "Fernanda", "Patricia", "Aline", "Sandra", "Monica", "Debora", "Andrea",
            "Carla", "Camila", "Cristina", "Luciana", "Renata", "Simone", "Vanessa"
        ]
        
        self.sobrenomes = [
            "Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves",
            "Pereira", "Lima", "Gomes", "Costa", "Ribeiro", "Martins", "Carvalho",
            "Almeida", "Lopes", "Soares", "Fernandes", "Vieira", "Barbosa", "Rocha",
            "Dias", "Monteiro", "Cardoso", "Reis", "Araújo", "Moreira", "Nascimento"
        ]
        
        # Comarcas e estados brasileiros - Foco em Sul, Sudeste e Centro-Oeste
        self.comarcas_estados = {
            # SUDESTE - Expandido
            "SP": ["São Paulo", "Campinas", "Santos", "Ribeirão Preto", "Sorocaba", "São José dos Campos", 
                   "Bauru", "Piracicaba", "Jundiaí", "São Bernardo do Campo", "Santo André", "Osasco", 
                   "Guarulhos", "Mogi das Cruzes", "Araraquara", "Franca", "Presidente Prudente", "Marília"],
            "RJ": ["Rio de Janeiro", "Niterói", "Petrópolis", "Nova Iguaçu", "Campos dos Goytacazes", 
                   "Duque de Caxias", "São Gonçalo", "Volta Redonda", "Magé", "Itaboraí", "Cabo Frio", 
                   "Angra dos Reis", "Resende", "Teresópolis", "Barra Mansa"],
            "MG": ["Belo Horizonte", "Uberlândia", "Contagem", "Juiz de Fora", "Betim", "Montes Claros", 
                   "Ribeirão das Neves", "Uberaba", "Governador Valadares", "Ipatinga", "Sete Lagoas", 
                   "Divinópolis", "Santa Luzia", "Ibirité", "Poços de Caldas", "Patos de Minas"],
            "ES": ["Vitória", "Serra", "Vila Velha", "Cariacica", "Linhares", "São Mateus", "Colatina", 
                   "Cachoeiro de Itapemirim", "Guarapari", "Viana", "Nova Venécia", "Aracruz"],
            
            # SUL - Expandido
            "RS": ["Porto Alegre", "Caxias do Sul", "Pelotas", "Canoas", "Santa Maria", "Gravataí", 
                   "Viamão", "Novo Hamburgo", "São Leopoldo", "Rio Grande", "Alvorada", "Passo Fundo", 
                   "Sapucaia do Sul", "Uruguaiana", "Santa Cruz do Sul", "Cachoeirinha", "Bagé"],
            "PR": ["Curitiba", "Londrina", "Maringá", "Ponta Grossa", "Cascavel", "São José dos Pinhais", 
                   "Foz do Iguaçu", "Colombo", "Guarapuava", "Paranaguá", "Araucária", "Toledo", 
                   "Apucarana", "Pinhais", "Campo Largo", "Arapongas", "Almirante Tamandaré"],
            "SC": ["Florianópolis", "Joinville", "Blumenau", "São José", "Criciúma", "Chapecó", 
                   "Itajaí", "Lages", "Jaraguá do Sul", "Palhoça", "Balneário Camboriú", "Brusque", 
                   "Tubarão", "São Bento do Sul", "Caçador", "Concórdia"],
            
            # CENTRO-OESTE - Expandido
            "GO": ["Goiânia", "Aparecida de Goiânia", "Anápolis", "Rio Verde", "Luziânia", "Águas Lindas de Goiás", 
                   "Valparaíso de Goiás", "Trindade", "Formosa", "Novo Gama", "Itumbiara", "Senador Canedo", 
                   "Catalão", "Jataí", "Planaltina", "Caldas Novas"],
            "MT": ["Cuiabá", "Várzea Grande", "Rondonópolis", "Sinop", "Tangará da Serra", "Cáceres", 
                   "Sorriso", "Lucas do Rio Verde", "Barra do Garças", "Primavera do Leste", "Alta Floresta", 
                   "Campo Grande", "Dourados", "Três Lagoas"],
            "MS": ["Campo Grande", "Dourados", "Três Lagoas", "Corumbá", "Ponta Porã", "Naviraí", 
                   "Nova Andradina", "Sidrolândia", "Maracaju", "Aquidauana", "Paranaíba", "Coxim"],
            "DF": ["Brasília", "Taguatinga", "Ceilândia", "Gama", "Guará", "Sobradinho", "Planaltina", 
                   "São Sebastião", "Recanto das Emas", "Samambaia", "Santa Maria", "Águas Claras"],
            
            # REMOVIDO: Estados Norte e Nordeste para concentrar em Sul, Sudeste e Centro-Oeste apenas
        }
        
        # Juízos especializados - Varas Judiciais por estado - Expandido
        self.juizos_por_estado = {
            "SP": [
                "1ª Vara Cível de São Paulo", "2ª Vara Cível de Campinas", "3ª Vara Cível de Santos",
                "4ª Vara Cível de Ribeirão Preto", "5ª Vara Cível de Sorocaba", "6ª Vara Cível de Bauru",
                "Vara de Família de São Paulo", "Vara de Família de Ribeirão Preto", "Vara de Família de Campinas",
                "1ª Vara do Trabalho de São Paulo", "2ª Vara do Trabalho de Campinas", "3ª Vara do Trabalho de Santos",
                "4ª Vara do Trabalho de Guarulhos", "5ª Vara do Trabalho de Osasco", "6ª Vara do Trabalho de Bauru",
                "1ª Vara Criminal de São Paulo", "2ª Vara Criminal de Sorocaba", "3ª Vara Criminal de Ribeirão Preto",
                "Vara da Fazenda Pública de São Paulo", "Vara de Execuções Fiscais de São Paulo",
                "Vara Empresarial de São Paulo", "JEC de São José dos Campos", "JEC de Jundiaí", "JEC de Piracicaba"
            ],
            "RJ": [
                "1ª Vara Cível do Rio de Janeiro", "2ª Vara Cível de Niterói", "3ª Vara Cível de Petrópolis",
                "4ª Vara Cível de Nova Iguaçu", "5ª Vara Cível de Duque de Caxias", "6ª Vara Cível de São Gonçalo",
                "Vara de Família do Rio de Janeiro", "Vara de Família de Niterói", "Vara de Família de Campos",
                "1ª Vara do Trabalho do Rio de Janeiro", "2ª Vara do Trabalho de Niterói", "3ª Vara do Trabalho de Volta Redonda",
                "1ª Vara Criminal do Rio de Janeiro", "2ª Vara Criminal de Niterói", "Vara da Fazenda Pública do Rio de Janeiro",
                "JEC de Nova Iguaçu", "JEC de Duque de Caxias", "JEC de Petrópolis"
            ],
            "MG": [
                "1ª Vara Cível de Belo Horizonte", "2ª Vara Cível de Uberlândia", "3ª Vara Cível de Contagem",
                "4ª Vara Cível de Juiz de Fora", "5ª Vara Cível de Montes Claros", "6ª Vara Cível de Uberaba",
                "Vara de Família de Belo Horizonte", "Vara de Família de Uberlândia", "Vara de Família de Juiz de Fora",
                "1ª Vara do Trabalho de Belo Horizonte", "2ª Vara do Trabalho de Juiz de Fora", "3ª Vara do Trabalho de Uberlândia",
                "1ª Vara Criminal de Belo Horizonte", "2ª Vara Criminal de Contagem", "Vara da Fazenda Pública de Belo Horizonte",
                "JEC de Ipatinga", "JEC de Governador Valadares", "JEC de Sete Lagoas"
            ],
            "RS": [
                "1ª Vara Cível de Porto Alegre", "2ª Vara Cível de Caxias do Sul", "3ª Vara Cível de Pelotas",
                "4ª Vara Cível de Canoas", "5ª Vara Cível de Santa Maria", "6ª Vara Cível de Novo Hamburgo",
                "Vara de Família de Porto Alegre", "Vara de Família de Caxias do Sul", "Vara de Família de Pelotas",
                "1ª Vara do Trabalho de Porto Alegre", "2ª Vara do Trabalho de Caxias do Sul", "3ª Vara do Trabalho de Rio Grande",
                "1ª Vara Criminal de Porto Alegre", "2ª Vara Criminal de Canoas", "Vara da Fazenda Pública de Porto Alegre",
                "JEC de Gravataí", "JEC de Viamão", "JEC de São Leopoldo"
            ],
            "PR": [
                "1ª Vara Cível de Curitiba", "2ª Vara Cível de Londrina", "3ª Vara Cível de Maringá",
                "4ª Vara Cível de Ponta Grossa", "5ª Vara Cível de Cascavel", "6ª Vara Cível de Foz do Iguaçu",
                "Vara de Família de Curitiba", "Vara de Família de Londrina", "Vara de Família de Maringá",
                "1ª Vara do Trabalho de Curitiba", "2ª Vara do Trabalho de Londrina", "3ª Vara do Trabalho de Maringá",
                "1ª Vara Criminal de Curitiba", "2ª Vara Criminal de Londrina", "Vara da Fazenda Pública de Curitiba",
                "JEC de São José dos Pinhais", "JEC de Colombo", "JEC de Guarapuava"
            ],
            "SC": [
                "1ª Vara Cível de Florianópolis", "2ª Vara Cível de Joinville", "3ª Vara Cível de Blumenau",
                "4ª Vara Cível de Chapecó", "5ª Vara Cível de Criciúma", "6ª Vara Cível de Itajaí",
                "Vara de Família de Florianópolis", "Vara de Família de Joinville", "Vara de Família de Blumenau",
                "1ª Vara do Trabalho de Florianópolis", "2ª Vara do Trabalho de Joinville", "3ª Vara do Trabalho de Chapecó",
                "1ª Vara Criminal de Florianópolis", "2ª Vara Criminal de Joinville", "Vara da Fazenda Pública de Florianópolis",
                "JEC de São José", "JEC de Lages", "JEC de Jaraguá do Sul"
            ],
            "GO": [
                "1ª Vara Cível de Goiânia", "2ª Vara Cível de Aparecida de Goiânia", "3ª Vara Cível de Anápolis",
                "4ª Vara Cível de Rio Verde", "5ª Vara Cível de Luziânia", "6ª Vara Cível de Catalão",
                "Vara de Família de Goiânia", "Vara de Família de Anápolis", "Vara de Família de Aparecida de Goiânia",
                "1ª Vara do Trabalho de Goiânia", "2ª Vara do Trabalho de Anápolis", "3ª Vara do Trabalho de Rio Verde",
                "1ª Vara Criminal de Goiânia", "2ª Vara Criminal de Anápolis", "Vara da Fazenda Pública de Goiânia",
                "JEC de Formosa", "JEC de Itumbiara", "JEC de Jataí"
            ],
            "MT": [
                "1ª Vara Cível de Cuiabá", "2ª Vara Cível de Várzea Grande", "3ª Vara Cível de Rondonópolis",
                "4ª Vara Cível de Sinop", "5ª Vara Cível de Tangará da Serra", "6ª Vara Cível de Cáceres",
                "Vara de Família de Cuiabá", "Vara de Família de Rondonópolis", "Vara de Família de Sinop",
                "1ª Vara do Trabalho de Cuiabá", "2ª Vara do Trabalho de Rondonópolis", "3ª Vara do Trabalho de Sinop",
                "1ª Vara Criminal de Cuiabá", "2ª Vara Criminal de Várzea Grande", "Vara da Fazenda Pública de Cuiabá",
                "JEC de Sorriso", "JEC de Lucas do Rio Verde", "JEC de Primavera do Leste"
            ],
            "MS": [
                "1ª Vara Cível de Campo Grande", "2ª Vara Cível de Dourados", "3ª Vara Cível de Três Lagoas",
                "4ª Vara Cível de Corumbá", "5ª Vara Cível de Ponta Porã", "6ª Vara Cível de Naviraí",
                "Vara de Família de Campo Grande", "Vara de Família de Dourados", "Vara de Família de Três Lagoas",
                "1ª Vara do Trabalho de Campo Grande", "2ª Vara do Trabalho de Dourados", "3ª Vara do Trabalho de Três Lagoas",
                "1ª Vara Criminal de Campo Grande", "2ª Vara Criminal de Dourados", "Vara da Fazenda Pública de Campo Grande",
                "JEC de Nova Andradina", "JEC de Aquidauana", "JEC de Sidrolândia"
            ],
            "DF": [
                "1ª Vara Cível de Brasília", "2ª Vara Cível de Taguatinga", "3ª Vara Cível de Ceilândia",
                "4ª Vara Cível do Gama", "5ª Vara Cível de Sobradinho", "6ª Vara Cível de Planaltina",
                "Vara de Família de Brasília", "Vara de Família de Taguatinga", "Vara de Família de Ceilândia",
                "1ª Vara do Trabalho de Brasília", "2ª Vara do Trabalho de Taguatinga", "3ª Vara do Trabalho de Ceilândia",
                "1ª Vara Criminal de Brasília", "2ª Vara Criminal de Taguatinga", "Vara da Fazenda Pública de Brasília",
                "JEC do Guará", "JEC de Samambaia", "JEC de Santa Maria"
            ],
            "ES": [
                "1ª Vara Cível de Vitória", "2ª Vara Cível de Serra", "3ª Vara Cível de Vila Velha",
                "4ª Vara Cível de Cariacica", "5ª Vara Cível de Linhares", "6ª Vara Cível de Cachoeiro de Itapemirim",
                "Vara de Família de Vitória", "Vara de Família de Serra", "Vara de Família de Vila Velha",
                "1ª Vara do Trabalho de Vitória", "2ª Vara do Trabalho de Serra", "3ª Vara do Trabalho de Linhares",
                "1ª Vara Criminal de Vitória", "2ª Vara Criminal de Vila Velha", "Vara da Fazenda Pública de Vitória",
                "JEC de Guarapari", "JEC de São Mateus", "JEC de Colatina"
            ],
            "default": [
                "1ª Vara Cível", "2ª Vara Cível", "3ª Vara Cível", "Vara de Família",
                "1ª Vara do Trabalho", "2ª Vara do Trabalho", "3ª Vara do Trabalho",
                "Vara Criminal", "1ª Vara Criminal", "2ª Vara Criminal",
                "Vara da Fazenda Pública", "Vara de Execuções Fiscais",
                "Vara Empresarial", "Vara de Falências e Recuperações Judiciais",
                "JEC - Juizado Especial Cível", "JECRIM - Juizado Especial Criminal",
                "Vara Previdenciária", "Vara de Registros Públicos"
            ]
        }
        
        # Advogados fictícios com OAB
        self.advogados = [
            "Dr. Ricardo Silva (OAB/SP 123.456)", "Dra. Mariana Santos (OAB/RJ 234.567)",
            "Dr. Fernando Costa (OAB/MG 345.678)", "Dra. Juliana Oliveira (OAB/RS 456.789)",
            "Dr. Roberto Ferreira (OAB/PR 567.890)", "Dra. Patrícia Lima (OAB/SC 678.901)",
            "Dr. Eduardo Souza (OAB/BA 789.012)", "Dra. Camila Rodrigues (OAB/PE 890.123)",
            "Dr. Gustavo Alves (OAB/CE 901.234)", "Dra. Aline Gomes (OAB/GO 012.345)",
            "Dr. Felipe Martins (OAB/AM 123.987)", "Dra. Renata Carvalho (OAB/MT 234.876)",
            "Dr. Leonardo Pereira (OAB/DF 345.765)", "Dra. Vanessa Ribeiro (OAB/ES 456.654)"
        ]
        
        # Empresas fictícias
        self.empresas = [
            "Tech Solutions Ltda", "Construtora Horizonte S.A.", "Indústria Metalúrgica ABC",
            "Serviços de Limpeza Clean Pro", "Empresa de Logística TranspoCorp",
            "Consultoria Empresarial Estratégia", "Farmácia São José Ltda",
            "Supermercado Família Feliz", "Oficina Mecânica Auto Center",
            "Escola Particular Saber", "Clínica Médica Saúde Total",
            "Restaurante Sabor Caseiro", "Loja de Roupas Fashion Style",
            "Empresa de Segurança Guardian", "Imobiliária Lar Doce Lar",
            "Distribuidora de Bebidas Tropical", "Metalúrgica São João S.A.",
            "Transportadora Rápida Express", "Construtora Nova Era Ltda",
            "Fábrica de Móveis Estilo", "Indústria Têxtil Fashion",
            "Empresa de TI Soluções Digitais", "Laboratório de Análises Clínicas Vida",
            "Auto Peças Central", "Padaria e Confeitaria Doce Sabor",
            "Posto de Combustíveis Energia", "Loja de Eletrônicos Tech Center"
        ]
        
        # Áreas que usam pessoas físicas (cliente é pessoa física)
        self.areas_pessoa_fisica = [
            "Recuperação de Crédito", "Direito do Consumidor"
        ]
        
        # Todas as outras áreas usam empresas (cliente é empresa)
        self.areas_empresariais = [
            "Direito Trabalhista", "Direito Empresarial", "Direito Tributário",
            "Direito Civil", "Direito Bancário", "Direito Previdenciário",
            "Direito Penal", "Direito Constitucional", "Direito Digital",
            "Negociação e Conflitos", "Direito Agrário", "Direito Ambiental",
            "Direito Securitário", "Direito Imobiliário"
        ]
        
        # Áreas que usam pessoas físicas (cliente é pessoa)
        self.areas_pessoais = [
            "Direito Civil", "Direito do Consumidor", "Direito Criminal", 
            "Direito Previdenciário", "Direito de Família"
        ]
        
        # Fases processuais por área
        self.fases_por_area = {
            "Direito Trabalhista": ["Inicial", "Citação", "Contestação", "Audiência Una", "Instrução", "Sentença", "Recurso", "Execução"],
            "Direito Civil": ["Inicial", "Citação", "Contestação", "Saneamento", "Instrução", "Alegações Finais", "Sentença", "Recurso"],
            "Direito Criminal": ["Inquérito", "Denúncia", "Citação", "Resposta à Acusação", "Instrução", "Alegações Finais", "Sentença", "Recurso"],
            "Direito Tributário": ["Inicial", "Citação", "Contestação", "Perícia", "Alegações Finais", "Sentença", "Recurso", "Execução"],
            "Direito do Consumidor": ["Inicial", "Citação", "Audiência de Conciliação", "Contestação", "Instrução", "Sentença", "Execução"],
            "Direito Empresarial": ["Inicial", "Citação", "Contestação", "Saneamento", "Perícia", "Alegações Finais", "Sentença", "Recurso"]
        }
        
        # Templates de resumos por área - Expandidos com descrições detalhadas mínimo 6 linhas
        self.resumos_templates = {
            "Direito Trabalhista": [
                """Reclamação trabalhista pleiteando diferenças salariais, horas extras e verbas rescisórias em face de ex-empregador. Contrato de trabalho mantido por {anos} anos, durante os quais o empregado exerceu função de confiança com jornada irregular e trabalho em finais de semana.
O reclamante alega que não recebeu o pagamento adequado pelas horas extras laboradas, bem como reflexos das mesmas no 13º salário, férias e FGTS.
Adicionalmente, requer o pagamento de verbas rescisórias não quitadas por ocasião da rescisão contratual, incluindo aviso prévio, férias proporcionais e multa do FGTS.
Durante o período laboral, foram identificadas irregularidades no controle de ponto e ausência de adicional noturno devido.
A empresa ré não forneceu equipamentos de proteção individual adequados, configurando ambiente insalubre.
Requer-se a condenação da ré ao pagamento integral das verbas pleiteadas, com correção monetária e juros legais.""",
                
                """Ação de indenização por danos morais decorrentes de assédio moral no ambiente de trabalho. Funcionário alega perseguição e humilhações por parte da chefia imediata durante período de {meses} meses.
Os atos de assédio incluíram críticas constantes ao trabalho do empregado na presença de colegas, exclusão de reuniões importantes e delegação de tarefas incompatíveis com o cargo.
O supervisor imediato utilizava linguagem depreciativa e ameaças de demissão como forma de coação e intimidação.
O ambiente hostil resultou em deterioração da saúde mental do trabalhador, necessitando acompanhamento psicológico e uso de medicação antidepressiva.
Foi registrada queixa no departamento de recursos humanos, porém a empresa não tomou medidas efetivas para cessar as práticas abusivas.
O empregado teve sua capacidade laborativa comprometida, resultando em afastamento médico por estresse ocupacional.""",
                
                """Pedido de equiparação salarial entre colegas de função e adicional de periculosidade. Trabalhador exercia atividades de risco não reconhecidas pelo empregador durante {anos} anos de contrato.
O autor executava as mesmas funções de colegas com remuneração superior, configurando discriminação salarial injustificada.
As atividades desenvolvidas envolviam manuseio de produtos químicos e equipamentos de alta tensão, caracterizando trabalho em condições perigosas.
A empresa não fornecia equipamentos de proteção adequados nem realizava treinamentos específicos para atividades de risco.
Foram apresentados laudos técnicos comprovando a exposição a agentes nocivos à saúde e integridade física.
Requer-se o pagamento das diferenças salariais e adicional de periculosidade retroativo, com reflexos em todas as verbas trabalhistas.""",
                
                """Reclamação por acidente de trabalho com pedido de indenização por incapacidade parcial permanente. Acidente ocorreu durante jornada laboral em {meses} meses atrás, resultando em lesões graves.
O trabalhador sofreu acidente com máquina industrial devido à ausência de dispositivos de segurança adequados no equipamento.
As lesões resultaram em amputação parcial de dedos da mão direita, comprometendo permanentemente a capacidade laborativa.
A empresa não havia realizado treinamento adequado sobre operação segura dos equipamentos nem fornecido EPIs específicos.
O laudo pericial confirmou nexo causal entre o acidente e as condições inadequadas de trabalho oferecidas pela empregadora.
Requer-se indenização por danos materiais, lucros cessantes e danos morais decorrentes da incapacidade permanente adquirida.""",
                
                """Ação de cobrança de FGTS não depositado e multa rescisória. Empregador não efetuou depósitos durante período de {anos} anos, violando direitos fundamentais do trabalhador.
Durante todo o contrato de trabalho, a empresa deixou de realizar os depósitos mensais obrigatórios na conta vinculada do FGTS.
A omissão nos depósitos privou o empregado do acesso aos recursos em situações previstas em lei, como aquisição de moradia própria.
Por ocasião da rescisão contratual, a empresa também não quitou a multa rescisória de 40% sobre o saldo do FGTS.
Os valores não depositados comprometem a aposentadoria e segurança financeira do trabalhador, configurando grave lesão a direito social.
Requer-se a condenação ao pagamento integral dos depósitos não realizados, multa rescisória e indenização pelos prejuízos causados."""
            ],
            "Direito Civil": [
                """Ação de cobrança de valores oriundos de contrato de prestação de serviços não adimplido. Serviços executados conforme contratado, porém pagamento não foi realizado pelo contratante.
O contrato celebrado entre as partes estabelecia cronograma específico de pagamentos mediante apresentação de relatórios mensais de atividades.
Todos os serviços foram prestados dentro dos prazos estabelecidos e com qualidade técnica adequada, conforme atestado por terceiros.
A empresa contratante recebeu e aprovou todos os relatórios apresentados, reconhecendo a execução satisfatória dos serviços.
Após o cumprimento integral das obrigações contratuais, a ré deixou de efetuar os pagamentos devidos há {meses} meses.
As tentativas de composição amigável restaram infrutíferas, sendo necessária a cobrança judicial dos valores em aberto.
Requer-se a condenação ao pagamento do principal, acrescido de correção monetária, juros de mora e honorários advocatícios.""",
                
                """Ação de indenização por danos materiais e morais decorrentes de acidente de trânsito. Colisão causou danos significativos ao veículo e lesões corporais na vítima.
O acidente ocorreu quando o veículo do requerido invadiu preferencial do autor, colidindo violentamente na lateral direita do automóvel.
A colisão resultou em perda total do veículo, bem como lesões corporais que exigiram internação hospitalar e cirurgia ortopédica.
O condutor responsável pelo acidente estava em alta velocidade e desrespeitou sinalização de trânsito, conforme apurado pela autoridade policial.
As lesões sofridas pelo autor resultaram em incapacidade temporária para o trabalho por período de {meses} meses.
Os danos materiais incluem destruição do veículo, gastos médicos, medicamentos e lucros cessantes durante afastamento laboral.
Requer-se indenização integral pelos danos patrimoniais e compensação pelos danos morais sofridos.""",
                
                """Ação de rescisão contratual com pedido de devolução de valores pagos. Contrato firmado apresentou vícios ocultos que inviabilizam seu cumprimento.
O contrato de compra e venda de imóvel foi celebrado com base em informações falsas sobre a regularidade da documentação.
Posteriormente à assinatura, descobriu-se que o imóvel possui restrições ambientais e pendências judiciais não informadas.
A situação jurídica irregular do bem impede a transferência da propriedade e fruição pelo adquirente.
O vendedor tinha conhecimento dos vícios existentes e deliberadamente omitiu informações essenciais durante as negociações.
A impossibilidade de regularização torna o contrato inexequível, justificando sua rescisão por culpa do vendedor.
Requer-se a rescisão contratual e devolução integral dos valores pagos, com correção monetária e indenização por danos morais.""",
                
                """Pedido de indenização por danos morais em razão de negativação indevida junto aos órgãos de proteção ao crédito.
O autor teve seu nome incluído nos cadastros restritivos por débito que já havia sido quitado tempestivamente.
A empresa ré, mesmo após receber o pagamento integral da dívida, manteve a restrição ativa por período de {meses} meses.
A negativação indevida impediu a obtenção de crédito bancário para financiamento de imóvel residencial.
Foram realizadas diversas tentativas de solução amigável, com apresentação de comprovantes de pagamento, sem sucesso.
A manutenção da restrição causou constrangimento e limitação ao exercício de atividades comerciais e pessoais.
Requer-se a baixa imediata da negativação e indenização por danos morais pelo abalo ao nome e credibilidade.""",
                
                """Ação de cobrança de aluguéis e encargos em atraso. Inquilino encontra-se inadimplente há {meses} meses, descumprindo sistematicamente obrigações contratuais.
O contrato de locação estabelece pagamento mensal até o dia 10 de cada mês, porém o locatário não vem cumprindo os prazos.
Além dos aluguéis em atraso, há pendências de pagamento de IPTU, taxas condominiais e conta de energia elétrica.
O imóvel vem sendo utilizado para finalidade diversa da contratada, configurando infração às cláusulas contratuais.
Foram enviadas notificações extrajudiciais exigindo regularização, sem manifestação ou pagamento por parte do devedor.
O inadimplemento compromete a capacidade financeira do locador para manutenção do imóvel e cumprimento de suas obrigações.
Requer-se a cobrança dos valores em aberto e, subsidiariamente, a rescisão contratual com despejo."""
            ],
            "Direito do Consumidor": [
                """Ação de indenização contra fornecedor por vício em produto adquirido. Produto apresentou defeitos dentro do prazo de garantia, causando prejuízos ao consumidor.
O aparelho eletrônico adquirido apresentou falhas de funcionamento após apenas {meses} meses de uso normal e adequado.
Foram realizadas três tentativas de reparo na assistência técnica autorizada, sem resolução definitiva do problema.
O fornecedor se recusou a substituir o produto ou devolver o valor pago, alegando mau uso sem comprovação técnica.
Os defeitos comprometem a funcionalidade essencial do equipamento, tornando-o inadequado para o fim a que se destina.
O consumidor foi privado do uso do bem pelo qual pagou integralmente, configurando vício de qualidade.
Requer-se a substituição por produto novo, devolução do valor pago ou abatimento proporcional do preço.""",
                
                """Pedido de rescisão de contrato de financiamento por abusividade de cláusulas. Juros e encargos desproporcionais violam direitos básicos do consumidor.
O contrato de financiamento contém cláusulas leoninas que impõem juros superiores à média de mercado e capitalizados mensalmente.
As taxas cobradas incluem diversos encargos não especificados previamente, elevando significativamente o custo total.
O consumidor não foi adequadamente informado sobre as condições contratuais, caracterizando vício de consentimento.
A prática de anatocismo e cobrança de juros abusivos fere princípios da boa-fé objetiva e equilíbrio contratual.
O valor das prestações compromete mais de 50% da renda familiar, caracterizando onerosidade excessiva.
Requer-se a revisão das cláusulas abusivas, recálculo dos valores e devolução de quantias pagas a maior.""",
                
                """Ação contra operadora de plano de saúde por negativa de cobertura de procedimento médico urgente.
O autor necessitou de cirurgia de emergência para tratamento de patologia coberta pelo plano de saúde contratado.
A operadora negou autorização alegando carência não cumprida, em desacordo com legislação específica para casos de urgência.
O procedimento foi realizado em caráter emergencial para preservação da vida, com indicação médica inequívoca.
A negativa de cobertura obrigou o consumidor a arcar com despesas médico-hospitalares elevadas de forma inesperada.
A conduta da operadora violou função social do contrato e direito fundamental à saúde constitucionalmente protegido.
Requer-se o reembolso integral das despesas médicas e indenização por danos morais pelo descumprimento contratual.""",
                
                """Indenização por danos morais contra empresa de telefonia por cobrança indevida e interrupção de serviços.
A empresa realizou cobrança de serviços não contratados pelo período de {meses} meses, elevando indevidamente o valor das faturas.
Mesmo após reclamações formais e contestação dos valores, a operadora manteve as cobranças abusivas.
Os serviços foram suspensos unilateralmente em razão do não pagamento dos valores contestados.
A interrupção dos serviços causou prejuízos profissionais e pessoais, impedindo comunicação essencial.
A empresa não disponibilizou canais eficazes de atendimento e resolução de conflitos com consumidores.
Requer-se o restabelecimento dos serviços, revisão das faturas e indenização pelos transtornos causados.""",
                
                """Ação de repetição de indébito contra instituição financeira por cobrança de tarifa abusiva.
O banco cobrou sistematicamente tarifas por serviços essenciais que deveriam ser gratuitos conforme regulamentação do Banco Central.
As cobranças incluíam taxa de manutenção de conta corrente para clientes que mantinham movimentação mínima exigida.
Foram cobradas tarifas por extratos, transferências entre contas da mesma instituição e consultas ao saldo.
O consumidor não foi previamente informado sobre a cobrança dessas tarifas nem concordou expressamente com elas.
A prática fere resolução do BACEN que estabelece gratuidade para serviços essenciais bancários.
Requer-se a devolução em dobro dos valores cobrados indevidamente e cessação das práticas abusivas."""
            ],
            "Direito Empresarial": [
                """Ação de dissolução de sociedade empresarial com apuração de haveres. Sócios não conseguem manter parceria comercial devido a divergências irreconciliáveis na condução dos negócios.
A sociedade foi constituída há {anos} anos com participação igualitária dos sócios, que inicialmente mantinham objetivos comuns.
Ao longo do tempo, surgiram conflitos sobre estratégias de investimento, distribuição de lucros e direcionamento das atividades empresariais.
Um dos sócios vem tomando decisões unilaterais sem consulta ao parceiro, violando princípios de gestão compartilhada.
As divergências resultaram em paralisia das atividades e prejuízos ao patrimônio social, tornando inviável a continuidade da parceria.
Requer-se a dissolução total da sociedade com liquidação do acervo e apuração de haveres para justa divisão dos bens.""",
                
                """Pedido de recuperação judicial para reorganização das atividades empresariais. Empresa atravessa crise financeira decorrente de fatores internos e externos ao mercado.
A empresa possui débitos que totalizam valor superior ao dobro do patrimônio líquido, caracterizando estado de crise econômico-financeira.
As dificuldades foram agravadas pela retração do mercado e inadimplência de clientes estratégicos durante período de {meses} meses.
Apesar da situação financeira adversa, a empresa mantém capacidade operacional e potencial de recuperação com reestruturação adequada.
O plano de recuperação prevê renegociação de dívidas, reestruturação de contratos e modernização dos processos produtivos.
Requer-se deferimento do pedido para viabilizar a superação da crise e preservação dos empregos e atividade econômica.""",
                
                """Ação de cobrança entre empresas por fornecimento de mercadorias não pagas. Valor em aberto há {meses} meses, comprometendo fluxo de caixa da empresa fornecedora.
O contrato de fornecimento estabelecia entrega de produtos mediante pagamento em 30 dias após apresentação da nota fiscal.
Todas as mercadorias foram entregues conforme especificações técnicas e dentro dos prazos contratualmente estabelecidos.
A empresa compradora recebeu e conferiu os produtos, emitindo atestados de qualidade e conformidade das entregas.
Apesar do cumprimento integral das obrigações contratuais, os pagamentos não foram efetuados nos vencimentos acordados.
A inadimplência compromete o capital de giro da fornecedora e sua capacidade de honrar compromissos com terceiros.
Requer-se a cobrança dos valores em aberto com encargos moratórios e eventuais perdas e danos sofridos.""",
                
                """Ação anulatória de assembleia geral extraordinária por vícios no processo de convocação e deliberação dos sócios.
A assembleia foi convocada sem observância do prazo mínimo legal e sem disponibilização prévia das informações necessárias.
O quórum foi artificialmente formado com participação de sócios que possuem conflito de interesse na matéria deliberada.
As decisões tomadas violam direitos essenciais de acionistas minoritários e princípios de governança corporativa.
A ordem do dia foi alterada durante a reunião, incluindo matérias não previstas na convocação original.
Os vícios no processo decisório comprometem a validade jurídica das deliberações e legitimidade das decisões.
Requer-se a anulação integral da assembleia e repetição do ato com observância das formalidades legais.""",
                
                """Pedido de registro de marca junto ao INPI com oposição de terceiro interessado alegando anterioridade de direitos.
A empresa desenvolve produtos sob marca específica há {anos} anos, utilizando-a comercialmente em todo território nacional.
O pedido de registro foi apresentado tempestivamente conforme regulamentação do Instituto Nacional da Propriedade Industrial.
Terceiro apresentou oposição alegando titularidade anterior sobre marca similar, sem comprovação do uso efetivo.
A marca da requerente possui distintividade e não gera confusão com sinais anteriores no mesmo segmento de mercado.
O uso comercial prolongado e investimentos em publicidade conferem direito ao registro pela aplicação do princípio da anterioridade.
Requer-se o deferimento do pedido de registro e rejeição da oposição por falta de fundamento jurídico válido."""
            ],
            "Direito Tributário": [
                """Ação anulatória de auto de infração fiscal por cobrança indevida de tributos. Lançamento tributário foi realizado sem observância dos princípios da legalidade e tipicidade.
A empresa foi autuada por suposto descumprimento de obrigação acessória não prevista expressamente na legislação vigente.
O auto de infração baseou-se em interpretação extensiva de norma tributária, violando princípio da reserva legal.
A penalidade aplicada é desproporcional à alegada infração e não observa critérios de razoabilidade estabelecidos em lei.
Durante o processo administrativo, foram negados direitos de ampla defesa e contraditório ao contribuinte.
A cobrança compromete o capital de giro da empresa e sua capacidade de manutenção das atividades operacionais.
Requer-se a anulação do auto de infração e declaração de inexigibilidade do crédito tributário constituído.""",
                
                """Mandado de segurança contra ato coativo de autoridade fiscal que determinou bloqueio de contas bancárias sem prévia intimação.
O bloqueio foi realizado em execução fiscal sem esgotamento das tentativas de localização de outros bens penhoráveis.
A medida constritiva recaiu sobre conta corrente essencial ao funcionamento da empresa, comprometendo pagamento de salários.
Não foi observado o princípio da menor onerosidade ao devedor, previsto no Código de Processo Civil.
A empresa possui outros bens suficientes para garantir a execução, tornando desnecessária a constrição da conta operacional.
O ato coativo causou grave lesão ao direito líquido e certo da empresa, configurando abuso de poder.
Requer-se a concessão de liminar para desbloqueio imediato das contas e posterior denegação da segurança.""",
                
                """Ação declaratória de inexistência de relação jurídico-tributária por aplicação indevida de legislação fiscal.
A empresa foi incluída em regime especial de fiscalização sem atender aos critérios legais estabelecidos para enquadramento.
A aplicação retroativa de norma tributária violou princípio da irretroatividade e segurança jurídica do contribuinte.
Os fatos geradores alegados pela fazenda não se subsumem às hipóteses de incidência previstas na legislação.
A empresa mantém escrituração fiscal regular e cumpre todas as obrigações tributárias principais e acessórias.
A insegurança jurídica prejudica o planejamento empresarial e desenvolvimento das atividades econômicas.
Requer-se declaração de inexistência de débito tributário e exclusão dos regimes especiais de fiscalização."""
            ],
            "Direito Criminal": [
                """Ação penal por apropriação indébita contra ex-funcionário que subtraiu valores da empresa. O acusado ocupava função de confiança com acesso aos recursos financeiros da corporação.
Durante período de {meses} meses, o réu realizou saques não autorizados da conta corrente empresarial para benefício próprio.
Os desvios foram descobertos durante auditoria interna que identificou inconsistências nos registros contábeis.
O montante apropriado compromete significativamente a situação financeira da empresa vítima e prejudica terceiros.
O acusado confessou parcialmente os fatos durante interrogatório policial, reconhecendo a prática delitiva.
As provas documentais e testemunhais confirmam a materialidade e autoria do delito de apropriação indébita.
Requer-se a condenação do réu à pena privativa de liberdade e reparação integral dos danos causados.""",
                
                """Queixa-crime por crime contra a honra (calúnia e difamação) praticado por concorrente comercial em redes sociais.
O querelado publicou informações falsas sobre produtos da empresa querelante, alegando irregularidades sanitárias inexistentes.
As publicações difamatórias foram compartilhadas amplamente, causando prejuízo à reputação comercial e redução nas vendas.
Laudo técnico comprova que os produtos atendem integralmente às normas sanitárias e possuem certificações regulamentares.
As declarações foram feitas com evidente intuito de prejudicar a concorrência e conquistar fatia de mercado.
O crime resultou em danos morais e materiais quantificáveis, afetando relações comerciais estabelecidas há anos.
Requer-se a condenação do querelado e fixação de indenização pelos prejuízos materiais e morais sofridos."""
            ]
        }
    
    def gerar_cpf(self) -> str:
        """Gera CPF válido"""
        def calcular_digito(cpf_parcial):
            soma = sum(int(cpf_parcial[i]) * (len(cpf_parcial) + 1 - i) for i in range(len(cpf_parcial)))
            resto = soma % 11
            return '0' if resto < 2 else str(11 - resto)
        
        # Gera os 9 primeiros dígitos
        cpf_base = ''.join([str(random.randint(0, 9)) for _ in range(9)])
        
        # Calcula os dígitos verificadores
        primeiro_digito = calcular_digito(cpf_base)
        segundo_digito = calcular_digito(cpf_base + primeiro_digito)
        
        cpf_completo = cpf_base + primeiro_digito + segundo_digito
        
        # Formata
        return f"{cpf_completo[:3]}.{cpf_completo[3:6]}.{cpf_completo[6:9]}-{cpf_completo[9:]}"
    
    def gerar_cnpj(self) -> str:
        """Gera CNPJ válido para testes"""
        # Gera os 12 primeiros dígitos
        cnpj = [random.randint(0, 9) for _ in range(12)]
        
        # Sequência para cálculo do primeiro dígito
        sequencia1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma1 = sum(cnpj[i] * sequencia1[i] for i in range(12))
        digito1 = (soma1 % 11)
        if digito1 < 2:
            digito1 = 0
        else:
            digito1 = 11 - digito1
        cnpj.append(digito1)
        
        # Sequência para cálculo do segundo dígito
        sequencia2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma2 = sum(cnpj[i] * sequencia2[i] for i in range(13))
        digito2 = (soma2 % 11)
        if digito2 < 2:
            digito2 = 0
        else:
            digito2 = 11 - digito2
        cnpj.append(digito2)
        
        # Formata CNPJ
        cnpj_str = ''.join(map(str, cnpj))
        return f"{cnpj_str[:2]}.{cnpj_str[2:5]}.{cnpj_str[5:8]}/{cnpj_str[8:12]}-{cnpj_str[12:]}"
    
    def gerar_cnj(self, estado: str) -> str:
        """Gera número CNJ válido para o estado"""
        # Códigos dos tribunais por estado (simplificado)
        codigos_tribunal = {
            "SP": "8.26", "RJ": "8.19", "MG": "8.13", "RS": "8.21", "PR": "8.16",
            "SC": "8.24", "BA": "8.05", "PE": "8.17", "CE": "8.06", "GO": "8.09",
            "AM": "8.04", "MT": "8.11", "DF": "8.07", "ES": "8.08"
        }
        
        # Formato: NNNNNNN-DD.AAAA.J.TR.OOOO
        sequencial = str(random.randint(1000000, 9999999))
        ano = random.randint(2018, 2024)
        segmento = "8"  # Justiça Estadual
        tribunal = codigos_tribunal.get(estado, "8.26")
        origem = str(random.randint(1000, 9999))
        
        # Simula dígito verificador (simplificado)
        digito = str(random.randint(10, 99))
        
        return f"{sequencial}-{digito}.{ano}.{segmento}.{tribunal}.{origem}"
    
    def gerar_nome_completo(self) -> str:
        """Gera nome completo realista"""
        genero = random.choice(["M", "F"])
        
        if genero == "M":
            primeiro_nome = random.choice(self.nomes_masculinos)
        else:
            primeiro_nome = random.choice(self.nomes_femininos)
        
        # 30% chance de ter nome do meio
        if random.random() < 0.3:
            segundo_nome = random.choice(self.nomes_masculinos + self.nomes_femininos)
            nome_completo = f"{primeiro_nome} {segundo_nome}"
        else:
            nome_completo = primeiro_nome
        
        # Adiciona sobrenomes (1-2)
        sobrenomes = random.sample(self.sobrenomes, random.randint(1, 2))
        nome_completo += " " + " ".join(sobrenomes)
        
        return nome_completo
    
    def gerar_empresa(self) -> str:
        """Gera nome de empresa"""
        if random.random() < 0.8:
            return random.choice(self.empresas)
        else:
            # Gera empresa baseada em nome + tipo
            nome_base = random.choice(self.sobrenomes)
            tipo_empresa = random.choice(["Ltda", "S.A.", "ME", "Eireli"])
            atividade = random.choice(["Serviços", "Comércio", "Indústria", "Consultoria"])
            return f"{nome_base} {atividade} {tipo_empresa}"
    
    def gerar_processo_sintetico(self, area_juridica: str | None = None) -> Dict[str, Any]:
        """Gera um processo jurídico sintético completo"""
        
        # Define área se não especificada
        if not area_juridica:
            areas = ["Direito Trabalhista", "Direito Civil", "Direito do Consumidor", 
                    "Direito Empresarial", "Direito Tributário", "Direito Criminal"]
            area_juridica = random.choice(areas)
        
        # Garantir que area_juridica não é None
        if area_juridica is None:
            area_juridica = "Direito Civil"
        
        # Seleciona estado e comarca
        estado = random.choice(list(self.comarcas_estados.keys()))
        comarca = random.choice(self.comarcas_estados[estado])
        
        # Seleciona vara judicial apropriada para o estado
        varas_disponiveis = self.juizos_por_estado.get(estado, self.juizos_por_estado["default"])
        vara_judicial = random.choice(varas_disponiveis)
        
        # Gera dados básicos
        processo = {
            "numero_processo_cnj": self.gerar_cnj(estado),
            "area_juridica": area_juridica,
            "estado": estado,
            "comarca": comarca,
            "juizo": vara_judicial,
            "data_distribuicao": self.gerar_data_recente(),
            "advogado_do_caso": random.choice(self.advogados),
            "fase": random.choice(self.fases_por_area.get(area_juridica, ["Inicial", "Instrução", "Sentença"])),
            "risco": random.choice(["Baixo", "Médio", "Alto"])
        }
        
        # Gera partes do processo - AUTOR e RÉU devem ser diferentes
        # Nova regra: apenas Recuperação de Crédito e Direito do Consumidor são pessoa física
        if area_juridica in self.areas_pessoa_fisica:
            # Áreas pessoa física: autor sempre pessoa física, réu pode ser pessoa ou empresa
            processo["autor"] = self.gerar_nome_completo()
            processo["cpf_autor"] = self.gerar_cpf()
            
            if random.random() < 0.7:  # 70% réu é empresa
                processo["cliente"] = self.gerar_empresa() 
                processo["cnpj"] = self.gerar_cnpj()
                # Garante que autor (pessoa) seja diferente do réu (empresa)
                while processo["cliente"] == processo["autor"]:
                    processo["cliente"] = self.gerar_empresa()
            else:  # 30% réu também é pessoa física
                processo["cliente"] = self.gerar_nome_completo()
                processo["cnpj"] = None
                # Garante que sejam pessoas diferentes
                while processo["cliente"] == processo["autor"]:
                    processo["cliente"] = self.gerar_nome_completo()
            
        else:  
            # Todas as outras áreas: empresas (pessoa jurídica)
            # Pode ser empresa vs empresa ou pessoa vs empresa, mas com foco empresarial
            if random.random() < 0.3:  # 30% autor é pessoa física (funcionário, sócio, etc.)
                processo["autor"] = self.gerar_nome_completo()
                processo["cpf_autor"] = self.gerar_cpf()
                processo["cnpj"] = None
                # Cliente/Réu é sempre empresa
                processo["cliente"] = self.gerar_empresa()
                # Garante que empresa cliente seja diferente do autor
                while processo["cliente"] == processo["autor"]:
                    processo["cliente"] = self.gerar_empresa()
            else:  # 70% autor é empresa
                processo["autor"] = self.gerar_empresa()
                processo["cnpj"] = self.gerar_cnpj()
                processo["cpf_autor"] = None
                # Réu/Cliente é empresa diferente
                processo["cliente"] = self.gerar_empresa()
                # Garante que sejam empresas diferentes
                while processo["cliente"] == processo["autor"]:
                    processo["cliente"] = self.gerar_empresa()
        
        # Sempre gera advogado adverso (representando o réu)
        processo["advogado_adverso"] = random.choice(self.advogados)
        # Garante que advogados sejam diferentes
        while processo["advogado_adverso"] == processo["advogado_do_caso"]:
            processo["advogado_adverso"] = random.choice(self.advogados)
        
        # Gera valores financeiros realistas
        processo.update(self.gerar_valores_financeiros(area_juridica))
        
        # Gera resumo dos fatos
        processo["resumo_dos_fatos"] = self.gerar_resumo_fatos(area_juridica)
        
        # Adiciona verbas trabalhistas se aplicável
        if area_juridica == "Direito Trabalhista":
            processo.update(self.gerar_verbas_trabalhistas())
        
        # Campos adicionais
        if random.random() < 0.3:
            processo["funcao"] = random.choice(["Vendedor", "Analista", "Gerente", "Operador", "Técnico", "Consultor"])
        
        if random.random() < 0.4:
            processo["andamento_relatorio"] = self.gerar_andamento_relatorio(area_juridica)
        
        # Datas opcionais
        if random.random() < 0.3:
            processo["previsao_de_pagamento"] = self.gerar_data_futura()
        
        if random.random() < 0.2:
            processo["data_acordo"] = self.gerar_data_recente()
        
        return processo
    
    def gerar_valores_financeiros(self, area_juridica: str) -> Dict[str, float]:
        """Gera valores financeiros realistas por área"""
        valores = {}
        
        if area_juridica == "Direito Trabalhista":
            # Valores aumentados para ficar similar ao empresarial
            valores["valor_da_causa"] = round(random.uniform(15000, 450000), 2)
            
            if random.random() < 0.7:
                valores["calculo_contadores"] = round(valores["valor_da_causa"] * random.uniform(0.8, 1.5), 2)
            
            if random.random() < 0.5:
                valores["provisao"] = round(valores["valor_da_causa"] * random.uniform(0.3, 0.8), 2)
                
        elif area_juridica == "Direito Civil":
            # Valores aumentados para ficar similar ao empresarial
            valores["valor_da_causa"] = round(random.uniform(12000, 480000), 2)
            
        elif area_juridica == "Direito Tributário":
            # Valores aumentados para ficar similar ao empresarial
            valores["valor_da_causa"] = round(random.uniform(18000, 520000), 2)
            
        elif area_juridica == "Direito do Consumidor":
            valores["valor_da_causa"] = round(random.uniform(500, 30000), 2)
            
        elif area_juridica == "Direito Empresarial":
            valores["valor_da_causa"] = round(random.uniform(10000, 500000), 2)
            
        else:
            valores["valor_da_causa"] = round(random.uniform(2000, 80000), 2)
        
        # Valores opcionais (20-40% de chance)
        if random.random() < 0.3:
            valores["execucao"] = round(valores["valor_da_causa"] * random.uniform(0.1, 0.5), 2)
        
        if random.random() < 0.2:
            valores["bloqueio"] = round(valores["valor_da_causa"] * random.uniform(0.05, 0.3), 2)
        
        if random.random() < 0.25:
            valores["acordo"] = round(valores["valor_da_causa"] * random.uniform(0.4, 0.9), 2)
        
        if random.random() < 0.15:
            valores["pagamento"] = round(valores["valor_da_causa"] * random.uniform(0.1, 1.0), 2)
        
        return valores
    
    def gerar_verbas_trabalhistas(self) -> Dict[str, bool]:
        """Gera verbas trabalhistas com probabilidades realistas"""
        verbas_comuns = {
            "horas_extras_e_reflexos": 0.7,
            "adicional_noturno_e_reflexos": 0.3,
            "fgts_e_a_multa_de_40_porcento": 0.8,
            "verbas_rescisoria": 0.9,
            "ferias_em_dobro": 0.4,
            "indenizacao_por_danos_morais": 0.3,
            "diferencas_salariais": 0.5,
            "equiparacao_salarial": 0.2,
            "adicional_de_periculosidade": 0.15,
            "acidente_de_trabalho": 0.1,
            "estabilidade": 0.2
        }
        
        return {verba: random.random() < prob for verba, prob in verbas_comuns.items()}
    
    def gerar_resumo_fatos(self, area_juridica: str) -> str:
        """Gera resumo dos fatos contextualizado com descrições detalhadas"""
        templates = self.resumos_templates.get(area_juridica, self.resumos_templates["Direito Civil"])
        template = random.choice(templates)
        
        # Substitui variáveis
        anos = random.randint(1, 8)
        meses = random.randint(3, 24)
        valor_especifico = random.randint(10000, 500000)
        dias = random.randint(15, 90)
        
        resumo = template.format(anos=anos, meses=meses, valor=valor_especifico, dias=dias)
        
        # Detalhes específicos expandidos por área
        detalhes_por_area = {
            "Direito Trabalhista": [
                f"Durante o período laborativo, foram registradas {random.randint(50, 200)} horas extras mensais não pagas adequadamente.",
                f"A empresa não forneceu equipamentos de segurança em {random.randint(5, 15)} ocasiões diferentes.",
                f"O trabalhador foi submetido a jornada de {random.randint(10, 14)} horas diárias sem intervalos adequados."
            ],
            "Direito Civil": [
                f"O valor do prejuízo material totaliza R$ {valor_especifico:,.2f}, devidamente comprovado por documentos.",
                f"A situação perdura há {meses} meses sem solução, agravando os danos sofridos.",
                f"Foram realizadas {random.randint(3, 8)} tentativas de composição amigável sem êxito."
            ],
            "Direito do Consumidor": [
                f"O produto possui defeito que compromete {random.randint(60, 90)}% de sua funcionalidade principal.",
                f"Foram gastos R$ {random.randint(500, 5000):,.2f} em tentativas de reparo sem sucesso.",
                f"O fornecedor violou {random.randint(2, 5)} dispositivos do Código de Defesa do Consumidor."
            ],
            "Direito Empresarial": [
                f"O patrimônio social envolve valores superiores a R$ {valor_especifico * 2:,.2f}.",
                f"A empresa possui {random.randint(15, 80)} funcionários que dependem da continuidade dos negócios.",
                f"Os conflitos societários perduram há {meses} meses, prejudicando a operação."
            ],
            "Direito Tributário": [
                f"O auto de infração totaliza R$ {valor_especifico:,.2f} em tributos e multas indevidas.",
                f"A empresa mantém regularidade fiscal há {anos} anos consecutivos.",
                f"O processo administrativo tramita há {meses} meses sem solução definitiva."
            ],
            "Direito Criminal": [
                f"O valor do prejuízo apurado soma R$ {valor_especifico:,.2f} em recursos desviados.",
                f"As investigações duraram {meses} meses com coleta de {random.randint(20, 50)} provas documentais.",
                f"O crime foi praticado durante {random.randint(6, 24)} meses de forma continuada."
            ]
        }
        
        # Adiciona detalhes específicos da área
        if area_juridica in detalhes_por_area:
            detalhes_area = detalhes_por_area[area_juridica]
            if random.random() < 0.8:  # 80% de chance de adicionar detalhes específicos
                resumo += " " + random.choice(detalhes_area)
        
        return resumo
    
    def gerar_andamento_relatorio(self, area_juridica: str) -> str:
        """Gera relatório de andamento processual"""
        andamentos = [
            "Processo em fase de instrução. Aguardando designação de audiência de instrução e julgamento.",
            "Contestação apresentada tempestivamente. Aguardando manifestação sobre preliminares arguidas.",
            "Perícia deferida pelo juízo. Aguardando nomeação de perito para início dos trabalhos técnicos.",
            "Audiência de conciliação realizada sem êxito. Processo seguirá para instrução.",
            "Sentença proferida em favor do autor. Prazo recursal em curso.",
            "Recurso de apelação interposto. Autos remetidos ao Tribunal de Justiça.",
            "Acordo celebrado em audiência. Aguardando cumprimento espontâneo pelos termos pactuados.",
            "Fase de execução iniciada. Citação da executada para pagamento em 15 dias.",
            "Penhora realizada sobre bem imóvel. Aguardando avaliação para hasta pública."
        ]
        
        return random.choice(andamentos)
    
    def gerar_data_recente(self) -> datetime.date:
        """Gera data entre 6 meses atrás e hoje"""
        hoje = datetime.date.today()
        dias_atras = random.randint(1, 180)
        return hoje - datetime.timedelta(days=dias_atras)
    
    def gerar_data_futura(self) -> datetime.date:
        """Gera data entre hoje e 6 meses no futuro"""
        hoje = datetime.date.today()
        dias_frente = random.randint(1, 180)
        return hoje + datetime.timedelta(days=dias_frente)
    
    def gerar_lote_processos(self, quantidade: int, distribuicao_areas: Dict[str, int] | None = None) -> List[Dict[str, Any]]:
        """Gera lote de processos sintéticos"""
        
        if distribuicao_areas is None:
            # Distribuição padrão baseada na realidade brasileira
            distribuicao_areas = {
                "Direito Trabalhista": 25,
                "Direito Civil": 20,
                "Direito do Consumidor": 15,
                "Direito Empresarial": 10,
                "Direito Tributário": 10,
                "Direito Criminal": 8,
                "Direito Previdenciário": 5,
                "Direito Imobiliário": 4,
                "Direito Digital": 2,
                "Direito Agrário": 1
            }
        
        processos = []
        
        for area, percentual in distribuicao_areas.items():
            qtd_area = int((percentual / 100) * quantidade)
            
            for _ in range(qtd_area):
                processo = self.gerar_processo_sintetico(area)
                processos.append(processo)
        
        # Gera processos restantes com áreas aleatórias
        while len(processos) < quantidade:
            area_aleatoria = random.choice(list(distribuicao_areas.keys()))
            processo = self.gerar_processo_sintetico(area_aleatoria)
            processos.append(processo)
        
        return processos[:quantidade]
    
    def exportar_para_sql(self, processos: List[Dict[str, Any]], arquivo: str = "processos_sinteticos.sql"):
        """Exporta processos para arquivo SQL"""
        
        sql_inserts = []
        
        for processo in processos:
            # Prepara valores para SQL
            valores = []
            campos = []
            
            for campo, valor in processo.items():
                campos.append(campo)
                
                if valor is None:
                    valores.append("NULL")
                elif isinstance(valor, str):
                    # Escapa aspas simples
                    valor_escapado = valor.replace("'", "''")
                    valores.append(f"'{valor_escapado}'")
                elif isinstance(valor, (datetime.date, datetime.datetime)):
                    valores.append(f"'{valor.strftime('%Y-%m-%d')}'")
                elif isinstance(valor, bool):
                    valores.append("TRUE" if valor else "FALSE")
                else:
                    valores.append(str(valor))
            
            campos_str = ", ".join(campos)
            valores_str = ", ".join(valores)
            
            sql_insert = f"INSERT INTO processo_juridico ({campos_str}) VALUES ({valores_str});"
            sql_inserts.append(sql_insert)
        
        # Salva arquivo
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write("-- Dados Sintéticos para Processos Jurídicos\n")
            f.write("-- Gerado automaticamente pelo LegalSyntheticDataGenerator\n\n")
            
            for insert in sql_inserts:
                f.write(insert + "\n")
        
        return arquivo
    
    def gerar_relatorio_estatistico(self, processos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Gera relatório estatístico dos dados sintéticos"""
        
        total_processos = len(processos)
        
        # Estatísticas por área
        areas = {}
        valores_por_area = {}
        
        for processo in processos:
            area = processo.get("area_juridica", "Não Informado")
            
            if area not in areas:
                areas[area] = 0
                valores_por_area[area] = []
            
            areas[area] += 1
            
            if processo.get("valor_da_causa"):
                valores_por_area[area].append(processo["valor_da_causa"])
        
        # Calcula valores médios por área
        valores_medios = {}
        for area, valores in valores_por_area.items():
            if valores:
                valores_medios[area] = {
                    "media": sum(valores) / len(valores),
                    "minimo": min(valores),
                    "maximo": max(valores),
                    "total": sum(valores)
                }
        
        # Distribuição por estado
        estados = {}
        for processo in processos:
            estado = processo.get("estado", "Não Informado")
            estados[estado] = estados.get(estado, 0) + 1
        
        # Distribuição por risco
        riscos = {}
        for processo in processos:
            risco = processo.get("risco", "Não Informado")
            riscos[risco] = riscos.get(risco, 0) + 1
        
        relatorio = {
            "total_processos": total_processos,
            "distribuicao_por_area": areas,
            "valores_financeiros": valores_medios,
            "distribuicao_por_estado": estados,
            "distribuicao_por_risco": riscos,
            "valor_total_causas": sum(p.get("valor_da_causa", 0) for p in processos)
        }
        
        return relatorio


# Função de conveniência para uso direto
def gerar_dados_sinteticos_juridicos(quantidade: int = 50, areas_personalizadas: Dict[str, int] | None = None) -> List[Dict[str, Any]]:
    """
    Função de conveniência para gerar dados sintéticos jurídicos
    
    Args:
        quantidade: Número de processos a gerar
        areas_personalizadas: Distribuição personalizada por área (opcional)
    
    Returns:
        Lista de processos jurídicos sintéticos
    """
    gerador = LegalSyntheticDataGenerator()
    return gerador.gerar_lote_processos(quantidade, areas_personalizadas or {})


if __name__ == "__main__":
    # Exemplo de uso
    gerador = LegalSyntheticDataGenerator()
    
    # Gera 100 processos sintéticos
    processos = gerador.gerar_lote_processos(100)
    
    # Gera relatório estatístico
    relatorio = gerador.gerar_relatorio_estatistico(processos)
    
    print("Relatório de Dados Sintéticos Gerados:")
    print(f"Total de processos: {relatorio['total_processos']}")
    print("\nDistribuição por área:")
    for area, quantidade in relatorio['distribuicao_por_area'].items():
        print(f"  {area}: {quantidade}")
    
    print(f"\nValor total das causas: R$ {relatorio['valor_total_causas']:,.2f}")
    
    # Exporta para SQL
    arquivo_sql = gerador.exportar_para_sql(processos)
    print(f"\nArquivo SQL exportado: {arquivo_sql}")