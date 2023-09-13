import json
import requests
import logging
import os
import urllib3

# Disable SSL/TLS warnings
urllib3.disable_warnings()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("OW Function Registration")


def get_cluster_info(cluster_name: str):
    clusters_config = os.getenv('CLUSTERS_CONFIG', "{}")
    clusters = json.loads(clusters_config)
    ow_url = clusters[cluster_name]["OW_URL"]
    ow_creds = clusters[cluster_name]["OW_CREDS"]
    return ow_url, ow_creds


def get_cluster_names():
    clusters_config = os.getenv('CLUSTERS_CONFIG', "{}")
    clusters = json.loads(clusters_config)
    return list(clusters.keys())


def ow_registration(cluster_name, memory=128):
    code_string = "def main(params):\n\tname = params.get('value', 'World')\n\treturn {'message': 'Hello, ' + name + '!'}"

    ow_url, ow_creds = get_cluster_info(cluster_name)

    url = f" https://{ow_url}/api/v1/namespaces/guest/actions/ClusterAvailabilityMonitor?overwrite=true"
    ow_user = ow_creds.split(':')[0]
    ow_pass = ow_creds.split(':')[1]
    payload = {
        "namespace": 'guest',
        "name": 'ClusterAvailabilityMonitor',
        "exec": {
            "kind": "python:3",
            "code": code_string
        },
        "limits": {
            "memory": memory
        }
    }
    headers = {"Content-Type": "application/json"}
    logger.info(f"Registering function ClusterAvailabilityMonitor at {cluster_name}")

    try:
        response = requests.put(url, headers=headers, data=json.dumps(payload), auth=(ow_user, ow_pass), verify=False)
        response.raise_for_status()
        logger.info(f"{cluster_name}: Function ClusterAvailabilityMonitor registered successfully.")
        return response
    except requests.RequestException as e:
        logger.error(f"{cluster_name}: Failed to register function ClusterAvailabilityMonitor. Error: {e}")


def ow_invocation(name, cluster_name, payload=None, blocking=True):
    ow_url, ow_creds = get_cluster_info(cluster_name)
    ow_user = ow_creds.split(':')[0]
    ow_pass = ow_creds.split(':')[1]
    if blocking:
        url = f"https://{ow_url}/api/v1/namespaces/guest/actions/{name}?blocking=true&result=true"
    else:
        url = f"https://{ow_url}/api/v1/namespaces/guest/actions/{name}"

    headers = {"Content-Type": "application/json"}

    # Log the action initiation
    logger.info(f"{cluster_name}: Initiating action {name} with blocking set to {blocking}")

    try:
        if payload is None:
            response = requests.post(url, headers=headers, auth=(ow_user, ow_pass), verify=False)
        else:
            response = requests.post(url, headers=headers, data=json.dumps(payload), auth=(ow_user, ow_pass),
                                     verify=False)

        # Log the HTTP status of the response
        logger.info(f"{cluster_name}: Received {response.status_code} response for action {name}")

        return response
    except requests.RequestException as e:
        logger.error(f"{cluster_name}: Failed to execute action {name}. Error: {e}")
