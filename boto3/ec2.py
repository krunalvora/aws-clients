#!/bin/python3

import argparse
import boto3
import jmespath
import json
import pandas as pd
import sys

class EC2:
  
  def __init__(self, profile):
    self.region = "us-east-1"
    self.profile = profile
    session = boto3.Session(profile_name=self.profile)
    self.ec2 = session.client('ec2', region_name=self.region)
    

  def describe_instances(self, instance_name):
    query = "Reservations[].Instances[].[Tags[?Key=='Name']|[0].Value,PrivateIpAddress,InstanceId,Tags[?Key=='aws:autoscaling:groupName']|[0].Value,SubnetId,VpcId]"
    filters = [
      {
        'Name': 'tag:Name',
        'Values': [
          "*{}*".format(instance_name)
        ]
      }
    ]
    subnets_dict = self.get_subnets_dict()
    vpcs_dict = self.get_vpcs_dict()
    response = self.ec2.describe_instances(Filters=filters)
    instances = jmespath.search(query, response)
    for instance in instances:
      if instance[4] is not None:
        instance[4] = subnets_dict[instance[4]]
        instance[5] = vpcs_dict[instance[5]]
    return instances


  def get_subnets_dict(self):
    subnets_dict = {}
    for i in self.describe_subnets():
      subnets_dict[i[1]] = i[0]
    return subnets_dict


  def describe_subnets(self):
    query = "Subnets[].[Tags[?Key=='Name']|[0].Value,SubnetId,CidrBlock,VpcId]"
    response = self.ec2.describe_subnets()
    subnets = jmespath.search(query, response)
    return subnets


  def get_vpcs_dict(self):
    vpcs_dict = {}
    for i in self.describe_vpcs():
      vpcs_dict[i[1]] = i[0]
    return vpcs_dict


  def describe_vpcs(self):
    query = "Vpcs[].[Tags[?Key=='Name'].Value|[0],VpcId,CidrBlock]"
    response = self.ec2.describe_vpcs()
    vpcs = jmespath.search(query, response)
    return vpcs


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('-a', '--account',
                        help='AWS account',
                        required='True',
                        default='staging7')
  parser.add_argument('-n', '--name',
                        help='EC2 instance name regex',
                        required='True')
  args = parser.parse_args(sys.argv[1:])
  profile = "{}-super-user".format(args.account)
  try:
    ec2 = EC2(profile)
    df = pd.DataFrame(ec2.describe_instances(args.name))
  except Exception as e:
    print(e)
    sys.exit()
  if df.empty:
    print("No output for instances - Check the name that you are searching for...")
    sys.exit(1)
  else:
    print(df.to_string(index=False, header=False))
