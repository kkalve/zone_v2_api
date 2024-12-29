from collections import OrderedDict
# List of free ip providers. API must return the IP address as plain text
# Using OrderedDict to keep the order of the providers
# Feel free to add more providers
ip_providers = OrderedDict({
    'ipify.org':{
        'ipv4': 'https://api.ipify.org',
        'ipv6': 'https://api6.ipify.org',
    },
   'ipinfo.io': {
        'ipv4': 'https://ipinfo.io/ip',
        'ipv6': 'https://v6.ipinfo.io/ip'
    },
   'ident.me': {
        'ipv4': 'https://4.ident.me/',
        'ipv6': 'https://6.ident.me/'
    },
})