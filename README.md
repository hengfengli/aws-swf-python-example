### aws-swf-python-example

A hello-world example of AWS Simple Workflow in Python. 

Very few SWF examples can be found. The official tutorials are based on Ruby and Java, which
are also not very clear. Especially, I found that it is very confusing about how `activity_list`
is used in [Ruby SWF Tutorial](https://docs.aws.amazon.com/amazonswf/latest/developerguide/swf-sns-tutorial.html). 
I think a decider should not store any state locally.   

Another intro example can be found in [aws-swf-boto3](https://github.com/jhludwig/aws-swf-boto3), 
but it only has a single activity task. So I enhanced it with sequential execution of four 
activities. 

### Some notes

I am very confused about `taskList`, which seems to be a very important identity to poll 
decision and activity tasks. But tutorials do not mention too much about it. 
My thought for AWS SWF: 

Pros:

* Track task states and events
* Reliable and stable (comparing to Celery Flower)
* Easy retry and terminate executions
* Built-in monitoring with CloudWatch


Cons:

* Not free (cost)
* No way to run SWF system locally
* Tricky issues can happen, like infinite loop and  
timed-out activity task 
* Slow (> 500 milliseconds)
* Throttling (push too fast)


### References
* [https://docs.aws.amazon.com/amazonswf/latest/developerguide/swf-sns-tutorial.html](https://docs.aws.amazon.com/amazonswf/latest/developerguide/swf-sns-tutorial.html)
* [https://github.com/jhludwig/aws-swf-boto3](https://github.com/jhludwig/aws-swf-boto3)

