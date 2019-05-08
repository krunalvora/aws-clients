Usage:

```
krunalvora:aws-cli-scripts krunalvora$ ./ec2/instances -h
Options:
    -h  Display this help message.
    -a  AWS account or set env var AWS_ACCOUNT.
    -n  Name of the instance or partial name.
    -i  Instance ID.
    -q  Optional query for output.
krunalvora:aws-cli-scripts krunalvora$ ./ec2/instances -a <ACCOUNT> -n grafana
grafana	10.10.###.###	i-#######ae9f####a6	grafana-ASG-$$$$$$$$$	subnet-********	vpc-@@@@@@
krunalvora:aws-cli-scripts krunalvora$

```
