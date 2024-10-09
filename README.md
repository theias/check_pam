check_pam
===========

check_pam is a [Nagios]/[Icinga2] plugin that uses `pamtester` to test Pluggable Authentication Module (PAM) operations

Requires Python 3.6+

# Installation

You can install with [pip]:

```sh
python3 -m pip install check_pam
```

Or install from source:

```sh
git clone <url>
pip install check_pam
```

# Usage

```
# Minimal example, will check user `root` against the `login` PAM
# service with the operation `open_session`

check_pam root

# Check a specific user against the `sshd` PAM service
# Depending on your auth configuration, this will likely require that a
# password be provided.

 export PAM_PASSWORD='mypass'
check_pam --operation authenticate --service sshd specific_user

# Check a specific_user against the `login` PAM service with the
# operation `authenticate` plus other options

check_pam --operation 'authenticate(PAM_SILENT | PAM_DISALLOW_NULL_AUTHTOK)' specific_user
```

For more on the possible combinations of services, operations, and other options, see `man pamtester`

```
usage: check_pam [-h] [--failure-mode {critical,warning}] [--verbose]
                   [--item ITEM=VALUE] [--env ENVVAR=VALUE]
                   [--service SERVICE] [--operation OPERATION]
                   [--password PASSWORD]
                   user

Icinga2/Nagios plugin which uses `pamtester` to test PAM operations

positional arguments:
  user                  The name of the user account to operate upon

options:
  -h, --help            show this help message and exit
  --failure-mode {critical,warning}, -f {critical,warning}
                        Report CRITICAL or WARNING if an operation fails
  --verbose, -v         Set output verbosity (-v=warning, -vv=debug)
  --item ITEM=VALUE, -i ITEM=VALUE
                        To include additional authentication information like
                        the name of the remote user, the remote host, etc.
                        E.g. `rhost=host.domain.tld`. Can be passed multiple
                        times.
  --env ENVVAR=VALUE, -e ENVVAR=VALUE
                        Environment variable to supply to PAM during the
                        operation. Can be passed multiple times.
  --service SERVICE, -s SERVICE
                        The PAM service name to use, e.g. `login` or `ssh`
  --operation OPERATION, -o OPERATION
                        The operation to test on the given user. Note that
                        some operations may eventually need additional
                        privileges to fulfill the request depending on the
                        service configuration. This field can be any of ['auth
                        enticate','acct_mgmt','open_session','close_session','
                        chauthtok'] and may also include option flags. Refer
                        to the `pamtester` documentation for more. This can be
                        passed multiple times.
  --password PASSWORD, -p PASSWORD
                        The user's password, which may be necessary for some
                        operations depending on your authorization
                        configuration. Can also point to a file on disk
                        containing the password, or be passed via environment
                        variable `PAM_PASSWORD`.
```

## Icinga2

Here is an Icinga2 `CheckCommand` object for this plugin:

```
object CheckCommand "pam" {
  command = [ PluginDir + "/check_pam", ]
  arguments = {
    "--env" = {
      description = "Environment variable to supply to PAM during the operation. Can be passed multiple times"
      repeat_key = true
      value = "$pam_env$"
    }
    "--failure-mode" = {
      description = "Report CRITICAL or WARNING if an operation fails"
      value = "$pam_failure_mode$"
    }
    "--item" = {
      description = "To include additional authentication information like the name of the remote user, the remote host, etc. E.g. `rhost=host.domain.tld`. Can be passed multiple times."
      repeat_key = true
      value = "$pam_item$"
    }
    "--operation" = {
      description = "The operation to test on the given user. Note that some operations may eventually need additional privileges to fulfill the request depending on the service configuration. This field can be any of ['authenticate','acct_mgmt','open_session','close_session','chauthtok'] and may also include option flags. Refer to the `pamtester` documentation for more. This can be passed multiple times."
      repeat_key = true
      value = "$pam_operation$"
    }
    "--password" = {
      description = "The user's password, which may be necessary for some operations depending on your authorization configuration. Can also point to a file on disk containing the password, or be passed via environment variable `PAM_PASSWORD`."
      value = "$pam_password$"
    }
    "--service" = {
      description = "The PAM service name to use, e.g. `login` or `sshd`"
      value = "$pam_service$"
    }
    user = {
      description = "The name of the user account to operate upon"
      skip_key = true
      value = "$pam_service$"
    }
  }
}
```

And a minimal example Icinga Service:

```
object Service "pam" {
  import "generic-service"

  display_name = "PAM login and open_session for user `root`"
  host_name = "host.domain.tld"
  check_command = "pam"
  zone = ZoneName
  command_endpoint = "host.domain.tld"
  notes = {{{The `check_pam` plugin is a custom plugin which uses `pamtester` to test PAM operations}}}
  notes_url = "https://github.com/theias/check_pam"
  vars.pam_user = "root"
}
```

Note on the command path: the preceding Icinga2 configuration object points to the command in Icinga2's configured `PluginDir`, but this can point wherever you want. For instance:

* point it to wherever it is installed by its full path
* symlink from the specified path to the actual script.

Up to you!

# Contributing

Merge requests are welcome. For major changes, open an issue first to discuss what you would like to change.

To run the test suite:

```bash
# Dependent targets create venv and install dependencies
make
```

Please make sure to update tests along with any changes.

# License

License :: OSI Approved :: MIT License


[Icinga2]: https://en.wikipedia.org/wiki/Icinga
[Nagios]: https://en.wikipedia.org/wiki/Nagios
[pip]: https://pip.pypa.io/en/stable/
