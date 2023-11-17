import os
from kubernetes import client, config

namespace = os.getenv("NAMESPACE")
older_then = os.getenv("OLDER_THEN")


def get_deployments_with_creation_time():
    config.load_incluster_config()
    api_instance = client.AppsV1Api()
    deployment_list = api_instance.list_namespaced_deployment(namespace=namespace)

    deployments_info = {}

    for deployment in deployment_list.items:
        # Extracting deployment name
        deployment_name = deployment.metadata.name

        # Extracting creation timestamp
        creation_time = deployment.metadata.creation_timestamp

        # Storing in the dictionary
        deployments_info[deployment_name] = creation_time

    return deployments_info


if __name__ == '__main__':
    deployments = get_deployments_with_creation_time()
    print(deployments)
