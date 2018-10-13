import boto3
from botocore.exceptions import ClientError, ParamValidationError
import sys
import os
import urllib2
import json

def lambda_handler(event, context):
    try:
        print("Lambda Event: " + json.dumps(event))

        responseData = {}

        region = os.environ['AWS_REGION']
        event_type = event['RequestType']

        ListenerArn = event['ResourceProperties']['ListenerArn']
        Conditions = event['ResourceProperties']['Conditions']
        Actions = event['ResourceProperties']['Actions']
        Priority = int(event['ResourceProperties']['Priority'])

        alb = boto3.client('elbv2')

        if event_type == 'Create':
            _create_rule(alb, ListenerArn, Conditions, Priority, Actions)
            responseStatus = 'SUCCESS'

        elif event_type == 'Delete':
            _delete_rule(alb, ListenerArn, Priority)
            responseStatus = 'SUCCESS'

        elif event_type == 'Update':
            OldPriority = int(event['OldResourceProperties']['Priority'])
            _delete_rule(alb, ListenerArn, OldPriority)
            _create_rule(alb, ListenerArn, Conditions, Priority, Actions)
            responseStatus = 'SUCCESS'

    except ClientError as e:
        print "Boto ClientError: %s" % e
        responseStatus = 'FAILED'
    except ParamValidationError as e:
        print "Boto ParamValidationError: %s" % e
        responseStatus = 'FAILED'
    except TypeError as e:
        print "TypeError: %s" % e
        responseStatus = 'FAILED'
    except NameError as e:
        print "NameError: %s" % e
        responseStatus = 'FAILED'
    except AttributeError as e:
        print "AttributeError: %s" % e
        responseStatus = 'FAILED'
    except:
        print("Error:", sys.exc_info()[0])
        responseStatus = 'FAILED'

    _sendResponse(event, context, responseStatus, responseData)

def _create_rule(alb, ListenerArn, Conditions, Priority, Actions):
    print('_create_rule ' + ListenerArn)
    response = alb.create_rule(
        ListenerArn=ListenerArn,
        Conditions=Conditions,
        Priority=Priority,
        Actions=Actions
    )

def _delete_rule(alb, ListenerArn, Priority):
    print('_delete_rule with Priority: %d' % Priority)
    response = alb.describe_rules(ListenerArn=ListenerArn)
    print("Found rules: " + json.dumps(response))
    for rule in response['Rules']:
        if rule['IsDefault']:
            continue
        if int(rule['Priority']) == Priority:
            RuleArn = rule['RuleArn']
            print("Deleting rule: " + json.dumps(rule))
            response=alb.delete_rule(RuleArn=RuleArn)
            break

def _sendResponse(event, context, responseStatus, responseData):
    print("responseStatus: " + responseStatus)
    print("responseData: " + json.dumps(responseData))
    data = json.dumps({
        'Status': responseStatus,
        'Reason': 'See the details in CloudWatch Log Stream: ' + context.log_stream_name,
        'PhysicalResourceId': context.log_stream_name,
        'StackId': event['StackId'],
        'RequestId': event['RequestId'],
        'LogicalResourceId': event['LogicalResourceId'],
        'Data': responseData
    })
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request(url=event['ResponseURL'], data=data)
    request.add_header('Content-Type', '')
    request.get_method = lambda: 'PUT'
    url = opener.open(request)
