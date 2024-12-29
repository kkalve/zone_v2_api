# Zone.eu API DNS updater with Python
This project provides a set of tools to interact with the Zone.eu API, specifically for managing DNS A records using Python3.

I wrote this for my own use to update the A records of my domains when my IP changes. The script runs on a Raspberry Pi, where I also have a web server.

## Requirements

- Python 3.6 or higher
- `requests` library
- `python-dotenv` library (only needed if environment variables are not set directly in the OS)  

## Installation

1. Clone the repository:
    ```sh
    git clone git@github.com:kkalve/zone_v2_api.git
    cd zone_v2_api
    ```

2. Install the required dependencies:
    ```sh
    pip3 install -r requirements.txt
    ```

3. Set up your environment variables in a .env file:
    ```sh
    ZONE_USERNAME='your_zone_username'
    ZONE_TOKEN='your_zone_token'
    ```

    You can use other methods for setting os variables.

## Usage

### Check and update DNS A record

The **a_record.py** script allows you to check if the IP address of a domain matches the destination IP and update the DNS record on Zone.eu if it does not match. It even supports using multiple A-records.

#### Arguments

- `-d`, `--domain`: Domain names to check (required, can be specified multiple times)
- `--dry-run`: Perform a dry-run without updating the DNS record
- `--destination`: Specify the destination IP address (default is your public IP)
- `--logging_level`: Set the logging level (default is 30 - WARNING)
- `--ip_provider`: Provider to get the public IP address if destination argument is not given
- `--force-nameserver-check`: Force check the nameserver IP against the destination IP

##### IP providers
The script uses the following IP providers to get your public IP address:

 * ipify.org
 * ipinfo.io
 * ident.me

The API endpoints for the IP providers (both IPv4 and IPv6) are defined in the **ip_provider.py** file. Feel free to add new providers to this list. Ensure that the API returns the IP address as a plain text response.

### Logging
The script logs to syslog and also supports the `--logging_level` argument for adjusting the logging verbosity.

#### Example

To check the DNS A record for `example.com` and perform a dry-run:
```sh
python3 a_record.py -d example.com --dry-run
```

To set the DNS A record to specific IP (not your own):
```sh
python3 a_record.py -d example.com --destination 127.0.0.1
```

## Zone API v2
For more information on the Zone API v2, refer to the [API documentation](https://api.zone.eu/v2). To learn how to obtain a token for the Zone API, visit the [Zone API token guide](https://help.zone.eu/en/kb/zone-api-en/).

## TODO
 * Add example how to set it up as linux systemd service
 * Create new A record if current not found (using argument)
