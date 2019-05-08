#!/bin/python3

import boto3
import jmespath
import json
import pandas as pd
import sys

class ELB:

  def __init__(self):
    self.region = "us-east-1"
    self.elb = boto3.client('elb', region_name=self.region)


  def describe_load_balancers(self, LoadBalancerNames=[], query="LoadBalancerDescriptions[].[LoadBalancerName,DNSName,Scheme,VPCId]"):
    response = self.elb.describe_load_balancers(LoadBalancerNames = LoadBalancerNames)
    elbs = jmespath.search(query, response)
    return elbs


  def describe_tags(self, LoadBalancerNames):
    return self.elb.describe_tags(LoadBalancerNames = LoadBalancerNames)

  def get_elbs_by_tag(self, key, value):
    all_elb_names = self.describe_load_balancers(query="LoadBalancerDescriptions[].LoadBalancerName")
    tag_query = "TagDescriptions[?(@.Tags[?(@.Key == '{}' && @.Value == '{}')])].LoadBalancerName".format(key, value)
    kafka_elb_names = []
    i = 0
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
  elb = ELB()
  key = "Monitor"
  value = ":elb:kafka:"
  pd.set_option('display.max_colwidth', -1)
  df = pd.DataFrame(elb.get_elbs_by_tag(key, value))
  print(df.to_string(index=False, header=False))
