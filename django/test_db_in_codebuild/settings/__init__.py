# -*- coding: utf-8 *-*
import requests
from boto import s3
from itertools import izip
import re

_cached_userdata = None
_s3_connection = None

USE_AWS_FOR_CREDENTIALS = True

def _connect_to_s3(region):
    global _s3_connection
    _s3_connection = s3.connect_to_region(region)

def get_credentials_from_s3(bucket_name, key, region=None):
    if region is None:
        region="eu-west-1"
    if _s3_connection is None:
        _connect_to_s3(region)
    return _s3_connection.get_bucket(bucket_name, validate=False).get_key(key).get_contents_as_string().strip()

def get_credentials_from_userdata(key):
    """
    This function loads the USERDATA attached to the AWS instance.
    (see: http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-metadata.html).
    With this, this function will extract any line that match an envvar
    definition (KEY=value) and creates a dictionary out of it. Since we dont
    want to make too many http call, that dictionnary is cached.

    If the KEY is not found, it returns None.
    """
    global _cached_userdata
    if _cached_userdata != None:
        try:
            return _cached_userdata[key]
        except KeyError:
            return None
    req = requests.get('http://169.254.169.254/latest/user-data')

    if req.status_code != 200:
        return None
    values = req.text.split("\n")
    # We remove any pesky whitespaces at the end
    values = map(lambda x: x.rstrip(), values)

    reg = re.compile("^([A-Z_]+)=(.*)$")
    # First we match anything that is like KEY=value
    values = map(lambda x: reg.match(x), values)
    # We remove any none matching entry
    values = filter(None, values)
    # We create a small submap of what we matched
    values = map(lambda x: [x.group(1), x.group(2)], values)
    # We flatten everything [key1, value1, key2, value2, ...]
    values = [item for sublist in values for item in sublist]
    # We turn this into a cached! dict :-)
    i = iter(values)
    _cached_userdata = dict(izip(i, i))
    # Annnnd, we loop.
    return get_credentials_from_userdata(key)

def get_credential_func(bucket_name, region=None):
    if USE_AWS_FOR_CREDENTIALS:
        def get_credential(key):
            value = get_credentials_from_userdata(key)
            if value:
                return value
            return get_credentials_from_s3(bucket_name, key, region)
    else:
        def get_credential(key):
            return "MOCKED in vault.settings.__init__"

    return get_credential
