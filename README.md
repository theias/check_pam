check_pam
===========

check_pam is a [Nagios]/[Icinga2] plugin which uses `pamtester` to test PAM

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

\[[...]\]

For more on Nagios plugin ranges, thresholds, perfdata, and return codes, see [Nagios Plugin Development Guidelines].

## Icinga2

Here is an Icinga2 `CheckCommand` object for this plugin:

```
```

And a minimal example Icinga Service:

```
```

NOTE on the command path: the above Icinga2 configuration object points to the command in Icinga2's configured `PluginDir`, but this can be configured however you like. For instance:

* point it to wherever it is installed by its full path
* symlink from the specified path to the actual script.

Up to you!

# Limitations

\[[...]\]

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
[Nagios Plugin Development Guidelines]: https://nagios-plugins.org/doc/guidelines.html
[Nagios]: https://en.wikipedia.org/wiki/Nagios
[pip]: https://pip.pypa.io/en/stable/
