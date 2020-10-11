from __future__ import unicode_literals
import soundcloud
import os
from youtubesearchpython import SearchVideos
import json
import pprint
import subprocess
from moviepy.editor import *


#-----------------EDIT-THIS---------------------------
user_id = "YOUR_USER_ID"
tracks_folder = "PATH_TO_FOLDER_FOR_DOWNLOADED_TRACKS"
#-----------------------------------------------------

stolen_client_id = "a3dd183a357fcff9a6943c0d65664087"
client = soundcloud.Client(client_id=stolen_client_id)

tracks = client.get(f'/users/{user_id}/favorites', limit = 50)

urls = []



downloaded = os.listdir(tracks_folder)
#remove counts from downloaded tracks
for i in range(len(downloaded)):
    a = downloaded[i]
    if len(downloaded[i].replace("]","[").split("[")) == 3:
        b = downloaded[i].replace("]","[").replace(" ","").replace("&", "and").split("[")[2]
        try: 
            os.rename(f"{tracks_folder}\{a}",f"{tracks_folder}\{b}")
        except:
            pass
downloaded = os.listdir(tracks_folder)


for track in tracks:
    author = track.user["username"]
    title = track.title
    i = tracks.index(track)+1
    name = ""
    #making full name
    if author in title:
        name = f"{title}"
    else:
        name = f"{author} - {title}"
    search_name = name.replace(" ", "_").replace("&","and")
    #check if it's already downloaded
    print("_"*100)
    if f"{search_name}.mp3" not in downloaded:
        #search on youtube to get a link
        search = SearchVideos(name, offset = 1, mode = "json", max_results = 20)
        results = json.loads(search.result())
        
        if len(results["search_result"])>0:
            link = results["search_result"][0]["link"]
            print(f"{i}. {name} - {link}")
            urls.append(link)

            
            try:
                #get worse video quality xd
                print("  Finding the worst video quality (for quick download)...")
                quality_data = os.popen(f"you-get -i {link}").read()
                num_of_types = round((len(quality_data.splitlines())-12)/6)
                best = None
                for i in range(num_of_types):
                    lines = quality_data.splitlines()
                    if lines[4+i*6+1].replace(" ","") == "container:mp4":
                        best = lines[4+i*6]
                best = best.replace(" ","")[6:]
                print(f"  Found! (--itag={best})")
                #download video
                search_name = search_name.replace("&","and")
                print(f"Downloading: you-get --no-caption --itag={best} -O {tracks_folder}\{search_name} {link}")
                os.system(f"you-get --no-caption --itag={best} -O {tracks_folder}\{search_name} {link}")
                print(f"{name} downloaded!")
            except:
                print("  Couldn't find worse quality, downloading with default settings")
                os.system(f"you-get --no-caption -O {tracks_folder}\{search_name} {link}")
                print(f"{name} downloaded!")
            #convert to mp3
            files = os.listdir(tracks_folder)
            #if not merged
            mp4_file = tracks_folder+'\\'+search_name+"[01].mp4" #[01] = audio
            mp3_file = tracks_folder+'\\['+str(i).zfill(3)+'] '+search_name+".mp3"
            #if merged 
            merged = False
            if search_name+".mp4" in files:
                mp4_file = tracks_folder+'\\'+search_name+".mp4"   
                merged = True
                videoclip = VideoFileClip(mp4_file)
                audioclip = videoclip.audio 
            else: #not merged; only audio
                videoclip = AudioFileClip(mp4_file)
                audioclip = videoclip
            print("Video merged" if merged else "Videos not merged")
            #conversion
            print(f"converting {name} to .mp3")
            videoclip = AudioFileClip(mp4_file)#VideoFileClip(mp4_file)
            audioclip = videoclip#.audio
            audioclip.write_audiofile(mp3_file)
            audioclip.close()
            videoclip.close()
            print(f"{name} succesfully converted!")
            if merged:
                os.system(f"del {tracks_folder}\{search_name}.mp4")
                print("  .mp4 file deleted")
            else:
                os.system(f"del {tracks_folder}\{search_name}[01].mp4")
                os.system(f"del {tracks_folder}\{search_name}[00].mp4")
                print("  Both .mp4 files deleted")

            #print(f"{name}.mp4 deleted")

        else:
            print(f"{i}. ERROR - Video not found ({name})")

    else:
        new_name = f"{tracks_folder}\[{str(i).zfill(3)}] {search_name}.mp3"
        print(f"{i}. Already downloaded ({name}), renaming {tracks_folder}\{search_name}.mp3 to {new_name}...")
        

        try:
            os.rename(f"{tracks_folder}\{search_name}.mp3",new_name)
            print("Renaming succesfull!")
        except: 
            try:
                new_search_name = search_name.replace("and","&")
                os.rename(f"{tracks_folder}\{new_search_name}.mp3",new_name)
            except:
                pass

print("_"*100)

#delete all .mp4 files from folder
print("Deleting all .mp4 files in folder")
os.system(f"del {tracks_folder}\*.mp4 --user")
print("All .mp4 files deleted!")
   
