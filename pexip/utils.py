import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# These globals are for 'requests_retry_session' in conjunction with sending requests to a
# freshly provisioning EC2 AMI (the conference node)
PROVISION_RETRIES = 10        # Make a total of int() requests.
PROVISION_BACKOFF_FACTOR = 1  # A backoff factor of 1 will look like 1, 2, 4, 8, 16 for 5 requests.

def requests_retry_session(
    retries=PROVISION_RETRIES,
    backoff_factor=PROVISION_BACKOFF_FACTOR,
    status_forcelist=(500, 502, 504),
    session=None,
):
    """ Create a requests 'session' object for multiple retries. """
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session
