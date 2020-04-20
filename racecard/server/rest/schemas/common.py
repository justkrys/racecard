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


"""Common utilities for schema objects."""

from collections import abc

import marshmallow as ma
from marshmallow_jsonapi import flask

from ..models import common as commonmodels
from . import fields


class Schema(flask.Schema):
    """Customized marshmallow-jsonapi Schema to include extra features.

    document_meta can be passed in to the schema and it will be added to any provided by
    the data object itself.

    A jsonapi key is always added that contains {"version": "1.0"}.

    Keys in output are always coverted to camelCase if they have underscores.

    self_view is required on Meta.
    """

    def __init__(self, *args, **kwargs):
        document_meta = kwargs.pop("document_meta", {})
        super().__init__(*args, **kwargs)
        if not self.opts.self_url:
            raise ValueError("Must specify self_view Meta option.")
        if isinstance(document_meta, commonmodels.CollectionMeta):
            document_meta = CollectionMetaSchema().dump(document_meta)
        self.document_meta.update(document_meta)

    @ma.post_dump(pass_many=True)
    def format_json_api_response(self, data, many, **kwargs):
        """Post-dump hook that formats serialized data as a top-level JSON API object.

        Overridden to also add a jsonapi verion property.
        """
        ret = super().format_json_api_response(data, many, **kwargs)
        ret["jsonapi"] = {"version": "1.0"}
        return ret

    def inflect(self, text):
        """Inflect text from using underscores to camelCase."""
        parts = iter(text.split("_"))
        return next(parts) + "".join(part.title() for part in parts)


class RemoveNonesMixin:  # pylint: disable=too-few-public-methods
    """Schema mixin class that recusively removes properties with None/null values."""

    @ma.post_dump()
    def remove_none_values(
        self, data, many
    ):  # pylint: disable=no-self-use,unused-argument
        """Removes properties with None/null values."""
        if not isinstance(data, abc.Mapping):
            return data
        return {
            key: self.remove_none_values(value, many)
            for key, value in data.items()
            if value is not None
        }


class CollectionMetaSchema(ma.Schema, RemoveNonesMixin):
    """Schema to handle our custom collection meta data.

    None/null values are removed automatically.
    property names are automatically camelCased.
    """

    total = fields.Integer()
    page = fields.Integer()
    page_size = fields.Integer(data_key="pageSize")
    total_pages = fields.Integer(data_key="totalPages")


class FailureSchema(Schema, RemoveNonesMixin):
    """Schema for error responses."""

    @ma.post_dump(pass_many=True)
    def format_json_api_response(self, data, many, **kwargs):
        """Post-dump hook that formats serialized data as a top-level JSON API object.

        Overridden to also add a jsonapi verion property.
        """
        orig_ret = super().format_json_api_response(data, many, **kwargs)
        ret = {"jsonapi": orig_ret["jsonapi"], "links": orig_ret["links"]}
        errors = orig_ret["data"]["attributes"]
        if not many:
            errors = [errors]
        ret["errors"] = errors
        return ret


class _SourceSchema(ma.Schema):
    """Failure source schema."""

    pointer = fields.String()
    parameter = fields.String()


class _ErrorSchema(FailureSchema):  # pylint: disable=too-many-ancestors
    """Schema for application errors and exceptions."""

    id = fields.Str()  # Must exist, but removed during serializaion per JSON:API spec.
    status = fields.String()
    code = fields.String()
    title = fields.String()
    detail = fields.String()
    source = fields.Nested(_SourceSchema)


def create_error_schema(base_schema):
    """Creates a JSON:API error schema that includes the base_schema's Meta class."""
    # Here there by dragons!  Dynamic class creation is magic.
    base_name = base_schema.__name__
    name = base_name[:-6] if base_name.lower().endswith("schema") else base_name
    name += "ErrorSchema"

    class NewMeta(base_schema.Meta):  # pylint: disable=too-few-public-methods
        """Replacement metadata class for error schemas."""

        # Using flask schema so, self_view is used, not self_url.  Need to erase the
        # lower level url attributes.  They will get repopulated when the error subclass
        # is created.
        self_url = None
        self_url_kwargs = None
        self_url_many = None

    return type(name, (_ErrorSchema,), {"Meta": NewMeta})
