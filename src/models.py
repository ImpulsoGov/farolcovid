from typing import NamedTuple, List
import enum

# Constants
class BackgroundColor(enum.Enum):
    GREEN='green-bg'
    DARK_GREEN = 'dark-green-bg'
    GREY='grey-bg'
    LIGHT_BLUE='light-blue-bg'
    GREY_GRADIENT='grey-gradient-bg'
    LIGHT_BLUE_GRADIENT='light-blue-gradient-bg '

class FontColor(enum.Enum):
    GREY='grey-span'
    GREEN='green-span'
    DARK_GREEN = 'dark-green-span'

class Document(enum.Enum):
    METHODOLOGY='https://docs.google.com/document/d/1C7LyLmeeQVV0A3vRqH03Ru0ABdJ6hCOcv_lYVMPQy2M/edit'
    FAQ='https://docs.google.com/document/d/1lanC52PjzU2taQISs1kO9mEJPtvwZM4uyvnHL9IalbQ/edit'
    GITHUB='https://github.com/ImpulsoGov/simulacovid/tree/master/COVID19_App'

# Models

class ResourceAvailability(NamedTuple):
    city: str
    cases: int
    deaths: int
    beds: int
    ventilators: int

class ContainmentStrategy(NamedTuple):
    background: BackgroundColor
    color: FontColor
    code: int
    name: str
    image_url : str
    description: str

class SimulatorOutput(NamedTuple):
    color: BackgroundColor
    min_range_beds: int
    max_range_beds: int
    min_range_ventilators: int
    max_range_ventilators: int

Strategies: List[ContainmentStrategy] = [
        ContainmentStrategy(BackgroundColor.GREY, FontColor.GREY, 1, "Não Intervencão", "https://i.imgur.com/pxYFm76.png", "Nenhuma medida de restrição de contato é adotada pelas autoridades."),
        ContainmentStrategy(BackgroundColor.GREEN, FontColor.GREEN, 2, "Medidas-Restritivas", "https://i.imgur.com/W0JI4AE.png", "Fechamento das fronteiras e do comércio não-essencial, além de restringir o transporte público e toda circulação não estritamente necessária."),
        ContainmentStrategy(BackgroundColor.DARK_GREEN, FontColor.DARK_GREEN, 3, "Quarentena", "https://i.imgur.com/FjHaC7A.png", "O governo amplia a capacidade de testes e proíbe estritamente o movimento das pessoas não-autorizadas (lockdown).")
]
