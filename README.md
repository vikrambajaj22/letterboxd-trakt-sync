# letterboxd-trakt-sync
Sync from Letterboxd to Trakt

- Run `python get_letterboxd_watch_history.py`
- Get Client ID and Secret from [Trakt.tv](https://trakt.tv) > User Icon > Settings > Your API Apps > letterboxd-sync and store them in client_id.txt and client_secret.txt respectively
- On the letterboxd-sync app page, click "Authorize", login, and copy the pin shown on the screen
- Run `python update_watch_history_on_trakt.py` to update watch history on Trakt
- Add the failed ones (persisted to trakt_letterboxd_import_not_found.json), if any, manually on Trakt

## TO-DO
- Add watchlist sync