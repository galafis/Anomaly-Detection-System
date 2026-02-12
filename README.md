# 🚀 Anomaly Detection System

[![JavaScript](https://img.shields.io/badge/JavaScript-ES2024-F7DF1E.svg)](https://developer.mozilla.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000.svg)](https://flask.palletsprojects.com/)
[![scikit-learn](https://img.shields.io/badge/scikit-learn-1.4-F7931E.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[English](#english) | [Português](#português)

---

## English

### 🎯 Overview

**Anomaly Detection System** — Scalable anomaly detection system using statistical methods, isolation forests, autoencoders, and time-series analysis. Designed for monitoring infrastructure, transactions, and IoT data.

Total source lines: **7,602** across **71** files in **5** languages.

### ✨ Key Features

- **Production-Ready Architecture**: Modular, well-documented, and following best practices
- **Comprehensive Implementation**: Complete solution with all core functionality
- **Clean Code**: Type-safe, well-tested, and maintainable codebase
- **Easy Deployment**: Docker support for quick setup and deployment

### 🚀 Quick Start

#### Prerequisites
- Node.js 20+ and npm
- Docker and Docker Compose (optional)

#### Installation

1. **Clone the repository**
```bash
git clone https://github.com/galafis/Anomaly-Detection-System.git
cd Anomaly-Detection-System
```

2. **Install dependencies**
```bash
npm install
```

#### Running

```bash
npm run dev
```

## 🐳 Docker

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### 🧪 Testing

```bash
npm test
```

### 📁 Project Structure

```
Anomaly-Detection-System/
├── config/
├── docs/
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── DEVELOPMENT.md
│   └── postman_collection.json
├── examples/
│   ├── README.md
│   ├── anomaly_data.json
│   ├── normal_data.json
│   └── usage_example.py
├── frontend/
│   ├── assets/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── lib/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── components.json
│   ├── eslint.config.js
│   ├── jsconfig.json
│   ├── package-lock.json
│   ├── package.json
│   ├── pnpm-lock.yaml
│   └── vite.config.js
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── simple_api.py
│   │   └── simple_app.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── data_models.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── alert_manager.py
│   │   ├── anomaly_detector.py
│   │   ├── database_manager.py
│   │   └── simple_anomaly_detector.py
│   ├── utils/
│   │   └── __init__.py
│   └── __init__.py
├── tests/
│   └── test_app.py
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── README.md
├── analytics.R
├── docker-compose.yml
└── requirements.txt
```

### 🛠️ Tech Stack

| Technology | Usage |
|------------|-------|
| JavaScript | 52 files |
| Python | 15 files |
| CSS | 2 files |
| R | 1 files |
| HTML | 1 files |

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### 👤 Author

**Gabriel Demetrios Lafis**

- GitHub: [@galafis](https://github.com/galafis)
- LinkedIn: [Gabriel Demetrios Lafis](https://linkedin.com/in/gabriel-demetrios-lafis)

---

## Português

### 🎯 Visão Geral

**Anomaly Detection System** — Scalable anomaly detection system using statistical methods, isolation forests, autoencoders, and time-series analysis. Designed for monitoring infrastructure, transactions, and IoT data.

Total de linhas de código: **7,602** em **71** arquivos em **5** linguagens.

### ✨ Funcionalidades Principais

- **Arquitetura Pronta para Produção**: Modular, bem documentada e seguindo boas práticas
- **Implementação Completa**: Solução completa com todas as funcionalidades principais
- **Código Limpo**: Type-safe, bem testado e manutenível
- **Fácil Implantação**: Suporte Docker para configuração e implantação rápidas

### 🚀 Início Rápido

#### Pré-requisitos
- Node.js 20+ e npm
- Docker e Docker Compose (opcional)

#### Instalação

1. **Clone the repository**
```bash
git clone https://github.com/galafis/Anomaly-Detection-System.git
cd Anomaly-Detection-System
```

2. **Install dependencies**
```bash
npm install
```

#### Execução

```bash
npm run dev
```

### 🧪 Testes

```bash
npm test
```

### 📁 Estrutura do Projeto

```
Anomaly-Detection-System/
├── config/
├── docs/
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── DEVELOPMENT.md
│   └── postman_collection.json
├── examples/
│   ├── README.md
│   ├── anomaly_data.json
│   ├── normal_data.json
│   └── usage_example.py
├── frontend/
│   ├── assets/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── lib/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── components.json
│   ├── eslint.config.js
│   ├── jsconfig.json
│   ├── package-lock.json
│   ├── package.json
│   ├── pnpm-lock.yaml
│   └── vite.config.js
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── simple_api.py
│   │   └── simple_app.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── data_models.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── alert_manager.py
│   │   ├── anomaly_detector.py
│   │   ├── database_manager.py
│   │   └── simple_anomaly_detector.py
│   ├── utils/
│   │   └── __init__.py
│   └── __init__.py
├── tests/
│   └── test_app.py
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── README.md
├── analytics.R
├── docker-compose.yml
└── requirements.txt
```

### 🛠️ Stack Tecnológica

| Tecnologia | Uso |
|------------|-----|
| JavaScript | 52 files |
| Python | 15 files |
| CSS | 2 files |
| R | 1 files |
| HTML | 1 files |

### 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

### 👤 Autor

**Gabriel Demetrios Lafis**

- GitHub: [@galafis](https://github.com/galafis)
- LinkedIn: [Gabriel Demetrios Lafis](https://linkedin.com/in/gabriel-demetrios-lafis)
