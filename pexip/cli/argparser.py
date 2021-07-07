import sys
import json
import argparse

from textwrap import dedent
from argparse import RawDescriptionHelpFormatter

from ..models import DataObject
from ..config import Config


class PexipHelpFormatter(RawDescriptionHelpFormatter):
    """A nicer help formatter.
    Help for arguments can be indented and contain new lines.
    It will be de-dented and arguments in the help
    will be separated by a blank line for better readability.
    """

    def __init__(self, max_help_position=6, *args, **kwargs):
        # A smaller indent for args help.
        kwargs["max_help_position"] = max_help_position
        super().__init__(*args, **kwargs)

    def _split_lines(self, text, width):
        text = dedent(text).strip() + "\n\n"
        return text.splitlines()


class PexipArgumentParser(argparse.ArgumentParser):
    """Adds additional logic to `argparse.ArgumentParser`.
    Handles all input (CLI args, file args, stdin), applies defaults,
    and performs extra validation.
    """

    def __init__(self, *args, formatter_class=PexipHelpFormatter, **kwargs):
        kwargs["add_help"] = True
        super().__init__(*args, formatter_class=formatter_class, **kwargs)
        self.cfg = None  # Represents the local config
        self.args = None  # Contains initial CLI data
        self.data = None  # Contains shaped CLI data
        self.action = None  # Represents the action to take
        self.hostname = None  # A 'hostname' or list of 'hostnames'

    def parse_args(self, cfg: Config, args=None, namespace=None) -> argparse.Namespace:
        self.cfg = cfg

        self.args = super().parse_args(args, namespace)
        try:
            self.action = self.args.subparser
        except AttributeError:
            super().print_help()
            sys.exit()

        self._apply_config_values()
        self._split_out_hostname()
        self._remerge_data()

        return (self.data, self.action)

    def _apply_config_values(self):
        """Iterate through values found in the config. If no CLI values were passed,
        set them to the configs value."""

        for key, value in self.cfg.items():
            cfg_key = key.lower()
            try:
                # Set values found in the config if they're not passed over CLI
                if not getattr(self.args, cfg_key):
                    setattr(self.args, cfg_key, value)
            except AttributeError:
                # During 'bootstrap' subcommand, certain attributes aren't always present
                pass

    def _split_out_hostname(self):
        """ Attempt to parse hostname positional argument as JSON blob """
        try:
            # Attempt load the 'hostname' argument up as a JSON dictionary
            self.hostname = json.loads(self.args.hostname)
        except json.decoder.JSONDecodeError:
            self.hostname = self.args.hostname
        except AttributeError:
            # No args.hostname supplied, nothing to do.
            return
        else:
            # Upon successful json.loads, remove the hostname attribute from self.args
            del self.args.hostname

    def _remerge_data(self):
        """ Merge in global argument data with every hostname object """
        if isinstance(self.hostname, list):
            # Create a list of DataObjects merged in with top level config values
            # NOTE: the 2nd merged value will win in the event of a key conflict.
            self.data = [DataObject({**vars(self.args), **hostname}) for hostname in self.hostname]
        else:
            self.data = self.args
