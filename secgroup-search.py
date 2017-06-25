#!/usr/bin/env python
import boto3
import argparse
from ipaddress import IPv4Network
import json


def prepare_arguments():

	parser = argparse.ArgumentParser(
		description="AWS VPC Security Groups Search Utility" \
		"\n\nAuthor: Tony P. Hadimulyono (github.com/tonyprawiro)",
		formatter_class=argparse.RawDescriptionHelpFormatter)

	parser.add_argument('--profile',
		metavar="profile-name",
		type=str,
		nargs='?',
		default="default",
		help="AWS credential profile to select, default is 'default'. Check your ~/.aws/credentials file.")

	parser.add_argument('--search', 
		metavar="search-term",
		type=str,
		nargs='?',
		default='0.0.0.0/0',
		help="Search term e.g. 10.20.30.40/32, default is 0.0.0.0/0 which will match any CIDR.")

	parser.add_argument('--egress', 
		metavar="Yes",
		type=str, 
		nargs='?', 
		default='No', 
		help="Search egress rules too, if omitted then egress is not searched")

	parser.add_argument('--regions',
		metavar="region_name",
		type=str, 
		nargs='*',
		default=['all'],
		help="Region(s) to search for. Default is all regions.")

	return parser.parse_args()


def get_all_regions(profile_name):

	arr = []
	session = boto3.session.Session(region_name='us-east-1', profile_name=profile_name)
	ec2 = session.client('ec2')
	response = ec2.describe_regions()
	regs = response["Regions"]
	for region in regs:
		arr.append(region["RegionName"])

	return arr


def evaluate_network(subnetwork, network):

	if subnetwork == '0.0.0.0/0':
		return True

	return IPv4Network(unicode(subnetwork, 'utf-8')).overlaps(IPv4Network(unicode(network, 'utf-8')))


def main():

	args = prepare_arguments()

	regions = args.regions
	if regions == ["all"]:
		regions = get_all_regions(args.profile)

	result = dict()

	for region in regions:

		session = boto3.session.Session(region_name=region, profile_name=args.profile)
		ec2 = session.client('ec2')
		response = ec2.describe_security_groups()

		# Get the security groups
		security_groups = []
		try:
			security_groups = response["SecurityGroups"]
		except:
			pass

		# Iterate the security groups
		for security_group in security_groups:

			ip_permissions = security_group["IpPermissions"]

			for ip_permission in ip_permissions:

				ip_ranges = ip_permission["IpRanges"]

				for ip_range in ip_ranges:

					cidr_ip = ip_range["CidrIp"]

					if cidr_ip != 'None':

						is_overlapping = evaluate_network(args.search, cidr_ip)

						if is_overlapping:

							if not region in result:
								result[region] = dict()

							if not security_group["GroupId"] in result[region]:
								result[region][security_group["GroupId"]] = dict()

							result[region][security_group["GroupId"]]["GroupName"] = security_group["GroupName"]

							if not "Ingress" in result[region][security_group["GroupId"]]:
								result[region][security_group["GroupId"]]["Ingress"] = []

							if cidr_ip not in result[region][security_group["GroupId"]]["Ingress"]:
								result[region][security_group["GroupId"]]["Ingress"].append(cidr_ip)


			if args.egress != 'No':

				ip_permissions_egress = security_group["IpPermissionsEgress"]

				for ip_permission_egress in ip_permissions_egress:

					ip_ranges = ip_permission_egress["IpRanges"]

					for ip_range in ip_ranges:

						cidr_ip = ip_range["CidrIp"]

						if cidr_ip != 'None':

							is_overlapping = evaluate_network(args.search, cidr_ip)

							if is_overlapping:

								if not region in result:
									result[region] = dict()

								if not security_group["GroupId"] in result[region]:
									result[region][security_group["GroupId"]] = dict()

								result[region][security_group["GroupId"]]["GroupName"] = security_group["GroupName"]

								if not "Ingress" in result[region][security_group["GroupId"]]:
									result[region][security_group["GroupId"]]["Egress"] = []

								if cidr_ip not in result[region][security_group["GroupId"]]["Egress"]:
									result[region][security_group["GroupId"]]["Egress"].append(cidr_ip)						

		del session

	print json.dumps(result,
		sort_keys=True,
		indent=2)


if __name__ == "__main__":
	main()


