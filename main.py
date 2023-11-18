import os
import re
import datetime
from kubernetes import client, config

namespace = os.getenv("NAMESPACE")
older_then = float(os.getenv("OLDER_THEN"))


def delete():
    config.load_incluster_config()
    api_instance = client.AppsV1Api()
    core_v1_api = client.CoreV1Api()
    networking_v1_api = client.NetworkingV1Api()
    deployment_list = api_instance.list_namespaced_deployment(namespace=namespace)

    for deployment in deployment_list.items:
        deployment_name = deployment.metadata.name
        creation_time = deployment.metadata.creation_timestamp

        now = datetime.datetime.now(datetime.timezone.utc)
        x = re.search("^deployment-.*$", deployment_name)

        if x and (now - creation_time) > datetime.timedelta(days=older_then):
            api_response = api_instance.delete_namespaced_deployment(
                name=deployment_name,
                namespace=namespace,
                body=client.V1DeleteOptions(
                    propagation_policy='Foreground',
                )
            )

            print(f"Status: {api_response.status}")

    service_list = core_v1_api.list_namespaced_service(namespace=namespace)

    for service in service_list.items:
        service_name = service.metadata.name
        creation_time = service.metadata.creation_timestamp

        now = datetime.datetime.now(datetime.timezone.utc)
        x = re.search("^service-.*$", service_name)

        if x and (now - creation_time) > datetime.timedelta(days=older_then):
            api_response = core_v1_api.delete_namespaced_service(
                name=service_name,
                namespace=namespace,
                body=client.V1DeleteOptions()
            )

            print(f"Status: {api_response.status}")

    secret_list = core_v1_api.list_namespaced_secret(namespace=namespace)

    for secret in secret_list.items:
        secret_name = secret.metadata.name
        creation_time = secret.metadata.creation_timestamp

        now = datetime.datetime.now(datetime.timezone.utc)
        x = re.search("^secret-.*$", secret_name)

        if x and (now - creation_time) > datetime.timedelta(days=older_then):
            api_response = core_v1_api.delete_namespaced_service(
                name=secret_name,
                namespace=namespace,
                body=client.V1DeleteOptions()
            )

            print(f"Status: {api_response.status}")
    
    ingress_list = networking_v1_api.list_namespaced_ingress(namespace=namespace)

    for ingress in ingress_list.items:
        secret_name = ingress.metadata.name
        creation_time = ingress.metadata.creation_timestamp

        now = datetime.datetime.now(datetime.timezone.utc)
        x = re.search("^secret-.*$", secret_name)

        if x and (now - creation_time) > datetime.timedelta(days=older_then):
            api_response = networking_v1_api.delete_namespaced_ingress(
                name=secret_name,
                namespace=namespace,
                body=client.V1DeleteOptions()
            )

            print(f"Status: {api_response.status}")


if __name__ == '__main__':
    delete()
