import requests
import random
import os
from yt_dlp import YoutubeDL
from supabase import create_client, Client
from dotenv import load_dotenv
import notify

load_dotenv()
SUPA_BASE_KEY = os.getenv("SUPA_BASE_KEY")
DATABASE = os.getenv("SUPABASE_DB")
ACCESS_BOT_TOKEN = os.getenv("FB_ACCESS_TOKEN")
page_id = '595985150275800'

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
    sourceVideos = ["perfectlycutscreams", "hatsunemiku", "kasaneteto", "frieren"]
    random.shuffle(sourceVideos)  # Aleatoriza el orden

    headers = {"User-agent": "Mozilla/5.0"}

    for subreddit in sourceVideos:
        url = f"https://www.reddit.com/r/{subreddit}/new/.json?limit=100"
        try:
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            posts = res.json()["data"]["children"]
            videos = [p['data'] for p in posts if p['data'].get('is_video')]
            print("Videos encontrados: ",len(videos))
            
            urls = ["https://reddit.com" + v['permalink'] for v in videos]
            usados = verify(urls)
            
            nuevos_videos = [v for v in videos if "https://reddit.com" + v['permalink'] not in usados]
            print("Nuevos videos: ", len(nuevos_videos))
            
            if nuevos_videos:
                selected = random.choice(nuevos_videos)
                video_url = "https://reddit.com" + selected['permalink']
                title = selected['title']
                print(f"\n🎥 NUEVO VIDEO ENCONTRADO EN /r/{subreddit}")
                print(f"Título: {title}\nURL: {video_url}\n")
                return title, video_url

        except requests.exceptions.RequestException as req_err:
            notify.Me(f"[VIDEOS] - Error de red o HTTP: {req_err}")
        except ValueError:
            notify.Me("[VIDEOS] - Error al decodificar JSON.")
        except Exception as e:
            notify.Me(f"[VIDEOS] - Error inesperado: {e}")

    print("❌ No se encontraron videos nuevos en los subreddits.")
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