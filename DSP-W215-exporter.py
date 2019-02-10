#!/usr/bin/env python

from prometheus_client import start_http_server, Gauge, Enum, Info
from pyW215.pyW215 import SmartPlug, ON, OFF

import time
import argparse


version = 0.10


# Parse commandline arguments
parser = argparse.ArgumentParser(
    description="D-Link DSP-W125 Wi-Fi Smart Plug Prometheus exporter v" +
    str(version))
parser.add_argument(
    "-t", "--target", metavar="<ip>", required=True,
    help="Target IP address", type=str)
parser.add_argument(
    "-f", "--frequency", metavar="<seconds>", required=False,
    help="Interval in seconds between checking measures", default=1, type=int)
parser.add_argument(
    "-p", "--port", metavar="<port>", required=False,
    help="Port for exporter to listen on", default=8210,
    type=int)
parser.add_argument(
    "-c", "--code", metavar="<code>", required=True,
    help="Secret code to access device api", type=str)
args = parser.parse_args()

# Set target IP, port and command to send
ip = args.target
listen_port = args.port
sleep_time = args.frequency
code = args.code

sp = None

# Send command and receive reply

# Create a metric to track time spent and requests made.
# Gaugage: it goes up and down, snapshot of state

REQUEST_POWER = Gauge('w125_power_watt', 'DSP-W125 Watt measure')
REQUEST_TEMP = Gauge('w125_temperature', 'DSP-W125 Temperature measure')
REQUEST_TOTAL = Gauge('w125_total', 'DSP-W125 Total energy measure')
REQUEST_STATE = Enum('w125_state', 'DSP-W125 switch status',
                     states=['ON', 'OFF', 'unknown'])


REQUEST_POWER.set_function(lambda: get_power())
REQUEST_TEMP.set_function(lambda: get_temp())
REQUEST_TOTAL.set_function(lambda: get_total())


def get_state():
    """ Get W125 switch state """
    return sp.state


def get_power():
    """ Get W125 power """
    val = sp.current_consumption
    if val == 'N/A':
        quit("Could not connect to host " + ip)
        return 0
    return val


def get_temp():
    """ Get W125 temperature """
    val = sp.temperature
    if val == 'N/A':
        quit("Could not connect to host " + ip)
        return 0
    return val


def get_total():
    """ Get W125 total energy usage """
    val = sp.total_consumption
    if val == 'N/A':
        quit("Could not connect to host " + ip)
        return 0
    return val


# Main entry point
if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(listen_port)

    # Main loop
    while True:

        sp = SmartPlug(ip, code)
        REQUEST_STATE.state(state=get_state())

        time.sleep(sleep_time)
