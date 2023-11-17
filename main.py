import os
import re
import datetime
from kubernetes import client, config

namespace = os.getenv("NAMESPACE")
older_then = os.getenv("OLDER_THEN")


def get_deployments_with_creation_time():
    config.load_incluster_config()
    api_instance = client.AppsV1Api()
    deployment_list = api_instance.list_namespaced_deployment(namespace=namespace)

    for deployment in deployment_list.items:
        deployment_name = deployment.metadata.name
        creation_time = deployment.metadata.creation_timestamp

        now = datetime.datetime.now(datetime.timezone.utc)
        x = re.search("^deployment-.*$", deployment_name)
        print(now - creation_time)

    return deployments_info


if __name__ == '__main__':
    deployments = get_deployments_with_creation_time()
    print(deployments)
