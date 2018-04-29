#!/usr/bin/python

import uuid
import boto3
from botocore.client import Config
from config import SWFConfig

botoConfig = Config(connect_timeout=50, read_timeout=70)
swf = boto3.client('swf', config=botoConfig)

print('Listening for Worker Tasks')

activities = {
    'get_contact_activity': lambda x: x + ',get_contact_activity',
    'subscribe_topic_activity': lambda x: x + ',subscribe_topic_activity',
    'wait_for_confirmation_activity': lambda x: x + ',wait_for_confirmation_activity',
    'send_result_activity': lambda x: x + ',send_result_activity'
}


while True:
    # Used by workers to get an ActivityTask from the specified activity taskList.
    task = swf.poll_for_activity_task(
        # The name of the domain that contains the task lists being polled.
        domain=SWFConfig.DOMAIN,
        # Specifies the task list to poll for activity tasks.
        taskList={'name': SWFConfig.TASK_LIST_NAME},
        # Identity of the worker making the request
        identity=f'worker-{uuid.uuid4()}')

    if 'taskToken' not in task or not task['taskToken']:
        print('Poll timed out, no new task. Repoll')
    else:
        print('New task arrived')

        activity_type_name = task['activityType']['name']
        input_param = task['input']

        if activity_type_name in activities:
            activity = activities[activity_type_name]

            result = activity(input_param)

            swf.respond_activity_task_completed(
                taskToken=task['taskToken'],
                result=result
            )

            print('Task Done')
        else:
            print(f'Activity type {activity_type_name} not found!')
