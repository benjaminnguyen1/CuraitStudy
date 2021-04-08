from flask import Flask, render_template, redirect, url_for, session, redirect, request
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)

app.secret_key = "CDajkh0877812896n"
app.config['SESSION_COOKIE_NAME'] = 'Curait Cookie'
TOKEN_INFO = "token_info"
PLAYLIST_NAME = 'Study Playlist by Curait'
PLAYLIST_DESCRIPTION = 'This is a study playlist curated through the use of Curait Study.'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/redirectPage')
def redirectPage():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('tune', _external=True))

@app.route('/tune')
def tune():
    return render_template('tune.html')

@app.route('/playlist', methods=['GET','POST'])
def playlist():
    genre = request.form['genre']
    danceability = request.form['danceability']
    valence = request.form['valence']
    energy = request.form['energy']
    instrumentalness = request.form['instrumentalness']
    session['selected_genre'] = genre
    session['selected_danceability'] = danceability
    session['selected_valence'] = valence
    session['selected_instrumentalness'] = instrumentalness
    session['selected_energy'] = energy
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect(url_for("login", _external=False))

    sp = spotipy.Spotify(auth=token_info['access_token'])
    userjson = sp.current_user()
    userid = userjson['id']
    session['user_id'] = userid


    sp.user_playlist_create(user = userid, name = genre + ' ' + PLAYLIST_NAME, public = True, description = PLAYLIST_DESCRIPTION)
    return redirect(url_for('reccomendations'))
    #return redirect(url_for('test'))

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise "exception"
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if (is_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info

@app.route('/test')
def test():
    genre = session.get('selected_genre')
    danceability = session.get('selected_danceability')
    valence = session.get('selected_valence')
    energy = session.get('selected_energy')
    instrumentalness = session.get('selected_instrumentalness')

    danceability = float(danceability)/10.0
    valence = float(valence)/10.0
    energy = float(energy)/10.0
    instrumentalness = float(instrumentalness)/10.0
    return render_template('testslider.html',content=danceability,content1 = valence, content2 = energy,
    content3 = instrumentalness, genre=genre, )

#get song reccomendations based on criteria and add them to page
@app.route('/reccomendations', methods=['GET'])
def reccomendations():

    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect(url_for("login", _external=False))

    sp = spotipy.Spotify(auth=token_info['access_token'])
    genre = session.get('selected_genre')
    danceability = session.get('selected_danceability')
    valence = session.get('selected_valence')
    energy = session.get('selected_energy')
    instrumentalness = session.get('selected_instrumentalness')
    list_of_songs = []
    danceability = float(danceability)/10.0
    valence = float(valence)/10.0
    energy = float(energy)/10.0
    instrumentalness = float(instrumentalness)/10.0

    if genre == 'Lofi':
        seed_genres=['Lofi']
        seed_artists = ['225l1KEprObX8xgl8xo2Gc,0RUwm9ukhlW1oXDzXxj3C0']
        seed_tracks = ['09GSyzKeyOThTdESNeWIPZ,4goIDy7GegReFNsicUu63h']


        target_danceability = danceability
        target_energy = energy
        target_valence = valence
        target_instrumentalness = instrumentalness

        #Dev will set beforehand
        target_liveness = 0.1534
        target_acousticness = 0.6389
        target_tempo = 106
        target_speechiness = 0.1243



    if genre == 'Classical':
        seed_genres=['Classical']
        seed_artists = ['4NJhFmfw43RLBLjQvxDuRS,7t8PD6GvlbqByM0g7ysSHH']
        seed_tracks = ['5kRBxcHNbWOUFvv15I0dMP,5jXA67Q4thnNLEDxMzu9QE']


        target_danceability = danceability
        target_energy = energy
        target_valence = valence
        target_instrumentalness = instrumentalness

        #Dev will set beforehand
        target_liveness = 0.1
        target_acousticness = 0.85
        target_tempo = 70
        target_speechiness = 0.1243


    if genre == 'Jazz':
        seed_genres=['Jazz']
        seed_artists = ['1QDou4hCker2eGblLzIq80,22KzEvCtrTGf9l6k7zFcdv']
        seed_tracks = ['7hdbfMdjsdclkZONmT7lD6,7E2435OwyheyRJkmJjEMW7']


        target_danceability = danceability
        target_energy = energy
        target_valence = valence
        target_instrumentalness = instrumentalness

        #Dev will set beforehand
        target_liveness = 0.75
        target_acousticness = 0.75
        target_tempo = 70
        target_speechiness = 0.15




    result = sp.recommendations(seed_artists=seed_artists,seed_genres=seed_genres,seed_tracks=seed_tracks,
    target_speechiness=target_speechiness,target_tempo=target_tempo,target_danceability=target_danceability,
    target_liveness=target_liveness,target_acousticness=target_acousticness,target_energy=target_energy,
    target_valence=target_valence,target_instrumentalness=target_instrumentalness)
    result1 = result['tracks'][:-1]
    for track in result1:
        list_of_songs.append(track['uri'])

    userid = session.get('user_id')

    prePlaylist = sp.user_playlists(user = userid)
    playlist = prePlaylist['items'][0]['id']

    sp.user_playlist_add_tracks(user = userid, playlist_id=playlist,tracks=list_of_songs)

    prePlaylist1 = sp.user_playlists(user=userid)
    playlist1 = prePlaylist1['items'][0]['id']

    playlist_url = sp.playlist(playlist_id=playlist1)['external_urls']['spotify']
    session['playlist_url'] = playlist_url
    return redirect(url_for('player'))

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise "exception"
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if (is_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info

#embed playlist player
@app.route('/player')
def player():

    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect(url_for("login", _external=False))

    sp = spotipy.Spotify(auth=token_info['access_token'])
    playlisturl = session.get('playlist_url')
    playlisturl = "https://open.spotify.com/embed" + playlisturl[24:]
    return render_template('player.html',playlisturl=playlisturl)

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise "exception"
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if (is_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info

#Practice code
'''@app.route('/tune')
def tune():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect(url_for("login", _external=False))

    sp = spotipy.Spotify(auth=token_info['access_token'])
    user = sp.current_user()
    userid = user['id']
    return

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise "exception"
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if (is_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info'''



def create_spotify_oauth():
    return SpotifyOAuth(
            client_id="9a6b473b72af45fa90a60f1c6280f61e",
            client_secret="b0472eabc2704e799fc485691d82c50f",
            redirect_uri=url_for('redirectPage', _external=True),
            scope="playlist-modify-public, user-library-read")


if __name__ == '__main__':
    app.run(debug=True)
