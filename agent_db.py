import traceback
import schedule
import time

from youtube_podcast_downloader import getCollection,getDetailMovie

def lastAudioForAllUsers():
    db = getCollection()
    collection = db['User_Audio']
    pipeline = [
        {"$sort":{"created_at":-1}},
        {
            "$group":{
                "_id":"$user_id",
                "last_audio":{"$first":"$$ROOT"}
            }
        }
    ]
    return list(collection.aggregate(pipeline))

def lastMovie():
    db = getCollection()
    audios = list(db.Video.find().sort("created_at",-1).limit(5))
    return {a['_id']for a in audios}

def agentDecisionDownload():
    try:
        last_audio_users = lastAudioForAllUsers()
        last_audio_ids = lastMovie()
        for u in last_audio_users:
            last_user_heard = u['last_audio']['Video_id']
            print(last_user_heard)
            if last_user_heard in last_audio_ids:
                print("the system need to download")
                getDetailMovie()
                return
            print("the system no need to download")
            
    except Exception as e:
        print("Error in downloadAudio")
        print(e)
        traceback.print_exc()
        
# schedule.every(2).days.at("23:00").do(agentDecisionDownload)
# while True:
#     schedule.run_pending()
#     time.sleep(60)

