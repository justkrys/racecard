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


from . import common, fields


class UserSchema(common.Schema):
    """Schema for user resources."""

    id = fields.ID(dump_only=True)
    name = fields.Str()
    email = fields.Str()
    document_meta = fields.DocumentMeta()
    resource_meta = fields.ResourceMeta()

    games = fields.Relationship(
        related_view=".games_search", related_view_kwargs={"player": "<id>"}, many=True,
    )
    games_not_started = fields.Relationship(
        related_view=".games_search",
        related_view_kwargs={"player": "<id>", "state": "notstarted"},
        many=True,
    )
    games_running = fields.Relationship(
        related_view=".games_search",
        related_view_kwargs={"player": "<id>", "state": "running"},
        many=True,
    )
    games_completed = fields.Relationship(
        related_view=".games_search",
        related_view_kwargs={"player": "<id>", "state": "completed"},
        many=True,
    )
    games_owned = fields.Relationship(
        related_view=".games_search", related_view_kwargs={"owner": "<id>"}, many=True,
    )

    class Meta:  # pylint: disable=too-few-public-methods
        """Metadata options for the schema."""

        type_ = "user"
        self_view = ".users_get"
        self_view_kwargs = {"id": "<id>"}
        self_view_many = ".users_search"
