from flask import Flask
from flask import request
import mechanize
import bs4
from flask_cors import CORS, cross_origin
import pandas as pd
import yaml
from dotenv import load_dotenv
from pathlib import Path
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

app.config["CORS_HEADERS"] = "Content-Type"

# URL INITIALIZATION
env_path = Path("..") / ".env"
load_dotenv(dotenv_path=env_path, override=True)
config = yaml.load(open("configs/config.yaml", "r"), Loader=yaml.FullLoader)

if os.getenv("IS_LOCAL") == "TRUE":
    datasource_url = config["br"]["api"]["local"]
else:
    datasource_url = config["br"]["api"]["external"]
# Remove before publication
datasource_url = "http://192.168.0.5:7000/"
datasource_url = datasource_url + config["br"]["api"]["endpoints"]["maps"]
# For trying to redownload the cache in case of failure at initialization
def check_for_cache_download():
    global cache_place_df
    if cache_place_df is None:
        try:
            cache_place_df = pd.read_csv(datasource_url)
            cache_place_df["cache"] = [None for i in range(cache_place_df.shape[0])]
        except Exception as e:
            print("Map Datasource unreachable" + str(e))
            cache_place_df = None


def get_iframe_map(place_id):
    """ Clones and adapts a map inteded for use in an iframe"""
    try:
        place_df = pd.read_csv(
            datasource_url
        )  # Reads our datasource for info of where to find the original plots
        # and what build version they are
    except:
        return "Map datasource unreachable"
    try:
        is_brazil = place_id == "BR"
        new_data = place_df.loc[place_df["place_id"] == place_id]
        map_id = new_data["map_id"].values[0]  # Datawrapper id of our map
        old_data = cache_place_df[
            cache_place_df["place_id"] == place_id
        ]  # Old data we have in store of that same state
        old_index = old_data.index[0]
        if (
            old_data["hashes"].values[0] == new_data["hashes"].values[0]
            and old_data["map_id"].values[0] == new_data["map_id"].values[0]
            and old_data["cache"].values[0] == None
        ):
            # its time to inser in our empty cache with the HTML code
            try:
                map_code = clone_map(
                    f"https://datawrapper.dwcdn.net/{map_id}/", is_brazil=is_brazil
                )
                cache_place_df.iloc[old_index]["cache"] = map_code
                return map_code
            except Exception as e:
                return "An unknown error happened : " + str(e)
        elif (
            old_data["hashes"].values[0] == new_data["hashes"].values[0]
            and old_data["map_id"].values[0] == new_data["map_id"].values[0]
        ):
            # Its already in cache, just return it
            # print("giving from cache")
            return cache_place_df.iloc[old_index]["cache"]
        else:
            # overriding the cache with new cache info and html code
            map_code = clone_map(
                f"https://datawrapper.dwcdn.net/{map_id}/", is_brazil=is_brazil
            )
            cache_place_df.iloc[old_index]["cache"] = map_code
            cache_place_df.iloc[old_index]["hashes"] = new_data["hashes"].values[0]
            cache_place_df.iloc[old_index]["map_id"] = new_data["map_id"].values[0]
            return map_code
    except Exception as e:
        return "A unknown exception has occured : " + str(e)


def preload_cache():
    """ Tries to fill in the entire cache at once. Useful for initialization"""
    try:
        place_df = pd.read_csv(datasource_url)
        for place_id in place_df["place_id"].values:
            get_iframe_map(place_id)
    except Exception as e:
        print("Unable to preload cache: " + str(e))


def main_clone(url):
    """ Simply clones the webpage, with no cleaning"""
    # Browser
    br = mechanize.Browser()

    # Browser options
    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    # br.set_handle_redirect(True)
    # br.set_handle_referer(True)
    br.set_handle_robots(False)

    # Follows refresh 0 but not hangs on refresh > 0
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    # Want debugging messages?
    # br.set_debug_http(True)
    # br.set_debug_redirects(True)
    # br.set_debug_responses(True)

    # User-Agent (this is cheating, ok?)
    br.addheaders = [
        (
            "User-agent",
            "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1",
        )
    ]
    try:
        html = br.open(url, timeout=2).read()
    except Exception as e:
        raise Exception(
            """Carregamento do mapa falhou, tente novamente mais tarde.<br> 
    <button type="button" onclick="location.reload();">Clique aqui apra tentar novamente</button>
    """
        )
    soup = bs4.BeautifulSoup(html, "html.parser")
    return soup  # gets our cloned page, but we still have some more cleaning to do


def clone_with_src(url):
    """ Clones but also redirects the URL so that the scripts hosted in that server will stil work.
        (At least most of the times)
    """
    soup = main_clone(url)
    for script in soup.find_all("script"):
        if script.get("src") != None and script["src"][0] != "h":
            script["src"] = url + script["src"]
    return soup.prettify()


def simple_clone(url):
    """ Just clones and makes it pretty by identing and etc"""
    return main_clone(url).prettify()


def clone_map(url, is_brazil=False):
    """ Clones our map webpage by replacing the script sources, link sources and adding new scripts hosted on our main streamlit server"""
    soup = main_clone(url)
    for script in soup.find_all("script"):  # Replaces the sources of scripts
        if script.get("src") != None and script["src"][0] != "h":
            script["src"] = url + script["src"]
    for link in soup.find_all("link"):  # Same with links
        if link.get("href") != None and link["href"][0] != "h":
            link["href"] = url + link["href"]
    # create a new tag
    body = soup.find("body")

    clicker = soup.new_tag("script")
    resizer = soup.new_tag("script")
    if is_brazil:
        clicker["src"] = "/resources/map-reader-internal-country.js"
        resizer["src"] = "/resources/resize-map-state.js"
    else:
        clicker["src"] = "/resources/map-reader-internal-state.js"
        resizer["src"] = "/resources/resize-map-state.js"
    body.insert_after(
        clicker
    )  # Adds the click listeners to engage with the parent page, which is farol
    body.insert_after(resizer)
    body[
        "onload"
    ] = "init_listener();resize_iframe_map();"  # Makes it so that the listeners are initialized at iframe load

    return soup.prettify()


def clone_two_levels(url):
    """ For cloning of stuff that already interacts with parent windows"""
    soup = main_clone(url)
    for script in soup.find_all("script"):
        if script.get("src") != None and script["src"][0] != "h":
            script["src"] = url + script["src"]
    return soup.prettify().replace("window.parent", "window.parent.parent")


# THESE CROSS ORIGIN DECORATORS ARE SUPER IMPORTANT FOR OU CROSS-SITE SCRIPTING
# BECAUSE BASICALLY THEY SAY WE ARE AN OPEN API, WHICH ALLOWS US AND
# OTHERS TO GET OUR MAPS, AS WELL AS USE THEM IT ON STREAMLIT APPLICATIONS BY
# FOLLOWING THE SAME PROTOCOL FOR FINDING THE STATE AND CITY SELECTION BOX
# THE STATE SELECTION BOX IS THE FIRST OF THE PAGE AND THE CITY SELECTION BOX IS THE THIRD


@app.route("/")
@cross_origin(
    origin="*", headers=["Content-Type", "Authorization", "access-control-allow-origin"]
)
def hello_world():
    return "Hello, World!"


@app.route("/map-iframe", methods=["GET"])
@cross_origin(
    origin="*", headers=["Content-Type", "Authorization", "access-control-allow-origin"]
)
def iframe_map():
    """ Map cloning endpoint
        Must be acessed by also providing a get argument called place_id
        ex: ?place_id=SP for São Paul state
        Gives the User our cloned datawrapper map with our custom javascript coded injected
    """
    check_for_cache_download()  # Checks for existing cache

    try:
        place_id = request.args.get("place_id")
    except:
        return "Place ID missing"

    return get_iframe_map(place_id)


if __name__ == "__main__":
    # This will try to load the data and save it in cache, if this is not able to do so we might try again later
    try:
        cache_place_df = pd.read_csv(datasource_url)
        cache_place_df["cache"] = [None for i in range(cache_place_df.shape[0])]
    except Exception as e:
        print("Map Datasource unreachable " + str(e))
        cache_place_df = None
    print("Preloading cache")
    preload_cache()
    print("cache loaded sucessfully")
    app.run(host="0.0.0.0", port=5000, debug=False)

