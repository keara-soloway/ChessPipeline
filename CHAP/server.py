#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : server.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: Python server with thread pool and CHAP pipeline

### Client side:
cat /tmp/chap.json
{
  "pipeline": [{"common.PrintProcessor": {}}],
  "input": 1
}

### curl call to the server with our CHAP pipeline
curl -X POST -H "Content-type: application/json" -d@/tmp/chap.json http://localhost:5000/input
{"pipeline":[{"common.PrintProcessor":{}}],"status":"ok"}

### Server side:
flask --app server run
 * Serving Flask app 'server'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
...

CHAP.server         : call pipeline args=() kwds={'pipeline': [{'common.PrintProcessor': {}}]}
CHAP.server         : pipeline
[{'common.PrintProcessor': {}}]
CHAP.server         : Loaded <CHAP.common.processor.PrintProcessor object at 0x10e0f1ed0>
CHAP.server         : Loaded <CHAP.pipeline.Pipeline object at 0x10e0f1f10> with 1 items

CHAP.server         : Calling "execute" on <CHAP.pipeline.Pipeline object at 0x10e0f1f10>
Pipeline            : Executing "execute"

Pipeline            : Calling "process" on <CHAP.common.processor.PrintProcessor object at 0x10e0f1ed0>
PrintProcessor      : Executing "process" with type(data)=<class 'NoneType'>
PrintProcessor data :
None
PrintProcessor      : Finished "process" in 0.000 seconds

Pipeline            : Executed "execute" in 0.000 seconds
127.0.0.1 - - [07/Apr/2023 09:11:22] "POST /input HTTP/1.1" 200 -
"""

# system modules
import logging

# thrid-party modules

# Flask modules
from flask import Flask, request, jsonify

# CHAP modules
from CHAP.TaskManager import TaskManager
from CHAP.runner import run, setLogger


# Task manager to execute our tasks
taskManager = TaskManager()

# Flask Server
app = Flask(__name__)

@app.route("/")
def index_route():
    return "CHAP daemon"

@app.route("/input", methods=["POST"])
def input_route():
    content = request.json
    if 'pipeline' in content:
        # spawn new pipeline task
        jobs = []
        jobs.append(taskManager.spawn(task, pipeline=content['pipeline']))
        taskManager.joinall(jobs)
        return {"status": "ok", "pipeline": content['pipeline']}
    else:
        return {"status": "fail", "reason": "no pipeline in incoming request"}

def task(*args, **kwds):
    """
    Helper function to execute CHAP pipeline
    """
    log_level = "INFO"
    logger, log_handler = setLogger(log_level)
    logger.info(f"call pipeline args={args} kwds={kwds}")
    pipeline = kwds['pipeline']
    logger.info(f"pipeline\n{pipeline}")
    run(pipeline, logger, log_level, log_handler)