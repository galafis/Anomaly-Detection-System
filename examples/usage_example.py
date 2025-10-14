#!/usr/bin/env python3
"""
Exemplo de uso da API de Detecção de Anomalias
Author: Gabriel Demetrios Lafis
"""

import requests
import numpy as np
import json
import time

# Configuração da API
API_URL = "http://localhost:5000"


def check_api_status():
    """Verifica se a API está online"""
    try:
        response = requests.get(f"{API_URL}/api/status", timeout=5)
        if response.status_code == 200:
            print("✅ API está online e funcionando!")
            data = response.json()
            print(f"   Status: {data['status']}")
            print(f"   Versão: {data['version']}")
            print(f"   Modelo carregado: {data['model_loaded']}")
            return True
        else:
            print("❌ API respondeu mas com erro")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar com a API: {e}")
        return False


def detect_anomaly(features, description=""):
    """Detecta anomalia nos dados fornecidos"""
    try:
        response = requests.post(
            f"{API_URL}/predict",
            json={"features": features},
            headers={"Content-Type": "application/json"},
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            print(f"\n{'='*60}")
            print(f"Resultado da Detecção{' - ' + description if description else ''}")
            print(f"{'='*60}")
            print(f"Status: {data['status']}")
            print(f"É Anomalia? {'🔴 SIM' if data['is_anomaly'] else '🟢 NÃO'}")
            print(f"Predição: {data['prediction']:.4f}")
            print(f"Confiança: {data['confidence']:.2%}")
            print(f"Features analisadas: {data['feature_count']}")
            print(f"Timestamp: {data['timestamp']}")
            return data
        else:
            print(f"❌ Erro na requisição: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Erro ao fazer predição: {e}")
        return None


def example_1_normal_data():
    """Exemplo 1: Dados normais (distribuição padrão)"""
    print("\n" + "=" * 60)
    print("EXEMPLO 1: Dados Normais")
    print("=" * 60)

    # Gerar dados com distribuição normal
    np.random.seed(42)
    features = np.random.randn(1000).tolist()

    detect_anomaly(features, "Distribuição Normal")


def example_2_anomaly_data():
    """Exemplo 2: Dados anômalos (alta variância)"""
    print("\n" + "=" * 60)
    print("EXEMPLO 2: Dados Anômalos")
    print("=" * 60)

    # Gerar dados com alta variância (provável anomalia)
    np.random.seed(123)
    features = (np.random.randn(1000) * 100).tolist()

    detect_anomaly(features, "Alta Variância")


def example_3_batch_detection():
    """Exemplo 3: Detecção em lote"""
    print("\n" + "=" * 60)
    print("EXEMPLO 3: Detecção em Lote")
    print("=" * 60)

    results = []
    num_samples = 5

    for i in range(num_samples):
        # Alternar entre normal e anômalo
        if i % 2 == 0:
            features = np.random.randn(1000).tolist()
            label = "Normal"
        else:
            features = (np.random.randn(1000) * 50).tolist()
            label = "Potencialmente Anômalo"

        print(f"\nProcessando amostra {i+1}/{num_samples} ({label})...")
        result = detect_anomaly(features, f"Amostra {i+1}")

        if result:
            results.append(
                {
                    "sample": i + 1,
                    "is_anomaly": result["is_anomaly"],
                    "confidence": result["confidence"],
                }
            )

    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DA DETECÇÃO EM LOTE")
    print("=" * 60)
    anomalies = sum(1 for r in results if r["is_anomaly"])
    print(f"Total de amostras: {len(results)}")
    print(f"Anomalias detectadas: {anomalies}")
    print(f"Taxa de anomalias: {anomalies/len(results):.1%}")


def example_4_from_file():
    """Exemplo 4: Carregar dados de arquivo"""
    print("\n" + "=" * 60)
    print("EXEMPLO 4: Carregar Dados de Arquivo")
    print("=" * 60)

    # Tentar carregar dados de exemplo
    try:
        with open("examples/normal_data.json", "r") as f:
            data = json.load(f)
            print("Arquivo 'normal_data.json' carregado")
            detect_anomaly(data["features"], "Do arquivo normal_data.json")
    except FileNotFoundError:
        print("⚠️  Arquivo de exemplo não encontrado. Gerando dados...")
        features = np.random.randn(1000).tolist()
        detect_anomaly(features, "Dados gerados")


def example_5_performance_test():
    """Exemplo 5: Teste de performance"""
    print("\n" + "=" * 60)
    print("EXEMPLO 5: Teste de Performance")
    print("=" * 60)

    num_requests = 10
    features = np.random.randn(1000).tolist()

    print(f"Fazendo {num_requests} requisições...")
    start_time = time.time()

    success_count = 0
    for i in range(num_requests):
        try:
            response = requests.post(
                f"{API_URL}/predict",
                json={"features": features},
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            if response.status_code == 200:
                success_count += 1
        except Exception as e:
            print(f"Erro na requisição {i+1}: {e}")

    end_time = time.time()
    elapsed = end_time - start_time

    print(f"\nResultados:")
    print(f"Requisições bem-sucedidas: {success_count}/{num_requests}")
    print(f"Tempo total: {elapsed:.2f} segundos")
    print(f"Tempo médio por requisição: {elapsed/num_requests:.3f} segundos")
    print(f"Throughput: {num_requests/elapsed:.2f} req/s")


def main():
    """Função principal"""
    print("\n" + "=" * 60)
    print("EXEMPLOS DE USO - API DE DETECÇÃO DE ANOMALIAS")
    print("=" * 60)

    # Verificar se a API está online
    if not check_api_status():
        print("\n❌ A API não está disponível.")
        print("Por favor, inicie a API primeiro com:")
        print("   python src/api/simple_app.py")
        return

    # Executar exemplos
    try:
        example_1_normal_data()
        time.sleep(1)

        example_2_anomaly_data()
        time.sleep(1)

        example_3_batch_detection()
        time.sleep(1)

        example_4_from_file()
        time.sleep(1)

        example_5_performance_test()

    except KeyboardInterrupt:
        print("\n\n⚠️  Execução interrompida pelo usuário")

    print("\n" + "=" * 60)
    print("EXEMPLOS CONCLUÍDOS!")
    print("=" * 60)


if __name__ == "__main__":
    main()
