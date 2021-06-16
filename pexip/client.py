import os
import sys
import json
import time
import requests

# Local import
from .utils import requests_retry_session

# Disable annoying warnings if we're knowingly setting SSL_VERIFY to False.
if not SSL_VERIFY:
    requests.packages.urllib3.disable_warnings()


class PexipClient:
    def __init__(self, args):
        # Pexip TLS Certificate / System Location
        self.tls_certificate_subject_name = args.tls_certificate_subject_name
        self.system_location_name = args.system_location_name

    def _get_tls_cert_id(self):
        data = self._get_pexip_config("/api/admin/configuration/v1/tls_certificate/")
        tls_cert_id = self._filter_by(
            data.get("objects", {}), key="subject_name", val=self.tls_certificate_subject_name
        )
        if not tls_cert_id:
            raise (
                "Error: TLS Certificate ID with name '{self.tls_certificate_subject_name}' was unable to be found."
            )
        return tls_cert_id["id"]

    def _get_system_location_id(self):
        data = self._get_pexip_config("/api/admin/configuration/v1/system_location/")
        system_location_id = self._filter_by(
            data.get("objects", {}), key="name", val=self.system_location_name
        )
        if not system_location_id:
            raise (
                "Error: System Location with name '{self.system_location_name}' was unable to be found."
            )
        return system_location_id["id"]

    def take_action(self, action):
        if action == "create":
            if not self.node_exists():
                xml_doc = self.create_node()
                self.provision_node(xml_doc)
            else:
                print(f"Configuration for '{self.hostname}' found at '{self.manager_url}'")
                print("No changes were made. Exiting.")
                sys.exit(0)
        elif action == "remove":
            self.remove_node()
        else:
            print(f"Action: {action} not yet implemented. Exiting.")

    def node_exists(self):
        data = self._get_pexip_config()
        node_existence = self._filter_by(data.get("objects", {}), key="name", val=self.hostname)
        if node_existence:
            return True
        else:
            return False
