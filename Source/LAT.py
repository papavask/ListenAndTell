import json
import requests
import datetime;
import warnings
warnings.filterwarnings("ignore")
import asyncio
from shazamio import Shazam
#from audio_extract import extract_audio
import ffmpeg as ff
import time as tm
import pandas as pd
import sys

def convert_to_wav2(input_file, output_file):
    print(f"Conver {input_file} to {output_file}")
    ff.input(input_file).output(output_file, format='wav').run(overwrite_output=True)
    
def convert_to_wav(input_file, output_file):
    ff.input(input_file).output(output_file, format="wav").run(
        overwrite_output=True,
        quiet=True,  # Suppresses most output
        capture_stdout=True,  # Captures stdout (removes printed messages)
        capture_stderr=True   # Captures stderr (removes warnings/errors)
    )


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
    }


#def cnv_audio(in_file, out_file):
    #print(in_file, out_file)
    #extract_audio(input_path=in_file,
    #              output_path=out_file,
    #              overwrite=True)   

def read_sample2(stream_url, buffer_file):
    i = 1
    try:
        with requests.get(stream_url, stream=True, timeout=3.0) as response:
            print("Size:", response.request.headers['Content-Length'])
            with open(buffer_file, 'wb') as sample_file:
                for chunk in response.iter_content(chunk_size=10000):
                    if  i > 200:
                        break
                    sample_file.write(chunk)
                    i+=1
        return True
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}") 
        return False


def read_sample(stream_url, buffer_file):
    i = 1
    try:
        # Increase timeout or remove it if necessary
        with requests.get(stream_url, stream=True, timeout=10.0) as response:
            if response.status_code == 200:
                #print("Size:", response.request.headers['Content-Length'])
                with open(buffer_file, 'wb') as sample_file:
                    for chunk in response.iter_content(chunk_size=10000):
                        if chunk:  # Filter out keep-alive new chunks
                            if i > 100:
                                break
                            sample_file.write(chunk)
                            i += 1
                return True
            else:
                print(f"Failed to retrieve stream: HTTP {response.status_code}")
                return False
    except requests.exceptions.RequestException as err:
        print(f"Request failed: {err}")
        return False
    except Exception as err:
        print(f"Unexpected error: {err}")
        return False

async def shazam_it(music_file):
    shazam = Shazam()
    out = await shazam.recognize(music_file)
    return out

def add_it_to_db(db_name, a_song):
    with open(db_name, 'a') as db_file:
        json.dump(a_song, db_file, default=song_to_dict)
        db_file.write('\n')

async def start_listen(station, live_url):
    file_for_buffer = r"./buffer.aac"
    file_for_buffer = r"./buffer.mp3"
    file_for_buffer = r"./buffer.mp3"
    file_for_mp3 = r".\buffer.mp3"
    output_file = r"./buffer.wav"

    prev_song = ""
    prev_artist = ""
    print(f"Start listen {station} on {live_url}\n")
    while True:
        sample = read_sample(live_url, file_for_buffer)
        if sample:
            #cnv_audio(file_for_buffer, file_for_mp3)
            #shazam_chars = await shazam_it(file_for_mp3)
            convert_to_wav(file_for_buffer, output_file)
            shazam_chars = await shazam_it(output_file)
            #tm.sleep(15)
            #print(len(shazam_chars["matches"]))
            if len(shazam_chars["matches"]) != 0:
                sample_song = shazam_chars['track']['title']
                sample_artist = shazam_chars['track']['subtitle']
                song = Song_Info(station, sample_song, sample_artist)
                if prev_song != sample_song:
                    add_it_to_db("RadioList.json", song)
                    print('Added ' + song.title, song.artist)
                    prev_song = sample_song     

def get_params() -> str:
    file_path = "C:/Users/papav/Documents/Python/Mus01/Data/StationList.csv"
    data = pd.read_csv(file_path, sep=",")
    n = len(sys.argv)
    if n != 2:
        sys.exit(f"Usage: pytohn {sys.argv[0]} n n:=0...max stations({len(data)-1} for the current available list)")
    StationNo = "0" if n == 1 else sys.argv[1]
    if not StationNo.isnumeric() or int(StationNo) > len(data)-1 or int(StationNo) < 0:
        sys.exit("Enter a station from 0 to "+str(len(data)-1))  
    surl = data.iloc[int(StationNo), 2].strip()
    snam = data.iloc[int(StationNo), 0].strip()
    return surl,snam
        

if __name__ == "__main__":
    #asyncio.run(start_listen())
    url_str, radio_station = get_params()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_listen(radio_station, url_str))
