from youtube_podcast_downloader import getDetailMovie,CollectionMovie

def need_new_audio(Collection):
    heard_content = Collection.count_documents({"heard":True})
    return heard_content % 4 == 0 and heard_content !=0

def podcast_agent():
    Collection = CollectionMovie()
    if not need_new_audio(Collection):
        print("no need to new podcast")
        return
    getDetailMovie(limit=5)
    
podcast_agent()