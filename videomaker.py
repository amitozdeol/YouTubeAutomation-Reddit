import multiprocessing
from os import listdir
from moviepy.audio.AudioClip import concatenate_audioclips, CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.video.fx.resize import resize
from moviepy.video.fx.crop import crop
import random
import time

import requests
import config

def prepare_background(length,W, H):
    my_config = config.load_config()

    background_path = my_config['Background']['path']
    files = [f for f in listdir(background_path) if f.endswith('.mp4')]
    video = VideoFileClip(f'{background_path}{files[random.randint(0, len(files)-1)]}').without_audio()
    vide_duration = video.duration

    random_start = random.randint(0, int(vide_duration))
    vid = video.subclip(random_start, random_start+length)
    video.close()

    vid_resized = resize(vid, height=H)
    clip = (vid_resized)
    # calculate the center of the background clip
    c = clip.w // 2

    # calculate the coordinates where to crop
    half_w = W // 2
    x1 = c - half_w
    x2 = c + half_w

    return crop(clip, x1=x1, y1=0, x2=x2, y2=H)

# Get all the trending hashtags
def get_hastags():
    print("Getting Hastags 📈")
    response = requests.get("https://ads.tiktok.com/creative_radar_api/v1/popular_trend/hashtag/list?period=30&page=1&limit=30&sort_by=popular", 
                    headers={"anonymous-user-id": "48ef160890fb48ddae1b53f1b662ccaa"})
    hashtags = []
    try:
        if response.status_code == 200:
            json = response.json()   
            for item in json['data']['list']:
                hashtags.append(item['hashtag_name'])
    except:
        print("Failed to get hashtags")
    
    return hashtags

def make_final_video(audio_paths,image_paths,length: int,filename):
    # settings values
    W = 1080
    H = 1920
    opacity = 0.95

    print("Creating the final video 🎥")
    background_clip = prepare_background(length,W,H)

    # Gather all audio clips
    audio_clips = [AudioFileClip(i)for i in audio_paths]
    audio_concat = concatenate_audioclips(audio_clips)
    audio_composite = CompositeAudioClip([audio_concat])
    print(f"Video Will Be: {length} Seconds Long")

    # add title to video
    image_clips = []
    # Gather all images
    new_opacity = 1 if opacity is None or float(opacity) >= 1 else float(opacity)

    screenshot_width = int((W * 90) // 100)

    for idx, i in enumerate(image_paths):
        comment = ImageClip(i).set_duration(audio_clips[idx].duration).set_opacity(new_opacity).set_position("center")
        resized_comment = resize(comment, width=screenshot_width)
        image_clips.append(
            resized_comment
        )

    image_concat = concatenate_videoclips(image_clips,)  # note transition kwarg for delay in imgs
    image_concat.audio = audio_composite
    audio_composite.close()
    final = CompositeVideoClip([background_clip, image_concat.set_position("center")])
    image_concat.close()

    hashtags = get_hastags()
    filename+=f' #fyp'
    #loop through hashtags and add them to the video
    for idx, hashtag in enumerate(hashtags):
        isSure = input(f'{hashtag} (y/n): ').lower().strip() == 'y'
        if isSure:
            filename+=f' #{hashtag}'

    final.write_videofile(
        f"./Results/{filename}.mp4",
        fps=int(24),
        audio_codec="aac",
        audio_bitrate="192k",
        threads=multiprocessing.cpu_count(),
        #preset="ultrafast", # for testing purposes
    )
    final.close()

    print("See result in the results folder!")
