class SWFConfig(object):
    DOMAIN = "SWFSampleDomain"
    WORKFLOW = "swf-sns-workflow"
    WORKFLOW_VERSION = "1"
    TASK_LIST_NAME = "swf-task-list"

    ACTIVITY_LIST = [
        {'name': 'get_contact_activity', 'version': 'v1'},
        {'name': 'subscribe_topic_activity', 'version': 'v1'},
        {'name': 'wait_for_confirmation_activity', 'version': 'v1'},
        {'name': 'send_result_activity', 'version': 'v1'},
    ]
