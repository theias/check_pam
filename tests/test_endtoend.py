""" End-to-end tests """

import os

import pytest  # type:ignore

import check_pam.__main__ as program  # type:ignore

testbin = os.path.join(os.getcwd(), "tests/bin")
os.environ["PATH"] = f"{testbin}:{os.environ['PATH']}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (
            # OK
            [
                "--operation=open_session",
                "valid_user",
            ],
            {
                "returncode": 0,
                "output": "OK",
            },
        ),
        (
            # WARN
            [
                "--failure-mode=warning",
                "--operation=open_session",
                "not_valid_user",
            ],
            {
                "returncode": 1,
                "output": "WARNING",
            },
        ),
        (
            # CRIT
            [
                "--operation=open_session",
                "not_valid_user",
            ],
            {
                "returncode": 2,
                "output": "CRITICAL",
            },
        ),
        (
            # OK with password prompt
            [
                "--service=login",
                "--operation=authenticate",
                "--password=valid_password",
                "valid_user",
            ],
            {
                "returncode": 0,
                "output": "OK",
            },
        ),
        (
            # CRIT for failed auth
            [
                "--service=login",
                "--operation=authenticate",
                "--password=not_valid_password",
                "valid_user",
            ],
            {
                "returncode": 2,
                "output": "CRITICAL",
            },
        ),
    ],
    ids=[
        "OK `open_session` with valid user",
        "WARN with invalid user",
        "CRIT with invalid user",
        "OK with password prompt",
        "CRIT for failed auth",
    ],
)
# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name
def test_end_to_end(
    capsys: pytest.CaptureFixture, test_input: list, expected: dict
) -> None:
    """Test"""
    with pytest.raises(SystemExit) as excinfo:
        program.main(argv=test_input)
    assert excinfo.value.code == expected["returncode"]
    assert expected["output"].encode() in capsys.readouterr()[0].encode().rstrip(b"\n")


# pylint: enable=unused-argument
# pylint: enable=redefined-outer-name
