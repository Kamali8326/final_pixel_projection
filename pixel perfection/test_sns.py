import boto3

sns = boto3.client("sns", region_name="us-east-1")
print("SNS client created successfully")
