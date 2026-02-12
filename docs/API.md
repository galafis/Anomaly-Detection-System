# Documentação da API - Sistema de Detecção de Anomalias

## 📚 Visão Geral

A API do Sistema de Detecção de Anomalias fornece endpoints RESTful para detecção em tempo real de anomalias em dados numéricos usando modelos de Machine Learning.

## 🔗 Base URL

```
http://localhost:5000
```

## 📋 Endpoints Disponíveis

### 1. GET `/`
**Descrição:** Retorna a página inicial com informações do sistema

**Resposta:** HTML com interface de informações do sistema

**Exemplo:**
```bash
curl http://localhost:5000/
```

---

### 2. GET `/api/status`
**Descrição:** Verifica o status e informações do sistema

**Resposta:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "model_loaded": true,
  "timestamp": "2024-10-14T15:30:00.000Z",
  "author": "Gabriel Demetrios Lafis"
}
```

**Exemplo:**
```bash
curl http://localhost:5000/api/status
```

---

### 3. GET `/api/info`
**Descrição:** Retorna informações detalhadas do sistema

**Resposta:**
```json
{
  "system": "Anomaly Detection System",
  "version": "1.0.0",
  "author": "Gabriel Demetrios Lafis",
  "model_type": "RandomForest Regression",
  "feature_count": 1000,
  "description": "Real-time anomaly detection using advanced machine learning algorithms"
}
```

**Exemplo:**
```bash
curl http://localhost:5000/api/info
```

---

### 4. POST `/predict`
**Descrição:** Detecta anomalias nos dados fornecidos

**Headers:**
- `Content-Type: application/json`

**Body:**
```json
{
  "features": [array de 1000 valores numéricos]
}
```

**Resposta de Sucesso (200):**
```json
{
  "status": "success",
  "prediction": -12.345,
  "is_anomaly": false,
  "confidence": 0.12,
  "timestamp": "2024-10-14T15:30:00.000Z",
  "feature_count": 1000
}
```

**Resposta de Erro (400):**
```json
{
  "status": "error",
  "error": "Invalid features. Expected 1000 numerical values."
}
```

**Exemplos:**

**Python:**
```python
import requests
import numpy as np

# Gerar features aleatórias
features = np.random.randn(1000).tolist()

# Fazer requisição
response = requests.post(
    'http://localhost:5000/predict',
    json={'features': features}
)

result = response.json()
print(f"É anomalia? {result['is_anomaly']}")
print(f"Confiança: {result['confidence']}")
```

**cURL:**
```bash
# Exemplo com arquivo JSON
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d @features.json

# Exemplo inline (primeiros 5 valores)
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [1.2, 3.4, 5.6, ..., 999.0]}'
```

**JavaScript:**
```javascript
// Gerar features aleatórias
const features = Array.from({length: 1000}, () => Math.random() * 100);

// Fazer requisição
fetch('http://localhost:5000/predict', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ features })
})
.then(response => response.json())
.then(data => {
  console.log('É anomalia?', data.is_anomaly);
  console.log('Confiança:', data.confidence);
});
```

---

## ⚠️ Códigos de Status HTTP

| Código | Descrição |
|--------|-----------|
| 200 | Requisição bem-sucedida |
| 400 | Erro na requisição (dados inválidos) |
| 404 | Endpoint não encontrado |
| 500 | Erro interno do servidor |

---

## 📊 Formato dos Dados

### Features (Características)
- **Tipo:** Array de números de ponto flutuante
- **Tamanho:** Exatamente 1000 valores
- **Exemplo:** `[1.2, 3.4, 5.6, ..., 999.0]`

### Prediction (Predição)
- **Tipo:** Número de ponto flutuante
- **Descrição:** Valor da predição do modelo
- **Interpretação:** Valores absolutos maiores indicam maior probabilidade de anomalia

### Confidence (Confiança)
- **Tipo:** Número de ponto flutuante
- **Faixa:** 0.0 a 1.0
- **Descrição:** Nível de confiança da predição (0 = baixa, 1 = alta)

### Is Anomaly (É Anomalia)
- **Tipo:** Boolean
- **Descrição:** Indica se o dado é classificado como anomalia
- **Threshold:** |prediction| > 50.0

---

## 🔧 Tratamento de Erros

### Erro: Features Inválidas
```json
{
  "status": "error",
  "error": "Invalid features. Expected 1000 numerical values."
}
```

### Erro: Dados JSON Ausentes
```json
{
  "status": "error",
  "error": "No JSON data provided"
}
```

### Erro: Campo Features Ausente
```json
{
  "status": "error",
  "error": "Missing \"features\" field in request"
}
```

---

## 📈 Exemplo Completo de Uso

```python
#!/usr/bin/env python3
"""
Exemplo completo de uso da API de Detecção de Anomalias
"""

import requests
import numpy as np
import json

API_URL = "http://localhost:5000"

def check_status():
    """Verifica o status da API"""
    response = requests.get(f"{API_URL}/api/status")
    print("Status:", json.dumps(response.json(), indent=2))

def detect_anomaly(features):
    """Detecta anomalia nos dados"""
    response = requests.post(
        f"{API_URL}/predict",
        json={"features": features}
    )
    return response.json()

def main():
    # 1. Verificar status
    check_status()
    
    # 2. Gerar dados normais
    normal_features = np.random.randn(1000).tolist()
    result_normal = detect_anomaly(normal_features)
    print("\nDados Normais:", json.dumps(result_normal, indent=2))
    
    # 3. Gerar dados anômalos
    anomaly_features = (np.random.randn(1000) * 100).tolist()
    result_anomaly = detect_anomaly(anomaly_features)
    print("\nDados Anômalos:", json.dumps(result_anomaly, indent=2))

if __name__ == "__main__":
    main()
```

---

## 🛠️ Ferramentas de Teste

### Postman Collection
Importe a coleção Postman disponível em `/docs/postman_collection.json`

### Swagger/OpenAPI
Documentação interativa disponível em `/api/docs` (em desenvolvimento)

---

## 📞 Suporte

Para questões ou problemas com a API, entre em contato:
- **GitHub Issues:** [github.com/galafis/Anomaly-Detection-System/issues](https://github.com/galafis/Anomaly-Detection-System/issues)
- **Email:** Gabriel Demetrios Lafis
- **Autor:** Gabriel Demetrios Lafis

---

## 📝 Changelog

### v1.0.0 (Atual)
- Endpoint `/predict` para detecção de anomalias
- Endpoints `/api/status` e `/api/info` para informações do sistema
- Suporte para 1000 features por predição
- Tratamento robusto de erros
- Documentação completa da API
