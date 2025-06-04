# python scripts/deploy.py --environment dev

import boto3
import click
import os
import shutil
import subprocess

@click.command()
@click.option('--environment', default='dev', help='Deployment environment (dev/staging/prod)')
@click.option('--region', default='ap-southeast-1', help='AWS region')
@click.option('--profile', default='ym3594216', help='AWS CLI profile to use')
def deploy(environment, region, profile):
    """Deploy the Currency Converter API to AWS"""
    
    # Initialize AWS clients
    session = boto3.Session(profile_name=profile, region_name=region)
    s3 = session.client('s3')
    cfn = session.client('cloudformation')
    bucket_name = f'currency-converter-deployment-{environment}'
    stack_name = f'currency-converter-{environment}'
    s3_key = f'{stack_name}/function.zip'
    
    # Create S3 bucket if it doesn't exist
    try:
        s3.head_bucket(Bucket=bucket_name)
        print(f"Using existing S3 bucket: {bucket_name}")
    except:
        print(f"Creating new S3 bucket: {bucket_name}")
        if region == 'us-east-1':
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
    
    # Build the Lambda package
    print("Building Lambda package...")
    if os.path.exists('package'):
        shutil.rmtree('package')
    os.mkdir('package')
    
    # Install dependencies
    subprocess.run([
        'pip', 'install', 
        '--target', 'package',
        '-r', 'requirements.txt'
    ])
    
    # Copy application code
    shutil.copytree('app', 'package/app')
    
    # Create deployment ZIP
    shutil.make_archive('function', 'zip', 'package')
    
    # Upload to S3
    print(f"Uploading package to S3 bucket: {bucket_name}")
    s3.upload_file(
        'function.zip',
        bucket_name,
        s3_key
    )
    
    # Deploy or update CloudFormation stack
    print(f"Deploying CloudFormation stack: {stack_name}")

    # Get the current directory of the script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to the parent directory
    parent_dir = os.path.dirname(current_dir)
    # Access the "template.yaml" file in the "infrastructure" folder
    yaml_file_path = os.path.join(parent_dir, "infrastructure", "template.yaml")
    with open(yaml_file_path, 'r') as f:
        template_body = f.read()
    
    try:
        # Try to create the stack
        cfn.create_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Parameters=[
                {
                    'ParameterKey': 'Environment',
                    'ParameterValue': environment
                },
                {
                    'ParameterKey': 'S3Bucket',
                    'ParameterValue': bucket_name
                },
                {
                    'ParameterKey': 'S3Key',
                    'ParameterValue': s3_key
                }
            ],
            Capabilities=['CAPABILITY_IAM']
        )
        print("Stack creation initiated. Check AWS Console for status.")
    except cfn.exceptions.AlreadyExistsException:
        # If the stack already exists, update it
        print("Stack already exists, updating stack...")
        cfn.update_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Parameters=[
                {
                    'ParameterKey': 'Environment',
                    'ParameterValue': environment
                },
                {
                    'ParameterKey': 'S3Bucket',
                    'ParameterValue': bucket_name
                },
                {
                    'ParameterKey': 'S3Key',
                    'ParameterValue': s3_key
                }
            ],
            Capabilities=['CAPABILITY_IAM']
        )
        print("Stack update initiated. Check AWS Console for status.")

if __name__ == '__main__':
    deploy()