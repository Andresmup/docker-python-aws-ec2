import pandas as pd
import json
import os
import time
from kafka import KafkaProducer
import argparse
from aws_msk_iam_sasl_signer import MSKAuthTokenProvider

class MSKTokenProvider():
    def token(self):
        token, _ = MSKAuthTokenProvider.generate_auth_token('us-east-1')
        return token

def main(topic, bootstrap_servers, n_samples):
    tp = MSKTokenProvider()

    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        security_protocol='SASL_SSL',
        sasl_mechanism='OAUTHBEARER',
        sasl_oauth_token_provider=tp,
    )

    df_ecommerce_sale_report = pd.read_csv("https://raw.githubusercontent.com/Andresmup/ArchivosDataScience/main/ecommerce_sale_report.csv", index_col="index", low_memory=False)
    df_ecommerce_sample = df_ecommerce_sale_report.sample(n=int(n_samples), random_state=44)

    for index, row in df_ecommerce_sample.iterrows():
        data = {}
        for column, value in row.items():
            if pd.isna(value):  # Convertir NaN a None
                value = None
            elif column == 'ship-postal-code':  # Convertir ship-postal-code a cadena
                value = str(value)
            data[column] = value
        
        producer.send(topic, json.dumps(data).encode('utf-8'))
        time.sleep(0.1)

    producer.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Procesar datos y enviarlos a Kafka')
    parser.add_argument('--topic', type=str, help='Nombre del topic de Kafka')
    parser.add_argument('--bootstrap_servers', type=str, help='Servidores de bootstrap de Kafka')
    parser.add_argument('--n_samples', type=int, help='Numero muestras')

    args = parser.parse_args()

    topic = args.topic or os.environ.get('KAFKA_TOPIC')
    bootstrap_servers = args.bootstrap_servers or os.environ.get('KAFKA_BOOTSTRAP_SERVERS').split(',')
    n_samples = args.n_samples or os.environ.get('N_SAMPLES')

    main(topic, bootstrap_servers, n_samples)