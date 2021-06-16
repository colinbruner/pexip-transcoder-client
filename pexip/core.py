import os
import sys
import json
import configparser

from .config import Config
from .models import DataObject, PexipNode
from .exceptions import TranscoderAlreadyExists


def create_node(transcoder):
    node = PexipNode(transcoder)
    try:
        node.create()
    except TranscoderAlreadyExists as msg:
        print(msg)


def create(args):
    """ Route transcoder creation, single transocder vs multiple. """
    if isinstance(args, list):
        for arg in args:
            create_node(arg)
    else:
        create_node(args)


def delete(args):
    print("TODO Delete!")
    print(args)


def manage(args):
    print("TODO Manage!")
    print(args)


def main(args=sys.argv, cfg=Config()):
    program_name, *args = args

    from .cli.args import parser

    data, action = parser.parse_args(args=args, cfg=cfg)

    actions = {
        "create": create,
        "delete": delete,
        "manage": manage,
    }

    actions[action](data)
