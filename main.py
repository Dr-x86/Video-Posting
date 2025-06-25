import requests
import random
import os
from yt_dlp import YoutubeDL
from supabase import create_client, Client
from dotenv import load_dotenv
import notify
import praw

load_dotenv()
SUPA_BASE_KEY = os.getenv("SUPABASE_KEY")
DATABASE = os.getenv("SUPABASE_DB")
ACCESS_BOT_TOKEN = os.getenv("FB_ACCESS_TOKEN")
page_id = '595985150275800'

print(f"\n{SUPA_BASE_KEY}\n{DATABASE}\n{ACCESS_BOT_TOKEN}")

## CLIENT FOR DB
supabase: Client = create_client(DATABASE, SUPA_BASE_KEY)

def agregar(url):
    insert_response = supabase.table('set_videos').insert({'url': url}).execute()
    return True if insert_response.data else False

def verify(urls: list):
    used = supabase.table('set_videos').select('url').in_('url', urls).execute()
    usados = set([v['url'] for v in used.data])
    return usados

def buscarVideo():
    try:
        reddit = praw.Reddit(
            client_id=os.environ["REDDIT_CLIENT_ID"],
            client_secret=os.environ["REDDIT_CLIENT_SECRET"],
            username=os.environ["REDDIT_USERNAME"],
            password=os.environ["REDDIT_PASSWORD"],
            user_agent="RedditVideoBot/1.0 by u/{}".format(os.environ["REDDIT_USERNAME"])
        )

        subreddits = ["bluearchive", "zenlesszonezero", "perfectlycutscreams", "hatsunemiku", "kasaneteto", "frieren"]
        for sub in subreddits:
            for post in reddit.subreddit(sub).new(limit=30):
                if post.is_video and not post.stickied:
                    print(f"🎥 Post encontrado: {post.title}")
                    return post.title, post.url
        print("❌ No se encontraron videos.")
        return None, None

    except Exception as e:
        notify.Me(f"[REDDIT] - Error con PRAW: {e}")
        return None, None


def descargarVideo(url):
    ydl_opts = {
        'outtmpl': 'Test.mp4',
        'merge_output_format': 'mp4',
        'quiet': False
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def subirPost(caption, urlVideo):
    url = f'https://graph.facebook.com/{page_id}/videos'
    
    try:
        with open(urlVideo, 'rb') as video_file:
            files = {
                'source': video_file
            }
            data = {
                'description': caption,
                'access_token': ACCESS_BOT_TOKEN
            }   
            response = requests.post(url, data=data, files=files)
    except Exception as e:
        notify.Me(f"[VIDEOS] - Error en post Detalles {e}")
    return response

if __name__=="__main__":
    print("\n >>> Inicio del script \n")
    
    title,url = buscarVideo()
    
    if(title == None and url ==  None):
        notify.Me(f"[VIDEOS] - ERROR Parametros None en url y title")
        exit()
    
    descargarVideo(url)
    response = subirPost(title,"Test.mp4")
    
    if(response.status_code == 200):
        agregar(url)
        notify.Me(f"[VIDEO] - Post de video correcto!! lets gooo https://facebook.com/{page_id}/videos/{response.json()['id']}")
    else:
        notify.Me(f"Error de codigo: {response.status_code}")
    
    os.remove("Test.mp4")
    
    print("\n >>> Fin del script \n")
