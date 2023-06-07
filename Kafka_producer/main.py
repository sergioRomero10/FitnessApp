import csv
import time
from kafka import KafkaProducer
import traceback
import json
import os

try:
    time.sleep(20)
    # Servidores de Kafka
    KAFKA_SERVERS = f"{os.environ.get('KAFKA_HOST')}:{os.environ.get('KAFKA_PORT')}"

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_SERVERS,
    )

    # Abrir el archivo CSV con la API
    with open('calories.csv', 'r') as file:
        # Crear un objeto lector CSV
        reader = csv.DictReader(file)

        for row in reader:
            # Envía un mensaje de Kafka con la fila a un tópico llamado 'data'
            message = json.dumps(row).encode('utf-8')
            producer.send('data', message)
            print(message)
    
    producer.flush()
    producer.close()

# En caso de haber un error durante la ejecución del código, se imprime un traceback y un mensaje con la descripción del error
except Exception as e:
    traceback.print_exc()
    print('Found unexpected error', e)
