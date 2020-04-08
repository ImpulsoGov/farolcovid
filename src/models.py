from typing import NamedTuple, List
import enum

# Constants
class BackgroundColor(enum.Enum):
    GREEN='green-bg'
    DARK_GREEN = 'dark-green-bg'
    GREY='grey-bg'
    LIGHT_BLUE='lightblue-bg'
    GREY_GRADIENT='grey-gradient-bg'
    LIGHT_BLUE_GRADIENT='light-blue-gradient-bg'
    DARK_BLUE='darkblue-bg'
    SIMULATOR_CARD_BG='simulator-card-bg'

class FontColor(enum.Enum):
    GREY='grey-span'
    LIGHT_BLUE='lightblue-span'
    DARK_BLUE='darkblue-span'

class Document(enum.Enum):
    METHODOLOGY='https://docs.google.com/document/d/1C7LyLmeeQVV0A3vRqH03Ru0ABdJ6hCOcv_lYVMPQy2M/edit'
    FAQ='https://docs.google.com/document/d/1lanC52PjzU2taQISs1kO9mEJPtvwZM4uyvnHL9IalbQ/edit'
    GITHUB='https://github.com/ImpulsoGov/simulacovid/tree/master/COVID19_App'


class Logo(enum.Enum):
    IMPULSO='https://i.imgur.com/zp9QCDU.png'
    CORONACIDADES='https://i.imgur.com/BamxSJE.png'
    ARAPYAU='https://i.imgur.com/SjsMK2A.jpg'

class Link(enum.Enum):
    AMBASSADOR_FORM='https://forms.gle/iPFE7T6Wrq4JzoEw9'

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
        ContainmentStrategy(BackgroundColor.GREY, FontColor.GREY, 1, "Não Intervenção", "https://i.imgur.com/pxYFm76.png", "Nenhuma medida de restrição de contato é adotada pelas autoridades."),
        ContainmentStrategy(BackgroundColor.LIGHT_BLUE, FontColor.LIGHT_BLUE, 2, "Medidas Restritivas", "https://i.imgur.com/W0JI4AE.png", "Fechamento das fronteiras e do comércio não-essencial, além de restringir o transporte público e toda circulação não estritamente necessária."),
        ContainmentStrategy(BackgroundColor.DARK_BLUE, FontColor.DARK_BLUE, 3, "Quarentena", "https://i.imgur.com/FjHaC7A.png", "O governo amplia a capacidade de testes e proíbe estritamente o movimento das pessoas não-autorizadas (lockdown).")
]
