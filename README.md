# job_communicaiton

## Summery  
```.
Implement communication between a Boss and Worker subprocesses 
```

## This is a Message Queue Demonstration
```.
This is an object-based Message Queue system

It seperates message processing logic from the boss and worker code.

It makes it easier to add a new message type.
It is better than string parsing (to figure out message types).
It uses meaningful variable names (instead of list indices, for multiple workers)

The MessageQueue subclasses defines the handler name and message type
The READER implements the handler
The WRITER writes the proper message for the subclasses
```

## Program Flow
```.
The boss starts a bunch of workers
The workers tell the boss they are Ready via the StatusMessage queue.
The boss tells the workers to BeginTest via the StatusMessage, once all workers are Ready.
The workers send status back to the boss via the LogMessage queue. 
Finally the workers send a QuitMessage to the boss.
When the boss has heard from each worker, the boss shuts down the workers and quits.
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

