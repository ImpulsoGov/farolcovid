import enum
from typing import NamedTuple

class Colors(enum.Enum):
        RED='red-bg'
        YELLOW='yellow-bg'
        ORANGE='orange-bg'
        GREEN='green-bg'

class Documents(enum.Enum):
        METHODOLOGY='https://docs.google.com/document/d/1C7LyLmeeQVV0A3vRqH03Ru0ABdJ6hCOcv_lYVMPQy2M/edit'
        FAQ='https://docs.google.com/document/d/1lanC52PjzU2taQISs1kO9mEJPtvwZM4uyvnHL9IalbQ/edit'
        GITHUB='https://github.com/ImpulsoGov/simulacovid/tree/master/COVID19_App'


class SimulatorOutput(NamedTuple):
        color: Colors
        min_range: int
        max_range: int
        label: str


class KPI(NamedTuple):
        label: str
        value: int