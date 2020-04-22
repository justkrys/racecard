#    Race Card - An implementation of the card game Mille Bornes
#    Copyright (C) 2020  Krys Lawrence <krys AT krys DOT ca>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""Excutable entry point for Race Card REST server."""


import sys

import click

from .app import simplecli


@click.group(invoke_without_command=True)
@click.pass_context
def cli(context):
    """Runs the CLI version of Race Card.

    Use sub-commands, if available, to trigger other behaviours.
    """
    if context.invoked_subcommand is not None:
        return
    simplecli.main()


try:
    # If REST server can be imported, assume all other dependencies are also installed.
    from flask import cli as flaskcli
    from .server.rest import app

    @cli.command(context_settings=dict(ignore_unknown_options=True,))
    @click.argument("args", nargs=-1, type=click.UNPROCESSED)
    def rest(args):
        """Runs the built-in Race Card REST server.

        NOTE: Any provided options or arguments will be passed to the "flask run"
        command. Run "flask run --help" for valid options.
        """
        flask_group = flaskcli.FlaskGroup(create_app=app.flask_app)
        flask_group.main(["run"] + list(args))


except ImportError:
    pass  # If not, no rest command.


def main(as_module=False):
    """Main entry point for Race Card."""
    # Copied from / based on flask.cli.
    # ATTN: Omit sys.argv once https://github.com/pallets/click/issues/536 is fixed
    cli.main(args=sys.argv[1:], prog_name="python -m racecard" if as_module else None)


if __name__ == "__main__":
    main(as_module=True)
