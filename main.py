import os
import re
import logging
import datetime
from kubernetes import client, config
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine, Column, String, DateTime, Integer

Base = declarative_base()
namespace = os.getenv("NAMESPACE") # The namespace in which to delete deployments, ingresses, secrets, services
older_then = int(os.getenv("OLDER_THEN")) # Older then some time

password = os.getenv("POSTGRES_PASSWORD").strip().replace("\n", "") # Postgres DB Password

engine = create_engine(f'postgresql+psycopg2://'
                       f'{os.getenv("POSTGRES_USER")}:{password}@{os.getenv("POSTGRES_HOST")}'
                       f':{os.getenv("POSTGRES_PORT")}/{os.getenv("POSTGRES_DB")}')
Session = sessionmaker(bind=engine)


# The table that is represented in Postgres
class MyTable(Base):
    __tablename__ = "notebooks"
    notebook_id = Column(String, primary_key=True)
    user_id = Column(String)
    last_accessed = Column(DateTime)
    created_at = Column(DateTime)
    description = Column(String)
    port = Column(Integer)
    notebook_type = Column(String)


# The function that gets all the ids from the database and looks for each if the creation time is before older then, and if yes than delete everything
def delete():
    config.load_incluster_config()
    api_instance = client.AppsV1Api()
    core_v1_api = client.CoreV1Api()
    networking_v1_api = client.NetworkingV1Api()

    session = Session()

    ten_days_ago = datetime.datetime.now() - datetime.timedelta(days=10)

    results = session.query(MyTable).filter(MyTable.last_accessed < ten_days_ago).all()

    notebook_ids = [result.notebook_id for result in results]

    ingress_list = networking_v1_api.list_namespaced_ingress(namespace=namespace)

    for ingress in ingress_list.items:
        ingress_name = ingress.metadata.name
        creation_time = ingress.metadata.creation_timestamp

        now = datetime.datetime.now(datetime.timezone.utc)
        x = re.search("^ingress-.*$", ingress_name)

        if x and (now - creation_time) > datetime.timedelta(days=older_then):
            if ingress_name[8:] in notebook_ids:
                try:
                    api_response = networking_v1_api.delete_namespaced_ingress(
                        name=ingress_name,
                        namespace=namespace,
                        body=client.V1DeleteOptions()
                    )
                    logging.info(f"Status: {api_response.status}")
                except client.exceptions.ApiException as e:
                    logging.error(f"Error: {e} deleting ingress!")
                

    service_list = core_v1_api.list_namespaced_service(namespace=namespace)

    for service in service_list.items:
        service_name = service.metadata.name
        creation_time = service.metadata.creation_timestamp

        now = datetime.datetime.now(datetime.timezone.utc)
        x = re.search("^service-.*$", service_name)

        if ((x and (now - creation_time) > datetime.timedelta(days=older_then)) or
                (service_name[8:] in notebook_ids and x)):
            try:
                api_response = core_v1_api.delete_namespaced_service(
                    name=service_name,
                    namespace=namespace,
                    body=client.V1DeleteOptions()
                )

                logging.info(f"Status: {api_response.status}")
            except client.exceptions.ApiException as e:
                logging.error(f"Error: {e} deleting service!")

    deployment_list = api_instance.list_namespaced_deployment(namespace=namespace)

    for deployment in deployment_list.items:
        deployment_name = deployment.metadata.name
        creation_time = deployment.metadata.creation_timestamp

        now = datetime.datetime.now(datetime.timezone.utc)
        x = re.search("^deployment-.*$", deployment_name)

        if ((x and (now - creation_time) > datetime.timedelta(days=older_then)) or
                (deployment_name[11:] in notebook_ids and x)):
            try:
                api_response = api_instance.delete_namespaced_deployment(
                    name=deployment_name,
                    namespace=namespace,
                    body=client.V1DeleteOptions(
                        propagation_policy='Foreground',
                    )
                )

                logging.info(f"Status: {api_response.status}")
            except client.exceptions.ApiException as e:
                logging.error(f"Error: {e} deleting deployment!")

    secret_list = core_v1_api.list_namespaced_secret(namespace=namespace)

    for secret in secret_list.items:
        secret_name = secret.metadata.name
        creation_time = secret.metadata.creation_timestamp

        now = datetime.datetime.now(datetime.timezone.utc)
        x = re.search("^secret-.*$", secret_name)

        if ((x and (now - creation_time) > datetime.timedelta(days=older_then)) or
                (secret_name[7:] in notebook_ids and x)):
            try:
                api_response = core_v1_api.delete_namespaced_service(
                    name=secret_name,
                    namespace=namespace,
                    body=client.V1DeleteOptions()
                )

                logging.info(f"Status: {api_response.status}")
            except client.exceptions.ApiException as e:
                logging.error(f"Error: {e} deleting secret!")

    session.close()


if __name__ == '__main__':
    delete()
