#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Object based Message Queue system
This class pulls the queue processing logic out of the middle of boss/worker code.

It makes it easier to add a new message type.
It is better than string parsing (to figure out message types).
It uses meaningful variable names (instead of list indices)

The class reading the queue implements the handler
The class writing to the queue writes the proper message for the handler subclass
"""


class QueueMessage(object):
    """Base class"""

    def handle(self, receiver):
        raise NotImplementedError

class StatusMessage(QueueMessage):
    """Worker<->Boss status messages"""
    def __init__(self, worker_id, data):
        self.worker_id = worker_id
        self.data = data

    def handle(self, receiver):
        # Promissed method implemented in receiver
        receiver.on_status(self.worker_id, self.data)

