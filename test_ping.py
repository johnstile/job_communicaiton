#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Call ping command
"""
import time
import platform
import subprocess
import retrying
import logging

__author__ = "John Stile"


class PingException(Exception):
    """Custom exception for output of ping"""
    pass


log = logging.getLogger('ping')


def ping(address, ipv_type, network_interface=None, timeout=60, num_packets=1):
    """
    Function to ping either an IPv4 or IPv6 address.
    ipv_type can either be 4 (IPv4) or 6 (IPv6).
    """

    response = None
    cmd = None
    elapsed_time = -1

    if platform.system() == "Windows":
        '''
        -6: force IPv6
        -n: number of packets to send
        -w: timeout, in milliseconds
        '''
        timeout *= 1000

        if ipv_type == 4:
            cmd = [
                "ping",
                "-n", "{}".format(num_packets),
                "-w", "{}".format(timeout),
                "{}".format(address)
            ]

        elif ipv_type == 6:
            if '%' in address:
                cmd = [
                    "ping", "-6",
                    "-n", "{}".format(num_packets),
                    "-w", "{}".format(timeout),
                    "{}".format(address)
                ]
            else:
                cmd = [
                    "ping", "-6",
                    "-n", "{}".format(num_packets),
                    "-w", "{}".format(timeout),
                    "{}%{}".format(address, network_interface)
                ]

    elif platform.system() == "Darwin":
        '''
        -c: number of packets to send
        -i: timeout, in seconds
        -I: network interface to use
        '''
        if ipv_type == 4:
            cmd = [
                "ping",
                "-c", "{}".format(num_packets),
                "-i", "{}".format(timeout),
                address
            ]

        elif ipv_type == 6:
            cmd = [
                "ping6",
                "-c", "{}".format(num_packets),
                "-i", "{}".format(timeout),
                "-I", network_interface,
                address
            ]

    else:
        '''
        Linux
        -c: number of packets to send
        -W: timeout, in seconds
        '''
        if ipv_type == 4:
            cmd = [
                "ping",
                "-c", "1",
                "{}".format(address)
            ]

        elif ipv_type == 6:
            if '%' in address:
                cmd = [
                    "ping6",
                    "-c", "{}".format(num_packets),
                    "{}".format(address)
                ]
            else:
                cmd = [
                    "ping6",
                    "-c", "{}".format(num_packets),
                    "{}%{}".format(address, network_interface)
                ]

    if cmd is None:
        return response, elapsed_time

    end_time = time.time() + timeout
    end_timestamp = time.time()

    while time.time() < end_time:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        stdoutdata, stderrdata = p.communicate()
        log.debug('stdout: {}, stderrdata: {}'.format(stdoutdata, stderrdata))
        response = p.returncode
        elapsed_time = time.time() - end_timestamp
        if response == 0:
            break

    return response, elapsed_time


def retry_if_ping_exception(exception):
    """Return True if we should retry (in this case when it's a socket.timeout), False otherwise"""
    log.debug("called retry_if_ping_exception: exception:{}".format(type(exception)))
    return isinstance(exception, PingException)


@retrying.retry(stop_max_delay=40000, wait_fixed=200, stop_max_attempt_number=200,
                retry_on_exception=retry_if_ping_exception)
def ping_until_down(address, ipv_type, network_interface=None, timeout=2, num_packets=1):
    """
    Ping until unit does not respond
    :param address:  string address
    :param ipv_type: int [4|6] (for ipv4 or ipv6)
    :param network_interface: string (local nic name)
    :param timeout: int (seconds)
    :param num_packets: int
    :return: Nothing
    try for 40 seconds
    sleep .2 second between each attempt
    retry 200 times
    retry on socket.timeout or test_ping.PingException
    """
    log.debug("\tPing until Down")
    start_time = time.time()
    stdout_value, elapsed_time = ping(
        address,
        ipv_type,
        network_interface,
        timeout=timeout,
        num_packets=num_packets
    )
    log.debug('stdout_value: {}, elapsed_time: {}'.format(stdout_value, elapsed_time))
    if stdout_value == 0:
        end_time = time.time() - start_time
        msg = "Host still Up after {} seconds: {}".format(end_time, address)
        raise PingException(msg)

    end_time = time.time() - start_time
    log.debug("\tHost Is Down after {} seconds: {}".format(end_time, address))


@retrying.retry(stop_max_delay=60000, wait_fixed=200, stop_max_attempt_number=300,
                retry_on_exception=retry_if_ping_exception)
def ping_until_up(address, ipv_type, network_interface=None, timeout=2, num_packets=1):
    """Ping until unit responds
        :param address:  string address
    :param ipv_type: int [4|6] (for ipv4 or ipv6)
    :param network_interface: string (local nic name)
    :param timeout: int (seconds)
    :param num_packets: int
    :return: Nothing
    try for 60 seconds
    sleep .2 second between each attempt
    retry 200 times
    retry on socket.timeout or test_ping.PingException
    """
    log.debug("\tPing until Up")
    start_time = time.time()
    stdout_value, elapsed_time = ping(
        address,
        ipv_type,
        network_interface,
        timeout=timeout,
        num_packets=num_packets
    )
    log.debug('stdout_value: {}, elapsed_time: {}'.format(stdout_value, elapsed_time))
    if stdout_value != 0:
        end_time = time.time() - start_time
        msg = "Host still Down after {} seconds: {}".format(end_time, address)
        raise PingException(msg)

    end_time = time.time() - start_time
    log.debug("\tHost Is Up after {} seconds: {}".format(end_time, address))


def main():
    """
    Main function.
    """
    print("this should pass")
    ipv6 = "fe80::9804:6f26:55fb:cdc8"
    network_interface = "wlan0"
    timeout = 60
    stdout_value, elapsed_time = ping(ipv6, 6, network_interface, timeout)

    print("stdout_value: {}".format(stdout_value))
    print( "elapsed_time: {}".format(elapsed_time))

    print("this should pass")
    ipv4 = "192.168.0.201"
    timeout = 60
    stdout_value, elapsed_time = ping(ipv4, 4)

    print("stdout_value: {}".format(stdout_value))
    print("elapsed_time: {}".format(elapsed_time))

    print("this should fail")
    ipv6 = "fe80::9804:6f26:55fb:cdc9"
    network_interface = "wlan0"
    timeout = 5
    stdout_value, elapsed_time = ping(ipv6, 6, network_interface, timeout)

    print("stdout_value: {}".format(stdout_value))
    print("elapsed_time: {}".format(elapsed_time))


if __name__ == "__main__":
    main()
