import os
import sys
import requests
import logging
import logging.config
import logging.handlers
from typing import List
from ip_provider import ip_providers

# only load environment variables from .env file if they are not already set (eg running as a systemd service)
if not os.environ.get('ZONE_USERNAME'):
    from dotenv import load_dotenv
    load_dotenv()

# Generate zone.eu API URL
# https://api.zone.eu/v2#section/URL-format-and-usage
def get_zone_api_url(service_type: str, service_name: str, parameters: List[str] = []) -> str:
    API_URL='https://api.zone.eu/v2/{service_type}/{service_name}'
    base_url = API_URL.format(service_type=service_type, service_name=service_name)
    if parameters:
        return base_url + '/' + '/'.join(parameters)
    return base_url

# Make request. If with_auth is set to True, use the credentials for basic auth from the environment variables (ZONE_USERNAME and ZONE_TOKEN)
def request(url: str, method: str = 'GET', data: dict = {}, with_auth: bool = False) -> dict:
    logging.debug(f'Requesting {method} {url} with data {data}')
    auth = (os.environ.get('ZONE_USERNAME'), os.environ.get('ZONE_TOKEN')) if with_auth else None
    
    if method == 'GET':
        response = requests.get(url, auth=auth)
    elif method == 'POST':
        response = requests.post(url, auth=auth, json=data)
    elif method == 'PUT':
        response = requests.put(url, auth=auth, json=data)
    else:
        raise ValueError('Invalid method')
    
    logging.debug(f'{method} {url} response ({response.status_code}) {response.text}')

    response.raise_for_status()

    return response

# list of available IP providers for argument choices
available_ip_providers = list(ip_providers.keys())

# Get my public IP address 
def get_my_ip(provider: str, ip_type: str = 'ipv4') -> str:
    logging.debug(f'Getting my IP address ({ip_type}) from {provider}')
    
    if provider not in available_ip_providers:
        raise ValueError(f'Invalid provider {provider}')
    
    if ip_type not in ip_providers[provider]:
        raise ValueError(f'Invalid ip_type {ip_type} for provider {provider}')
    
    return request(ip_providers[provider][ip_type]).text.strip()

LOGGING_LEVEL_HELPER = """
0  - DISABLED
10 - DEBUG
20 - INFO
30 - WARNING
40 - ERROR
50 - CRITICAL
"""

def init_logging(console_logging_level: int = 20, syslog_logging_level: int = 20,logging_formatter = None):
    if sys.platform.startswith('linux'):
        SYSLOG_SOCKET = '/dev/log'
    elif sys.platform.startswith('freebsd'):
        SYSLOG_SOCKET = "/var/run/log"
    elif sys.platform.startswith('darwin'):
        SYSLOG_SOCKET = "/var/run/syslog"
    else:
        raise Exception("unknown platform. I have no idea where to log!")

    my_logger = logging.getLogger('')
    my_logger.setLevel(logging.DEBUG)

    if logging_formatter:
        formatter = logging_formatter
    else:
        formatter = logging.Formatter('%(asctime)s [%(process)d] %(levelname)s: %(filename)s:%(lineno)d %(message)s')

    if syslog_logging_level != 0:
        syslog = logging.handlers.SysLogHandler(address = SYSLOG_SOCKET)
        syslog.setFormatter(formatter)
        syslog.setLevel(syslog_logging_level)
        my_logger.addHandler(syslog)

    if console_logging_level != 0:
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(formatter)

        consoleHandler.setLevel(console_logging_level)

        my_logger.addHandler(consoleHandler)
