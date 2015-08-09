import spotify
import time
import threading
import sys
import paho.mqtt.client as mqtt
import random
import os

def on_connect(client, userdata, rc):
    print('Connected with result code '+str(rc))
    client.subscribe('music/#')

def processSearch(results):
    choice = random.choice(results.playlists)
    print 'Will play {}'.format(choice)
    playPlaylist(choice)

def playPlaylist(searchPlaylist):
    playlist = searchPlaylist.playlist.load()
    print playlist.tracks
    track = playlist.tracks[0].load()
    print track
    session.player.load(track)
    session.player.play()

def selectPlaylist(client, userdata, message):
    print 'Searching for playlist with {}'.format(message.payload)
    session.search(message.payload, processSearch)

client = mqtt.Client("spotify_controller")
client.on_connect = on_connect
client.message_callback_add('music/playlist', selectPlaylist)
client.connect('192.168.1.74', 1883,60)

logged_in_event = threading.Event()

def connection_state_listener(session):
    if session.connection.state is spotify.ConnectionState.LOGGED_IN:
        logged_in_event.set()

session = spotify.Session()
session.on(
    spotify.SessionEvent.CONNECTION_STATE_UPDATED,
    connection_state_listener)

session.login(os.environ['SPOTIFY_USERNAME'], os.environ['SPOTIFY_PASSWORD'])

audio = spotify.AlsaSink(session)

event_loop = spotify.EventLoop(session)
event_loop.start()

client.loop_start()

while not logged_in_event.wait(0.1):
    session.process_events()

track = session.get_track('spotify:track:6xZtSE6xaBxmRozKA0F6TA').load()
session.player.load(track)
session.player.play()

while 1:
    pass
