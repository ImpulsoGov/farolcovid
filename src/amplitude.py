import requests
import yaml
import json

headers = {"Content-Type": "application/json", "Accept": "*/*"}
secrets = yaml.load(open("../src/configs/secrets.yaml", "r"), Loader=yaml.FullLoader)
r = requests.post("https://api.amplitude.com/2/httpapi", params={}, headers=headers)
names = [  # Please keep this at a length equal to a prime at ALL TIMES
    "ho",
    "jung",
    "kim",
    "pak",
    "lee",
    "su",
    "chi",
    "san",
    "ne",
    "po",
    "koi",
    "sen",
    "kai",
    "ki",
    "xu",
    "wu",
    "han",
    "nem",
    "lil",
    "sa",
    "ka",
    "goi",
    "pan",
    "yi",
    "choi",
    "min",
    "joi",
    "ye",
    "joo",
    "young",
    "il",
]


def hash_mock_name(ip):
    total = 1
    parts = [int(i) for i in ip.split(".")]
    for char in ip:
        total = total * ord(char)
    size = len(names)
    pos1 = total % size
    pos2 = (total * parts[0] + 929) % size
    pos3 = (total * parts[0] * 349 * parts[1] + 571) % size
    name = names[pos1] + " " + names[pos2] + " " + names[pos3]
    print(name)
    return name


def gen_user(current_server_session):
    user_ip = list(current_server_session._session_info_by_id.values())[
        0
    ].ws.request.remote_ip
    user_name = hash_mock_name(user_ip)
    return Amplitude_user(secrets["amplitude"]["api_key"], user_ip, user_name)


class Amplitude_user:
    def __init__(self, apikey, inip, inname):
        self.key = apikey
        self.ip = inip
        self.name = inname

    def log_event(self, event, event_args):
        event_data = {"user_id": self.name}
        event_data["event_type"] = event
        event_data["user_properties"] = event_args
        event_data["ip"] = self.ip
        request_data = {"api_key": self.key, "events": [event_data]}
        response = requests.post(
            "https://api.amplitude.com/2/httpapi", json=request_data, headers=headers
        )
        return response.json()
