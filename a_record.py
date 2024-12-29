import sys

# f-strings were introduced in Python 3.6
if sys.version_info < (3, 6): 
    print('Please start script with python3.6')
    sys.exit(1)

from argparse import ArgumentParser, RawTextHelpFormatter
from common import *
import socket

# Get the A record for a domain
def get_a_record(domain: str, identificator: int = None) -> List[dict]:
    params = ['a']
    if identificator:
        params.append(str(identificator))
    url = get_zone_api_url('dns', domain, params)
    return request(url, with_auth=True).json()

def check_dns(domains: List[str], destination_ip: str, dry_run: bool = False, force_nameserver_check: bool = False):
    for domain in domains:
        # domain can be in the format domain:identificator
        domain_split = domain.split(':')
        domain_name = domain_split[0]

        domain_identificator = None
        if len(domain_split) > 1:
            domain_identificator = int(domain_split[1])

        domains_data = get_a_record(domain_name, domain_identificator)
        if not domains_data:
            # @TODO: create a new record if not found
            # https://api.zone.eu/v2#operation/creatednsarecord
            logging.warning(f'No data found for {domain}')
            continue

        if len(domains_data) > 1:
            logging.warning(f'Multiple records found for {domain}. Please specify the record identificator by adding a colon and the identificator after the domain name, eg. example.com:123 {domains_data}')
            continue

        # first and only record in list
        domain_data = domains_data[0]
        domain_ip = domain_data['destination']
        if domain_ip != destination_ip:
            logging.warning(f'IP does not match for {domain} - destination IP is {destination_ip} and domain IP is {domain_ip}')
            if dry_run:
                logging.info(f'Dry-run: Would update IP for {domain} to {destination_ip}')
            else:
                request(domain_data['resource_url'], method='PUT', data={'destination': destination_ip, 'name': domain_name}, with_auth=True)
                logging.info(f'IP updated for {domain_name} ({domain_data["id"]}) - {destination_ip}')
        else:
            logging.info(f'{domain} IP matches {destination_ip} @ zone API')

        # let's assume that if domain_identificator is not set then we have one A record and can compare the IP against the nameserver IP. Or if force_nameserver_check is set then do it anyway
        if not domain_identificator or force_nameserver_check:
            ns_ip = socket.gethostbyname(domain_name)
            if ns_ip != destination_ip:
                logging.warning(f'{domain} IP does not match in nameserver - ns: {ns_ip} destination_ip: {destination_ip}')
            else:
                logging.info(f'{domain} IP matches {destination_ip} @ nameserver')

if __name__ == '__main__':
    parser = ArgumentParser(formatter_class=RawTextHelpFormatter, description='Check if the IP address of a domain matches the destination IP, update the DNS record on zone.eu if it does not match', epilog='Repository: https://github.com/kkalve/zone_v2_api')
    parser.add_argument('-d', '--domain', action='append', required=True, help="""Domain names to check.
If you have multiple domains, you can specify multiple --domain arguments.
If you have multiple records for a domain, you can specify the record identificator by adding a colon and the identificator after the domain name, eg. example.com:123""")
    parser.add_argument('--dry-run', action='store_true', help='Perform a dry-run without updating the DNS record')
    parser.add_argument('--destination', help='Specify the destination IP address (default is your public IP provided by --ip_provider)')
    parser.add_argument('--syslog_logging_level', default=20, help=LOGGING_LEVEL_HELPER, type=int)
    parser.add_argument('--console_logging_level', default=20, help=LOGGING_LEVEL_HELPER, type=int)
    parser.add_argument('--ip_provider', default=(available_ip_providers[0] if len(available_ip_providers) else None), help='Provider to get the public IP address if destination argument is not given', choices=available_ip_providers)
    parser.add_argument('--force-nameserver-check', action='store_true', help="""Force check the nameserver IP against the destination IP. This is done automatically if you do not specify the record identificator. 
With this option you can force the check while specifying the record identificator.""")
    args = parser.parse_args()

    init_logging(syslog_logging_level=args.syslog_logging_level, console_logging_level=args.console_logging_level)

    destination_ip = args.destination
    if not destination_ip:
        destination_ip = get_my_ip(args.ip_provider)
        logging.info(f'Destination IP not specified, using public IP address: {destination_ip} (from {args.ip_provider})')

    check_dns(args.domain, destination_ip, args.dry_run, args.force_nameserver_check)
