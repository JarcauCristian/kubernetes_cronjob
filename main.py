import os
import re
import datetime
from kubernetes import client, config
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine, Column, String, DateTime, Integer

Base = declarative_base()
namespace = os.getenv("NAMESPACE")
older_then = float(os.getenv("OLDER_THEN"))

engine = create_engine(f'postgresql+psycopg2://'
                       f'{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@{os.getenv("POSTGRES_HOST")}'
                       f':{os.getenv("POSTGRES_PORT")}/{os.getenv("POSTGRES_DB")}')
Session = sessionmaker(bind=engine)


class MyTable(Base):
    __tablename__ = "notebooks"
    notebook_id = Column(String, primary_key=True)
    user_id = Column(String)
    last_accessed = Column(DateTime)
    created_at = Column(DateTime)
    description = Column(String)
    port = Column(Integer)


def delete():
    config.load_incluster_config()
    api_instance = client.AppsV1Api()
    core_v1_api = client.CoreV1Api()

    session = Session()

    ten_days_ago = datetime.datetime.now() - datetime.timedelta(days=10)

    results = session.query(MyTable).filter(MyTable.last_accessed < ten_days_ago).all()

    notebook_ids = [result.notebook_id for result in results]

    service_list = core_v1_api.list_namespaced_service(namespace=namespace)

    for service in service_list.items:
        service_name = service.metadata.name
        creation_time = service.metadata.creation_timestamp

        now = datetime.datetime.now(datetime.timezone.utc)
        x = re.search("^service-.*$", service_name)

        if (x and (now - creation_time) > datetime.timedelta(days=older_then)) or (service_name[8:] in notebook_ids and x):
            api_response = core_v1_api.delete_namespaced_service(
                name=service_name,
                namespace=namespace,
                body=client.V1DeleteOptions()
            )

            print(f"Status: {api_response.status}")

    deployment_list = api_instance.list_namespaced_deployment(namespace=namespace)

    for deployment in deployment_list.items:
        deployment_name = deployment.metadata.name
        creation_time = deployment.metadata.creation_timestamp

        now = datetime.datetime.now(datetime.timezone.utc)
        x = re.search("^deployment-.*$", deployment_name)

        if (x and (now - creation_time) > datetime.timedelta(days=older_then)) or (deployment_name[11:] in notebook_ids and x):
            api_response = api_instance.delete_namespaced_deployment(
                name=deployment_name,
                namespace=namespace,
                body=client.V1DeleteOptions(
                    propagation_policy='Foreground',
                )
            )

            print(f"Status: {api_response.status}")

    secret_list = core_v1_api.list_namespaced_secret(namespace=namespace)

    for secret in secret_list.items:
        secret_name = secret.metadata.name
        creation_time = secret.metadata.creation_timestamp

        now = datetime.datetime.now(datetime.timezone.utc)
        x = re.search("^secret-.*$", secret_name)

        if (x and (now - creation_time) > datetime.timedelta(days=older_then)) or (secret_name[7:] in notebook_ids and x):
            api_response = core_v1_api.delete_namespaced_service(
                name=secret_name,
                namespace=namespace,
                body=client.V1DeleteOptions()
            )

            print(f"Status: {api_response.status}")

    session.close()


if __name__ == '__main__':
    delete()
