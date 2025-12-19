import os
import isodate

from dotenv import load_dotenv
from googleapiclient.discovery import  build
from pymongo import MongoClient

load_dotenv()
API_KEY = os.getenv("API_KEY")

def requestYoutube():
    youtube = build(
        "youtube",
        "v3",
        developerKey=API_KEY
    )
    return youtube

def convertDuration(ISO):
    if not ISO:
        return False,0
    parse_duration=str(isodate.parse_duration(ISO))
    parts = parse_duration.split(":")
    minutes = int(parts[1])
    return minutes<=10 and minutes>=5,minutes

def CollectionMovie():
    client = MongoClient("mongodb://localhost:27017")
    db = client['speech_shadowing']
    return db['Video']
    
def getDetailMovie():
    youtube = requestYoutube()           
    next_page_token = None
    saved_count = 0
    collection = CollectionMovie()
    
    while saved_count <= 10:
        request = youtube.video().list(
            q='english podcast',
            part='snippet',
            type='video',
            maxResults=10,
            pageToken = next_page_token)
        response = request.execute()
        # print(response)
        for i in response['items']:
            video_id = i['id']['videoId']
            video_title = i['snippet']['title']
            detail_req = youtube.videos().list(
                part='contentDetails',      
                id=video_id
            )
            detail_res  = detail_req.execute()
            for i in detail_res['items']:
                ISO_Duration=i['contentDetails']['duration']
                time_accept,minutes=convertDuration(ISO_Duration)
                print(time_accept)
                if time_accept:
                    if collection.find_one({"video_id":video_id}):
                        continue
                    collection.insert_one({
                        "video_id":video_id,
                        "video_title":video_title,
                        "duration":minutes
                    })
                    saved_count+=1
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break        
getDetailMovie()



    
        












