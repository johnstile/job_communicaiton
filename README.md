# job_communicaiton
Implement communication between boss and worker subprocess

## Message queue  
```.
This is an Object-based Message Queue system

Pulls queue processing logic out of the boss and worker code.

It makes it easier to add a new message type.
It is better than string parsing (to figure out message types).
It uses meaningful variable names (instead of list indices, for multiple workers)

The READER implements the handler
The WRITER writes the proper message for the handler
The message queue subclasses the generic MessageQueue with a defined handler and message type
```

## Layout
```.
Use virtualenv for isolated python interpreter

class Boss will create Workers
class Worker will run some process 
class QueueMessage, and subclasses will define the communicaiton 
Worker and boss will communication over QueueMessage subclasses
```
