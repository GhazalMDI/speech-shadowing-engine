import os
import isodate
import yt_dlp
import random
import time

from dotenv import load_dotenv
from googleapiclient.discovery import  build
from pymongo import MongoClient
load_dotenv()
API_KEY = os.getenv("API_KEY")
MONGO_IP = os.getenv("MONGO_IP")

def requestYoutube():
    youtube = build(
        "youtube",
        "v3",
        developerKey=API_KEY
    )
    return youtube
def downloadAudio(video_id):
    url = f'https://www.youtube.com/watch?v={video_id}'
    output_path = f'audio/{video_id}.mp3'
    ydl_opts = {
        'format':'bestaudio/best',
        'outtmpl':f'audio/{video_id}.%(ext)s',
        'postprocessors':[{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet':True,
        'sleep_interval': 5,
        'max_sleep_interval': 10,
        'noplaylist': True,     
        'cookies': 'cookies.txt'
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                url,
                download=True
            )
            time.sleep(random.randint(4, 7))
            ydl.prepare_filename(info)
        return output_path
    except Exception as e:
        print(e)
        return None
        
def convertDuration(ISO):
    if not ISO:
        return False,0
    parse_duration=str(isodate.parse_duration(ISO))
    parts = parse_duration.split(":")
    minutes = int(parts[1])
    return minutes<=30 and minutes>=5,minutes

def CollectionMovie():
    client = MongoClient(MONGO_IP)
    db = client['speech_shadowing']
    return db['Video']
    
def getDetailMovie(limit):
    youtube = requestYoutube()           
    collection = CollectionMovie()
    saved_count = 0
    
    search_res  = youtube.search().list(
        q='english padcast',
        part='snippet',
        type='video',
        maxResults=70).execute()
    
    video_map = {}
    for i in search_res['items']:
        video_id = i['id']['videoId']
        video_title = i['snippet']['title']
        
        if not collection.find_one({"video_id":video_id}):
            video_map[video_id]=video_title
    if not video_map:
        print("new video")
        return
    
    detail_req = youtube.videos().list(
        part='contentDetails',      
        id=",".join(video_map.keys())
    ).execute()

    for i in detail_req['items']:
        
        video_id = i['id'] 
        video_title = video_map[video_id]  
        
        ISO_Duration=i['contentDetails']['duration']
        time_accept,minutes=convertDuration(ISO_Duration)
        
        if time_accept:
            if collection.find_one({"video_id":video_id}):
                continue
            audio_path=downloadAudio(video_id)
            if not audio_path:
                continue
            collection.insert_one({
                "video_id":video_id,
                "video_title":video_title,
                "duration":minutes,
                "sound":audio_path
            })
            saved_count+=1
            print(saved_count)
            time.sleep(random.randint(2, 5))
            if saved_count >= limit:
                break
    
getDetailMovie(limit=10)



    
        












