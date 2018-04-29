#!/usr/bin/python

import uuid
import boto3
from config import SWFConfig

swf = boto3.client('swf')


response = swf.start_workflow_execution(
    # The name of the domain in which the workflow execution is created.
    domain=SWFConfig.DOMAIN,
    # The user defined identifier associated with the workflow execution.
    workflowId=f'test-{uuid.uuid4()}',
    # The type of the workflow to start.
    workflowType={
        "name": SWFConfig.WORKFLOW,
        "version": SWFConfig.WORKFLOW_VERSION
    },
    taskList={
        'name': SWFConfig.TASK_LIST_NAME
    },
    input='test'
)

print("Workflow requested: ", response)
