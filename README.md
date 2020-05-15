# job_communicaiton

## Summery  
```.
Implement communication between a Boss and Worker subprocesses 
```

## About  
```.
This is a toy app that excercises a Message Queue system

Run boss.py, with an IPv4 address argument (used in ping later).
The boss starts a bunch of workers
The workers tell the boss they are Ready via the StatusMessage queue.
The boss tells the workers to BeginTest via the StatusMessage, once all workers are Ready.
The workers sned status back to the boss via the LogMessage queue. 
Finally the workers send a quit message to the boss.
When the boss has heard from each worker, they are told to start doing work.
The workers report status back to the boss
```

## Setup 
```.
1. Open console/shell in this directory
2. run setup:
  On Linux and MacOs: ./setup.bash
  On Windows: ./setup.bat
```

## Run 
```.
1. Open console/shell in this directory
2. Activate the isolated python environemtn
  . venv/bin/activate
3. Execute the script
  ./boss.py -i 192.168.0.1
```

## Message queue  
```.
This is an Object-based Message Queue system
seperating message processing logic out of the boss and worker code.

It makes it easier to add a new message type.
It is better than string parsing (to figure out message types).
It uses meaningful variable names (instead of list indices, for multiple workers)

The MessageQueue subclasses defines the handler name and message type
The READER implements the handler
The WRITER writes the proper message for the subclasses
```
