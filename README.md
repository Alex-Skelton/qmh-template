# qmh-template

**A Queue'd Message Handler Architecture template utilising multiprocessing, queues, and PyQt graphical user interfaces to create single monolithic applications within Python.**

## Overview

A Queued Message Handler (QMH) template enables parallel execution of different code segments while facilitating data exchange among them. Each code segment embodies a specific task, such as data acquisition, data logging, or handling user events, and operates in a manner akin to a state machine. This approach allows for the segmentation of tasks into distinct states.

Acting as a variant of the Producer/Consumer design pattern, the QMH template allows the user interface (acting as the producer) to generate messages that are then processed by the tasks (the consumers). Uniquely, the QMH template also permits the generation of messages from within a consumer loop.

In this template application, `main.py` creates the named queues and separates out the workers (producer/consumer loops) to their own process. The `named_queues.py` stores the named queues for easier referencing.

## TODO

- Populate at least 3 unit tests for each function within `base_worker`, `log_worker`, and `main_worker`.
- Populate integration test.
- Generate a UI that facilitates some kind of timed execution test, with a start button, timer, and result field.

## Getting Started

Clone the repository, create a python interpreter, run command 'pip install -r requirements.txt' to install required dependencies. Run `main.py` to start application.
