import json
import re
import requests
import sys

from bs4 import BeautifulSoup
from tqdm import tqdm


URL = "https://letterboxd.com"
USER_URL = "https://letterboxd.com/vikrambajaj/films/"

try:
    res = requests.get(USER_URL)
    if res.status_code != 200:
        print("[ERROR] non-200 status code ({}) while getting watched movies".format(res.status_code))
        sys.exit(0)
    soup = BeautifulSoup(res.text, "html.parser")
    # get number of pages
    pagination_links = soup.find_all("li", {"class": "paginate-page"})
    # check last one because count is not reliable (contains hidden pages)
    last_page = int(pagination_links[-1].a.text)
    print("[INFO] there are {} pages of watched movies".format(last_page))
    movies = []
    failed = []
    for i in range(1, last_page+1):
        print("[INFO] processing page {}/{}".format(i, last_page))
        page_url = USER_URL + f"page/{i}/"
        try:
            res = requests.get(page_url)
            if res.status_code != 200:
                print("[ERROR] non-200 status code ({}) while getting watched movies on page {}".format(res.status_code, i))
                sys.exit(0)
            page_soup = BeautifulSoup(res.text, "html.parser")
            page_movies = page_soup.find_all("div", {"class": "linked-film-poster"})
            for movie in tqdm(page_movies):
                movie_url = URL + movie["data-target-link"]
                try:
                    res = requests.get(movie_url)
                    if res.status_code != 200:
                        print("[ERROR] non-200 status code ({}) while getting movies details via {}".format(res.status_code, movie_url))
                        failed.append((movie_url, "non-200 status code"))
                    else:
                        # extract title and year, needed by trakt API to add to watch history
                        regex_pattern = "name: \"(.+)\", releaseYear: \"(\d+)\""
                        match_groups = re.search(regex_pattern, res.text).groups()
                        if len(match_groups) != 2:
                            print("[ERROR] could not extract movies details (title and year) via {}".format(movie_url))
                            failed.append((movie_url, "title/year extraction error"))
                        else:
                            title, year = match_groups
                            movies.append({"title": title, "year": year})
                except Exception as exc:
                    print("[ERROR] exception while getting movies detais for {}: {}".format(movie_url, repr(exc)))
        except Exception as exc:
            print("[ERROR] exception while getting movies on page {}: {}".format(i, repr(exc)))
except Exception as exc:
    print("[ERROR] exception while getting watched movies: {}".format(repr(exc)))

print(f"Parsed {len(movies)} movies successfully, {len(failed)} failed")
with open("watched_movies.json", "w", encoding="utf-8") as f:
    json.dump(movies, f, indent=4)
with open("failed_watched_movies.json", "w", encoding="utf-8") as f:
    json.dump(failed, f, indent=4)