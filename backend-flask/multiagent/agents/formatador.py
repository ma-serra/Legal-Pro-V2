import logging
import json
import re
from multiagent.core.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class FormatadorAgent(BaseAgent):
    """
    Agente responsável por formatar o resultado final para apresentação.
    
    Este agente aplica formatação, estilos e estrutura ao conteúdo sintetizado,
    adequando-o para o formato de saída desejado (HTML, Markdown, JSON, etc).
    """
    
    def _inicializar(self):
        """Inicialização específica do agente"""
        # Configurações específicas de formatação
        self.formato_saida = self.config.get("formato_saida", "html")
        self.estilo = self.config.get("estilo", "padrao")
        self.incluir_metadados = self.config.get("incluir_metadados", True)
        
        # Formatos suportados
        self.formatos_suportados = ["html", "markdown", "md", "json", "texto", "txt"]
        
        # Normaliza formato para um dos suportados
        if self.formato_saida not in self.formatos_suportados:
            self.logger.warning(f"Formato {self.formato_saida} não suportado, usando 'html'")
            self.formato_saida = "html"
            
        self.logger.info(f"FormatadorAgent inicializado com formato {self.formato_saida}")
    
    def _formatar_html(self, data):
        """
        Formata o resultado em HTML.
        
        Args:
            data: Dados acumulados dos agentes anteriores
            
        Returns:
            String HTML formatada
        """
        # Extrai os dados relevantes
        sintese = data.get("sintese", {})
        classificacao = data.get("classificacao", {})
        analises = data.get("analises", {})
        tags = data.get("tags", [])
        
        # Obtém o conteúdo da síntese
        conteudo = sintese.get("conteudo", "")
        formato = sintese.get("formato", "resumo")
        
        # Converte para string se for dicionário
        if isinstance(conteudo, dict):
            conteudo_json = json.dumps(conteudo, indent=2, ensure_ascii=False)
            # Para JSON, usamos um bloco pré-formatado
            if formato == "json":
                conteudo = f"<pre class='json-content'>{conteudo_json}</pre>"
            else:
                # Transforma o dicionário em HTML estruturado
                conteudo_html = "<div class='sintese-estruturada'>"
                for chave, valor in conteudo.items():
                    conteudo_html += f"<div class='item-sintese'>"
                    conteudo_html += f"<h4>{chave.replace('_', ' ').title()}</h4>"
                    
                    if isinstance(valor, list):
                        conteudo_html += "<ul>"
                        for item in valor:
                            conteudo_html += f"<li>{item}</li>"
                        conteudo_html += "</ul>"
                    else:
                        conteudo_html += f"<p>{valor}</p>"
                        
                    conteudo_html += "</div>"
                conteudo_html += "</div>"
                conteudo = conteudo_html
        
        # Para formatos de texto, converte quebras de linha em parágrafos e formata listas
        elif formato in ["resumo", "relatorio", "narrativa", "resposta"]:
            # Formata listas (linhas que começam com - ou *)
            conteudo = re.sub(r'(?m)^[\s]*[-*][\s]+(.+)$', r'<li>\1</li>', conteudo)
            conteudo = re.sub(r'(?s)(<li>.+?</li>)', r'<ul>\1</ul>', conteudo)
            
            # Formata títulos (linhas que começam com # ou ##)
            conteudo = re.sub(r'(?m)^[\s]*#[\s]+(.+)$', r'<h2>\1</h2>', conteudo)
            conteudo = re.sub(r'(?m)^[\s]*##[\s]+(.+)$', r'<h3>\1</h3>', conteudo)
            
            # Divide em parágrafos (linhas vazias separam parágrafos)
            paragrafos = re.split(r'\n\s*\n', conteudo)
            # Evita converter listas e títulos já formatados
            paragrafos_html = []
            for p in paragrafos:
                if not (p.strip().startswith('<ul>') or p.strip().startswith('<h')):
                    p = f"<p>{p}</p>"
                paragrafos_html.append(p)
                
            conteudo = "\n".join(paragrafos_html)
        
        # Para pontos, converte explicitamente para lista
        elif formato == "pontos":
            # Divide por linhas e formata como lista
            linhas = conteudo.split('\n')
            itens_lista = []
            for linha in linhas:
                linha = linha.strip()
                if linha:
                    # Remove marcadores de lista existentes
                    linha = re.sub(r'^[-*•]?\s*', '', linha)
                    itens_lista.append(f"<li>{linha}</li>")
                    
            if itens_lista:
                conteudo = f"<ul>\n{''.join(itens_lista)}\n</ul>"
            else:
                conteudo = f"<p>{conteudo}</p>"
        
        # Constrói o HTML completo
        html = f"""
        <div class="resultado formato-{formato}">
            <div class="conteudo-principal">
                {conteudo}
            </div>
        """
        
        # Adiciona metadados se configurado
        if self.incluir_metadados:
            # Seção de metadados
            html += """
            <div class="metadados-container">
                <h3>Metadados da Análise</h3>
                <div class="metadados">
            """
            
            # Adiciona tags
            if tags:
                html += """
                <div class="metadado-secao tags-container">
                    <h4>Tags</h4>
                    <div class="tags">
                """
                for tag in tags:
                    html += f'<span class="tag">{tag}</span>'
                html += """
                    </div>
                </div>
                """
                
            # Adiciona classificação
            if classificacao and "categorias" in classificacao:
                html += """
                <div class="metadado-secao">
                    <h4>Classificação</h4>
                    <div class="categorias">
                """
                for cat, score in classificacao.get("categorias", {}).items():
                    # Formata o score como porcentagem
                    score_percent = int(score * 100)
                    html += f"""
                    <div class="categoria-item">
                        <span class="categoria-nome">{cat}</span>
                        <div class="categoria-barra-container">
                            <div class="categoria-barra" style="width: {score_percent}%"></div>
                        </div>
                        <span class="categoria-score">{score_percent}%</span>
                    </div>
                    """
                html += """
                    </div>
                </div>
                """
                
            # Adiciona sentimento se disponível
            if analises and "sentimento" in analises:
                sentimento = analises["sentimento"]
                html += f"""
                <div class="metadado-secao">
                    <h4>Sentimento</h4>
                    <div class="sentimento-info">
                        <div class="sentimento-item">
                            <span class="sentimento-label">Polaridade:</span>
                            <span class="sentimento-valor polaridade-{sentimento.get('polaridade', 'neutro')}">{sentimento.get('polaridade', 'Neutro').capitalize()}</span>
                        </div>
                        <div class="sentimento-item">
                            <span class="sentimento-label">Intensidade:</span>
                            <span class="sentimento-valor">{sentimento.get('intensidade', 'Moderada').capitalize()}</span>
                        </div>
                """
                
                # Adiciona emoções se disponíveis
                if "emocoes" in sentimento and sentimento["emocoes"]:
                    html += """
                        <div class="sentimento-item">
                            <span class="sentimento-label">Emoções:</span>
                            <div class="emocoes-container">
                    """
                    for emocao in sentimento["emocoes"]:
                        html += f'<span class="emocao">{emocao}</span>'
                    html += """
                            </div>
                        </div>
                    """
                    
                html += """
                    </div>
                </div>
                """
                
            # Fecha a seção de metadados
            html += """
                </div>
            </div>
            """
            
        # Fecha a div principal
        html += "</div>"
        
        return html
    
    def _formatar_markdown(self, data):
        """
        Formata o resultado em Markdown.
        
        Args:
            data: Dados acumulados dos agentes anteriores
            
        Returns:
            String em formato Markdown
        """
        # Extrai os dados relevantes
        sintese = data.get("sintese", {})
        classificacao = data.get("classificacao", {})
        analises = data.get("analises", {})
        tags = data.get("tags", [])
        
        # Obtém o conteúdo da síntese
        conteudo = sintese.get("conteudo", "")
        formato = sintese.get("formato", "resumo")
        
        # Converte para string se for dicionário
        if isinstance(conteudo, dict):
            if formato == "json":
                # Para JSON, usa bloco de código Markdown
                conteudo_json = json.dumps(conteudo, indent=2, ensure_ascii=False)
                conteudo = f"```json\n{conteudo_json}\n```"
            else:
                # Transforma o dicionário em Markdown estruturado
                conteudo_md = ""
                for chave, valor in conteudo.items():
                    titulo = chave.replace('_', ' ').title()
                    conteudo_md += f"### {titulo}\n\n"
                    
                    if isinstance(valor, list):
                        for item in valor:
                            conteudo_md += f"- {item}\n"
                        conteudo_md += "\n"
                    else:
                        conteudo_md += f"{valor}\n\n"
                        
                conteudo = conteudo_md
        
        # Inicializa o resultado em Markdown
        markdown = f"# Resultado da Análise\n\n"
        
        # Adiciona conteúdo principal
        if formato == "pontos" and not conteudo.startswith("- "):
            # Converte para formato de lista
            linhas = conteudo.split('\n')
            conteudo_formatado = ""
            for linha in linhas:
                linha = linha.strip()
                if linha:
                    # Remove marcadores existentes
                    linha = re.sub(r'^[-*•]?\s*', '', linha)
                    conteudo_formatado += f"- {linha}\n"
            conteudo = conteudo_formatado
            
        markdown += f"{conteudo}\n\n"
        
        # Adiciona metadados se configurado
        if self.incluir_metadados:
            markdown += "## Metadados da Análise\n\n"
            
            # Adiciona tags
            if tags:
                markdown += "### Tags\n\n"
                markdown += ", ".join([f"`{tag}`" for tag in tags]) + "\n\n"
                
            # Adiciona classificação
            if classificacao and "categorias" in classificacao:
                markdown += "### Classificação\n\n"
                for cat, score in classificacao.get("categorias", {}).items():
                    # Formata o score como porcentagem
                    score_percent = int(score * 100)
                    markdown += f"- **{cat}**: {score_percent}%\n"
                markdown += "\n"
                
            # Adiciona sentimento se disponível
            if analises and "sentimento" in analises:
                sentimento = analises["sentimento"]
                markdown += "### Sentimento\n\n"
                markdown += f"- **Polaridade**: {sentimento.get('polaridade', 'Neutro').capitalize()}\n"
                markdown += f"- **Intensidade**: {sentimento.get('intensidade', 'Moderada').capitalize()}\n"
                
                # Adiciona emoções se disponíveis
                if "emocoes" in sentimento and sentimento["emocoes"]:
                    markdown += f"- **Emoções**: {', '.join(sentimento['emocoes'])}\n"
                    
                markdown += "\n"
                
        return markdown
    
    def _formatar_json(self, data):
        """
        Formata o resultado em JSON.
        
        Args:
            data: Dados acumulados dos agentes anteriores
            
        Returns:
            Dicionário com o resultado formatado
        """
        # Extrai os dados relevantes
        sintese = data.get("sintese", {})
        classificacao = data.get("classificacao", {})
        analises = data.get("analises", {})
        tags = data.get("tags", [])
        
        # Obtém o conteúdo da síntese
        conteudo = sintese.get("conteudo", "")
        formato = sintese.get("formato", "resumo")
        
        # Cria o objeto de resultado
        resultado = {
            "conteudo": conteudo,
            "formato": formato
        }
        
        # Adiciona metadados se configurado
        if self.incluir_metadados:
            resultado["metadados"] = {
                "tags": tags,
                "classificacao": classificacao.get("categorias", {}) if classificacao else {},
            }
            
            # Adiciona sentimento se disponível
            if analises and "sentimento" in analises:
                resultado["metadados"]["sentimento"] = analises["sentimento"]
                
        return resultado
    
    def _formatar_texto(self, data):
        """
        Formata o resultado em texto simples.
        
        Args:
            data: Dados acumulados dos agentes anteriores
            
        Returns:
            String em formato de texto simples
        """
        # Extrai os dados relevantes
        sintese = data.get("sintese", {})
        classificacao = data.get("classificacao", {})
        analises = data.get("analises", {})
        tags = data.get("tags", [])
        
        # Obtém o conteúdo da síntese
        conteudo = sintese.get("conteudo", "")
        formato = sintese.get("formato", "resumo")
        
        # Converte para string se for dicionário
        if isinstance(conteudo, dict):
            if formato == "json":
                conteudo_str = json.dumps(conteudo, indent=2, ensure_ascii=False)
                conteudo = conteudo_str
            else:
                # Transforma o dicionário em texto estruturado
                conteudo_texto = ""
                for chave, valor in conteudo.items():
                    titulo = chave.replace('_', ' ').title()
                    conteudo_texto += f"{titulo}:\n"
                    
                    if isinstance(valor, list):
                        for item in valor:
                            conteudo_texto += f"- {item}\n"
                        conteudo_texto += "\n"
                    else:
                        conteudo_texto += f"{valor}\n\n"
                        
                conteudo = conteudo_texto
        
        # Inicializa o resultado em texto
        texto = "RESULTADO DA ANÁLISE\n"
        texto += "=" * 20 + "\n\n"
        
        # Adiciona conteúdo principal
        texto += f"{conteudo}\n\n"
        
        # Adiciona metadados se configurado
        if self.incluir_metadados:
            texto += "METADADOS DA ANÁLISE\n"
            texto += "-" * 20 + "\n\n"
            
            # Adiciona tags
            if tags:
                texto += "Tags: " + ", ".join(tags) + "\n\n"
                
            # Adiciona classificação
            if classificacao and "categorias" in classificacao:
                texto += "Classificação:\n"
                for cat, score in classificacao.get("categorias", {}).items():
                    # Formata o score como porcentagem
                    score_percent = int(score * 100)
                    texto += f"- {cat}: {score_percent}%\n"
                texto += "\n"
                
            # Adiciona sentimento se disponível
            if analises and "sentimento" in analises:
                sentimento = analises["sentimento"]
                texto += "Sentimento:\n"
                texto += f"- Polaridade: {sentimento.get('polaridade', 'Neutro').capitalize()}\n"
                texto += f"- Intensidade: {sentimento.get('intensidade', 'Moderada').capitalize()}\n"
                
                # Adiciona emoções se disponíveis
                if "emocoes" in sentimento and sentimento["emocoes"]:
                    texto += f"- Emoções: {', '.join(sentimento['emocoes'])}\n"
                    
                texto += "\n"
                
        return texto
    
    def _processar(self, data):
        """
        Processa os dados para formatar o resultado final.
        
        Args:
            data: Dados acumulados dos agentes anteriores
            
        Returns:
            Dicionário com o resultado formatado
        """
        try:
            # Formata o conteúdo de acordo com o formato solicitado
            if self.formato_saida in ["html"]:
                conteudo_formatado = self._formatar_html(data)
            elif self.formato_saida in ["markdown", "md"]:
                conteudo_formatado = self._formatar_markdown(data)
            elif self.formato_saida in ["json"]:
                conteudo_formatado = self._formatar_json(data)
            elif self.formato_saida in ["texto", "txt"]:
                conteudo_formatado = self._formatar_texto(data)
            else:
                # Formato padrão como fallback
                conteudo_formatado = self._formatar_html(data)
                
            # Constrói o resultado final
            resultado = {
                "resultado_formatado": conteudo_formatado,
                "formato": self.formato_saida,
                "estilo": self.estilo,
                # Mantém os dados de processamento para referência
                "dados_processamento": data
            }
            
            return resultado
            
        except Exception as e:
            self.logger.error(f"Erro na formatação: {str(e)}")
            raise
