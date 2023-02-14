from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
from mutagen.mp3 import MP3
from pathlib import Path
from pydub import AudioSegment
from util import markdown_to_text
import config
import random
import sys

#Text to speech using AWS Polly
class TTS:
    reddit = None
    video_duration = 0

    def __init__(self, reddit):
        self.session = self.create_session()
        self.polly = self.session.client("polly")
        self.reddit = reddit
        # create a mp3 directory for the tts files
        Path(f"./Assets/temp/{reddit.thread.id}/mp3").mkdir(parents=True, exist_ok=True)
        Path(f"./Assets/temp/{reddit.thread.id}/mp3_clean").mkdir(parents=True, exist_ok=True)
        print("Getting mp3 files..")

    def create_session(self):
        my_config = config.load_config()
        return Session(aws_access_key_id=my_config['AmazonAWSCredential']['aws_access_key_id'],
                          aws_secret_access_key=my_config['AmazonAWSCredential']['aws_secret_access_key'],
                          region_name=my_config['AmazonAWSCredential']['region_name']
                          )

    '''
    Create audio using AWS Polly and save it to a /mp3 directory
    Then add a pause to the end of the file and save it to a new /mp3_clean directory
    '''
    def create_tts(self, text, path):
        my_config = config.load_config()
        text = markdown_to_text(text)
        try:
            voice_id = my_config['TextToSpeechSetup']['voice_id']
            if my_config['TextToSpeechSetup']['multiple_voices']:
                voices = ["Joanna", "Justin", "Kendra", "Matthew"]
                voice_id = random.choice(voices)

            response = self.polly.synthesize_speech(Text=text,
                                               OutputFormat="mp3",
                                               VoiceId=voice_id)
        except (BotoCoreError, ClientError) as error:
            print(error)
            sys.exit(-1)

        # Access the audio stream from the response
        if "AudioStream" in response:
                with closing(response["AudioStream"]) as stream:
                   try:
                        # Open a file for writing the output as a binary stream
                        with open(path, "wb") as file:
                           file.write(stream.read())

                        current_duration = self.get_length(path)
                        pause = my_config['VideoSetup']['pause']
                        max_duration = my_config['VideoSetup']['total_video_duration']
                        if self.video_duration + current_duration + pause <= max_duration:
                            self.video_duration += current_duration + pause
                            # add a pause to the end of the file
                            self.add_pause(path, path.replace("/mp3", "/mp3_clean"), pause)
                            return True
                        else:
                            print("Video duration exceeded")
                            return False
                   except IOError as error:
                      # Could not write to file, exit gracefully
                      print(error)
                      sys.exit(-1)
        else:
            # The response didn't contain audio data, exit gracefully
            print("Could not stream audio")
            sys.exit(-1)

    '''
    Get the length of the mp3 file
    '''
    def get_length(self, path):
        try:
            audio = MP3(path)
            length = audio.info.length
            return length
        except:
            return 0

    '''
    Add a pause to the end of the mp3 file
    '''
    def add_pause(self, input_path, output_path, pause):
        original_file = AudioSegment.from_mp3(input_path)
        silenced_file = AudioSegment.silent(duration=pause*1000)
        combined = original_file + silenced_file
        combined.export(output_path, format="mp3")
