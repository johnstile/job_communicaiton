#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Worker for simultaneous opteration, communicates with the boss
"""

import multiprocessing
import logging
import queue
import retrying

# Our modules
import message_queue
from test_ping import ping

__author__ = 'John Stile'


class Worker(multiprocessing.Process):
    """
        Worker subprocess is created for each of the simultaneous commands
    """

    def __init__(
            self,
            ipv4,
            worker_id,
            cycles,
            queue_from_boss,
            queue_to_boss,
    ):
        super(Worker, self).__init__()
        self.ipv4 = ipv4
        self.queue_from_boss = queue_from_boss
        self.queue_to_boss = queue_to_boss
        self.cycles = cycles
        self.worker_id = worker_id
        self.begin_test = False
        #
        # non-pickle-able objects to be initialized in run()
        # to avoid limitation of multiprocessing on windows
        #
        self.log = None
        # Result counter
        self.error_count = 0

    def run(self):
        """"Initialize Logger and notify Boss that Worker is ready"""
        #
        # Setup log
        #
        log_file_name = "Worker_{}.log".format(self.worker_id)
        rh = logging.FileHandler(log_file_name)
        fmt = logging.Formatter("%(asctime)s (%(levelname)-8s): %(message)s")
        rh.setFormatter(fmt)
        self.log = logging.getLogger()
        self.log.setLevel('DEBUG')
        self.log.addHandler(rh)
        self.log.info("Log Initialized")
        #
        # Empty Multiprocessing queue
        #
        while not self.queue_from_boss.empty():
            self.log.debug('Inside clear() loop -- getting items from queue')
            self.queue_from_boss.get()
        #
        # Tell boss Worker is ready
        #
        self.log.info("Send Ready o Boss")
        self.queue_to_boss.put(message_queue.StatusMessage(self.worker_id, {'Ready': True}))
        #
        # Poll messages from Boss to start test
        #
        self.process_queue()
        #
        # Tell boss Worker is complete 
        #
        self.log.info("Send Complete to Boss")
        self.queue_to_boss.put(message_queue.StatusMessage(self.worker_id, {'Complete': True}))
        #
        # send quit message
        #
        self.log.info("Send Quit to Boss")
        self.queue_to_boss.put(message_queue.QuitMessage(self.worker_id, self.error_count))

    def process_queue(self):
        """Poll the message queue for BeginTest message from Boss
        When message is received, set self.begin_test to True,
        Run command.
        When command is complete, tell Boss job is done"""

        continue_test = True
        while continue_test:
            # Listen for messages from Boss
            if not self.queue_from_boss.empty():
                try:
                    self.log.debug("reading queue")
                    msg = self.queue_from_boss.get(timeout=0.001)
                    msg.handle(self)
                except queue.Empty:
                    "Queue unexpectedly empty"

            # Boss sends status message, which toggles this to true
            if self.begin_test:
                self.test()
                continue_test = False
                continue

        self.log.info("Exit while loop.")

    def on_status(self, worker_id, data):
        """Boss will send a BeginTest message once all Workers are ready"""
        self.log.debug('Status({})'.format(worker_id, data))
        if data['BeginTest']:
            self.begin_test = True

    def test(self):
        """Do command
        If command fails, terminate test"""
        self.log.info('Run Test')

        try:
            # This is how many times we run the command
            for iteration in range(1, self.cycles + 1):
                self.log.info(
                    (
                        "=====Worker: {:>2}, Iteration:{:>3}, Error Count:{:>3}===="
                    ).format(
                        self.worker_id,
                        iteration,
                        self.error_count
                    )
                )
                self.log.info('Run Command')
                self.queue_to_boss.put(
                    message_queue.LogMessage(
                        self.worker_id,
                        "INFO",
                        "run{: }".format(iteration)
                    )
                )
                try:
                    self.log.info("ipv4:{}".format(self.ipv4))
                    stdout_value, elapsed_time = ping(self.ipv4, 4, timeout=0.2)
                    self.log.info("stdout_value: {}".format(stdout_value))

                    if stdout_value != 0:
                        self.log.critical("Failed")
                        self.error_count += 1

                except retrying.RetryError as e:
                    self.log.critical("Retry FAILED. Iteration:{:>3}, Exception:{}".format(iteration, str(e)))
                    message_queue.LogMessage(
                        self.worker_id,
                        "ERROR",
                        "Retry FAILED. Iteration:{:>3}, Exception:{}".format(iteration, str(e))
                    )
                    self.error_count += 1

            # End For loop
            self.queue_to_boss.put(message_queue.QuitMessage(self.worker_id, self.error_count))

        except Exception as e:
            self.log.exception("Exception occurred: {}".format(e))
            raise
