# Zone.eu API DNS updater with Python
This project provides a set of tools to interact with the Zone.eu API, specifically for managing DNS A records using Python 3.

## Why?
I wrote this for my own use to update the A records of my domains when my IP changes. The script runs on a Raspberry Pi, where I also have a web server.

## Requirements

- Python 3.6 or higher
- `requests` library
- `python-dotenv` library (only needed if environment variables are not set directly in the OS)
- A domain name hosted on zone.ee
- User token for authentication, refer to the [Zone API v2 documentation](#zone-api-v2) for more information

## Installation

1. Clone the repository:
    ```sh
    git clone git@github.com:kkalve/zone_v2_api.git
    cd zone_v2_api
    ```

2. Install the required dependencies.
    - Recommended for production:
        ```sh
        pip3 install -r requirements.txt
        ```

    - Recommended for local environment:

        In development, you can use the `python-dotenv` library to manage environment variables.
        ```sh
        pip3 install -r requirements.txt -r requirements-dev.txt
        ```

3. Set up your environment variables in a `.env` file (recommended only for local environment):
    ```sh
    ZONE_USERNAME='your_zone_username'
    ZONE_TOKEN='your_zone_token'
    ```

    You can use other methods for setting os variables.

## Usage

### Check and update DNS A record

The [a_record.py](a_record.py) script allows you to check if the IP address of a domain matches the destination IP and update the DNS record on Zone.eu if it does not match. It even supports using multiple A-records.

#### Arguments

- `-d`, `--domain`: Domain names to check (required, can be specified multiple times)
- `--dry-run`: Perform a dry-run without updating the DNS record
- `--destination`: Specify the destination IP address (default is your public IP)
- `--logging_level`: Set the logging level (default is 30 - WARNING)
- `--ip_provider`: Provider to get the public IP address if destination argument is not given
- `--force-nameserver-check`: Force check the nameserver IP against the destination IP

##### IP providers
The script uses the following IP providers to get your public IP address:

* [ipify.org](https://www.ipify.org)
* [ipinfo.io](https://ipinfo.io)
* [ident.me](https://api.ident.me/)

The API endpoints for the IP providers (both IPv4 and IPv6) are defined in the [ip_provider.py](ip_provider.py) file. Feel free to add new providers to this list. Ensure that the API returns the IP address as a plain text response.

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

### Setting up as a service on Linux
To avoid manual intervention, it is advisable to run this script as a service. This ensures that the DNS record is updated whenever the IP changes. Below is a guide with examples for setting it up using systemd periodically.

This guide has been tested on Raspbian GNU/Linux 10 (Buster).

If Python 3 is not installed, see [this guide](https://projects.raspberrypi.org/en/projects/generic-python-install-python3).

First, refer to the [Installation Guide](#installation-guide) for detailed setup instructions.

To set up the service:

1. Copy the service and timer files to the systemd directory:
    ```sh
    sudo cp systemd/a_record_update.service /etc/systemd/system/
    sudo cp systemd/a_record_update.timer /etc/systemd/system/
    ```

2. Reload the systemd daemon to recognize the new service and timer:
    ```sh
    sudo systemctl daemon-reload
    ```

3. Enable and start the timer to run the script periodically:
    ```sh
    sudo systemctl enable a_record_update.timer
    sudo systemctl start a_record_update.timer
    ```

Currently, the script is set to run every 1 minute, but you can adjust the interval as needed. Additionally, review and update any placeholders starting with `YOUR_` in the `systemd/a_record_update.service` file to match your configuration.

Alternatively, you can add the script to crontab for scheduled execution, but using systemd is recommended for better management and logging.

## Zone API v2
For more information on the Zone API v2, refer to the [API documentation](https://api.zone.eu/v2). To learn how to obtain a token for the Zone API, visit the [Zone API token guide](https://help.zone.eu/en/kb/zone-api-en/).

## Supported platforms
This project was created to automate the updating of A-records with the goal of keeping the process simple and up-to-date. The code has not been extensively tested on different platforms. It was developed on a Mac and runs on a Raspberry Pi (Python 3.6), so some compatibility is covered. There are no known limitations for using this on other platforms.

## TODO
 * Create new A record if current not found (using argument)
