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


"""Schema for game resources."""


from . import common, fields


class GameSchema(common.Schema):
    """Schema for game resources."""

    id = fields.ID(dump_only=True)
    state = fields.Str()
    document_meta = fields.DocumentMeta()
    resource_meta = fields.ResourceMeta()

    owner = fields.Relationship(
        related_view=".users_get", related_view_kwargs={"id": "<owner.id>"},
    )
    players = fields.Relationship(
        related_view=".users_search", related_view_kwargs={"game": "<id>"}, many=True,
    )

    @common.post_dump
    def lowercase_state(
        self, data, **kwargs
    ):  # pylint: disable=unused-argument,no-self-use
        """Converts state string to lowercase.

        states are a) specified in lowercase in our spec and b) should be lowercase in
        URLs per internet best practice.
        """
        data["state"] = data["state"].lower()
        return data

    class Meta:  # pylint: disable=too-few-public-methods
        """Metadata options for the schema."""

        type_ = "game"
        self_view = ".games_get"
        self_view_kwargs = {"id": "<id>"}
        self_view_many = ".games_search"
