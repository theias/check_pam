#!/usr/bin/env python3
"""
Icinga2/Nagios plugin which uses `pamtester` to test PAM operations
"""

import argparse
import logging
import os
import re
import shutil
import sys
from typing import List, Optional

import nagiosplugin  # type:ignore

from pamtester import PamTester

UNKNOWN: int = 3


def parse_args(argv: Optional[list] = None) -> argparse.Namespace:
    """Parse args"""

    usage_examples: str = """examples:

        # Minimal example, will check user `root` against the `login` PAM
        # service with the operation `open_session`

        %(prog)s root

        # Check a specific user against the `sshd` PAM service
        # Depending on your auth configuration, this will likely require that a
        # password be provided.

         export PAM_PASSWORD='mypass'
        %(prog)s --operation authenticate --service sshd specific_user

        # Check a specific_user against the `login` PAM service with the
        # operation `authenticate` plus other options

        %(prog)s --operation 'authenticate(PAM_SILENT | PAM_DISALLOW_NULL_AUTHTOK)' \\
            specific_user

        For more on the various combinations of services, operations, and other
        options, see `man pamtester`

    """
    descr: str = __doc__
    parser = argparse.ArgumentParser(
        description=descr,
        epilog=usage_examples,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--failure-mode",
        "-f",
        choices=["critical", "warning"],
        default="critical",
        help=("Report CRITICAL or WARNING if an operation fails"),
        type=str.lower,
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
        "--item",
        "-i",
        action="append",
        dest="additional_auth_items",
        help=(
            "To include additional authentication information like the name of the "
            "remote user, the remote host, etc. E.g. `rhost=host.domain.tld`. Can be "
            "passed multiple times."
        ),
        metavar="ITEM=VALUE",
        type=str.lower,
    )

    parser.add_argument(
        "--env",
        "-e",
        action="append",
        help=(
            "Environment variable to supply to PAM during the operation. Can be "
            "passed multiple times."
        ),
        metavar="ENVVAR=VALUE",
        type=str.lower,
    )

    parser.add_argument(
        "--service",
        "-s",
        help=("The PAM service name to use, e.g. `login` or `ssh`"),
        default="login",
        type=str,
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
        metavar="OPERATION",
        type=str.lower,
    )

    parser.add_argument(
        "--password",
        "-p",
        help=(
            "The user's password, which may be necessary for some operations "
            "depending on your authorization configuration. Can also point to a file "
            "on disk containing the password, or be passed via environment variable "
            "`PAM_PASSWORD`."
        ),
        default=os.environ.get("PAM_PASSWORD", None),
        type=str,
    )

    parser.add_argument(
        "user",
        help=("The name of the user account to operate upon"),
        type=str,
    )

    if len(sys.argv) == 0:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args(argv) if argv else parser.parse_args([])

    if args.password is not None and os.path.isfile(args.password):
        with open(args.password, "r", encoding="utf-8") as pwfile:
            args.password = pwfile.readline().rstrip()

    # Check that the operations are valid, though we're not going to check the
    # option flags that can follow
    allowed_operations = [
        "acct_mgmt",
        "authenticate",
        "chauthtok",
        "close_session",
        "open_session",
    ]
    if args.operations:
        bare_ops: List[str] = [re.sub(r"\(.*", "", s) for s in args.operations]
        if not all(op if op in allowed_operations else None for op in bare_ops):
            raise argparse.ArgumentTypeError(
                f"Operations must be one of `{allowed_operations}`"
            )
    else:
        args.operations = ["open_session"]

    # Validate the keys for additional auth info
    allowed_additional_auth = [
        "service",
        "user",
        "prompt",
        "tty",
        "ruser",
        "rhost",
    ]
    if args.additional_auth_items:
        bare_items: List[str] = [s.split("=")[0] for s in args.additional_auth_items]
        if not all(i if i in allowed_additional_auth else None for i in bare_items):
            raise argparse.ArgumentTypeError(
                f"Additional auth items must be one of `{allowed_additional_auth}`"
            )

    # Just set the crit/warn values into something Nagios understands here
    if args.failure_mode == "critical":
        args.warning = "~:"
        args.critical = "0"
    else:
        args.critical = "~:"
        args.warning = "0"

    if args.verbosity >= 2:
        log_level = logging.DEBUG
    elif args.verbosity >= 1:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    logging.basicConfig(level=log_level)

    return args


@nagiosplugin.guarded
def main(
    argv: list,
) -> None:
    """Main"""
    args = parse_args(argv)
    logging.debug("Argparse results: %s", args)

    if shutil.which("pamtester") is None:
        print("`pamtester` command not found. Aborting.", file=sys.stderr)
        sys.exit(UNKNOWN)

    some_resource = PamTester(
        additional_auth_items=args.additional_auth_items,
        env=args.env,
        operations=args.operations,
        password=args.password,
        service=args.service,
        user=args.user,
    )
    context = nagiosplugin.ScalarContext(
        "context",
        warning=args.warning,
        critical=args.critical,
    )
    check = nagiosplugin.Check(some_resource, context)
    check.main(args.verbosity)


if __name__ == "__main__":
    main(sys.argv[1:])
