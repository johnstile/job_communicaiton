# job_communicaiton
Implement communication between parent and subprocess

## Message queue  
```.
Object-based Message Queue system
Use a class to pull queue processing logic out of the middle of the boss and worker code.

It makes it easier to add a new message type.
It is better than string parsing (to figure out message types).
It uses meaningful variable names (instead of list indices, for multiple workers)

The READER implements the handler
The WRITER writes the proper message for the handler for the subclass
The message queue creates a subclass of the generic message queue with a defined handler and message type
```

## Layout
```.
Use virtualenv for isolated python interpreter

class Boss will create Workers
class Worker will run some process 
class QueueMessage will be the base class
Worker and boss will communicate over QueueMessage subclasses
```
