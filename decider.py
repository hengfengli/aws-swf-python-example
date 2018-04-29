#!/usr/bin/python

import uuid
import boto3
from botocore.client import Config
from config import SWFConfig

botoConfig = Config(connect_timeout=50, read_timeout=70)
swf = boto3.client('swf', config=botoConfig)

print('Listening for Decision Tasks')

while True:
    # A decision task may be returned for any open workflow execution
    # that is using the specified task list.
    #
    # The task includes a paginated view of the history of the workflow
    # execution.
    #
    # The decider should use the workflow type and the history to
    # determine how to properly handle the task.
    newTask = swf.poll_for_decision_task(
        # The name of the domain containing the task lists to poll.
        domain=SWFConfig.DOMAIN,
        # Specifies the task list to poll for decision tasks.
        taskList={'name': SWFConfig.TASK_LIST_NAME},
        # Identity of the decider making the request
        identity=f'decider-{uuid.uuid4()}',
        # When set to true , returns the events in reverse order.
        reverseOrder=False)

    if 'taskToken' not in newTask or not newTask['taskToken']:
        print('Poll timed out, no new task. Repoll')

    elif 'events' in newTask:
        eventHistory = [evt for evt in newTask['events'] if not evt['eventType'].startswith('Decision')]
        lastEvent = eventHistory[-1]

        if lastEvent['eventType'] == 'WorkflowExecutionStarted':
            print('Dispatching task to worker', newTask['workflowExecution'], newTask['workflowType'])
            # make a decision that schedules the first activity task
            activity_type = SWFConfig.ACTIVITY_LIST[0]
            input_param = lastEvent['workflowExecutionStartedEventAttributes']['input']
            swf.respond_decision_task_completed(
                taskToken=newTask['taskToken'],
                decisions=[
                    {
                        'decisionType': 'ScheduleActivityTask',
                        'scheduleActivityTaskDecisionAttributes': {
                            'activityType': {
                                'name': activity_type['name'],
                                'version': activity_type['version']
                            },
                            'activityId': 'activityid-' + str(uuid.uuid4()),
                            'input': input_param,
                            'scheduleToCloseTimeout': '3800',
                            'scheduleToStartTimeout': '120',
                            'startToCloseTimeout': '3600',
                            'heartbeatTimeout': '900',
                            'taskList': {'name': SWFConfig.TASK_LIST_NAME},
                        }
                    }
                ]
            )
            print('Task Dispatched:', newTask['taskToken'])
        elif lastEvent['eventType'] == 'ActivityTaskCompleted':
            # lookup the ActivityTaskScheduled to find current `activity_type`
            # to decide the next activity.
            activity_task_scheduled_event_history = [evt for evt in newTask['events'] if
                                                     evt['eventType'] == 'ActivityTaskScheduled']
            last_activity_task_scheduled_event = activity_task_scheduled_event_history[-1]

            if not last_activity_task_scheduled_event:
                # if last event of ActivityTaskScheduled cannot be found
                swf.respond_decision_task_completed(
                    taskToken=newTask['taskToken'],
                    decisions=[
                        {
                            'decisionType': 'FailWorkflowExecution',
                            'failWorkflowExecutionDecisionAttributes': {
                                'reason': 'last activity task scheduled event cannot be found',
                                'details': 'last activity task scheduled event cannot be found details'
                            }
                        }
                    ]
                )
                continue

            activity_type_name = last_activity_task_scheduled_event['activityTaskScheduledEventAttributes']['activityType']['name']
            input_param = lastEvent['activityTaskCompletedEventAttributes']['result']
            # print(json.dumps(newTask, default=str))
            print('current activity type name:', activity_type_name)
            current_index = -1

            # search the index for current activity type
            for i, activity_type in enumerate(SWFConfig.ACTIVITY_LIST):
                if activity_type['name'] == activity_type_name:
                    current_index = i
                    break

            if current_index == -1:
                # if not found
                swf.respond_decision_task_completed(
                    taskToken=newTask['taskToken'],
                    decisions=[
                        {
                            'decisionType': 'FailWorkflowExecution',
                            'failWorkflowExecutionDecisionAttributes': {
                                'reason': 'activity type cannot be found',
                                'details': 'activity type cannot be found details'
                            }
                        }
                    ]
                )
            elif current_index + 1 == len(SWFConfig.ACTIVITY_LIST):
                # all activities are done!
                swf.respond_decision_task_completed(
                    taskToken=newTask['taskToken'],
                    decisions=[
                        {
                            'decisionType': 'CompleteWorkflowExecution',
                            'completeWorkflowExecutionDecisionAttributes': {
                                'result': input_param
                            }
                        }
                    ]
                )
                print('Task Completed!')
            else:
                activity_type = SWFConfig.ACTIVITY_LIST[current_index + 1]
                print(activity_type)
                swf.respond_decision_task_completed(
                    taskToken=newTask['taskToken'],
                    decisions=[
                        {
                            'decisionType': 'ScheduleActivityTask',
                            'scheduleActivityTaskDecisionAttributes': {
                                'activityType': {
                                    'name': activity_type['name'],
                                    'version': activity_type['version']
                                },
                                'activityId': 'activityid-' + str(uuid.uuid4()),
                                'input': input_param,
                                'scheduleToCloseTimeout': '3800',
                                'scheduleToStartTimeout': '120',
                                'startToCloseTimeout': '3600',
                                'heartbeatTimeout': '900',
                                'taskList': {'name': SWFConfig.TASK_LIST_NAME},
                            }
                        }
                    ]
                )
        elif lastEvent['eventType'] == 'ActivityTaskTimedOut':
            print('!! Failing workflow execution! (timed out activity)')
            swf.respond_decision_task_completed(
                taskToken=newTask['taskToken'],
                decisions=[
                    {
                        'decisionType': 'FailWorkflowExecution',
                        'failWorkflowExecutionDecisionAttributes': {
                            'reason': 'activity task timeouts',
                            'details': 'activity task timeouts details'
                        }
                    }
                ]
            )
        elif lastEvent['eventType'] == 'ActivityTaskFailed':
            print('!! Failing workflow execution! (failed activity)')
            swf.respond_decision_task_completed(
                taskToken=newTask['taskToken'],
                decisions=[
                    {
                        'decisionType': 'FailWorkflowExecution',
                        'failWorkflowExecutionDecisionAttributes': {
                            'reason': 'activity task fails',
                            'details': 'activity task fails details'
                        }
                    }
                ]
            )
        elif lastEvent['eventType'] == 'WorkflowExecutionCompleted':
            print('## Yesss, workflow execution completed!')
