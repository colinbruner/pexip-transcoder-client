import os
import sys

from argparse import FileType, OPTIONAL, SUPPRESS, ZERO_OR_MORE

from .argparser import PexipArgumentParser

from textwrap import dedent

parser = PexipArgumentParser(
    prog="pexip",
    description="Pexip API Interface",
)

# Create Sub parsers
subparsers = parser.add_subparsers()

global_options = parser.add_argument_group(title="Global Options", description=None)

###
# Global Opts
###

global_options.add_argument(
    "--manager-url",
    help="""
    The URL of the Pexip Manager to interface with. This value will override 
    any MANAGER_URL values defined within the Pexip config.json file.
    """,
)
global_options.add_argument(
    "--config-file",
    help="""
    Name of the JSON configuration file within the .pexip/ directory. E.g. 'prod.config.json'
    """,
)
global_options.add_argument(
    "--insecure",
    action="store_true",
    help="""
    Allow insecure (non-TLS) connections with the Pexip Manager.
    """,
)

###
# Create
###
provision_create = subparsers.add_parser("create")
provision_create.set_defaults(subparser="create")

provision_create.add_argument(
    "--domain",
    help="The domain of the new node.",
)
provision_create.add_argument(
    "--private-ip",
    help="The private IP address of the Pexip node to provision.",
)
provision_create.add_argument(
    "--public-ip",
    help="The public IP address of the Pexip node to provision.",
)
provision_create.add_argument(
    "--netmask",
    default="255.255.255.0",
    help="The IP netmask of the new node. Default: '255.255.255.0'",
)
provision_create.add_argument(
    "--gateway",
    help="The Gateway IP for new node.",
)
provision_create.add_argument(
    "--node-password",
    default=os.environ.get("PEXIP_TRANSCODER_PASSWORD", "SuperSecr3t!"),
    help="The password to use for the new Transcoder node.",
)
provision_create.add_argument(
    "--tls-certificate-subject-name",
    help="""
    Subject name of the TLS Certificate to apply to the node.""",
)

###
# Delete
###
provision_delete = subparsers.add_parser("delete")
provision_delete.set_defaults(subparser="delete")

###
# Common Create / Delete Arguments
###

for subparser in [provision_create, provision_delete]:
    subparser.add_argument(
        "hostname",
        help="The hostname of the Pexip node to target.",
    )
    subparser.add_argument(
        "-e",
        "--environment",
        default="staging",
        help="""
        The deployment environment of the conference node. 
        Default: staging""",
    )
    subparser.add_argument(
        "-u",
        "--auth_user",
        default=os.environ.get("MEETING_MANAGER_USER", "admin"),
        help="""
        User to authenticate against meet manager with. 
        Default: 'admin'""",
    )
    subparser.add_argument(
        "-p",
        "--auth_pass",
        default=os.environ.get("MEETING_MANAGER_PASS", ""),
        help="""
        Password to auhenticate against meet manager with. 
        Default: env['MEETING_MANAGER_PASS']""",
    )
    subparser.add_argument(
        "--system-location-name",
        help="Name of the system location to create or delete conferencing node from.",
    )


###
# Bootstrap
###
provision_bootstrap = subparsers.add_parser("bootstrap")
provision_bootstrap.set_defaults(subparser="bootstrap")

provision_bootstrap.add_argument(
    "--xml-file",
    help="The XML file to bootstrap the node with.",
)
provision_bootstrap.add_argument(
    "--node-address",
    help="The domain name or private IP address of the Pexip node to bootstrap.",
)
