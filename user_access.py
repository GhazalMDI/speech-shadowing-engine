from youtube_podcast_downloader import getCollection
from bson import ObjectId


# وقتی فراخوانی شود که کاربر یک اپیزود را کامل گوش کرده است
def addCounterHeard(user_id):
    try:
        if not ObjectId.is_valid(user_id):
            return False
        db = getCollection()
        Collection_user = db['User']
        Collection_user.update_one(
            {"_id":ObjectId(user_id)},
            {"$inc":{"heared_count":1}}
        )
        return True   
    except Exception as e:
        print(e)
        
def openNewEpisode(user_id,heared_count):
    try:
        if heared_count%5!=0:
            return []
        db = getCollection()
        user_audio = db['User_Audio']
        audios = db["Audio"]
        
        last_listened = user_audio.find(
            {"user_id":ObjectId(user_id)}
        ).sort("created_at",-1).limit(1)
        
        last_audio_id = None
        if last_listened:
            last_audio_id = last_listened[0]["Video_id"]
        if last_audio_id:
            next_episodes = list(audios.find({"_id":{"$gt":last_audio_id}}).sort("_id",1).limit(5))
        else:
            next_episodes = list(audios.find().sort("_id", 1).limit(5))
        
        return next_episodes
    except Exception as e:
        print(e)
        
        
        
# lasts=openNewEpisode("694798a2735dc79e8700acbe",1)
# print(lasts)    
    
        
                