#-- coding: utf-8 --

'''
apt install ffmpeg
pip install pytube
'''

import os
import shutil
import time
import argparse
from pytube import YouTube

ffmpeg_path = "C:/iwatake/tool/ffmpeg-20170827-ef0c6d9-win64-static/bin/ffmpeg.exe"
# ffmpeg_path = "ffmpeg"

def download_from_youtube(url):
    while True:
        try:
            print("[download_from_youtube] " + url)
            yt = YouTube(url)
            yt.check_availability()
            break
        except Exception as e:
            print("YouTube Error: " + str(e))
            if "Too Many Requests" in str(e):
                print("retry")
                time.sleep(300)
                continue
            return ""

    try:
        filename = yt.streams.filter(only_audio=True,subtype='mp4').order_by('abr').last().download()
        return filename
    except Exception as e:
        print(e)
        return ""

def convert_to_wav(video_filename, output_dir):
    base, ext = os.path.splitext(os.path.basename(video_filename))
    ffmpeg_cmd = f'{ffmpeg_path} -y -loglevel quiet -i "{video_filename}" -ac 1 -ar 16000 -acodec pcm_s16le -f segment -segment_time 10 "{output_dir}/{base}_%04d.wav"'
    ffmpeg_cmd = ffmpeg_cmd.replace(os.sep, "/")
    # print(f"{ffmpeg_cmd}")
    os.system(f"{ffmpeg_cmd}") 

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Download AudioSet")
    parser.add_argument("-o", "--output_dir", help="output directory", type=str, required=False, default="./youtube")
    parser.add_argument("-u", "--url", help="url", type=str, required=False, default="https://www.youtube.com/watch?v=sulOYazBsvg")
    args = parser.parse_args()
    output_dir = args.output_dir
    url = args.url
    print(f"output_dir = {output_dir}, url = {url}")
    os.makedirs(output_dir, exist_ok=True)


    # print(url)
    video_filename = download_from_youtube(url)
    youtube_id = url[32:]
    if video_filename == "":
        pass
    else:
        base, ext = os.path.splitext(os.path.basename(video_filename))
        video_filename = shutil.move(video_filename, str(youtube_id) + ext)
        convert_to_wav(video_filename, output_dir)
        # os.remove(video_filename)



