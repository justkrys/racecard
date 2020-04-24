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


import pathlib

import connexion
import jsonschema
import prance
import timeflake
from connexion import resolver as connexionresolver
from jsonschema import compat
from prance.util import resolver as pranceresolver

from .. import common as servercommon
from . import exceptions
from .models import common as modelscommon
from .resources import common as resourcescommon
from .schemas import common as schemascommon


class ImplicitPackageResolver(connexionresolver.Resolver):
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
        return connexionresolver.Resolution(function, operation_id)


class RESTApp(servercommon.ServerBase, connexion.App):  # noqa
    """REST server application."""

    def __init__(self):
        super().__init__(__package__)
        self.add_api(
            self._get_bundled_specs(
                pathlib.Path(__file__).parent / "openapi" / "openapi.yaml"
            ),
            strict_validation=True,
            validate_responses=True,
            pythonic_params=True,
            resolver=ImplicitPackageResolver(__package__ + ".resources"),
        )
        self.add_error_handler(exceptions.RESTAppException, self._handle_app_exceptions)

    @staticmethod
    def _get_bundled_specs(main_file_path):
        """Stiches all external $ref references in to the main openapi spec file."""
        # Connexion cannot currently handle external file $refs.  This works around the
        # issue.  Based on https://github.com/zalando/connexion/issues/254
        parser = prance.ResolvingParser(
            str(pathlib.Path(main_file_path).absolute()),
            lazy=True,
            strict=True,
            backend="openapi-spec-validator",
            resolve_types=pranceresolver.RESOLVE_HTTP | pranceresolver.RESOLVE_FILES,
        )
        parser.parse()
        return parser.specification

    @staticmethod
    def _handle_app_exceptions(error):
        """Return application exceptions as JSON:API documents."""
        data = modelscommon.Error(
            id=error.id_,
            status=str(error.status),
            code=error.__class__.__name__,
            title=str(error),
            detail=error.detail,
        )
        if error.pointer or error.parameter:
            data.source = modelscommon.ErrorSource(
                pointer=error.pointer, parameter=error.parameter
            )
        error_schema_class = schemascommon.create_error_schema(error.schema_class)
        return resourcescommon.single(data, error_schema_class, error.status)


# connexion's OpenAPI 3 validation uses JSON Schema Draft 4 as a base.
@jsonschema.draft4_format_checker.checks("base62", Exception)
def base62_format_checker(instance):
    """Validates strings with "format: base62" as being a base62-encoded timeflake."""
    if not isinstance(instance, compat.str_types):
        return True
    if not len(instance) == 22:
        raise ValueError("Not a base62 string.")
    timeflake.parse(from_base62=instance)
    return True


app = RESTApp()  # pylint: disable=invalid-name


def flask_app():
    """Entry point for the "flask run" command."""
    return app.app
