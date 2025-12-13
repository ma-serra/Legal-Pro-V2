# 💰 Sistema Universal de Formatação Monetária

## 📋 Padrão Implementado

O sistema agora possui **formatação monetária universal** em todos os módulos, seguindo o padrão brasileiro **R$ XX.XXX,XX**.

## 🔧 Como Usar

### **1. Em Templates HTML (Jinja2)**

```html
<!-- Formatação básica -->
{{ valor_da_causa | currency }}
{{ acordo | moeda }}
{{ pagamento | real }}

<!-- Função global -->
{{ format_currency(valor_da_causa) }}
{{ format_currency(processo.acordo, False) }}  <!-- Sem símbolo R$ -->

<!-- Exemplos práticos -->
<td>{{ processo.valor_da_causa | currency }}</td>
<td>{{ processo.acordo | moeda }}</td>
<td>{{ processo.pagamento | real }}</td>
```

### **2. Em Python (Backend)**

```python
from utils.currency_formatter import format_currency, parse_currency

# Formatação básica
valor_formatado = format_currency(1234.56)  # "R$ 1.234,56"
valor_sem_simbolo = format_currency(1234.56, False)  # "1.234,56"

# Parsing de valores
valor_numerico = parse_currency("R$ 1.234,56")  # 1234.56

# Usando a função legacy (compatibilidade)
from app import formatar_moeda_brl
valor_formatado = formatar_moeda_brl(1234.56)  # "R$ 1.234,56"

# Em rotas Flask
@app.route('/processo/<int:id>')
def processo_detalhes(id):
    processo = ProcessoJuridico.query.get_or_404(id)
    return render_template('processo.html', 
                         processo=processo)
```

### **3. Em JavaScript (Frontend)**

```javascript
// Formatação básica
const valorFormatado = formatCurrency(1234.56);  // "R$ 1.234,56"
const valorSemSimbolo = formatCurrency(1234.56, false);  // "1.234,56"

// Parsing de valores
const valorNumerico = parseCurrency("R$ 1.234,56");  // 1234.56

// Validação de entrada
const {isValid, parsedValue} = CurrencyFormatter.validateCurrencyInput("R$ 1.234,56");

// Configurar input automático
CurrencyFormatter.setupCurrencyInput(document.getElementById('valor-input'));

// Formatar todos os displays automaticamente
CurrencyFormatter.formatAllCurrencyDisplays('.currency-display');
```

### **4. Em Formulários HTML**

```html
<!-- Input com formatação automática -->
<input type="text" class="form-control currency-input" 
       name="valor_da_causa" placeholder="R$ 0,00">

<!-- Display formatado automaticamente -->
<span class="currency-display">{{ processo.valor_da_causa }}</span>

<!-- Script necessário -->
<script src="{{ url_for('static', filename='js/currency-formatter.js') }}"></script>
```

## 🏗️ Estrutura do Sistema

### **Arquivos Criados:**
- `utils/currency_formatter.py` - Utilitário Python
- `static/js/currency-formatter.js` - Utilitário JavaScript

### **Modificações:**
- `main.py` - Registros dos filtros Jinja2
- `app.py` - Import da função utilitária

### **Filtros Jinja2 Disponíveis:**
- `{{ valor | currency }}` - Formatação completa
- `{{ valor | moeda }}` - Alias em português
- `{{ valor | real }}` - Alias para R$

### **Funções JavaScript Globais:**
- `formatCurrency(valor, incluirSimbolo, casasDecimais)`
- `parseCurrency(valorFormatado)`
- `formatMoeda(valor)` - Alias
- `formatReal(valor)` - Alias

## 📊 Exemplos de Uso

### **Template de Lista de Processos**
```html
{% for processo in processos %}
<tr>
    <td>{{ processo.numero_cnj }}</td>
    <td>{{ processo.valor_da_causa | currency }}</td>
    <td>{{ processo.acordo | moeda }}</td>
    <td>{{ processo.pagamento | real }}</td>
</tr>
{% endfor %}
```

### **Dashboard Financeiro**
```html
<div class="kpi-card">
    <div class="kpi-value">{{ total_causas | currency }}</div>
    <div class="kpi-label">Valor Total das Causas</div>
</div>

<div class="kpi-card">
    <div class="kpi-value">{{ total_acordos | moeda }}</div>
    <div class="kpi-label">Total em Acordos</div>
</div>
```

### **Formulário de Cadastro**
```html
<form id="processo-form">
    <div class="mb-3">
        <label class="form-label">Valor da Causa</label>
        <input type="text" class="form-control currency-input" 
               name="valor_da_causa" required>
    </div>
    
    <div class="mb-3">
        <label class="form-label">Valor do Acordo</label>
        <input type="text" class="form-control currency-input" 
               name="acordo">
    </div>
</form>

<script>
// Configurar formatação automática
document.addEventListener('DOMContentLoaded', function() {
    CurrencyFormatter.initializeAllCurrencyInputs();
});
</script>
```

## 🎯 Padrões Obrigatórios

### **Para Novos Módulos:**

1. **Sempre importar** a função de formatação:
   ```python
   from utils.currency_formatter import format_currency
   ```

2. **Incluir script JavaScript** nos templates:
   ```html
   <script src="{{ url_for('static', filename='js/currency-formatter.js') }}"></script>
   ```

3. **Usar filtros em templates**:
   ```html
   {{ valor | currency }}
   ```

4. **Campos monetários** devem ter classe `currency-input`:
   ```html
   <input class="form-control currency-input">
   ```

### **Para Campos Existentes:**

- Substituir `formatar_moeda_brl()` por `format_currency()`
- Adicionar filtros `| currency` nos templates
- Incluir classes `currency-input` em formulários

## ✅ Validação

O sistema garante:
- **Formato brasileiro**: R$ XX.XXX,XX
- **Parsing robusto**: Aceita diversos formatos de entrada
- **Validação automática**: Inputs só aceitam números válidos
- **Compatibilidade**: Função legacy mantida
- **Performance**: Formatação otimizada

## 🚀 Próximos Passos

1. Atualizar templates existentes para usar novos filtros
2. Migrar formulários para classes `currency-input`
3. Substituir funções legacy por novas funções
4. Testar integração em todos os módulos