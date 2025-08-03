from dotenv import load_dotenv
import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
from pathlib import Path
import random
from flask import Flask, session, redirect, url_for, request

script_dir = Path(__file__).parent
cache_path = script_dir / ".cache"

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")
scope = "user-modify-playback-state,user-read-playback-state"

app = Flask(__name__)
app.secret_key = os.urandom(64)
cache_handler = FlaskSessionCacheHandler(session)

oauth = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope, cache_handler=cache_handler, show_dialog=True)
sp = Spotify(auth_manager=oauth)

app = Flask(__name__)
app.secret_key = os.urandom(64)
cache_handler = FlaskSessionCacheHandler(session)

@app.route("/")
def home():
    if not oauth.validate_token(cache_handler.get_cached_token()):
        return redirect(oauth.get_authorize_url())
    return redirect(url_for("get_artist"))

@app.route("/callback")
def callback():
    oauth.get_access_token(request.args["code"])
    return redirect(url_for("get_artist"))

@app.route("/get_artist")




def get_artist_id_name(artist_name: str) -> tuple[str, str] | None:
    searched = sp.search(q=artist_name, type="artist", limit=5)
    if not searched["artists"]["items"]:
        print("Couldn't find any artist with that name.")
        return None
    print("\n------------------------------------------\nFound the following artists:\n-------------------------------------------\n")
    for i, artist in enumerate(searched["artists"]["items"]):
        print(f"{i + 1}. {artist["name"]} (Followers: {artist["followers"]["total"]})")
    
    chosen = int(input("------------------------------------------\nChoose an artist by number: (e.g. 1, 2, 3)\n------------------------------------------\n"))
    if not str(chosen).isdigit() or chosen < 1 or chosen > len(searched["artists"]["items"]):
        print("Invalid choice. Please enter a valid number.")
        return None
    chosen_index = chosen - 1
    return searched["artists"]["items"][chosen_index]["id"], searched["artists"]["items"][chosen_index]["name"]

def play_top_track_random(artist_name: str) -> None:
    result = get_artist_id_name(artist_name)
    if not result:
        return None
    artist_id, name  = result
    top_tracks = sp.artist_top_tracks(artist_id)["tracks"]

    if not top_tracks:
        print("Artist has no tracks.")
        return None
    
    track = random.choice(top_tracks)
    print(f"------------------------------------------\nPlaying {track['name']} by {name}\n------------------------------------------\n")

    devices = sp.devices()
    if not devices["devices"]:
        print("\n------------------------------------------\nNo active devices found. Open spotify on a device and try again.\n------------------------------------------\n")
        return
    device_id = devices["devices"][0]["id"]
    sp.start_playback(device_id=device_id, uris=[track["uri"]])


def main() -> None:
    chosen_artist = input("\n------------------------------------------\nEnter the name of the artist: ")
    play_top_track_random(chosen_artist)

if __name__ == "__main__":
    app.run(debug=True)
    #main()