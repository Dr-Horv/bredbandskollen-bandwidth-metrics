#!/usr/bin/python3

from prometheus_client import start_http_server, Gauge, Counter
import random
import time
import subprocess
import logging

MIN_DELAY_BETWEEN_MEASSUREMENTS_IN_SECONDS = 3600*4 # 4 hours
RANDOM_DELAY_FACTOR_IN_SECONDS = 60 * 30 # 30 minutes

LATENCY_GAUGE = Gauge('latency', 'Response time in ms')
DOWNLOAD_GAUGE = Gauge('download_speed', 'Speed of download in Mbit/s')
UPLOAD_GAUGE = Gauge('upload_speed', 'Speed of upload in Mbit/s')
MEASSUREMENTS_COUNTER = Counter('meassurements', 'Times meassured')

LATENCY_TOTAL = 0.0
DOWNLOAD_TOTAL = 0.0
UPLOAD_TOTAL = 0.0
MEASSUREMENTS = 0.0

def meassure_bandwidth():
    global LATENCY_TOTAL, DOWNLOAD_TOTAL, UPLOAD_TOTAL, MEASSUREMENTS

    logging.info("Starting meassure...")
    process = subprocess.run(['bbk_cli','--server=gbg4.bredbandskollen.se', "--quiet"], check=True, stdout=subprocess.PIPE, universal_newlines=True)
    output = process.stdout
    logging.info("Meassurment output %s" % output.rstrip())
    (latency, download, upload) = map(lambda x: float(x),output.split(" ")[:3])

    MEASSUREMENTS += 1
    MEASSUREMENTS_COUNTER.inc()

    LATENCY_GAUGE.set_to_current_time()
    LATENCY_GAUGE.set(latency)
    LATENCY_TOTAL += latency

    DOWNLOAD_GAUGE.set_to_current_time()
    DOWNLOAD_GAUGE.set(download)
    DOWNLOAD_TOTAL += download

    UPLOAD_GAUGE.set_to_current_time()
    UPLOAD_GAUGE.set(upload)
    UPLOAD_TOTAL += upload

def log_avarage():
    meassurements = float(MEASSUREMENTS)
    latency_avg = LATENCY_TOTAL/meassurements
    download_avg = DOWNLOAD_TOTAL/meassurements
    upload_avg = UPLOAD_TOTAL/meassurements
    logging.info("Latency avg: %.2f Download avg: %.2f Upload avg: %.2f Total meassurements: %d" % (latency_avg, download_avg, upload_avg, MEASSUREMENTS))


if __name__ == '__main__':
    logging.basicConfig(
        filename='bandwidth.log',
        level=logging.INFO,
        format='%(asctime)s %(message)s')
    # Start up the server to expose the metrics.
    start_http_server(8999)
    while True:
        meassure_bandwidth()
        log_avarage()
        time.sleep(MIN_DELAY_BETWEEN_MEASSUREMENTS_IN_SECONDS + random.randint(0, RANDOM_DELAY_FACTOR_IN_SECONDS))
