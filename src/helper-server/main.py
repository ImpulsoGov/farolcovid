from flask import Flask
from flask import request
import mechanize
import bs4
from flask_cors import CORS, cross_origin
import pandas as pd

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

app.config["CORS_HEADERS"] = "Content-Type"
try:
    cache_place_df = pd.read_csv("http://192.168.0.5:7000/br/maps")
    cache_place_df["cache"] = [None for i in range(cache_place_df.shape[0])]
except:
    print("Map Datasource unreachable")
    cache_place_df = None


def check_for_cache_download():
    global cache_place_df
    if cache_place_df is None:
        try:
            cache_place_df = pd.read_csv("http://192.168.0.5:7000/br/maps")
            cache_place_df["cache"] = [None for i in range(cache_place_df.shape[0])]
        except:
            print("Map Datasource unreachable")
            cache_place_df = None


def main_clone(url):
    # Browser
    br = mechanize.Browser()

    # Browser options
    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
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
    html = br.open(url).read()
    soup = bs4.BeautifulSoup(html, "html.parser")
    return soup


def clone_with_src(url):
    soup = main_clone(url)
    for script in soup.find_all("script"):
        if script.get("src") != None and script["src"][0] != "h":
            script["src"] = url + script["src"]
    return soup.prettify()


def simple_clone(url):
    return main_clone(url).prettify()


def clone_map(url):
    soup = main_clone(url)
    for script in soup.find_all("script"):
        if script.get("src") != None and script["src"][0] != "h":
            script["src"] = url + script["src"]
    for link in soup.find_all("link"):
        if link.get("href") != None and link["href"][0] != "h":
            link["href"] = url + link["href"]
    # create a new tag
    body = soup.find("body")
    tag = soup.new_tag("script")
    tag[
        "src"
    ] = "https://datawrapper.dwcdn.net/lib/blocks/subscriptions.chart-blocks.255d0b80.js"
    clicker = soup.new_tag("script")
    clicker["src"] = "/resources/map-reader-internal.js"
    body.insert_after(clicker)
    body["onload"] = "init_listener();"
    # insert new tag after head tag
    # body.insert_after(tag)
    return soup.prettify()


def clone_two_levels(url):
    soup = main_clone(url)
    for script in soup.find_all("script"):
        if script.get("src") != None and script["src"][0] != "h":
            script["src"] = url + script["src"]
    return soup.prettify().replace("window.parent", "window.parent.parent")


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
    check_for_cache_download()
    try:
        place_df = pd.read_csv("http://192.168.0.5:7000/br/maps")
    except:
        return "Map datasource unreachable"
    try:
        place_id = request.args.get("place_id")
        new_data = place_df.loc[place_df["place_id"] == place_id]
        map_id = new_data["map_id"].values[0]
        old_data = cache_place_df[cache_place_df["place_id"] == place_id]
        old_index = old_data.index[0]
        if (
            old_data["hashes"].values[0] == new_data["hashes"].values[0]
            and old_data["map_id"].values[0] == new_data["map_id"].values[0]
            and old_data["cache"].values[0] == None
        ):
            # its time to update with the new code
            try:
                map_code = clone_map(f"https://datawrapper.dwcdn.net/{map_id}/")
                cache_place_df.iloc[old_index]["cache"] = map_code
                return map_code
            except Exception as e:
                return "An unknown error happened : " + str(e)
        elif (
            old_data["hashes"].values[0] == new_data["hashes"].values[0]
            and old_data["map_id"].values[0] == new_data["map_id"].values[0]
        ):
            # Its already in cache
            return cache_place_df.iloc[old_index]["cache"]
        else:
            # overriding the cache
            map_code = clone_map(f"https://datawrapper.dwcdn.net/{map_id}/")
            cache_place_df.iloc[old_index]["cache"] = map_code
            cache_place_df.iloc[old_index]["hashes"] = new_data["hashes"].values[0]
            cache_place_df.iloc[old_index]["map_id"] = new_data["map_id"].values[0]
            return map_code
    except exception as e:
        return "Place id either not given or not found in our database : " + str(e)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

