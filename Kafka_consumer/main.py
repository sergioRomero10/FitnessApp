import datetime
import json
import time

from kafka import KafkaConsumer
import os

from pymongo import MongoClient

# Se hace una pausa de 30 segundos para esperar a que otros componentes consumidores estén listos
#Quitar sleep
time.sleep(30)
print("Empieza")

# Servidores de Kafka
KAFKA_SERVERS = f"{os.environ.get('KAFKA_HOST')}:{os.environ.get('KAFKA_PORT')}"
consumer = KafkaConsumer(
    'data',
    bootstrap_servers=[KAFKA_SERVERS],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    auto_commit_interval_ms= 1000,
    group_id='greenlake-checker-group'
)

cliente = MongoClient("mongodb://mongodb:27017/")
base_de_datos = cliente['CaloriasDB']
coleccion = base_de_datos['CaloriasCollection']
print("va bien")
for message in consumer:
    row = json.loads(message.value.decode('utf-8'))
    print(row)
    #Convertir valores en minúsculas
    row = {key : value.lower() for key, value in row.items()}
    # Buscar si ya existe esa comida
    existing_doc = coleccion.find_one({"FoodItem": row["FoodItem"]})

    # Si existe, comprobar si hay cambios y actualizar el registro en caso de que haya cambios
    if existing_doc:
        has_changes = False

        for field in row:
            # Comprobar si el valor del campo ha cambiado
            if row.get(field) != existing_doc.get(field):
                has_changes = True
                break

        if has_changes:
            # Actualizar la fecha del registro
            row["RegisterDay"] = datetime.datetime.now()
            coleccion.replace_one({"FoodItem": row["FoodItem"]}, row)

    # Si no existe, insertar la nueva comida
    else:
        row["RegisterDay"] = datetime.datetime.now()
        coleccion.insert_one(row)

