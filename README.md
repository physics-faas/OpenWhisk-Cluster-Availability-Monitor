# OpenWhisk Cluster Availability Monitor

A service to monitor the health of OpenWhisk clusters. This application continuously checks the availability of your clusters by invoking a mock function to each registered cluster, then stores the response over time to calculate a weekly availability score. Changes in the availability score are tracked and logged accordingly. 


## Getting Started

These instructions will help you set up and run the project on your local machine or in a Docker environment.

### Prerequisites

- Python 3.8 or later
- Docker (if you wish to run the app in a container)

### Installation

#### Local Installation

1. Clone the repository to your local machine.
2. Navigate to the project directory and install the necessary Python packages using the following command:

```bash
pip install -r requirements.txt
```

#### Docker Installation
1. Make sure Docker is installed on your system.
2. Build the Docker image using the following command in the project directory:
```bash
docker build -t cluster-availability-monitor .
```
#### Ran Docker container

```bash
docker run -d -e CLUSTERS_CONFIG='{"aws": {"OW_URL": "<ow_url>","OW_CREDS": "<user>:<pass>"},"azure": {"OW_URL": "ow_url","OW_CREDS": "<ow_user>:<ow_pass>"}}' cluster-availability-monitor
```

### Usage
Once installed, the application will start monitoring the availability of the specified clusters (AWS and Azure in this case) and update the Reasoning Framework with the availability scores every minute. It will also log important information and errors in the console.

### Configuration
Before running the application, you must configure the OpenWhisk clusters to be monitored through the CLUSTERS_CONFIG environment variable. This JSON object should map cluster names to objects containing the OW_URL and OW_CREDS properties for each cluster.

### Usage
Once installed, the application will start monitoring the availability of the specified OpenWhisk clusters with the availability scores every minute. It will log important information (i.e., updates in the scores) to the console.

It can be extended to update external services requiring such info. 

To check the logs of the running Docker container, use the following command:

```bash
docker logs <CONTAINER_ID>
```
