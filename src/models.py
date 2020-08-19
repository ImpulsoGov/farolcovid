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
        risk="nan",
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
    icu_beds: int


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
        header="SITUAÇÃO DA DOENÇA",
        caption="Hoje são <b>reportados</b>❗ em média",
        unit="casos/100k hab.",
        left_label="Nesta tendência há:",
        right_label="Tendência:",
    ),
    IndicatorType.CONTROL.value: Indicator(
        header="CONTROLE DA DOENÇA",
        caption="Não há dados abertos sistematizados de testes ou rastreamento de contatos no Brasil. Logo, <b>usamos estimativas de Rt para classificação.</b>",
        unit="There is no public data on testing.",
        left_label="Rt:",
        right_label="Tendência:",
    ),
    IndicatorType.CAPACITY.value: Indicator(
        header="CAPACIDADE DO SISTEMA",
        caption="A capacidade hospitalar será atingida em",
        unit="mês(es)",
        left_label="Número de Leitos*:",
        right_label="Capacidade de UTI:",
    ),
    IndicatorType.TRUST.value: Indicator(
        header="CONFIANÇA DOS DADOS",
        caption="A cada 10 pessoas infectadas, somente ",
        unit="são diagnosticadas",
        left_label="Mortes por dia:",
        right_label="Tendência:",
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
        caption="O que acontecerá com meu sistema de saúde local se o ritmo de contágio aumentar ou diminuir?",
        image="https://i.imgur.com/4MLOdTL.png",
    ),
    Product(
        recommendation="Descubra",
        name="Distanciamento Social<br>",
        caption="As pessoas do meu município estão ficando em casa?",
        image="https://i.imgur.com/xUzGirB.png",
    ),
    Product(
        recommendation="Explore",
        name="Saúde em Ordem<br>",
        caption="Quais atividades econômicas meu município deveria reabrir primeiro?",
        image="https://i.imgur.com/PV38lNs.png",
    ),
    Product(
        recommendation="Navegue",
        name="Onda Covid<br>",
        caption="Onde meu município está na curva da doença?",
        image="https://i.imgur.com/l3vuQdP.png",
    ),
]


class Dimension:
    def __init__(self, text):
        self.text = text


DimensionCards: List[Dimension] = [
    Dimension(
        text="<b>1. Situação da doença,</b> que busca medir como a doença está se espalhando no território.",
    ),
    Dimension(
        text="<b>2. Controle da doença,</b> que retrata a capacidade do poder público de detectar os casos.",
    ),
    Dimension(
        text="<b>3. Capacidade de respostas do sistema de saúde,</b> que reflete a situação do sistema de saúde e risco de colapso.",
    ),
    Dimension(
        text="<b>4. Confiança dos dados,</b> que reflete a qualidade das medições de casos sendo feitas pelos governos.",
    ),
]
