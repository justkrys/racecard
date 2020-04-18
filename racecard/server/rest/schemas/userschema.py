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


"""Schema for user resources."""


from .common import Schema, fields


class UserSchema(Schema):
    """Schema for user resources."""

    id = fields.UUID(dump_only=True)
    name = fields.Str()
    email = fields.Str()
    document_meta = fields.DocumentMeta()
    resource_meta = fields.ResourceMeta()

    # owned = fields.Relationship(
    #     self_url="/users/{id}/owned",
    #     self_url_kwargs={"id": "<id>"},
    #     related_url="/games/{id}",
    #     related_url_kwargs={"id": "<owned.id>"},
    #     schema=,
    # )

    # playing = fields.Relationship(
    #     self_url="/users/{id}/playing",
    #     self_url_kwargs={"id": "<id>"},
    #     related_url="/games/{id}",
    #     related_url_kwargs={"id": "<playing.id>"},
    #     schema=,
    # )

    # completed = fields.Relationship(
    #     self_url="/users/{id}/completed",
    #     self_url_kwargs={"id": "<id>"},
    #     related_url="/games/{id}",
    #     related_url_kwargs={"id": "<completed.id>"},
    #     schema=,
    # )

    class Meta:  # pylint: disable=too-few-public-methods
        """Metadata options for the schema."""

        type_ = "users"
        self_url = "/users/{id}"
        self_url_kwargs = {"id": "<id>"}
        self_url_many = "/users"
