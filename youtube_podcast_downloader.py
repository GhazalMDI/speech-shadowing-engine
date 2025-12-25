import os
import isodate
import random
import time
import subprocess


from dotenv import load_dotenv
from googleapiclient.discovery import  build
from pymongo import MongoClient



load_dotenv()
API_KEY = os.getenv("API_KEY")
MONGO_IP = os.getenv("MONGO_IP")
SPEECH_TEXT_KEY = os.getenv("SPEECH_TEXT_API")
WHISPER_EXE = os.getenv("WHISPER_EXE")
MODEL_PATH = os.getenv("MODEL_PATH")
FULL_PATH_AUDIO = r"D:\Machine learning\speech-shadowing-engine"
def requestYoutube():
    youtube = build(
        "youtube",
        "v3",
        developerKey=API_KEY
    )
    return youtube
def downloadAudio(video_id):
    import yt_dlp
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

def getCollection():
    client = MongoClient(MONGO_IP)
    db = client['speech_shadowing']
    return db
    
def getDetailMovie(limit):
    db = getCollection()
    youtube = requestYoutube()           
    Audio = db['Audio']
    saved_count = 0
    
    search_res  = youtube.search().list(
        q='english padcast',
        part='snippet',
        type='video',
        maxResults=limit).execute()
    
    video_map = {}
    for i in search_res['items']:
        video_id = i['id']['videoId']
        video_title = i['snippet']['title']
        
        if not Audio.find_one({"video_id":video_id}):
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
            if Audio.find_one({"video_id":video_id}):
                continue
            audio_path=downloadAudio(video_id)
            if not audio_path:
                continue
            Audio.insert_one({
                "video_id":video_id,
                "video_title":video_title,
                "duration":minutes,
                "sound":audio_path,
                "created_at": time.time()
            })
            saved_count+=1
            print(saved_count)
            time.sleep(random.randint(2, 5))
            if saved_count >= limit:
                break
# getDetailMovie(limit=10)


def createTrnscript(audio_path):
    db = getCollection()
    audios = db['Audio']
    audio=audios.find_one({
        "sound":audio_path
    })
    if not audio or "mp3" not in audio["sound"]:
        return False
    
    audio_file = audio['sound']
    audio_path = os.path.join(FULL_PATH_AUDIO, audio_file.replace("/", os.sep))

    print(audio_path)
    print(WHISPER_EXE)
    print(MODEL_PATH)
    
    command = [
        WHISPER_EXE,
        "-m",MODEL_PATH,
        "-f",audio_path,
        "-l","en"
    ]
    
    
    print("start process")
    
    
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    for line in process.stdout:
        print(line, end="") 

    process.wait()
    print("Process finished")
    # result = subprocess.run(
    #     command,capture_output=True,text=True
    # )
    # print("start transcript")
    # transcript=result.stdout

    

    audios.update_one({
        {"_id":audio['_id']},
        {
            "$set":{
                "transcript":process.stdout
            }
        }
    })
    
    
createTrnscript("audio/vqzqXBSdkYY.mp3")
    



    
        












