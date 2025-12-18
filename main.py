import os
import isodate

from dotenv import load_dotenv
from googleapiclient.discovery import  build

load_dotenv()
API_KEY = os.getenv("API_KEY")

def requestYoutube():
    youtube = build(
        "youtube",
        "v3",
        developerKey=API_KEY
    )
    return youtube

def getListVideo():
    list_id = []
    youtube = requestYoutube()
    request = youtube.search().list(
        q='english padcast',
        part='snippet',
        type='video',
        maxResults=3
    )
    response = request.execute()
    for i in response['items']:
        video_id = i['id']['videoId']
        list_id.append(video_id)
    return list_id

    
def getDetailMovie():
    youtube = requestYoutube()           
    lists_of_video = getListVideo()     
    ids_string = ",".join(lists_of_video)
    request = youtube.videos().list(
       part='contentDetails',      
       id=ids_string
    )
    response = request.execute()
    print(response)
    
# get_detail_movie()

def convertDuration(ISO):
    if ISO:
        parse_duration=str(isodate.parse_duration(ISO))
        parts = parse_duration.split(":")
        minutes = int(parts[1])
        if minutes<=10:
            pass 
        












