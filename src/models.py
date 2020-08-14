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
    SITUATION = "situation"
    CONTROL = "control"
    CAPACITY = "capacity"
    TRUST = "trust"


class AlertBackground(enum.Enum):
    hide = ""
    blue = "novo normal"
    yellow = "moderado"
    orange = "alto"
    red = "altíssimo"


class IndicatorBackground(enum.Enum):
    hide = "nan"
    blue = 0
    yellow = 1
    orange = 2
    red = 3
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
    IndicatorType.SITUATION.value: Indicator(
        header="SITUAÇÃO",
        caption="Casos por dia por 100 mil habitantes:",
        unit="",
        left_label="Semana passada:",
        right_label="Tendência 📈:",
    ),
    IndicatorType.CONTROL.value: Indicator(
        header="CONTROLE",
        caption="",
        unit="There is no public data on testing.",
        left_label="Rt:",
        right_label="Tendência 📈:",
    ),
    IndicatorType.CAPACITY.value: Indicator(
        header="CAPACIDADE",
        caption="A capacidade hospitalar será atingida em",
        unit="mês(es)",
        left_label="Número de Leitos*:",
        right_label="Capacidade de UTI:",
    ),
    IndicatorType.TRUST.value: Indicator(
        header="CONFIANÇA",
        caption="A cada 10 pessoas infectadas, somente ",
        unit="são diagnosticadas",
        left_label="Mortes por dia:",
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
        recommendation="Simule",
        name="SimulaCovid<br>",
        caption="Simule o impacto de diferentes ritmos de contágio da Covid-19 no seu sistema de saúde.",
        image="https://i.imgur.com/4MLOdTL.png",
    ),
    Product(
        recommendation="Leia",
        name="Distanciamento Social<br>",
        caption="Entenda como o seu local está seguindo medidas de segurança sanitária.",
        image="https://i.imgur.com/xUzGirB.png",
    ),
    Product(
        recommendation="",
        name="Saúde em Ordem<br>",
        caption="Explore setores econômicos de seu <b>Estado</b> ou <b>Regional</b> menos expostos a contaminação por Covid-19",
        image="https://i.imgur.com/PV38lNs.png",
    ),
    Product(
        recommendation="Explore",
        name="Onda Covid<br>",
        caption="Veja aonde estão municípios e estados na curva de mortes registradas até hoje",
        image="https://i.imgur.com/l3vuQdP.png",
    ),
]
