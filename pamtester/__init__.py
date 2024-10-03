"""
Model `pamtester` as a Nagios plugin resource
"""

import logging
import subprocess
import sys

from typing import Dict, List, Generator, Optional, Union

import nagiosplugin  # type: ignore


class PamTester(nagiosplugin.Resource):
    """
    Run pamtester
    """

    def __init__(
        self,
        *,
        additional_auth_items: List[str],
        env: List[str],
        operations: List[str],
        password: Optional[str],
        service: str,
        user: str,
    ) -> None:
        # pamtester [-v] [-I item=value] [-E var=value] service user operation
        # [operation ...]
        self.password: Optional[str] = password
        args: List[str] = ["-v"]
        self.cmd: List[str] = ["pamtester"]
        # -I/--item
        if additional_auth_items:
            args.extend(
                [
                    arg
                    for addauth in additional_auth_items
                    for arg in ["--item", addauth]
                ]
            )
        # -E/--env
        if env:
            args.extend([arg for envkv in env for arg in ["--env", envkv]])
        args.append(service)
        args.append(user)
        args.extend(operations)
        self.cmd.extend(args)
        logging.info("Setting `pamtester` command to: `%s`", self.cmd)

    def probe(self) -> Generator[nagiosplugin.Metric, None, None]:
        """
        Run the check itself
        """
        pamtester: subprocess.CompletedProcess
        value: int
        try:
            logging.info("Running `pamtester`")
            logging.debug(self.cmd)
            cond_args: Dict[str, Union[bool, str, bytes]]
            if sys.version_info >= (3, 7):
                # Unfortunately we need to support Python 3.6
                cond_args = {"text": True}
            else:
                cond_args = {"universal_newlines": True}
            if self.password:
                logging.debug("Preparing to pass password into `pamtester` STDIN")
                cond_args["input"] = f"{self.password}\n"
            pamtester = subprocess.run(  # type:ignore
                self.cmd,
                capture_output=True,
                check=True,
                encoding="utf-8",
                **cond_args,
            )
            logging.info("`pamtester` succeeded")
            if pamtester.stdout:
                logging.debug("`pamtester` STDOUT: `%s`", pamtester.stdout.rstrip())
            if pamtester.stderr:
                logging.debug("`pamtester` STDERR: `%s`", pamtester.stderr.rstrip())
            value = 0
        except subprocess.CalledProcessError as err:
            # PS it appears the only return values produced by `pamtester` are
            # 0 and 1
            logging.info(
                ("`pamtester` failed with the STDERR: `%s`"), err.stderr.rstrip()
            )
            value = 1
        yield nagiosplugin.Metric(
            "pam_failure",
            value,
            context="context",
        )
