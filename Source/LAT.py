import json
import requests
import datetime;
import warnings
warnings.filterwarnings("ignore")
import asyncio
from shazamio import Shazam
from audio_extract import extract_audio

class Song_Info:
    def __init__(self, station, title, artist):
        self.station = station
        self.title = title
        self.artist = artist
        self.cur_tm = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def song_to_dict(song_info):
    return {
        'timestamp': song_info.cur_tm,
        'station': song_info.station,
        'title': song_info.title,
        'artist': song_info.artist


def cnv_audio(in_file, out_file):
    print(in_file, out_file)
    extract_audio(input_path=in_file,
                  output_path=out_file,
                  overwrite=True)   

def read_sample(stream_url, buffer_file):
    i = 1
    try:
        with requests.get(stream_url, stream=True, timeout=5.0) as response:
            with open(buffer_file, 'wb') as sample_file:
                for chunk in response.iter_content(chunk_size=10000):
                    if  i > 100:
                        break
                    sample_file.write(chunk)
                    i+=1
        return True
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}") 
        return False

async def shazam_it(music_file):
    shazam = Shazam()
    out = await shazam.recognize(music_file)
    return out

def add_it_to_db(db_name, a_song):
    with open(db_name, 'a') as db_file:
        json.dump(a_song, db_file, default=song_to_dict)
        db_file.write('\n')

async def start_listen():
    file_for_buffer = r"./buffer.aac"
    file_for_mp3 = r"./buffer.mp3"

    station = "Trito"
    live_url = "http://radiostreaming.ert.gr/ert-trito"
    station = "STAR FM Rock Ballads"
    live_url = "https://stream.starfm.de/ballads/mp3-128/"
    station = "RockFM"
    live_url = "https://az10.yesstreaming.net/radio/8060/radio.mp3"
    
    prev_song = ""
    prev_artist = ""
    while True:
        sample = read_sample(live_url, file_for_buffer)
        if sample:
            cnv_audio(file_for_buffer, file_for_mp3)
            shazam_chars = await shazam_it(file_for_mp3)
            print(len(shazam_chars["matches"]))
            if len(shazam_chars["matches"]) != 0:
                sample_song = shazam_chars['track']['title']
                sample_artist = shazam_chars['track']['subtitle']
                song = Song_Info(station, sample_song, sample_artist)
                if prev_song != sample_song:
                    add_it_to_db("RadioList.json", song)
                    print('Added ' + song.title, song.artist)
                    prev_song = sample_song     


await start_listen()
