# alb-rule
A CloudFormation custom resource for creating ALB redirection rules.

At the time this was created, AWS had introduced redirect rules on ALBs but
had not yet made them available in CloudFormation. The boto3 Python library does support it however.

Here is a how to create a Lambda-backed CloudFormation custom resource that can be used to implement redirect rules.

## Lambda Function
This is a Python 2.7 function. All Python libraries it uses are available in the standard Lambda environment.

To build the Lambda zip file:

    cd lambda
    zip -r /tmp/AlbListenerRule .

Copy /tmp/AlbListenerRule.zip to your S3 bucket.

## CloudFormation Example
The example CloudFormation template demonstrates how to use the Lambda-backed Custom Resource. It creates:-

* A Lambda function with and appropriate IAM role.
* An ALB with HTTP and HTTPS listeners.
* A default target group for the listeners.
* Some example redirect rules for the ALB.
  * Redirect to HTTP to HTTPS.
  * Redirect the /images path to a CloudFront distribution.

### Rule Parameters

Parameters to create a rule are as required by the boto3 [elb2 create_rule](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.create_rule) method. Only the `Conditions`, `Actions`, `ListenerArn` and `Priority` are used. They are defined in CloudFormation YAML in the same format that the boto3 method expects them.

For example:-

    Conditions:
      - Field: host-header
        Values:
          - "*.*"
    Actions:
      - Type: redirect
        RedirectConfig:
          Protocol: HTTPS
          Port: 443
          StatusCode: HTTP_301
    ListenerArn: !Ref HTTPlistener
    Priority: 10


* Multiple Conditions can be specified. All must be true for the rule to apply. The `Field` value can be only 'host-header' or 'path-pattern'.
* Multiple Actions can be specified. If there is more than one, an `Order` element is required in each. The last Action must be of `Type` 'forward' or 'fixed-response'.
