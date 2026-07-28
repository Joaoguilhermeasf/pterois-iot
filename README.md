# pterois-iot — Monitoramento IoT do Peixe-leão no GSRA

Projeto acadêmico da disciplina de Internet das Coisas (IoT) — UFG/INF.
Rede de estações submersas com visão computacional na borda para detecção
precoce do peixe-leão (*Pterois volitans*) no Grande Sistema de Recifes da
Amazônia (GSRA), com comunicação via MQTT.

**Grupo:** Alexandre Pedroza, João Guilherme Faria, Lucca Magnino, Sophia Luna

## Estrutura do repositório

```
pterois-iot/
├── README.md
├── docs/
│   ├── atividade1-planejamento.pdf
│   ├── atividade2-mqtt.pdf
│   └── diagrama-arquitetura-mqtt.png
├── src/
│   ├── publisher.py        # simula a estação submersa (ESP32 + Jetson Nano)
│   ├── subscriber.py       # simula o assinante (dashboard / AWS IoT Core)
│   └── requirements.txt
└── LICENSE
```

## Como rodar a simulação (PoC)

A prova de conceito usa o broker público **HiveMQ** (`broker.hivemq.com:1883`),
sem autenticação, apenas para validar tópicos, formato de payload e QoS antes
da integração real com o AWS IoT Core.

```bash
pip install -r src/requirements.txt

# terminal 1
python src/subscriber.py

# terminal 2
python src/publisher.py
```

## Tópicos MQTT

| Tópico | QoS | Frequência | Descrição |
|---|---|---|---|
| `pterois/{estacao_id}/deteccao` | 1 | evento (assíncrono) | Detecção do peixe-leão pelo modelo YOLO |
| `pterois/{estacao_id}/ambiente` | 0 | a cada 5 min | Temperatura, salinidade, turbidez, profundidade |
| `pterois/{estacao_id}/status` | 1 (retained) | a cada 60 s | Heartbeat da estação + Last Will and Testament |
| `pterois/{estacao_id}/alerta` | 2 | evento crítico | Notificação push quando confiança ≥ 0,75 |

## Próximos passos

- Migrar do broker público para o **AWS IoT Core** com autenticação mútua
  (certificados X.509) e políticas de acesso por dispositivo.
- Configurar **regras do IoT Core** para gravar `deteccao` e `ambiente` no
  AWS Timestream e disparar alertas via SNS/Lambda a partir de `alerta`.
- Substituir os geradores aleatórios de `publisher.py` pela leitura real
  dos sensores (ESP32) e pela inferência do modelo YOLO (Jetson Nano).

## Referência

Continuação da Atividade 1 (Planejamento de uma Solução IoT) da mesma disciplina.
# pterois-iot
# pterois-iot
