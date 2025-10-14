# 🤝 Guia de Contribuição

**Autor:** Gabriel Demetrios Lafis

---

Ficamos felizes com o seu interesse em contribuir para o **Advanced Anomaly Detection System**! Este guia ajudará você a contribuir de forma efetiva.

## 📋 Índice

1. [Como Contribuir](#como-contribuir)
2. [Reportando Bugs](#reportando-bugs)
3. [Sugerindo Melhorias](#sugerindo-melhorias)
4. [Configuração do Ambiente](#configuração-do-ambiente)
5. [Processo de Pull Request](#processo-de-pull-request)
6. [Padrões de Código](#padrões-de-código)
7. [Testes](#testes)
8. [Documentação](#documentação)
9. [Código de Conduta](#código-de-conduta)

---

## 🚀 Como Contribuir

Existem várias formas de contribuir:

- 🐛 **Reportar bugs** - Encontrou um problema? Nos avise!
- 💡 **Sugerir melhorias** - Tem ideias para novas funcionalidades?
- 📝 **Melhorar documentação** - Documentação nunca é demais
- 🔧 **Corrigir bugs** - Veja nossas issues abertas
- ✨ **Adicionar features** - Implemente novas funcionalidades
- 🧪 **Escrever testes** - Aumente a cobertura de testes

## 🐛 Reportando Bugs

Ao reportar um bug, siga estes passos:

### 1. Verifique Issues Existentes

Antes de abrir uma nova issue, verifique se o bug já não foi reportado em [Issues](https://github.com/galafis/Anomaly-Detection-System/issues).

### 2. Crie uma Issue Detalhada

Use o template de bug report e inclua:

- **Título claro**: Descreva o problema em poucas palavras
- **Descrição**: Explique o que aconteceu
- **Passos para reproduzir**:
  ```
  1. Execute `python src/api/app.py`
  2. Faça requisição POST para `/predict`
  3. Veja o erro...
  ```
- **Comportamento esperado**: O que deveria acontecer
- **Comportamento atual**: O que realmente aconteceu
- **Screenshots/Logs**: Se aplicável
- **Ambiente**:
  - SO: [e.g., Ubuntu 22.04]
  - Python: [e.g., 3.9.7]
  - Node.js: [e.g., 18.0.0]
  - Versão do projeto: [e.g., 1.0.0]

### 3. Labels Sugeridas

- `bug` - Algo não está funcionando
- `critical` - Erro crítico que impede uso
- `help wanted` - Precisa de ajuda da comunidade

## 💡 Sugerindo Melhorias

Para sugerir uma melhoria:

### 1. Abra uma Issue

Crie uma issue com a tag `enhancement` incluindo:

- **Problema**: Que problema a melhoria resolve?
- **Solução proposta**: Como você sugere resolver?
- **Alternativas**: Considerou outras abordagens?
- **Contexto adicional**: Screenshots, exemplos, etc.

### 2. Discussão

Aguarde feedback da comunidade antes de implementar.

---

## ⚙️ Configuração do Ambiente

### 1. Fork e Clone

```bash
# Fork o repositório no GitHub, então:
git clone https://github.com/SEU-USUARIO/Anomaly-Detection-System.git
cd Anomaly-Detection-System
```

### 2. Configurar Ambiente de Desenvolvimento

#### Backend (Python)

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Instalar ferramentas de desenvolvimento
pip install black flake8 pylint pytest pytest-cov
```

#### Frontend (React)

```bash
cd frontend
npm install --legacy-peer-deps
```

### 3. Configurar Git Hooks (Opcional)

```bash
# Criar pre-commit hook para formatar código
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
black src/ tests/
git add -u
EOF

chmod +x .git/hooks/pre-commit
```

---

## 🔄 Processo de Pull Request

### 1. Criar Branch

```bash
# Para nova feature
git checkout -b feature/nome-da-feature

# Para correção de bug
git checkout -b fix/nome-do-bug

# Para documentação
git checkout -b docs/descricao
```

### 2. Desenvolver

- Escreva código limpo e bem documentado
- Siga os padrões do projeto
- Adicione testes para novas funcionalidades
- Atualize a documentação conforme necessário

### 3. Testar

```bash
# Backend
export PYTHONPATH=$PYTHONPATH:$(pwd)
python -m pytest tests/ -v --cov=src

# Frontend
cd frontend
npm run build
npm run lint
```

### 4. Formatar Código

```bash
# Python
black src/ tests/
flake8 src/ tests/ --max-line-length=120

# Frontend
cd frontend
npm run lint -- --fix
```

### 5. Commit

Use mensagens de commit descritivas seguindo [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Formato: <tipo>(<escopo>): <descrição>

git commit -m "feat(api): adiciona endpoint de estatísticas"
git commit -m "fix(detector): corrige threshold de anomalia"
git commit -m "docs(api): atualiza exemplos de uso"
git commit -m "test(api): adiciona testes para /predict"
git commit -m "refactor(services): simplifica lógica de detecção"
```

**Tipos de commit:**
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação (não afeta código)
- `refactor`: Refatoração
- `test`: Testes
- `chore`: Tarefas gerais, build, etc.

### 6. Push e Pull Request

```bash
# Push para seu fork
git push origin feature/nome-da-feature

# Abra PR no GitHub
# - Título claro e descritivo
# - Descrição detalhada das mudanças
# - Referência a issues relacionadas (#123)
# - Screenshots/GIFs se aplicável
```

### 7. Code Review

- Responda aos comentários
- Faça as alterações solicitadas
- Mantenha o PR atualizado com a branch main

---

## 📏 Padrões de Código

### Python

#### Style Guide

- Seguir [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Usar Black para formatação automática
- Máximo 120 caracteres por linha

#### Exemplos

```python
# ✅ BOM
def detect_anomaly(features: List[float]) -> Dict[str, Any]:
    """
    Detecta anomalias em features fornecidas.
    
    Args:
        features: Lista de valores numéricos
        
    Returns:
        Dicionário com resultado da detecção
    """
    if not validate_features(features):
        raise ValueError("Features inválidas")
    
    return {"is_anomaly": False, "confidence": 0.95}


# ❌ RUIM
def detect(f):
    if not f: raise ValueError("Invalid")
    return {"anomaly": False}
```

#### Imports

```python
# Ordem de imports:
# 1. Standard library
import os
import json
from datetime import datetime

# 2. Third-party
import numpy as np
from flask import Flask, jsonify

# 3. Local
from src.models.data_models import AnomalyResult
from src.services.detector import Detector
```

### JavaScript/React

#### Style Guide

- Seguir [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Usar ESLint para validação
- 2 espaços para indentação

#### Exemplos

```javascript
// ✅ BOM
const DetectionComponent = ({ features, onDetect }) => {
  const [result, setResult] = useState(null);
  
  const handleDetection = async () => {
    const response = await detectAnomaly(features);
    setResult(response);
  };
  
  return (
    <div className="detection-panel">
      <button onClick={handleDetection}>Detectar</button>
      {result && <ResultDisplay data={result} />}
    </div>
  );
};

// ❌ RUIM
function DetectionComponent(props) {
    var r;
    return <div><button onClick={()=>{r=detect(props.f)}}>Detect</button></div>
}
```

---

## 🧪 Testes

### Backend (Python)

```python
import unittest
from src.api.simple_app import app, AnomalyDetector

class TestAnomalyDetection(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.detector = AnomalyDetector()
    
    def test_valid_prediction(self):
        """Testa predição com dados válidos"""
        features = [1.0] * 1000
        result = self.detector.predict(features)
        
        self.assertIsInstance(result, dict)
        self.assertIn('is_anomaly', result)
        self.assertIn('confidence', result)
```

### Frontend (React)

```javascript
import { render, screen, fireEvent } from '@testing-library/react';
import DetectionPanel from './DetectionPanel';

test('renders detection button', () => {
  render(<DetectionPanel />);
  const button = screen.getByText(/detectar/i);
  expect(button).toBeInTheDocument();
});
```

### Executar Testes

```bash
# Backend - todos os testes
pytest tests/ -v

# Backend - com coverage
pytest tests/ --cov=src --cov-report=html

# Frontend
cd frontend
npm test
```

---

## 📚 Documentação

### Docstrings (Python)

Use Google Style docstrings:

```python
def calculate_score(features: np.ndarray, threshold: float = 0.5) -> float:
    """
    Calcula score de anomalia.
    
    Args:
        features: Array numpy com features
        threshold: Limite para classificação (default: 0.5)
        
    Returns:
        Score de anomalia entre 0 e 1
        
    Raises:
        ValueError: Se features estiver vazio
        
    Examples:
        >>> features = np.array([1.0, 2.0, 3.0])
        >>> score = calculate_score(features)
        >>> print(score)
        0.75
    """
    if len(features) == 0:
        raise ValueError("Features não pode estar vazio")
    
    return min(np.abs(features).mean() / threshold, 1.0)
```

### JSDoc (JavaScript)

```javascript
/**
 * Detecta anomalias em features fornecidas
 * 
 * @param {number[]} features - Array com 1000 valores numéricos
 * @returns {Promise<Object>} Resultado da detecção
 * @throws {Error} Se features for inválido
 * 
 * @example
 * const features = Array(1000).fill(0).map(() => Math.random());
 * const result = await detectAnomaly(features);
 * console.log(result.is_anomaly);
 */
async function detectAnomaly(features) {
  // implementação
}
```

### Atualizar Documentação

Ao adicionar novas funcionalidades, atualize:

- `README.md` - Visão geral e exemplos
- `docs/API.md` - Novos endpoints
- `docs/ARCHITECTURE.md` - Mudanças arquiteturais
- `docs/DEVELOPMENT.md` - Novos processos de dev
- `examples/README.md` - Novos exemplos

---

## 📜 Código de Conduta

Este projeto adere a um código de conduta para garantir um ambiente acolhedor e inclusivo para todos.

### Nossos Padrões

**Comportamentos esperados:**
- ✅ Ser respeitoso com diferentes pontos de vista
- ✅ Aceitar críticas construtivas
- ✅ Focar no que é melhor para a comunidade
- ✅ Mostrar empatia com outros membros

**Comportamentos inaceitáveis:**
- ❌ Uso de linguagem sexualizada ou imagens
- ❌ Trolling, comentários insultuosos
- ❌ Assédio público ou privado
- ❌ Publicar informações privadas de outros

### Aplicação

Instâncias de comportamento abusivo podem ser reportadas para [gabriel.lafis@example.com](mailto:gabriel.lafis@example.com). Todas as reclamações serão revisadas e investigadas.

Leia o [Código de Conduta completo](CODE_OF_CONDUCT.md).

---

## 🏆 Reconhecimento

Contribuidores serão reconhecidos em:

- Lista de contribuidores no README
- Release notes quando aplicável
- Agradecimentos especiais para contribuições significativas

---

## 📞 Precisa de Ajuda?

- 💬 Abra uma [Discussion](https://github.com/galafis/Anomaly-Detection-System/discussions)
- 📧 Entre em contato: gabriel.lafis@example.com
- 📖 Leia a [documentação](docs/)

---

## 📝 Checklist para Contributors

Antes de enviar seu PR, verifique:

- [ ] Código segue os padrões do projeto
- [ ] Todos os testes estão passando
- [ ] Novos testes foram adicionados (se aplicável)
- [ ] Documentação foi atualizada
- [ ] Código foi formatado (Black/ESLint)
- [ ] Commits seguem padrão de mensagens
- [ ] PR tem descrição clara
- [ ] Issues relacionadas foram referenciadas

---

**Obrigado por contribuir! 🎉**

*Este projeto é mantido por Gabriel Demetrios Lafis e pela comunidade open source.*

