# python scripts/deploy.py --environment dev
import boto3
import click
import os
import shutil
import subprocess

@click.command()
@click.option('--environment', default='dev', help='Deployment environment (dev/staging/prod)')
@click.option('--region', default='ap-southeast-1', help='AWS region')
def deploy(environment, region):
    """Deploy the Currency Converter API to AWS"""
    
     # Initialize AWS clients
    s3 = boto3.client('s3')
    bucket_name = f'currency-converter-deployment-{environment}'
    
    # Create S3 bucket if it doesn't exist
    try:
        s3.head_bucket(Bucket=bucket_name)
        print(f"Using existing S3 bucket: {bucket_name}")
    except:
        print(f"Creating new S3 bucket: {bucket_name}")
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
    shutil.make_archive('currency-converter', 'zip', 'package')
    
    # Upload to S3
    s3 = boto3.client('s3')
    bucket_name = f'currency-converter-deployment-{environment}'
    
    print(f"Uploading package to S3 bucket: {bucket_name}")
    s3.upload_file(
        'currency-converter.zip',
        bucket_name,
        'currency-converter.zip'
    )
    
    # Deploy CloudFormation stack
    cfn = boto3.client('cloudformation', region_name=region)
    stack_name = f'currency-converter-{environment}'
    
    print(f"Deploying CloudFormation stack: {stack_name}")
    with open('template.yaml', 'r') as f:
        template_body = f.read()
    
    cfn.create_stack(
        StackName=stack_name,
        TemplateBody=template_body,
        Parameters=[
            {
                'ParameterKey': 'Environment',
                'ParameterValue': environment
            }
        ],
        Capabilities=['CAPABILITY_IAM']
    )
    
    print("Deployment initiated. Check AWS Console for status.")

if __name__ == '__main__':
    deploy()