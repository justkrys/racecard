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


"""OpenAPI 3 RESTful web service application entry point."""


from pathlib import Path
from uuid import UUID

from connexion import App
from connexion.resolver import Resolution, Resolver
from jsonschema import compat, draft4_format_checker
from prance import ResolvingParser
from prance.util.resolver import RESOLVE_FILES, RESOLVE_HTTP


class ImplicitPackageResolver(Resolver):
    """Resolver that uses an implicit base package to resolve operationId functions.

    This basically provides and implied router_controller value.

    This means operationId becomes required, but the full package path does not need to
    be included in openapi spec file, since, frankly, that is an implementation detail
    and not really part of the interface.

    operationId should be just that, and ID, not necessarily an absolute path in to the
    system.
    """

    def __init__(self, base_package_name):
        self._base_package_name = base_package_name
        super().__init__()

    def resolve(self, operation):
        """Resolve operation by pre-pending the base package name.

        Also keeps the base package name out of the routing table so that Flask's
        url_for(), for example, can be used would including all the base package parts.

        E.g. url_for(".games_search") instead of
             url_for(".racecard_servers_rest_api_games_search")
        """
        operation_id = self.resolve_operation_id(operation)
        full_operation_id = f"{self._base_package_name}.{operation_id}"
        function = self.resolve_function_from_operation_id(full_operation_id)
        return Resolution(function, operation_id)


# connexion's OpenAPI 3 validation uses JSON Schema Draft 4 as a base.
@draft4_format_checker.checks("uuid", ValueError)
def uuid_format_checker(instance):
    """Validates strings with "format: uuid" as being uuid v4."""
    if not isinstance(instance, compat.str_types):
        return True
    UUID(instance, version=4)
    return True


def get_bundled_specs(main_file_path):
    """Stiches all external $ref references in to the main openapi spec file."""
    # Connexion cannot currently handle external file $refs.  This works around the
    # issue.  Based on https://github.com/zalando/connexion/issues/254
    parser = ResolvingParser(
        str(Path(main_file_path).absolute()),
        lazy=True,
        strict=True,
        backend="openapi-spec-validator",
        resolve_types=RESOLVE_HTTP | RESOLVE_FILES,
    )
    parser.parse()
    return parser.specification


app = App(__package__)  # pylint: disable=invalid-name
app.add_api(
    get_bundled_specs(Path(__file__).parent / "openapi" / "openapi.yaml"),
    strict_validation=True,
    validate_responses=True,
    resolver=ImplicitPackageResolver(__package__ + ".resources"),
)


def flask_app():
    """Entry point for the "flask run" command."""
    return app.app


def main():
    """Entry point for the "racecard-rest" command and for running app.py directly."""
    app.run()


if __name__ == "__main__":
    main()
