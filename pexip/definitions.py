SYSTEM_SERVICES = ["dns", "ntp", "syslog"]
PLATFORM_SERVICES = ["license", "license_request", "tls"]
ALL_SERVICES = [SYSTEM_SERVICES, PLATFORM_SERVICES]

SYSTEM_MAP = {
    "dns": "/api/admin/configuration/v1/dns_server/",
    "ntp": "/api/admin/configuration/v1/ntp_server/",
    "syslog": "/api/admin/configuration/v1/syslog_server/",
    "proxy": "/api/admin/configuration/v1/http_proxy/",
    "smtp": "/api/admin/configuration/v1/snmp_network_management_system/",
    "vm_manager": "/api/admin/configuration/v1/host_system/",
    "static_route": "/api/admin/configuration/v1/static_route/",
}

PLATFORM_MAP = {
    "system_location": "/api/admin/configuration/v1/system_location/",
    "management": "/api/admin/configuration/v1/management_vm/",
    "node": "/api/admin/configuration/v1/worker_vm/",
    "license": "/api/admin/configuration/v1/licence/",
    "license_request": "/api/admin/configuration/v1/licence_request/",
    "ca_cert": "/api/admin/configuration/v1/ca_certificate/",
    "tls_cert": "/api/admin/configuration/v1/tls_certificate/",
    "csr": "/api/admin/configuration/v1/certificate_signing_request/",
    "global": "/api/admin/configuration/v1/global/",
    "diag_graphs": "/api/admin/configuration/v1/diagnostic_graphs/",
}

API_MAP = {**SYSTEM_MAP, **PLATFORM_MAP}

# Default data object for Node creation.
DEFAULT_CREATE_DATA = {
    "description": "Transcoding Node",
    "node_type": "CONFERENCING",
    "deployment_type": "MANUAL-PROVISION-ONLY",
}
