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


class QuitMessage(QueueMessage):
    """Worker tells Boss it is ending"""
    def __init__(self, sender_id, this_exit_code):
        self.worker_id = sender_id 
        self.this_exit_code = this_exit_code

    def handle(self, receiver):
        receiver.on_quit(self.sender_id, self.this_exit_code)


class LogMessage(QueueMessage):
    """Worker tells Boss to write to it's log"""
    def __init__(self, sender_id, log_level, msg):
        self.sender_id = sender_id
        self.log_level = log_level
        self.msg = msg

    def handle(self, receiver):
        receiver.on_log(self.sender_id, self.log_level, self.msg)


class StatusMessage(QueueMessage):
    """Worker<->Boss status messages"""
    def __init__(self, sender_id, data):
        self.sender_id = sender_id
        self.data = data

    def handle(self, receiver):
        # Promissed method implemented in receiver
        receiver.on_status(self.sender_id, self.data)

