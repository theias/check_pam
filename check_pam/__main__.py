#!/usr/bin/env python3
"""
Icinga2/Nagios plugin which...
uses `pamtester` to test PAM
"""

import argparse
import logging
import re
import sys
from typing import Generator, Optional

import nagiosplugin  # type:ignore


def parse_args(argv: Optional[list] = None) -> argparse.Namespace:
    """Parse args"""

    # bool_action = (
    #     # Should be `BooleanOptionalAction` if Python >= 3.9, else the old way
    #     argparse.BooleanOptionalAction
    #     if hasattr(argparse, "BooleanOptionalAction")
    #     else "store_true"
    # )

    usage_examples: str = """examples:

        # Description

        %(prog)s <args>

        # For more on how to set warning and critical ranges, see Nagios
        # Plugin Development Guidelines:
        #
        # https://nagios-plugins.org/doc/guidelines.html#THRESHOLDFORMAT

    """
    descr: str = """
        Icinga2/Nagios plugin which uses `pamtester` to test PAM
        """
    parser = argparse.ArgumentParser(
        description=descr,
        epilog=usage_examples,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--critical",
        "-c",
        help=("Critical range for ..."),
        type=str,
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        dest="verbosity",
        help="Set output verbosity (-v=warning, -vv=debug)",
    )

    parser.add_argument(
        "--warning",
        "-w",
        help=("Warning range for ..."),
        type=str,
    )

    parser.add_argument(
        "--auth-config",
        "-i",
        action="append",
        choices=[
            "service",
            "user",
            "prompt",
            "tty",
            "ruser",
            "rhost",
        ],
        help=(
            "To include additional authentication information like the name of the "
            "remote user, the remote host, etc. Can be passed multiple times."
        ),
        type=str.lower,
    )

    parser.add_argument(
        "--operation",
        "-o",
        action="append",
        dest="operations",
        help=(
            "The operation to test on the given user. Note that some operations "
            "may eventually need additional privileges to fulfill the request "
            "depending on the service configuration. This field can be any of "
            "['authenticate','acct_mgmt','open_session','close_session','chauthtok'] "
            "and may also include option flags. Refer to the `pamtester` "
            "documentation for more. This can be passed multiple times."
        ),
        type=str.lower,
    )

    parser.add_argument(
        "--service",
        "-s",
        help=("A PAM service name to use."),
        type=str,
    )

    parser.add_argument(
        "user",
        help=("The name of the user account to operate with the PAM facility."),
        type=str,
    )

    if len(sys.argv) == 0:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args(argv) if argv else parser.parse_args([])

    allowed_operations = [
        "acct_mgmt",
        "authenticate",
        "chauthtok",
        "close_session",
        "open_session",
    ]
    if args.operations:
        bare_ops = [re.sub(r"\(.*", "", s) for s in args.operations]
        if not all(op if op in allowed_operations else None for op in bare_ops):
            raise argparse.ArgumentTypeError(
                f"Operations must be one of `{allowed_operations}`"
            )
    else:
        args.operations = ["open_session"]

    if args.verbosity >= 2:
        log_level = logging.DEBUG
    elif args.verbosity >= 1:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    logging.basicConfig(level=log_level)

    return args


# pylint: disable=too-few-public-methods
class SomeResource(nagiosplugin.Resource):
    """
    A model of the thing being monitored
    """

    def __init__(
        self,
    ) -> None:
        pass

    def probe(self) -> Generator[nagiosplugin.Metric, None, None]:
        """
        Run the check itself
        """
        yield nagiosplugin.Metric(
            "metric_name",
            0,
            context="context",
        )


# pylint: enable=too-few-public-methods


@nagiosplugin.guarded
def main(
    argv: list,
) -> None:
    """Main"""
    args = parse_args(argv)
    logging.debug("Argparse results: %s", args)

    some_resource = SomeResource()
    context = nagiosplugin.ScalarContext(
        "context",
        warning=args.warning,
        critical=args.critical,
    )
    check = nagiosplugin.Check(some_resource, context)
    check.main(args.verbosity)


if __name__ == "__main__":
    main(sys.argv[1:])
