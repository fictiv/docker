#!/usr/bin/python
import subprocess
import argparse

CONFIG = "development"
REGION = "us-west-2"
ECR_REPO = "754040250767.dkr.ecr.us-west-2.amazonaws.com"

parser = argparse.ArgumentParser(description='Get an ECR token from AWS')
parser.add_argument('--env', default=CONFIG, help='The name of the config in your .aws/config file to use for credentials. Default: development')
parser.add_argument('--region', default=REGION, help='The AWS region where the ECR repository is located, the token issued will only work in the specified region. Default: us-west-2')
parser.add_argument('--repo', default=ECR_REPO, help='The name of the ERC repository. Default: 754040250767.dkr.ecr.us-west-2.amazonaws.com')
args = parser.parse_args()

version = subprocess.check_output(["pip list installed | grep awscli"], shell=True).replace('awscli (','').replace(')','').rstrip()

if version[0].isdigit():
    print "You have awscli version: ",version
    result = ""

    if version.startswith('1.'):
        print "Getting AWS ECR token with V1 command"
        result = subprocess.check_output(["aws", "ecr", "get-login", "--region", args.region, "--no-include-email", "--profile", args.env])

    if version.startswith('2.'):
        print "Getting AWS ECR token with V2 command"
        result = subprocess.check_output(["aws", "ecr", "get-login-password", "--region", args.region, "--profile", args.env, "|", "docker", "login", "--password-stdin", "--username", "AWS", args.repo])

    print result

else:
    print "Failed to find installed version of awscli. Please install before continuing."

exit(0)