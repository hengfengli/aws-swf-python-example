#!/usr/bin/python

import boto3
from botocore.exceptions import ClientError
from config import SWFConfig

swf = boto3.client('swf')

# register a domain
try:
    swf.register_domain(
        name=SWFConfig.DOMAIN,
        description=f'{SWFConfig.DOMAIN} domain',
        workflowExecutionRetentionPeriodInDays="10"
    )
    print(f"{SWFConfig.DOMAIN} is registered!")
except ClientError as e:
    print("Domain already exists: ", e.response.get("Error", {}).get("Code"))

# register a workflow
try:
    swf.register_workflow_type(
        domain=SWFConfig.DOMAIN,
        name=SWFConfig.WORKFLOW,
        version=SWFConfig.WORKFLOW_VERSION,
        description=f"{SWFConfig.WORKFLOW} workflow",
        defaultTaskStartToCloseTimeout=str(3600),
        defaultExecutionStartToCloseTimeout=str(24*3600),
        defaultChildPolicy="TERMINATE",
        defaultTaskList={"name": SWFConfig.TASK_LIST_NAME}
    )
    print(f"Workflow {SWFConfig.WORKFLOW} created!")
except ClientError as e:
    print("Workflow already exists: ", e.response.get("Error", {}).get("Code"))

# register an activity type
try:
    for activity_type in SWFConfig.ACTIVITY_LIST:
        swf.register_activity_type(
            domain=SWFConfig.DOMAIN,
            name=activity_type['name'],
            version=activity_type['version'],
            description=f"Activity type {activity_type['name']}",
            defaultTaskList={"name": SWFConfig.TASK_LIST_NAME},
            defaultTaskHeartbeatTimeout="900",
            defaultTaskScheduleToStartTimeout="120",
            defaultTaskScheduleToCloseTimeout="3800",
            defaultTaskStartToCloseTimeout="3600"
        )
        print(f"Activity type {activity_type['name']} created!")
except ClientError as e:
    print("Activity already exists: ", e.response.get("Error", {}).get("Code"))
