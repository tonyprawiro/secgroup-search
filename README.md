# secgroup-search

This is a very simple script to do an extensive search of your VPC security groups for an IP address or IPv4 Network address.

You could search security groups in a region for a specific IP using the AWS console.

However, there are times when you need to search multiple regions at the same time, or search for a network address instead.

This script was written for such purposes.

Usage:

```
$ ./secgroup-search.py -h
usage: secgroup-search.py [-h] [--profile [profile-name]]
                          [--search [search-term]] [--egress [Yes]]
                          [--regions [region_name [region_name ...]]]

AWS VPC Security Groups Search Utility

Author: Tony P. Hadimulyono (github.com/tonyprawiro)

optional arguments:
  -h, --help            show this help message and exit
  --profile [profile-name]
                        AWS credential profile to select, default is
                        'default'. Check your ~/.aws/credentials file.
  --search [search-term]
                        Search term e.g. 10.20.30.40/32, default is 0.0.0.0/0
                        which will match any CIDR.
  --egress [Yes]        Search egress rules too, if omitted then egress is not
                        searched
  --regions [region_name [region_name ...]]
                        Region(s) to search for. Default is all regions.
```

The `--profile-name` argument specifies with AWS credential you wish to use.

You could specify a single region (`--regions ap-southeast-1`), multiple regions (`--regions ap-southeast-1 us-east-1`), or search all regions (`--regions all`).

You could also specify to search egress rules. The argument `--egress` does not need any value.

The search term can be an IP address e.g. `10.20.30.40/321, or network address e.g. `10.20.30.40/24`. The script will search your security groups CIDR where the network addresses overlap. Note that the default value for this argument is `0.0.0.0/0`, which will match any CIDR in the ingress/egress rules (always returns `True`).

Example:

```
$ ./secgroup-search.py --profile default --search 10.20.30.40/32 --egress --regions all
```

The above will search for a specific host IP `10.20.30.40/32` in all regions, both ingress and egress.

