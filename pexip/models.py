import sys
import json
import time

import requests
from requests.exceptions import ConnectTimeout

from .utils import requests_retry_session
from .exceptions import MissingArgumentError, TranscoderAlreadyExists
from .definitions import API_MAP, DEFAULT_CREATE_DATA
from .cli.definitions import REQUIRED_CREATE_ARGS


class PexipConnection:
    """Abstract class for a connection to Pexip Meeting Manager."""

    routes = API_MAP

    def __init__(self, args):
        """ Minimal Requirements to establish a remote connection. """
        self.url = args.manager_url
        self.username = args.auth_user
        self.password = args.auth_pass

        # Supress warnings if explicitly running with --insecure
        if args.insecure:
            requests.packages.urllib3.disable_warnings()
        # Flip --insecure (store_true) to Verify -> false
        self.verify = not args.insecure

        # Create Client with Auth
        self.client = requests.Session()
        self.client.auth = (self.username, self.password)

        # Store args for access later
        self.args = args

    def _filter_by(self, objs, key, val=None):
        """ Iterate over a list of dicts, search check each obj for key == val """
        for obj in objs:
            if obj.get(key) == val:
                return obj
        return None

    def _log_error(self, status, content):
        if status == 401:
            print(f"Error {status}: Are auth_user and auth_pass set correctly?")
        else:
            print(f"Error {status}: Content: {content}")

    def _get_config(self):
        raise NotImplementedError()


class PexipClient(PexipConnection):
    """ A Client for basic operations with a PexipManager """

    def _get_config(self, endpoint):
        """ Requests config attributes from the Pexip Meeting Manager. """
        route = self.routes[endpoint]
        response = self.client.get(f"{self.url}{route}", verify=self.verify)
        if not response.ok:
            self._log_error(response.status_code, response.content)

        data = json.loads(response.content)

        return data

    def _get_tls_config(self, tls_certificate_subject_name):
        """Fetch the ID of the supplied TLS Certificate Subject Name and return a
        string pointing at its full path on system."""

        data = self._get_config("tls_cert")
        tls_cert_id = self._filter_by(
            data.get("objects", {}), key="subject_name", val=tls_certificate_subject_name
        )
        if not tls_cert_id:
            raise Exception(
                f"Error: TLS Certificate ID with name '{tls_certificate_subject_name}' was unable to be found."
            )
        # e.g. '/api/admin/configuration/v1/tls_certificate/1/'
        return f"{self.routes['tls_cert']}{tls_cert_id['id']}/"

    def _get_system_location_id(self, system_location_name):
        """Fetch the ID of the supplied System Location and return a
        string pointing at its full path on system."""

        data = self._get_config("system_location")
        system_location_id = self._filter_by(
            data.get("objects", {}), key="name", val=system_location_name
        )
        if not system_location_id:
            raise Exception(
                f"Error: System Location with name '{system_location_name}' was unable to be found."
            )
        # e.g. '/api/admin/configuration/v1/system_location/1/'
        return f"{self.routes['system_location']}{system_location_id['id']}/"

    def _node_exists(self, hostname) -> bool:
        """ Check if a specific node exists within Manager's 'worker_vm' API """
        data = self._get_config("node")
        return bool(self._filter_by(data.get("objects", {}), key="name", val=hostname))

    def _sanity_check(self):
        for arg in REQUIRED_CREATE_ARGS:
            if not getattr(self.args, arg):
                raise MissingArgumentError(
                    f"Argument --{arg.replace('_', '-')} is required to create a node."
                )
        if self._node_exists(self.args.hostname):
            raise TranscoderAlreadyExists(
                f"Transcoder Node {self.args.hostname} already exists. Nothing to do."
            )


class PexipNode(PexipClient):
    """ A Pexip Transcoder Node. """

    def create(self):
        # Validate input data before POSTing config to manager
        self._sanity_check()

        tls_cert_path = self._get_tls_config(self.args.tls_certificate_subject_name)
        system_location_path = self._get_system_location_id(self.args.system_location_name)

        data = {
            "name": self.args.hostname,
            "hostname": self.args.hostname,
            "domain": self.args.domain,
            "address": self.args.private_ip,
            "static_nat_address": self.args.public_ip,
            "netmask": self.args.netmask,
            "gateway": self.args.gateway,
            "password": self.args.node_password,
            "tls_certificate": tls_cert_path,
            "system_location": system_location_path,
        }

        response = self.client.post(
            f"{self.url}/{self.routes['node']}",
            stream=True,
            data=json.dumps({**data, **DEFAULT_CREATE_DATA}),
        )

        if not response.ok:
            # TODO: if debug print(data) ?
            self._log_error(response.status_code, response.content)
            sys.exit(1)

        # TODO: Logging
        print(f"Successfully created configuration for {self.args.hostname}")
        self._provision(response.content)

    def _provision(self, content, hostname=None):
        # Set hostname if not passed
        if not hostname:
            hostname = self.args.hostname

        start_time = time.time()
        try:
            # Supress warnings, we realize this is a self-signed certificate.
            requests.packages.urllib3.disable_warnings()
            print(f"Attempting to provision the node {hostname} at {self.args.private_ip}")
            # Send request, wait up to 5s (timeout=5) for a response.
            # NOTE: This will not wait the full 5s if the host response with an error after, 2 seconds
            # NOTE: This is a freshly stood up node, it will have a self-signed certificate. Verify MUST be false.
            response = requests_retry_session().post(
                f"https://{self.args.private_ip}:8443/configuration/bootstrap",
                verify=False,
                headers={"Content-Type": "text/xml"},
                data=content,
                timeout=5,
            )
        except ConnectTimeout as e:
            print(f"Connection timed out when attempting to provision node: {hostname}. Error: {e}")
            self._error_and_write_xml(content)
        except Exception as e:
            print(f"Unknown error when attempting to provision node: {hostname}. Error: {e}")
            self._error_and_write_xml(content)
        else:
            if response.ok:
                print(f"Success: {response.status_code} status code.")
            else:
                print(
                    f"Error in response returned when provisioning node. Status code: {response.status_code}. Response Content: {response.content}."
                )
                self._error_and_write_xml(content)
        finally:
            end_time = time.time()
            print(f"Total time {end_time - start_time}")

    def _error_and_write_xml(self, content):
        with open(f"{self.args.hostname}.xml", "wb") as xml_file:
            print(f"Writing {self.args.hostname}.xml config to disk for retry.")
            xml_file.write(content)

        sys.exit(1)


# TODO: Merge this into PexipNode._provision for DRY.
def provision(content, hostname):

    start_time = time.time()
    try:
        print(f"Attempting to provision the node {hostname}")
        # Send request, wait up to 5s (timeout=5) for a response.
        # NOTE: This will not wait the full 5s if the host response with an error after, 2 seconds
        # NOTE: This is a freshly stood up node, it will have a self-signed certificate. Verify MUST be false.
        response = requests_retry_session().post(
            f"https://{hostname}:8443/configuration/bootstrap",
            verify=False,
            headers={"Content-Type": "text/xml"},
            data=content,
            timeout=5,
        )
    except ConnectTimeout as e:
        print(f"Connection timed out when attempting to provision node: {hostname}. Error: {e}")
    except Exception as e:
        print(f"Unknown error when attempting to provision node: {hostname}. Error: {e}")
    else:
        if response.ok:
            print(f"Success: {response.status_code} status code.")
        else:
            print(
                f"Error in response returned when provisioning node. Status code: {response.status_code}. Response Content: {response.content}."
            )
    finally:
        end_time = time.time()
        print(f"Total time {end_time - start_time}")


class PexipManager(PexipConnection):
    """Class for controlling the Pexip Manager configuration.  """

    pass


class DataObject(dict):
    """ Simple object for dot walking """

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        del self.__dict__[key]
