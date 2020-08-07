from typing import NamedTuple, List, Dict
import enum

# Constants
class BackgroundColor(enum.Enum):
    GREEN = "green-bg"
    DARK_GREEN = "dark-green-bg"
    GREY = "grey-bg"
    LIGHT_BLUE = "lightblue-bg"
    GREY_GRADIENT = "grey-gradient-bg"
    LIGHT_BLUE_GRADIENT = "light-blue-gradient-bg"
    DARK_BLUE = "darkblue-bg"
    SIMULATOR_CARD_BG = "simulator-card-bg"


class FontColor(enum.Enum):
    GREY = "grey-span"
    LIGHT_BLUE = "lightblue-span"
    DARK_BLUE = "darkblue-span"


class Document(enum.Enum):
    METHODOLOGY = "https://docs.google.com/document/d/1C7LyLmeeQVV0A3vRqH03Ru0ABdJ6hCOcv_lYVMPQy2M/edit"
    FAQ = "https://docs.google.com/document/d/1lanC52PjzU2taQISs1kO9mEJPtvwZM4uyvnHL9IalbQ/edit"
    GITHUB = "https://github.com/ImpulsoGov/simulacovid/tree/master/COVID19_App"


class Logo(enum.Enum):
    IMPULSO = "https://i.imgur.com/zp9QCDU.png"
    CORONACIDADES = "https://i.imgur.com/BamxSJE.png"
    ARAPYAU = "https://i.imgur.com/SjsMK2A.jpg"


class Link(enum.Enum):
    AMBASSADOR_FORM = "https://forms.gle/iPFE7T6Wrq4JzoEw9"
    YOUTUBE_TUTORIAL = "https://www.youtube.com/watch?v=-4Y0wHMmWAs"


class Illustration(enum.Enum):
    CITY = "https://i.imgur.com/UP2ZylF.png"
    BUILDING = "https://i.imgur.com/zaGvVzy.png"


class IndicatorType(enum.Enum):
    RT = "rt"
    SUBNOTIFICATION_RATE = "subnotification_rate"
    HOSPITAL_CAPACITY = "hospital_capacity"
    SOCIAL_ISOLATION = "social_isolation"


class AlertBackground(enum.Enum):
    hide = ""
    green = "baixo"
    yellow = "médio"
    red = "alto"


class IndicatorBackground(enum.Enum):
    hide = "nan"
    green = "bom"
    yellow = "insatisfatório"
    red = "ruim"
    inloco = "Fonte: inloco"


# Models
class Indicator:
    def __init__(
        self,
        header,
        caption,
        unit,
        left_label,
        right_label,
        risk="",
        display="",
        left_display="",
        right_display="",
    ):
        self.header = header
        self.caption = caption
        self.unit = unit
        self.display = display
        self.risk = risk
        self.left_label = left_label
        self.right_label = right_label
        self.left_display = left_display
        self.right_display = right_display


class ResourceAvailability(NamedTuple):
    locality: str
    cases: int
    deaths: int
    beds: int
    ventilators: int


class ContainmentStrategy(NamedTuple):
    background: BackgroundColor
    color: FontColor
    code: int
    name: str
    image_url: str
    description: str


class SimulatorOutput(NamedTuple):
    color: BackgroundColor
    min_range_beds: int
    max_range_beds: int
    min_range_ventilators: int
    max_range_ventilators: int
    min_range_icu_beds: int
    max_range_icu_beds: int


Strategies: List[ContainmentStrategy] = [
    ContainmentStrategy(
        BackgroundColor.GREY,
        FontColor.GREY,
        1,
        "Não Intervenção",
        Illustration.CITY.value,
        "Nenhuma medida de restrição de contato é adotada pelas autoridades.",
    ),
    ContainmentStrategy(
        BackgroundColor.LIGHT_BLUE,
        FontColor.LIGHT_BLUE,
        2,
        "Medidas Restritivas",
        "https://i.imgur.com/W0JI4AE.png",
        "Fechamento das fronteiras e do comércio não-essencial. Restrição do transporte público e toda circulação não estritamente necessária.",
    ),
    ContainmentStrategy(
        BackgroundColor.DARK_BLUE,
        FontColor.DARK_BLUE,
        3,
        "Quarentena",
        Illustration.BUILDING.value,
        "O governo amplia a capacidade de testes e proíbe estritamente o movimento das pessoas não-autorizadas (lockdown).",
    ),
]

IndicatorCards: Dict[str, Indicator] = {
    IndicatorType.RT.value: Indicator(
        header="Ritmo de Contágio",
        caption="Cada contaminado infecta em média outras",
        unit="pessoas",
        left_label="Semana passada:",
        right_label="Tendência 📈:",
    ),
    IndicatorType.SUBNOTIFICATION_RATE.value: Indicator(
        header="Subnotificação",
        caption="A cada 10 pessoas doentes,",
        unit="são diagnosticadas",
        left_label="Casos confirmados:",
        right_label="Ranking da UF:",
    ),
    IndicatorType.HOSPITAL_CAPACITY.value: Indicator(
        header="Capacidade Hospitalar",
        caption="Os seus leitos estarão todos ocupados em",
        unit="mês(es)",
        left_label="Leitos*:",
        right_label="Leitos UTI:",
    ),
    IndicatorType.SOCIAL_ISOLATION.value: Indicator(
        header="Isolamento Social",
        caption="Na última semana, ficaram em casa cerca de",
        unit="das pessoas",
        left_label="Média semana passada:",
        right_label="Tendência 📈:",
    ),
}


class Product:
    def __init__(self, name, caption: str, image: Illustration, recommendation=""):
        self.recommendation = recommendation
        self.name = name
        self.caption = caption
        self.image = image


ProductCards: List[Product] = [
    Product(
        recommendation="Sugerido",
        name="SimulaCovid",
        caption="simule o impacto de diferentes ritmos de contágio da Covid-19 no seu sistema de saúde.",
        image=Illustration.BUILDING.value,
    ),
    Product(
        recommendation="",
        name="Saúde em Ordem<br>",
        caption="explore que setores não-essenciais da sua economia são menos expostos ao risco de contaminação por Covid-19",
        image=Illustration.CITY.value,
    ),
]
