"""
subscriber.py
Simula os assinantes da plataforma em nuvem (equivalente ao AWS IoT
Core / dashboard web / app mobile) recebendo dados da(s) estação(ões)
submersas via broker MQTT público (HiveMQ), como prova de conceito
da Atividade 2.

Uso:
    pip install -r requirements.txt
    python subscriber.py
"""

import json

import paho.mqtt.client as mqtt

BROKER_HOST = "broker.hivemq.com"
BROKER_PORT = 1883

# wildcard: escuta todas as estações da rede (ex.: gsra-01, gsra-02, ...)
TOPIC_FILTER = "pterois/+/#"


def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"[subscriber] conectado ao broker (rc={reason_code})")
    client.subscribe(TOPIC_FILTER, qos=1)
    print(f"[subscriber] inscrito em: {TOPIC_FILTER}")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
    except json.JSONDecodeError:
        payload = msg.payload.decode()

    partes = msg.topic.split("/")
    # pterois/{estacao_id}/{tipo}
    tipo = partes[2] if len(partes) > 2 else "desconhecido"

    if tipo == "alerta":
        print(f"\n🚨 [ALERTA PUSH] tópico={msg.topic}\n    {payload}\n")
    elif tipo == "deteccao":
        print(f"📍 [DETECÇÃO] tópico={msg.topic}\n    {payload}")
    elif tipo == "ambiente":
        print(f"🌡️  [AMBIENTE] tópico={msg.topic}\n    {payload}")
    elif tipo == "status":
        print(f"💓 [STATUS] tópico={msg.topic}\n    {payload}")
    else:
        print(f"[MSG] tópico={msg.topic}\n    {payload}")


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="dashboard-subscriber-sim")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_forever()


if __name__ == "__main__":
    main()
