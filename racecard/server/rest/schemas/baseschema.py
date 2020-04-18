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


"""Base/common schema objects for resources."""

import marshmallow as ma
from marshmallow_jsonapi import Schema as _MJSchema
from marshmallow_jsonapi import fields  # noqa: F401

from ..models import base


class Schema(_MJSchema):
    """Customized marshmallow-jsonapi Schema to include extra features.

    document_meta can be passed in to the schema and it will be added to any provided by
    the data object itself.

    A jsonapi key is always added that contains {"version": "1.0"}.

    Keys in output are always coverted to camelCase if they have underscores.
    """

    def __init__(self, *args, **kwargs):
        document_meta = kwargs.pop("document_meta", {})
        super().__init__(*args, **kwargs)
        if isinstance(document_meta, base.CollectionMeta):
            document_meta = CollectionMetaSchema().dump(document_meta)
        self.document_meta.update(document_meta)

    @ma.post_dump(pass_many=True)
    def format_json_api_response(self, data, many, **kwargs):
        ret = super().format_json_api_response(data, many, **kwargs)
        ret["jsonapi"] = {"version": "1.0"}
        return ret

    def inflect(self, text):
        parts = iter(text.split("_"))
        return next(parts) + "".join(part.title() for part in parts)


class CollectionMetaSchema(ma.Schema):
    """Schema to handle our custom collection meta data.

    None/null values are removed automatically.
    property names are automatically camelCased.
    """

    total = fields.Integer()
    page = fields.Integer()
    page_size = fields.Integer(data_key="pageSize")
    total_pages = fields.Integer(data_key="totalPages")

    @ma.post_dump()
    def remove_skip_values(self, data, many):
        return {key: value for key, value in data.items() if value is not None}