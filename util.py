from pydub import AudioSegment
from bs4 import BeautifulSoup
from markdown import markdown
import re


def add_pause(input_path, output_path, pause):
    input_mp3_file = input_path
    output_mp3_file = output_path

    original_file = AudioSegment.from_mp3(input_mp3_file)
    silenced_file = AudioSegment.silent(duration=pause)
    combined_file = original_file + silenced_file

    combined_file.export(output_mp3_file, format="mp3")

#Converts a markdown string to plaintext
def markdown_to_text(markdown_string):
    # md -> html -> text since BeautifulSoup can extract text cleanly
    html = markdown(markdown_string)
    # remove code snippets
    html = re.sub(r'<pre>(.*?)</pre>', ' ', html)
    html = re.sub(r'<code>(.*?)</code >', ' ', html)
    # extract text
    soup = BeautifulSoup(html, "html.parser")
    text = ''.join(soup.findAll(text=True))
    return text

