# alb-rule
A CloudFormation custom resource for creating ALB redirection rules.

At the time this was created, AWS had introduced redirect rules on ALBs but
had not yet made them available in CloudFormation. A new version of the botocore Python library did support it however.

Here is a how to create a Lambda-backed CloudFormation custom resource that can be used to implement redirect rules.

## Lambda Function
This is a Python 2.7 function. At the time of writing the version of botocore available in the default AWS Lambda environment was not the newest. A newer version had to be included in the zip file in order to use the new redirect functionality.

To build the Lambda zip file:

    cd lambda
    pip install -r requirements.txt -t .
    zip -r /tmp/AlbListenerRule .

Copy /tmp/AlbListenerRule.zip to your S3 bucket.

## CloudFormation Example
The provided CloudFormation template creates :-

* The Lambda function with and appropriate IAM role.
* An ALB with HTTP and HTTPS listeners
* A default target group
* Some example redirect rules for the ALB
  * Redirect to HTTP to HTTPS
  * Redirect the /images path to a CloudFront distribution

A full implementation will require something behind the target group such as EC2 instances or an Auto-Scaling Group.
