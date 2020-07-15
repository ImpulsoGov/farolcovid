import requests
import yaml
import json
import os
import amplitude
import utils

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
    data = utils.parse_headers(current_server_session.ws.request)
    user_data = {"has_precise_ip": False}
    if "user_public_data" in data["Cookie"].keys():
        for key in data["Cookie"]["user_public_data"].keys():
            user_data[key] = data["Cookie"]["user_public_data"][key]
        user_data["has_precise_ip"] = True
    else:
        user_data["ip"] = data["Remote_ip"]
    if "user_unique_id" in data["Cookie"].keys():
        user_data["user_id"] = data["Cookie"]["user_unique_id"]
    else:
        user_data["user_id"] = "anonymous"

    return Amplitude_user(os.getenv("AMPLITUDE_KEY"), user_data)


class Amplitude_user:
    def __init__(self, apikey, inuser_data):
        self.key = apikey
        self.user_data = inuser_data

    def log_event(self, event, event_args=dict()):
        event_data = {"user_id": self.user_data["user_id"]}
        # print(self.name + " has " + event)
        event_data["event_type"] = event
        event_data["user_properties"] = event_args
        event_data["ip"] = self.user_data["ip"]
        if self.user_data["has_precise_ip"]:
            event_data["country"] = self.user_data["country_name"]
            event_data["region"] = self.user_data["region"]
            event_data["city"] = self.user_data["city"]
            event_data["location_lat"] = self.user_data["latitude"]
            event_data["location_lng"] = self.user_data["longitude"]
            event_data["carrier"] = self.user_data["isp"]
        request_data = {"api_key": self.key, "events": [event_data]}
        response = requests.post(
            "https://api.amplitude.com/2/httpapi", json=request_data, headers=headers
        )
        return response.json()
