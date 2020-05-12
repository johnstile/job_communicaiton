#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Run simultaneous workers
"""

import multiprocessing
import time
import logging
import argparse
import queue
import retrying

# Our modules
from worker import Worker
import message_queue

__author__ = 'John Stile'


class Boss(object):
    """Create workers and start
       Workers tell boss when they are ready
       Boss monitors the message queue for ready and quit
       Once all the workers are ready, boss has them all start the test command
       If any quit message has an error exit_status, boss stops all workers
       Once all workers have quit, boss terminates workers.
    """


    def __init__(self, ipv4):
        self.ipv4 = ipv4

        # set up multiprocessing logger
        multiprocessing.log_to_stderr()
        self.log = multiprocessing.get_logger()
        fh = logging.FileHandler('Boss_stdout.log')
        log_format = '%(asctime)s [%(levelname)s/%(processName)s] - %(message)s'
        formatter = logging.Formatter(log_format)
        fh.setFormatter(formatter)
        self.log.addHandler(fh)
        self.log.setLevel('INFO')
        self.log.info('Start Log')

        self.worker_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
        
        # List of of Workers
        self.workers = []

        # Store results for all workers 
        self.worker_results = {} 

        # How many times to run
        self.number_of_runs_cycles = 10

        # count total number of quit messages
        self.quit_counter = 0
        self.ready_counter = 0

        # processing queue for all DUTs
        self.queue = multiprocessing.Queue()

    def main(self):
        # Create workers, and start
        for worker_id in self.worker_ids:
            # Each worker runs one command
            w = Worker(
                self.ipv4,
                worker_id,
                queue_to_boss=self.queue,
                queue_from_boss=multiprocessing.Queue(),
                cycles=self.number_of_runs_cycles
            )

            # Add worker to our list of workers
            self.workers.append(w)

            # start Worker object run()
            w.start()

        # process messages from Works
        self.process_queue()

        #
        # Block until workers report quit
        #
        while len(self.workers):
            time.sleep(2)

        #
        # Print the result for each worker
        #
        self.log.info("Results for {} cycles".format(self.number_of_runs_cycles))
        for (worker_id, error_count) in list(self.worker_results.items()):
            if error_count == 0:
                this_log = self.log.info
            else:
                this_log = self.log.critical
            this_log("\tworker:{:>2}, error_count:{:>3}".format(worker_id, error_count))


    def process_queue(self):
        # loop until we read a 'quit' for worker, or an error
        # When all workers are ready, start the tests
        continue_test = True
        while continue_test:
            # When the number of ready messages == workers, start test
            if self.ready_counter == len(self.workers):
                self.log.info("All Workers ready, start test")

                # Send the message to start testing
                for worker in self.workers:
                    worker.queue_from_boss.put(message_queue.StatusMessage('BOSS', {'BeginTest': True}))
                self.ready_counter = False

            if self.quit_counter == len(self.workers):
                self.log.info("All Workers quit, end program")
                continue_test = False
                continue

            if not self.queue.empty():
                try:
                    msg = self.queue.get(timeout=0.001)
                    msg.handle(self)
                except queue.Empty as e:
                    self.log.warning(
                        "Queue unexpectedly Empty. {}".format(e)
                    )


    def on_status(self, worker_id, data):
        """MessageQueue: Counts the number of workers that are ready
        """
        self.log.debug("worker_id:{}, status: {}".format(worker_id, data))
        self.ready_counter += 1


    def on_quit(self, worker_id, exit_code):
        self.log.info(
            (
                "Quit received from {}, error_count: {}"
            ).format(
                worker_id,
                exit_code
            )
        )
        #
        # Store Exit code
        #
        self.worker_results[worker_id] = exit_code
        #
        # Force process to end
        #
        w = next((w for w in self.workers if w.worker_id == worker_id), None)
        if w:
            self.log.info("Calling clean_up on {}".format(worker_id))
            self.clean_up(w)


    def on_log(self, worker_id, log_level, msg):
        """MessageQueue: Log some message
        """
        self.log.info("[{}][{}] - {}".format(worker_id, log_level, msg))


    def clean_up(self, worker):
        self.log.info("Jobs should be done. Force End if not ended")

        # Must give the children enough time to end, or we kill in the middle of an snmp request.
        timeout = 100

        self.log.critical("worker:{}, exitcode:{}".format(worker.worker_id, worker.exitcode))

        end_time = time.time() + timeout
        continue_cleanup = True
        while continue_cleanup:

            if not worker.is_alive():
                continue_cleanup = False
                continue

            self.log.debug("{} is_alive".format(worker.name))

            # This should end the process
            worker.join(timeout)

            # Force quit the process
            if time.time() >= end_time:
                self.log.warning("{} did not end after {} seconds".format(
                    worker.name,
                    timeout
                ))
                self.log.warning("call terminate on {}".format(worker.name))
                worker.terminate()
                self.log.warning("call final join on {}".format(worker.name))
                worker.join()
        #
        # Remove worker from the workers list
        #
        self.workers.remove(worker)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--ipv4', '-i',
        required=True,
        help='netbooter ipv4 address'
    )
    args = parser.parse_args()

    boss = Boss(args.ipv4)
    boss.main()
