"""
publisher.py
Simula a Estação Submersa (ESP32 + Jetson Nano) publicando dados
ambientais periódicos, heartbeat de status e eventos de detecção
do peixe-leão (Pterois volitans) em um broker MQTT público (HiveMQ),
como prova de conceito da Atividade 2.

Uso:
    pip install -r requirements.txt
    python publisher.py
"""

import json
import random
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
BROKER_HOST = "broker.hivemq.com"
BROKER_PORT = 1883
ESTACAO_ID = "gsra-01"  # Grande Sistema de Recifes da Amazônia, estação 01
LAT, LON = 0.9167, -49.8833  # ponto de referência aproximado na foz do Amazonas

TOPIC_DETECCAO = f"pterois/{ESTACAO_ID}/deteccao"
TOPIC_AMBIENTE = f"pterois/{ESTACAO_ID}/ambiente"
TOPIC_STATUS = f"pterois/{ESTACAO_ID}/status"
TOPIC_ALERTA = f"pterois/{ESTACAO_ID}/alerta"

AMBIENTE_INTERVALO_S = 10   # reduzido para fins de simulação (produção: 300 s / 5 min)
STATUS_INTERVALO_S = 15     # reduzido para fins de simulação (produção: 60 s)
LIMIAR_CONFIANCA = 0.75     # confiança mínima do modelo YOLO para gerar alerta


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def ler_sensores_simulado():
    """Simula as leituras do ESP32 (DS18B20, EZO-EC, turbidez, Bar30)."""
    return {
        "temperatura_c": round(random.uniform(26.0, 29.5), 2),
        "salinidade_ppt": round(random.uniform(18.0, 34.0), 2),  # baixa por influência da pluma amazônica
        "turbidez_ntu": round(random.uniform(5.0, 40.0), 2),
        "profundidade_m": round(random.uniform(15.0, 25.0), 2),
    }


def detectar_peixe_leao_simulado():
    """Simula a saída do modelo YOLO rodando no Jetson Nano."""
    if random.random() < 0.25:  # ~25% de chance de "detecção" a cada checagem, só para a PoC
        return {
            "confianca": round(random.uniform(0.6, 0.98), 2),
            "individuos": random.randint(1, 3),
        }
    return None


def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"[publisher] conectado ao broker (rc={reason_code})")


def publicar_status(client, online=True):
    payload = {
        "estacao_id": ESTACAO_ID,
        "timestamp": now_iso(),
        "status": "online" if online else "offline",
        "bateria_pct": round(random.uniform(55, 100), 1),
    }
    client.publish(TOPIC_STATUS, json.dumps(payload), qos=1, retain=True)
    print(f"[status] {payload}")


def publicar_ambiente(client):
    payload = {
        "estacao_id": ESTACAO_ID,
        "timestamp": now_iso(),
        **ler_sensores_simulado(),
    }
    client.publish(TOPIC_AMBIENTE, json.dumps(payload), qos=0)
    print(f"[ambiente] {payload}")


def publicar_deteccao_e_alerta(client, deteccao):
    payload = {
        "estacao_id": ESTACAO_ID,
        "timestamp": now_iso(),
        "lat": LAT,
        "lon": LON,
        "individuos": deteccao["individuos"],
        "confianca": deteccao["confianca"],
        "imagem_url": None,  # opcional: URL de imagem comprimida em storage (S3)
    }
    client.publish(TOPIC_DETECCAO, json.dumps(payload), qos=1)
    print(f"[deteccao] {payload}")

    if deteccao["confianca"] >= LIMIAR_CONFIANCA:
        alerta = {
            "estacao_id": ESTACAO_ID,
            "timestamp": now_iso(),
            "mensagem": "Peixe-leão detectado com alta confiança — remoção dirigida recomendada",
            "lat": LAT,
            "lon": LON,
            "confianca": deteccao["confianca"],
        }
        client.publish(TOPIC_ALERTA, json.dumps(alerta), qos=2)
        print(f"[ALERTA] {alerta}")


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"estacao-{ESTACAO_ID}")
    client.will_set(TOPIC_STATUS, json.dumps({"estacao_id": ESTACAO_ID, "status": "offline"}),
                     qos=1, retain=True)  # Last Will and Testament
    client.on_connect = on_connect
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_start()

    ultimo_ambiente = 0
    ultimo_status = 0

    try:
        while True:
            agora = time.time()

            if agora - ultimo_ambiente >= AMBIENTE_INTERVALO_S:
                publicar_ambiente(client)
                ultimo_ambiente = agora

            if agora - ultimo_status >= STATUS_INTERVALO_S:
                publicar_status(client, online=True)
                ultimo_status = agora

            deteccao = detectar_peixe_leao_simulado()
            if deteccao:
                publicar_deteccao_e_alerta(client, deteccao)

            time.sleep(3)
    except KeyboardInterrupt:
        publicar_status(client, online=False)
        client.loop_stop()
        client.disconnect()
        print("[publisher] encerrado")


if __name__ == "__main__":
    main()
