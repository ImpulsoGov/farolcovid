import requests
import yaml
import json
import os

ipinfo_url = "https://geolocation-db.com/json/"
headers = {"Content-Type": "application/json", "Accept": "*/*"}

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
    "koto",
    "buran",
    "soto",
    "iji",
    "shima",
    "naru",
    "to",
    "iwo",
    "oki",
    "ya",
    "ma",
    "waza",
    "mura",
    "jima",
    "uji",
    "sama",
    "uzu",
    "maki",
    "ko",
    "hideo",
    "saki",
    "mate",
]

# Changing this function means probably ERASING ALL OF OUR USER DATA, SO PROCEED CAREFULLY
def hash_mock_name(ip):
    total = 1
    parts = [int(i) for i in ip.split(".")]
    for char in ip:
        total = total * ord(char)
    size = len(names)
    pos1 = total % size
    pos2 = (total * parts[0] + 929) % size
    pos3 = (total * parts[0] * 349 * parts[1] + 571) % size
    pos4 = (total * parts[1] * 571 * +parts[2] * 191 + 571) % size
    pos5 = (total * parts[1] * 487 * +parts[2] * 571 + parts[3] * 199 + 929) % size
    pos6 = (
        total * parts[0] * 929 * +parts[1] * 199 + parts[3] * 383 + parts[2] * 929 + 571
    ) % size
    name = (
        names[pos1]
        + names[pos2]
        + " "
        + names[pos3]
        + names[pos4]
        + " "
        + names[pos5]
        + names[pos6]
    )
    # print(name)
    return name


def gen_user(current_server_session):
    user_ip = list(current_server_session._session_info_by_id.values())[
        0
    ].ws.request.remote_ip
    user_name = hash_mock_name(user_ip)
    return Amplitude_user(os.getenv("AMPLITUTE_KEY"), user_ip, user_name)


class Amplitude_user:
    def __init__(self, apikey, inip, inname):
        self.key = apikey
        self.ip = inip
        self.name = inname
        self.has_ip_info = False
        try:
            self.ip_data = json.loads(requests.get(ipinfo_url + str(inip)).content)
            if self.ip_data["country_code"] != "Not found":
                self.has_ip_info = True
        except:
            pass

    def log_event(self, event, event_args=dict()):
        event_data = {"user_id": self.name}
        # print(self.name + " has " + event)
        event_data["event_type"] = event
        event_data["user_properties"] = event_args
        event_data["ip"] = self.ip
        if self.has_ip_info:
            event_data["country"] = self.ip_data["country_name"]
            event_data["region"] = self.ip_data["state"]
            event_data["city"] = self.ip_data["city"]
            event_data["location_lat"] = self.ip_data["latitude"]
            event_data["location_lng"] = self.ip_data["longitude"]
        request_data = {"api_key": self.key, "events": [event_data]}
        response = requests.post(
            "https://api.amplitude.com/2/httpapi", json=request_data, headers=headers
        )
        return response.json()
