from typing import NamedTuple
import enum
from typing import List

# Constants
class Colors(enum.Enum):
    RED='red-bg'
    YELLOW='yellow-bg'
    ORANGE='orange-bg'
    GREEN='green-bg'

class Documents(enum.Enum):
    METHODOLOGY='https://docs.google.com/document/d/1C7LyLmeeQVV0A3vRqH03Ru0ABdJ6hCOcv_lYVMPQy2M/edit'
    FAQ='https://docs.google.com/document/d/1lanC52PjzU2taQISs1kO9mEJPtvwZM4uyvnHL9IalbQ/edit'
    GITHUB='https://github.com/ImpulsoGov/simulacovid/tree/master/COVID19_App'

# Models
class KPI(NamedTuple):
    label: str
    value: int

class ContainmentStrategy(NamedTuple):
    color: str
    code: int
    name: str
    image_url : str
    description: str

class SimulatorOutput(NamedTuple):
    color: Colors
    min_range: int
    max_range: int
    label: str

Strategies: List[ContainmentStrategy] = [
        ContainmentStrategy('grey', 1, "Não Intervencão", "https://i.imgur.com/pxYFm76.png", "Nenhuma medida de restrição de contato é adotada pelas autoridades."),
        ContainmentStrategy('green', 2, "Medidas-Restritivas", "https://i.imgur.com/W0JI4AE.png", "Fechamento das fronteiras e do comércio não-essencial, além de restringir o transporte público e toda circulação não estritamente necessária."),
        ContainmentStrategy('dark-green', 3, "Quarentena", "https://i.imgur.com/FjHaC7A.png", "O governo amplia a capacidade de testes e proíbe estritamente o movimento das pessoas não-autorizadas (lockdown).")
]
