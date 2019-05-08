#!/bin/python3

import argparse
import boto3
import jmespath
import json
import pandas as pd
import sys

class ELB:
  
  def __init__(self, profile):
    self.region = "us-east-1"
    self.profile = profile
    session = boto3.Session(profile_name=self.profile)
    self.elb = session.client('elb', region_name=self.region)
        

  def describe_load_balancers(self, LoadBalancerNames=[], query="LoadBalancerDescriptions[].[LoadBalancerName,DNSName,Scheme,VPCId]"):
    response = self.elb.describe_load_balancers(LoadBalancerNames = LoadBalancerNames)
    elbs = jmespath.search(query, response)
    return elbs


  def describe_tags(self, LoadBalancerNames):
    return self.elb.describe_tags(LoadBalancerNames = LoadBalancerNames)
    
  def get_elbs_by_tag(self):
    all_elb_names = self.describe_load_balancers(query="LoadBalancerDescriptions[].LoadBalancerName")
    i = 0
    key = "Monitor"
    value = ":elb:kafka:"
    tag_query = "TagDescriptions[?(@.Tags[?(@.Key == '{}' && @.Value == '{}')])].LoadBalancerName".format(key, value)
    kafka_elb_names = []
    # 20 ELB names at a time for the tag checks
    while i < len(all_elb_names):
      if i+19 < len(all_elb_names):
        tags = self.describe_tags(all_elb_names[i:i+20])
      else:
        tags = self.describe_tags(all_elb_names[i:])
      kafka_elb_names.extend(jmespath.search(tag_query, tags))
      i = i+20
    kafka_elb_info = self.describe_load_balancers(LoadBalancerNames=kafka_elb_names, 
      query="LoadBalancerDescriptions[].[LoadBalancerName, DNSName]")
    return kafka_elb_info
    


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('-p', '--profile',
                        help='AWS profile',
                        required='True',
                        default='staging7-super-user')
  args = parser.parse_args(sys.argv[1:])
  elb = ELB(args.profile)
  elb.get_elbs_by_tag()
  pd.set_option('display.max_colwidth', -1)
  df = pd.DataFrame(elb.get_elbs_by_tag())
  # df = pd.DataFrame(elb.describe_load_balancers(names=["prom-kafka"]))
  print(df.to_string(index=False, header=False))
  
