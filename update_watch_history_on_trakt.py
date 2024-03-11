import json
import requests
import simplejson
import sys


trakt_api = "https://api.trakt.tv"


def get_auth():
    with open("client_id.txt", "r") as f:
        client_id = f.read().strip()
    with open("client_secret.txt", "r") as f:
        client_secret = f.read().strip()
    client_pin = input("Paste PIN from Login Success page:").strip()
    if not client_pin:
        print("[ERROR] PIN needed!")
        sys.exit(0)
    res = requests.post(trakt_api+"/oauth/token", data=simplejson.dumps({
        "code": client_pin,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
        "grant_type": "authorization_code"
    }), headers={"Content-Type": "application/json"})
    if res.status_code != 200:
        print("[ERROR] Aath error: {}".format(res.json()))
    else:
        access_token = res.json()["access_token"]
    return client_id, access_token


def get_watched_movies(client_id, access_token):
    # returns name and year of watched movies to prevent duplicate add
    res = requests.get(trakt_api+"/sync/watched/movies", headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(access_token),
        "trakt-api-version": "2",
        "trakt-api-key": client_id
    })
    if res.status_code != 200:
        print("[ERROR] could not get watch history")
        sys.exit(0)
    else:
        watched = [{"title": item["movie"]["title"], "year": str(
            item["movie"]["year"])} for item in res.json()]
    return watched


client_id, access_token = get_auth()
trakt_watched = get_watched_movies(client_id, access_token)

with open("letterboxd_watched_movies.json", "r") as f:
    letterboxd_watched = json.load(f)
    letterboxd_watched = [{"title": item["title"].replace("\\", ""), "year": item["year"]} for item in letterboxd_watched]

print("[INFO] watched {} movies on Letterboxd, {} movies on Trakt".format(
    len(letterboxd_watched), len(trakt_watched)))
letterboxd_not_trakt = [
    item for item in letterboxd_watched if item not in trakt_watched]
print("[INFO] {} Letterboxd movies not on Trakt, adding them ...".format(
    len(letterboxd_not_trakt)))

res = requests.post(trakt_api+"/sync/history", data=simplejson.dumps({
    "movies": letterboxd_not_trakt
}), headers={
    "Content-Type": "application/json",
    "Authorization": "Bearer {}".format(access_token),
    "trakt-api-version": "2",
    "trakt-api-key": client_id
})
if not str(res.status_code).startswith("2"):
    print("[ERROR] non-2xx status code when updating watch history on Trakt: {}".format(res.status_code))
else:
    added = res.json()["added"]["movies"]
    not_found = res.json()["not_found"]["movies"]
    print("[INFO] added {} movies from Letterboxd to Trakt, {} failed/not-found".format(added, len(not_found)))
    with open("trakt_letterboxd_import_not_found.json", "w", encoding="utf-8") as f:
        json.dump(not_found, f, indent=4)