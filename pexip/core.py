import os
import sys
import json
import configparser

from .config import Config
from .models import DataObject, PexipNode, provision
from .exceptions import TranscoderAlreadyExists


def create_node(transcoder):
    node = PexipNode(transcoder)
    try:
        node.create()
    except TranscoderAlreadyExists as msg:
        print(msg)


def create(args):
    """ Route Pexip Transcoder creation. """
    if isinstance(args, list):
        for arg in args:
            create_node(arg)
    else:
        create_node(args)


def delete(args):
    print("TODO: Implement Delete!")
    sys.exit()


def bootstrap(args):
    with open(args.xml_file, "rb") as xml_file:
        provision(xml_file, args.node_address)


def main(args=sys.argv):
    program_name, *args = args

    from .cli.args import parser

    data, action = parser.parse_args(args=args)

    actions = {"create": create, "delete": delete, "bootstrap": bootstrap}

    actions[action](data)
