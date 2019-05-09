import click

import pystache


@click.group()
def app():
    pass


@app.command()
@click.option("--dataset")
@click.option("--tables-list")
def oracle(dataset, tables_list):
    job_yaml = """
    - name: oracle-everwin-{{table_name}}
    image:
      repository: eu.gcr.io/global-finance-dashboard/nautilus-connectors-kit
      tag: latest
    schedule: "*/5 * * * *"
    args:
      - "oracle"
      - "--gcs-bucket"
      - "raw"
      - "--gcs-folder"
      - {{ dataset_name }}
      - "--bq-dataset"
      - {{ dataset_name }}
      - "--bq-table"
      - {{ table_name }}
      - "--oracle-credentials"
      - "oracle.json"
      - "--oracle-tables"
      - {{ table_name }}
    volumes:
    - name: ingestion-secrets
      secret:
            secretName: ingestion-secrets
            items:
            - key: oracle.json
              path: oracle.json
            - key: google_credentials.json
              path: google_credentials.json
    """

    for table in tables_list.strip().split(","):
        print pystache.render(job_yaml, {"dataset_name": dataset, "table_name": table.lower()})


@app.command()
@click.option("--dataset")
@click.option("--tables-list")
def mysql(dataset, tables_list):
    job_yaml = """
    - name: mysql-{{dataset_name}}-{{table_name_normalize}}
    image:
      repository: eu.gcr.io/global-finance-dashboard/nautilus-connectors-kit
      tag: latest
    schedule: "*/5 * * * *"
    args:
      - "mysql"
      - "--gcs-bucket"
      - "raw"
      - "--gcs-folder"
      - {{ dataset_name }}
      - "--bq-dataset"
      - {{ dataset_name }}
      - "--bq-table"
      - {{ table_name }}
      - "--mysql-credentials"
      - "mysql.json"
      - "--mysql-tables"
      - {{ table_name }}
    volumes:
    - name: ingestion-secrets
      secret:
          secretName: ingestion-secrets
          items:
          - key: mysql.json
            path: mysql.json
          - key: google_credentials.json
            path: google_credentials.json
    """

    for table in tables_list.strip().split(","):
        print pystache.render(job_yaml, {"dataset_name": dataset, "table_name": table.lower(), "table_name_normalize": table.lower().replace('_', '-')})

if __name__ == '__main__':
    app()
