# 📚 Exemplos de Uso - API de Detecção de Anomalias

Este diretório contém exemplos práticos de como usar a API de Detecção de Anomalias.

## 📁 Arquivos Disponíveis

### Scripts Python

- **`usage_example.py`** - Exemplo completo com 5 casos de uso diferentes
  - Detecção em dados normais
  - Detecção em dados anômalos
  - Detecção em lote
  - Leitura de arquivo
  - Teste de performance

### Dados de Exemplo

- **`normal_data.json`** - Dataset com 1000 features de distribuição normal
- **`anomaly_data.json`** - Dataset com 1000 features anômalas (alta variância)

## 🚀 Como Usar

### Pré-requisitos

1. **API em execução:**
   ```bash
   # Na raiz do projeto
   python src/api/simple_app.py
   ```

2. **Dependências instaladas:**
   ```bash
   pip install requests numpy
   ```

### Executar Exemplos

#### Exemplo Completo (Recomendado)

```bash
# Da raiz do projeto
python examples/usage_example.py
```

Este script executa 5 exemplos diferentes:

1. ✅ **Dados Normais** - Verifica como a API classifica dados de distribuição normal
2. 🔴 **Dados Anômalos** - Testa com dados de alta variância
3. 📊 **Detecção em Lote** - Processa múltiplas amostras
4. 📁 **Dados de Arquivo** - Carrega e processa dados JSON
5. ⚡ **Teste de Performance** - Mede throughput e latência

#### Exemplo Rápido - Python

```python
import requests
import numpy as np

# Gerar dados
features = np.random.randn(1000).tolist()

# Fazer requisição
response = requests.post(
    'http://localhost:5000/predict',
    json={'features': features}
)

# Ver resultado
result = response.json()
print(f"É anomalia? {result['is_anomaly']}")
print(f"Confiança: {result['confidence']:.2%}")
```

#### Exemplo Rápido - cURL

```bash
# Usando dados de exemplo
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d @examples/normal_data.json

# Ver apenas se é anomalia
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d @examples/normal_data.json | jq '.is_anomaly'
```

#### Exemplo JavaScript/Node.js

```javascript
const axios = require('axios');

// Gerar dados aleatórios
const features = Array.from({length: 1000}, () => Math.random() * 10);

// Fazer requisição
axios.post('http://localhost:5000/predict', {
    features: features
})
.then(response => {
    const { is_anomaly, confidence, prediction } = response.data;
    console.log('É anomalia?', is_anomaly);
    console.log('Confiança:', (confidence * 100).toFixed(2) + '%');
    console.log('Predição:', prediction);
})
.catch(error => {
    console.error('Erro:', error.message);
});
```

## 📊 Saída Esperada

### Dados Normais
```
Resultado da Detecção - Distribuição Normal
============================================================
Status: success
É Anomalia? 🟢 NÃO
Predição: -12.3456
Confiança: 12.35%
Features analisadas: 1000
Timestamp: 2024-10-14T15:30:00.000Z
```

### Dados Anômalos
```
Resultado da Detecção - Alta Variância
============================================================
Status: success
É Anomalia? 🔴 SIM
Predição: -89.7654
Confiança: 89.77%
Features analisadas: 1000
Timestamp: 2024-10-14T15:30:01.000Z
```

## 🔧 Personalizando os Exemplos

### Modificar Threshold de Anomalia

Os dados são considerados anômalos quando `|prediction| > 50.0`. Para ajustar:

```python
# No arquivo src/api/simple_app.py, linha ~111
is_anomaly = bool(abs(prediction) > 50.0)  # Ajustar threshold aqui
```

### Gerar Dados Customizados

```python
import numpy as np
import json

# Dados com padrão específico
features = []
for i in range(1000):
    if i % 100 == 0:
        features.append(np.random.randn() * 50)  # Pico
    else:
        features.append(np.random.randn())  # Normal

# Salvar
with open('custom_data.json', 'w') as f:
    json.dump({'features': features}, f)
```

## 📈 Benchmarks

### Performance Esperada

| Métrica | Valor Típico |
|---------|--------------|
| Latência média | ~50ms |
| Throughput | ~20 req/s |
| Taxa de sucesso | >99% |

### Executar Benchmark

```bash
# Teste de carga simples
for i in {1..100}; do
  curl -X POST http://localhost:5000/predict \
    -H "Content-Type: application/json" \
    -d @examples/normal_data.json &
done
wait
```

## 🐛 Troubleshooting

### Erro: "Connection refused"

**Solução:** Verifique se a API está rodando
```bash
curl http://localhost:5000/api/status
```

### Erro: "Invalid features count"

**Solução:** Certifique-se de enviar exatamente 1000 features
```python
features = [0.0] * 1000  # Array com 1000 valores
```

### Erro: "Module not found"

**Solução:** Instale as dependências
```bash
pip install -r requirements.txt
```

## 📚 Recursos Adicionais

- [Documentação da API](../docs/API.md)
- [Guia de Desenvolvimento](../docs/DEVELOPMENT.md)
- [Arquitetura do Sistema](../docs/ARCHITECTURE.md)
- [Postman Collection](../docs/postman_collection.json)

## 🤝 Contribuindo

Quer adicionar mais exemplos? Veja [CONTRIBUTING.md](../CONTRIBUTING.md)

---

**Autor:** Gabriel Demetrios Lafis  
**Versão:** 1.0.0
