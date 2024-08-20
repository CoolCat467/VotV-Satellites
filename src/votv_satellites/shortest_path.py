"""Voices of the Void Best Path Between Satellites Solver."""

# Programmed by CoolCat467

from __future__ import annotations

# Voices of the Void Best Path Between Satellites Solver
# Copyright (C) 2024  CoolCat467
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__title__ = "Voices of the Void Best Path Between Satellites Solver"
__author__ = "CoolCat467"
__license__ = "GNU General Public License Version 3"


from pathlib import Path
from typing import TYPE_CHECKING, Final, NamedTuple, Self, TypeVar

import numpy as np
from python_tsp.exact import solve_tsp_branch_and_bound

from votv_satellites.result import Result
from votv_satellites.vector import Vector2

if TYPE_CHECKING:
    from collections.abc import Iterable

DATA_FOLDER: Final = Path(__file__).parent / "data"
LOCATIONS_FILE: Final = DATA_FOLDER / "locations.txt"


T = TypeVar("T")


def colin_dict(line: str) -> dict[str, str]:
    """Return dictionary from a colin-seperated key value pair."""
    key, value = line.split(":", 1)
    return {key: value}


def multiline_colin_dict(lines: Iterable[str]) -> dict[str, str]:
    """Return dictionary from multiple colin-seperated key value pairs."""
    data = {}
    for line in lines:
        data.update(colin_dict(line))
    return data


class Location(NamedTuple):
    """VotV Location."""

    name: str
    pos: Vector2

    @classmethod
    def from_line(cls, line: str) -> Self:
        """<name> - X:<x>, Y:<y>."""
        raw_name, pos_data = line.split("-", 1)
        name = raw_name.strip()
        coords = multiline_colin_dict(
            x.strip() for x in pos_data.strip().split(",", 1)
        )
        pos = Vector2(float(coords["X"]), float(coords["Y"]))
        return cls(name, pos)

    @property
    def names(self) -> tuple[str, ...]:
        """All names this location goes by."""
        if "/" in self.name:
            return tuple(self.name.split("/"))
        return (self.name,)


def read_locations() -> list[Location]:
    """Read locations data and return location objects."""
    locations = []
    with open(LOCATIONS_FILE, encoding="utf-8") as fp:
        for line in fp.read().splitlines():
            if not line or line.startswith("#"):
                continue
            locations.append(Location.from_line(line))
    return locations


def combine_end(data: Iterable[str], final: str = "and") -> str:
    """Join values of text, and have final with the last one properly."""
    data = list(map(str, data))
    if len(data) >= 2:
        data[-1] = f"{final} {data[-1]}"
    if len(data) > 2:
        return ", ".join(data)
    return " ".join(data)


def find_fullnames(
    locations: list[Location],
    short_names: list[str],
) -> Result[list[Location]] | Result[str]:
    """Find locations from short names."""
    result = []
    for short_name in (sn.lower() for sn in short_names):
        close = []
        for location in locations:
            for name in location.names:
                if name.lower().startswith(short_name):
                    close.append(location)
                    break
        if len(close) != 1:
            if close:
                names_or = combine_end((loc.name for loc in close), "or")
                return Result.fail(
                    f"Multiple locations match {short_name!r}: {names_or}",
                )
            return Result.fail(f"No locations match {short_name!r}")
        result.append(close[0])
    return Result.ok(result)


def find_shortest_path(
    to_visit: list[Location],
    start: Location,
) -> list[Location]:
    """Return the shortest path between locations."""
    locations = [start, *sorted(set(to_visit), key=lambda loc: loc.name)]
    distance_matrix = np.zeros([len(locations)] * 2, dtype=float)
    for row, row_location in enumerate(locations):
        for col, col_location in enumerate(locations):
            distance_matrix[row, col] = row_location.pos.get_distance_to(
                col_location.pos,
            )
    permutation, _distance = solve_tsp_branch_and_bound(distance_matrix)
    return [locations[idx] for idx in permutation]


def run(version: str) -> None:
    """Run program."""
    print(f"{__title__} v{version}\nProgrammed by {__author__}.")
    locations = read_locations()
    while True:
        try:
            to_visit_resp = input(
                "\nEnter locations to visit (can be shortened, space separation, Ctrl+C to quit):\n",
            )
        except KeyboardInterrupt:
            break
        to_visit_short = to_visit_resp.split()
        to_visit = find_fullnames(locations, to_visit_short)
        if not to_visit:
            print(f"Error: {to_visit.value}")
            continue
        assert isinstance(to_visit.value, list)

        start_short = (
            input("\nStart & End location (if blank, 'Root'):\n") or "Root"
        )
        start = find_fullnames(locations, [start_short])
        if not start:
            print(f"Error: {start.value}")
            continue
        assert isinstance(start.value, list)

        path = find_shortest_path(to_visit.value, start.value[0])
        print("\nBest Path:")
        for idx, location in enumerate(path):
            if not idx:
                continue
            # print(f'{idx}: {location.name}')
            print(f"sv.target {location.names[0]}")
        print(f"sv.target {path[0].names[0]}")
    print("\nProgram is stopping.")


if __name__ == "__main__":
    run("ersion+dev")
