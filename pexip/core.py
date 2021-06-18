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
    """ Route Pexip Transcoder creation. """
    if isinstance(args, list):
        for arg in args:
            create_node(arg)
    else:
        create_node(args)


def delete(args):
    print("TODO: Implement Delete!")
    sys.exit()


def main(args=sys.argv, cfg=Config()):
    program_name, *args = args

    from .cli.args import parser

    data, action = parser.parse_args(args=args, cfg=cfg)

    actions = {
        "create": create,
        "delete": delete
    }

    actions[action](data)
