import config
from reddit import Reddit
import math
import subprocess
import time
import sys

# 1. Login to reddit and get the thread and comments
# 2. Create screenshot of reddit posts
# 3. Create mp3 files of the thread title and comments
# 4. Create the final video
def main():
    my_config = config.load_config()
    reddit = Reddit(sys.argv[1] if len(sys.argv)>1 else None)

    # Create a temp folder to store screenshots and mp3
    # Path(f"./Assets/temp").mkdir(parents=True, exist_ok=True)
    # thread_id_path = f"./Assets/temp/{thread.id}"

    # get_screenshots_of_reddit_posts(reddit_thread=thread, reddit_comments=comments)

if __name__ == '__main__':
    my_config = config.load_config()
    while True:
        print('Starting ..........\n')
        main()
        print('\n-------------------------------------------\n')
        time.sleep(my_config['App']['run_every'])


