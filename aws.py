import boto3
from moto import mock_aws
import json

##I'm sure there's a more persistent way to do infrastructure setup that persists outside of functions
@mock_aws
def getS3BucketCount():
    s3 = boto3.client("s3", region_name="us-east-1")
    #create a public and private bucket
    s3.create_bucket(Bucket="TestBucket1")
    s3.create_bucket(Bucket="TestBucket2", ACL='public-read')
    allBuckets = s3.list_buckets()
    count = 0
    #loop all buckets and look for allusers uri. This is what I was finding as a method to determine public exposure
    for s3Bucket in allBuckets.get('Buckets'):
        acl = s3.get_bucket_acl(Bucket=s3Bucket.get('Name'))
        for grant in acl.get('Grants'):
            if grant.get('Grantee').get('URI') and 'AllUsers' in grant.get('Grantee').get('URI'):
                count = count + 1
    return count
@mock_aws
def getS3Files(name):
    #create and return files inside the s3 bucket. Assumption that this suffices for type of data a bucket holds
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket=name)
    s3.upload_file('files/hello.txt', 'TestBucket1', 'hello.txt')
    s3.upload_file('files/password.txt', 'TestBucket1', 'password.txt')
    return [files.get('Key') for files in s3.list_objects(Bucket=name).get('Contents')]
@mock_aws
def getUserPermissions(name):
    iam = boto3.client('iam')
    iam.create_user(UserName=name)
    #utilizing example policy from https://docs.aws.amazon.com/boto3/latest/reference/services/iam/client/put_user_policy.html
    permissive_policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "*",
                "Resource": "*"
            }
        ]
    }
    iam.put_user_policy(UserName=name,PolicyName="AllowEverything",PolicyDocument=json.dumps(permissive_policy_document))
    #https://docs.aws.amazon.com/boto3/latest/reference/services/iam/client/list_user_policies.html
    policies = iam.list_user_policies(UserName=name).get('PolicyNames')
    allPermissions = []
    for policy in policies:
        allPermissions.extend(iam.get_user_policy(UserName=name, PolicyName=policy).get('PolicyDocument').get('Statement'))
    return allPermissions
@mock_aws
def getEC2ResourceSize(ip):
    ec2 = boto3.client("ec2", region_name="us-east-1")
    # Example AMI ID available in Moto's default set
    ami_id = "ami-12345678" 
    instance_type = "t2.micro"
    vpc = ec2.create_vpc(CidrBlock="10.0.0.0/16")["Vpc"]
    subnet = ec2.create_subnet(CidrBlock="10.0.1.0/24", VpcId=vpc["VpcId"])["Subnet"]
    subnet_id = subnet["SubnetId"]
    desired_private_ip = "10.0.1.3"
    #https://github.com/getmoto/moto/issues/7896
    network_interfaces = [
        {
            "DeviceIndex": 0,
            "SubnetId": subnet_id,
            "PrivateIpAddress": desired_private_ip,
            "DeleteOnTermination": True 
        }
    ]
    ec2.run_instances(ImageId=ami_id,MinCount=1,MaxCount=1,InstanceType=instance_type,NetworkInterfaces=network_interfaces)
    details = ec2.describe_instances(Filters=[{
                'Name': 'private-ip-address',
                'Values': [
                    ip,
                ]
            }
            ])
    #did it this way because during my research I didn't find a way to more dynamically create a resource based on the ip a user provided because a subnet etc. needs to be created ahead of time
    if not details.get('Reservations'):
        return('No ec2 found')
    return details.get('Reservations')[0].get('Instances')[0].get('InstanceType')