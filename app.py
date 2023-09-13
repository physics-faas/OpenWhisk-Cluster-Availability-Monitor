import time
import logging
from collections import deque
from datetime import datetime, timedelta
import threading
import requests
from functions import ow_invocation, get_cluster_names, ow_registration

# Setting up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Deque will store success and failure counts over the past week
# Each item in deque is a tuple (datetime, success_boolean)
cluster_names = get_cluster_names()  # get the list of cluster names dynamically
clusters_stats = {cluster: deque(maxlen=10080) for cluster in cluster_names}
previous_scores = {cluster: 0 for cluster in cluster_names}

def test_cluster_availability():
    while True:
        for cluster in get_cluster_names():

            r = ow_invocation('ClusterAvailabilityMonitor', cluster, {'name': 'George'})
            if r.status_code == 404:
                ow_registration(cluster, memory=128)
                r = ow_invocation('ClusterAvailabilityMonitor', cluster, {'name': 'George'})
            if r.status_code == 200:
                clusters_stats[cluster].append((datetime.now(), True))
            else:
                logger.error(f"Error {r.status_code} while checking {cluster}")
                clusters_stats[cluster].append((datetime.now(), False))
                continue

            logger.info(f"Availability check for {cluster} completed successfully.")
        # sleep for a minute before checking again
        time.sleep(60)


def calculate_availability_score():
    while True:
        needs_update = False
        for cluster_name, stats in clusters_stats.items():
            one_week_ago = datetime.now() - timedelta(weeks=1)
            # Filter out the stats of the last week
            recent_stats = [s for t, s in stats if t > one_week_ago]
            if recent_stats:  # Avoid division by zero
                score = sum(recent_stats) / len(recent_stats) * 100
                if score != previous_scores.get(cluster_name):
                    previous_scores[cluster_name] = score
                    needs_update = True
        if needs_update:
            logger.info(f"Updated Availability scores:{previous_scores}")
        time.sleep(60)


if __name__ == '__main__':
    # start the test_cluster_availability thread
    threading.Thread(target=test_cluster_availability).start()
    # start the calculate_availability_score thread
    threading.Thread(target=calculate_availability_score).start()


