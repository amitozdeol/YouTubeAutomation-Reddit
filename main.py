from pathlib import Path
from reddit import Reddit
from tiktok import TikTok
from tts import TTS
from util import markdown_to_text
from videomaker import VideoMaker
import config
import math
import subprocess
import sys
import time

# 1. Login to reddit and get the thread and comments
# 2. Create screenshot of reddit posts
# 3. Create mp3 files of the thread title and comments
# 4. Create the final video
def main():
    # tiktok = TikTok()
    # sys.exit(0)
    reddit = Reddit(sys.argv[1] if len(sys.argv)>1 else None)
    video = VideoMaker()
    video.get_hastags()
    reddit.get_screenshots()
    tts = TTS(reddit)
    title_audio_path = f'./Assets/temp/{reddit.thread.id}/mp3/title.mp3'
    tts.create_tts(reddit.thread.title, title_audio_path)

    audio_paths = [f'./Assets/temp/{reddit.thread.id}/mp3_clean/title.mp3']
    image_paths = [f'./Assets/temp/{reddit.thread.id}/png/title.png']
    for idx, comment in enumerate(reddit.comments):
        path = f"./Assets/temp/{reddit.thread.id}/mp3/{idx}.mp3"
        audio_added = tts.create_tts(comment.body, path)
        if audio_added:
            audio_paths.append(f'./Assets/temp/{reddit.thread.id}/mp3_clean/{idx}.mp3')
            image_paths.append(f'./Assets/temp/{reddit.thread.id}/png/{idx}.png')
        else:
            break

    # create final video
    video.make_final_video(audio_paths, image_paths, math.ceil(tts.video_duration), f'{reddit.thread.id} {markdown_to_text(reddit.thread.title)}')

    if my_config['App']['upload_to_youtube']:
        upload_file = f'./Results/{thread.id+thread_title}.mp4'
        directory_path = my_config['Directory']['path']
        cmd = ['python', f'{directory_path}/Youtube/upload.py', '--file', upload_file, '--title',
               f'{thread_title}', '--description', f'{thread_title}']
        subprocess.run(cmd)


if __name__ == '__main__':
    my_config = config.load_config()
    while True:
        print('Starting ..........\n')
        main()
        print('\n-------------------------------------------\n')
        time.sleep(my_config['App']['run_every'])