# 🛠️ Guia de Desenvolvimento - Sistema de Detecção de Anomalias

## 📋 Índice

1. [Configuração do Ambiente](#configuração-do-ambiente)
2. [Estrutura do Projeto](#estrutura-do-projeto)
3. [Desenvolvimento Backend](#desenvolvimento-backend)
4. [Desenvolvimento Frontend](#desenvolvimento-frontend)
5. [Testes](#testes)
6. [Debugging](#debugging)
7. [Boas Práticas](#boas-práticas)
8. [Deploy](#deploy)

---

## 🚀 Configuração do Ambiente

### Pré-requisitos

- **Python**: 3.9 ou superior
- **Node.js**: 16 ou superior
- **npm/pnpm**: Gerenciador de pacotes
- **Git**: Controle de versão
- **Docker** (opcional): Para containerização

### Setup Rápido

#### 1. Clone o Repositório

```bash
git clone https://github.com/galafis/Anomaly-Detection-System.git
cd Anomaly-Detection-System
```

#### 2. Backend Setup

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente (opcional)
cp config/.env.example .env
# Editar .env com suas configurações
```

#### 3. Frontend Setup

```bash
cd frontend

# Instalar dependências
npm install --legacy-peer-deps
# ou
pnpm install

# Criar arquivo .env.local (opcional)
echo "VITE_API_BASE_URL=http://localhost:5000" > .env.local
```

---

## 📁 Estrutura do Projeto

```
Anomaly-Detection-System/
│
├── 📂 src/                          # Backend (Python/Flask)
│   ├── 📂 api/
│   │   ├── app.py                   # API principal completa
│   │   ├── simple_app.py            # API simplificada
│   │   └── __init__.py
│   │
│   ├── 📂 models/
│   │   ├── data_models.py           # Modelos de dados
│   │   └── __init__.py
│   │
│   ├── 📂 services/
│   │   ├── anomaly_detector.py      # Detector principal
│   │   ├── alert_manager.py         # Gerenciador de alertas
│   │   ├── database_manager.py      # Gerenciador de BD
│   │   └── __init__.py
│   │
│   └── 📂 utils/
│       └── __init__.py
│
├── 📂 frontend/                     # Frontend (React/Vite)
│   ├── 📂 src/
│   │   ├── 📂 components/
│   │   │   └── 📂 ui/              # Componentes Shadcn/ui
│   │   ├── App.jsx                 # Componente principal
│   │   ├── App.css                 # Estilos principais
│   │   └── main.jsx                # Entry point
│   │
│   ├── 📂 public/                  # Arquivos estáticos
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── 📂 tests/                       # Testes
│   ├── test_app.py                 # Testes backend
│   └── ...
│
├── 📂 docs/                        # Documentação
│   ├── API.md                      # Documentação API
│   ├── ARCHITECTURE.md             # Arquitetura
│   └── DEVELOPMENT.md              # Este arquivo
│
├── 📂 config/                      # Configurações
│   └── .env.example
│
├── requirements.txt                # Dependências Python
├── README.md
└── .gitignore
```

---

## 🐍 Desenvolvimento Backend

### Executar o Servidor de Desenvolvimento

```bash
# Método 1: API Principal (Completa)
python src/api/app.py

# Método 2: API Simples
python src/api/simple_app.py
```

O servidor estará disponível em `http://localhost:5000`

### Criar Novo Endpoint

1. **Abrir `src/api/app.py`**

2. **Adicionar novo endpoint:**

```python
@app.route('/api/nova-funcionalidade', methods=['POST'])
def nova_funcionalidade():
    """Descrição da funcionalidade"""
    try:
        data = request.get_json()
        
        # Sua lógica aqui
        resultado = processar_dados(data)
        
        return jsonify({
            'status': 'success',
            'data': resultado
        }), 200
        
    except Exception as e:
        logger.error(f"Erro: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
```

3. **Adicionar testes em `tests/test_app.py`:**

```python
def test_nova_funcionalidade(self):
    """Testa nova funcionalidade"""
    payload = {'dados': 'teste'}
    response = self.app.post('/api/nova-funcionalidade',
                            data=json.dumps(payload),
                            content_type='application/json')
    
    self.assertEqual(response.status_code, 200)
    data = json.loads(response.data)
    self.assertEqual(data['status'], 'success')
```

### Adicionar Novo Serviço

1. **Criar arquivo em `src/services/`:**

```python
# src/services/meu_servico.py

import logging

logger = logging.getLogger(__name__)

class MeuServico:
    """Descrição do serviço"""
    
    def __init__(self):
        self.configuracao = {}
    
    def processar(self, dados):
        """Processa dados"""
        try:
            # Lógica aqui
            return resultado
        except Exception as e:
            logger.error(f"Erro no processamento: {str(e)}")
            raise
```

2. **Importar e usar no `app.py`:**

```python
from src.services.meu_servico import MeuServico

servico = MeuServico()

@app.route('/api/usar-servico', methods=['POST'])
def usar_servico():
    data = request.get_json()
    resultado = servico.processar(data)
    return jsonify(resultado)
```

### Trabalhar com Machine Learning

#### Treinar Novo Modelo

```python
from sklearn.ensemble import IsolationForest
import joblib

# Preparar dados
X_train = preparar_dados(dados_treino)

# Treinar modelo
modelo = IsolationForest(
    contamination=0.1,
    random_state=42
)
modelo.fit(X_train)

# Salvar modelo
joblib.dump(modelo, 'models/novo_modelo.pkl')
```

#### Carregar e Usar Modelo

```python
import joblib

# Carregar modelo
modelo = joblib.load('models/novo_modelo.pkl')

# Fazer predição
predicao = modelo.predict(X_novo)
```

---

## ⚛️ Desenvolvimento Frontend

### Executar o Servidor de Desenvolvimento

```bash
cd frontend
npm run dev
# ou
pnpm dev
```

O frontend estará disponível em `http://localhost:5173`

### Criar Novo Componente

1. **Criar arquivo em `src/components/`:**

```jsx
// src/components/MeuComponente.jsx

import React from 'react';

export default function MeuComponente({ dados, onAcao }) {
    return (
        <div className="p-4 bg-white rounded-lg shadow">
            <h2 className="text-xl font-bold">{dados.titulo}</h2>
            <button 
                onClick={onAcao}
                className="mt-4 px-4 py-2 bg-blue-500 text-white rounded"
            >
                Ação
            </button>
        </div>
    );
}
```

2. **Usar no componente pai:**

```jsx
import MeuComponente from './components/MeuComponente';

function App() {
    const handleAcao = () => {
        console.log('Ação executada');
    };
    
    return (
        <MeuComponente 
            dados={{ titulo: 'Teste' }}
            onAcao={handleAcao}
        />
    );
}
```

### Fazer Requisições à API

```jsx
import { useState, useEffect } from 'react';

function useDeteccaoAnomalia() {
    const [resultado, setResultado] = useState(null);
    const [carregando, setCarregando] = useState(false);
    const [erro, setErro] = useState(null);
    
    const detectar = async (features) => {
        setCarregando(true);
        setErro(null);
        
        try {
            const response = await fetch('http://localhost:5000/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ features })
            });
            
            const data = await response.json();
            setResultado(data);
        } catch (err) {
            setErro(err.message);
        } finally {
            setCarregando(false);
        }
    };
    
    return { resultado, carregando, erro, detectar };
}

// Usar no componente
function App() {
    const { resultado, carregando, detectar } = useDeteccaoAnomalia();
    
    const handleDetectar = () => {
        const features = gerarFeatures();
        detectar(features);
    };
    
    return (
        <div>
            <button onClick={handleDetectar}>Detectar Anomalia</button>
            {carregando && <p>Carregando...</p>}
            {resultado && <p>Resultado: {resultado.is_anomaly ? 'Anomalia!' : 'Normal'}</p>}
        </div>
    );
}
```

### Usar Chart.js

```jsx
import { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';

function GraficoAnomalia({ dados }) {
    const chartRef = useRef(null);
    const chartInstance = useRef(null);
    
    useEffect(() => {
        if (chartInstance.current) {
            chartInstance.current.destroy();
        }
        
        const ctx = chartRef.current.getContext('2d');
        chartInstance.current = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dados.labels,
                datasets: [{
                    label: 'Anomaly Score',
                    data: dados.scores,
                    borderColor: '#f44336',
                    backgroundColor: 'rgba(244, 67, 54, 0.1)',
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
        
        return () => {
            if (chartInstance.current) {
                chartInstance.current.destroy();
            }
        };
    }, [dados]);
    
    return <canvas ref={chartRef} />;
}
```

---

## 🧪 Testes

### Testes Backend (Pytest)

#### Executar Todos os Testes

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
python -m pytest tests/ -v
```

#### Executar Teste Específico

```bash
python -m pytest tests/test_app.py::TestFlaskAPI::test_predict_endpoint_valid_request -v
```

#### Executar com Coverage

```bash
pip install pytest-cov
python -m pytest tests/ --cov=src --cov-report=html
```

#### Escrever Novo Teste

```python
import unittest
from src.api.simple_app import app

class TestNovaFuncionalidade(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_exemplo(self):
        """Testa exemplo"""
        response = self.app.get('/api/endpoint')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn('campo', data)
```

### Testes Frontend (Jest/Vitest)

```bash
cd frontend
npm test
```

---

## 🐛 Debugging

### Backend (Python)

#### Usar Python Debugger (pdb)

```python
import pdb

@app.route('/api/debug')
def debug_endpoint():
    dados = processar()
    pdb.set_trace()  # Breakpoint aqui
    return jsonify(dados)
```

#### VS Code Debug Configuration

`.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Flask",
            "type": "python",
            "request": "launch",
            "module": "flask",
            "env": {
                "FLASK_APP": "src/api/app.py",
                "FLASK_ENV": "development"
            },
            "args": ["run", "--no-debugger"],
            "jinja": true
        }
    ]
}
```

### Frontend (React)

#### Console Logging

```javascript
console.log('Dados:', dados);
console.table(arrayDados);
console.error('Erro:', erro);
```

#### React DevTools

1. Instalar extensão React DevTools
2. Inspecionar componentes
3. Visualizar props e state

---

## ✅ Boas Práticas

### Código Limpo

#### Python (PEP 8)

```bash
# Instalar formatadores
pip install black pylint flake8

# Formatar código
black src/

# Verificar qualidade
pylint src/
flake8 src/
```

#### JavaScript/React (ESLint)

```bash
cd frontend

# Executar linting
npm run lint

# Corrigir automaticamente
npm run lint -- --fix
```

### Git Workflow

```bash
# Criar branch para feature
git checkout -b feature/nova-funcionalidade

# Fazer commits pequenos e descritivos
git add arquivo.py
git commit -m "feat: adiciona nova funcionalidade X"

# Push e criar PR
git push origin feature/nova-funcionalidade
```

### Padrões de Commit

- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Documentação
- `style:` Formatação
- `refactor:` Refatoração
- `test:` Testes
- `chore:` Tarefas gerais

---

## 🚀 Deploy

### Docker

```bash
# Build da imagem
docker build -t anomaly-detection .

# Executar container
docker run -p 5000:5000 anomaly-detection
```

### Docker Compose

```bash
# Subir todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down
```

---

## 📚 Recursos Adicionais

- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://react.dev/)
- [Scikit-learn Documentation](https://scikit-learn.org/)
- [TailwindCSS Documentation](https://tailwindcss.com/)
- [Chart.js Documentation](https://www.chartjs.org/)

---

## 🤝 Contribuindo

Consulte [CONTRIBUTING.md](../CONTRIBUTING.md) para diretrizes de contribuição.

---

**Autor:** Gabriel Demetrios Lafis  
**Última Atualização:** Outubro 2024
