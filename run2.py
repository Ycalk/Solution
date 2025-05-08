import sys
from enum import Enum
from collections import deque
from dataclasses import dataclass
from typing import FrozenSet, Generator, Optional, Dict, List, Set


@dataclass(frozen=True, order=True)
class Point:
    x: int
    y: int

    @staticmethod
    def zero() -> "Point":
        return Point(0, 0)


@dataclass(frozen=True, order=True)
class Path:
    length: int
    start: Point
    end: Point


@dataclass
class State:
    field: "Field"
    steps: int


@dataclass(frozen=True)
class FieldState:
    robots: FrozenSet[Point]
    keys: FrozenSet[Point]


class Field:
    KEYS_CHARS = set(chr(i) for i in range(ord("a"), ord("z") + 1))
    DOORS_CHAR = set(k.upper() for k in KEYS_CHARS)
    _values: Dict[str, "Field.Element"] = {}

    class Element(str, Enum):
        EMPTY = "."
        WALL = "#"
        DOOR = "DOOR"
        KEY = "KEY"
        ROBOT = "@"

        @classmethod
        def from_string(cls, value: str) -> "Field.Element":
            if len(Field._values) == 0:
                Field._values.update(
                    {
                        **{char: cls.KEY for char in Field.KEYS_CHARS},
                        **{char: cls.DOOR for char in Field.DOORS_CHAR},
                        ".": cls.EMPTY,
                        "#": cls.WALL,
                        "@": cls.ROBOT,
                    }
                )
            return Field._values[value]

    def __init__(self, data: List[List[str]]) -> None:
        self._robots: Set[Point] = set()
        self._keys: Set[Point] = set()

        self.doors_keys: Dict[Point, Point] = {}
        self.doors: Set[Point] = set()
        self.walls: Set[Point] = set()
        self.x_max_value = len(data[0]) - 1
        self.y_max_value = len(data) - 1

        self._initialize_field(data)

    @property
    def keys_count(self) -> int:
        return len(self._keys)

    @property
    def robots(self) -> Set[Point]:
        return self._robots

    def collect_key(self, robot_position: Point, key_position: Point) -> None:
        self._robots.remove(robot_position)
        self._robots.add(key_position)
        self._keys.remove(key_position)

    def get_neighbors(self, position: Point) -> Generator[Point, None, None]:
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for dx, dy in directions:
            neighbor = Point(position.x + dx, position.y + dy)
            if (
                0 < neighbor.x < self.x_max_value
                and 0 < neighbor.y < self.y_max_value
                and neighbor not in self._robots
                and neighbor not in self.walls
                and (
                    neighbor not in self.doors
                    or self.doors_keys[neighbor] not in self._keys
                )
            ):
                yield neighbor

    def copy(self) -> "Field":
        inst = self.__class__.__new__(self.__class__)
        inst._robots = self._robots.copy()
        inst._keys = self._keys.copy()

        inst.doors_keys = self.doors_keys
        inst.doors = self.doors
        inst.walls = self.walls
        inst.x_max_value = self.x_max_value
        inst.y_max_value = self.y_max_value
        return inst

    def dump(self) -> FieldState:
        return FieldState(robots=frozenset(self._robots), keys=frozenset(self._keys))

    def _initialize_field(self, data: List[List[str]]) -> None:
        keys: Dict[str, Point] = {}
        for y, row in enumerate(data):
            for x, element in enumerate(row):
                new_element = Field.Element.from_string(element)
                if new_element == Field.Element.KEY:
                    self._keys.add(Point(x, y))
                    keys[element] = Point(x, y)
                elif new_element == Field.Element.DOOR:
                    self.doors.add(Point(x, y))
                elif new_element == Field.Element.ROBOT:
                    self._robots.add(Point(x, y))
                elif new_element == Field.Element.WALL:
                    self.walls.add(Point(x, y))

        for y, row in enumerate(data):
            for x, element in enumerate(row):
                new_element = Field.Element.from_string(element)
                if new_element == Field.Element.DOOR:
                    self.doors_keys[Point(x, y)] = keys[element.lower()]

    def get_nearest_key(self, robot_position: Point) -> Optional[Path]:
        distance = {robot_position: 0}
        queue = deque([robot_position])
        while queue:
            current_position = queue.popleft()
            if current_position in self._keys:
                return Path(
                    distance[current_position], robot_position, current_position
                )
            for neighbor in self.get_neighbors(current_position):
                if neighbor in distance:
                    continue
                distance[neighbor] = distance[current_position] + 1
                queue.append(neighbor)

        return None


def solve(data: List[List[str]]) -> int:
    result = float("inf")
    visited: Set[FieldState] = set()
    states: deque[State] = deque([State(Field(data), 0)])
    while states:
        state = states.popleft()
        if state.field.keys_count == 0:
            result = min(result, state.steps)
            continue
        for robot in state.field.robots:
            path = state.field.get_nearest_key(robot)
            if not path:
                continue
            new_field = state.field.copy()
            new_field.collect_key(path.start, path.end)
            dump = new_field.dump()
            if dump not in visited:
                visited.add(dump)
                states.append(State(new_field, state.steps + path.length))

    return result if result is not float("inf") else 0  # type: ignore


def main():
    data = [list(line.strip()) for line in sys.stdin]
    result = solve(data)
    print(result)


if __name__ == "__main__":
    main()
