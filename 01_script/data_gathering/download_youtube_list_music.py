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

list_video = ["https://www.youtube.com/watch?v=Dc2NeSH81qU", "https://www.youtube.com/watch?v=MYrEkuwy2qg", "https://www.youtube.com/watch?v=NPl4C6NQzRs", "https://www.youtube.com/watch?v=-5fXNxKWrAY", "https://www.youtube.com/watch?v=vqIzXrXo-6c", "https://www.youtube.com/watch?v=_8ksOgWYleA"]
# list_video = ["https://www.youtube.com/watch?v=-Lx6-QgTRpw", "https://www.youtube.com/watch?v=EJy0zywRFkc"]

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
    parser.add_argument("-o", "--output_dir", help="output directory", type=str, required=False, default="./yoshimoto")
    args = parser.parse_args()
    output_dir = args.output_dir
    print(f"output_dir = {output_dir}")
    os.makedirs(output_dir, exist_ok=True)

    total_num = len(list_video)
    success_cnt = 0
    fail_cnt = 0

    for url in list_video:
        print("Progress: " + str(success_cnt + fail_cnt) + " / " + str(total_num) + ". Success cnt: " + str(success_cnt) + ". Fail cnt: " + str(fail_cnt))
        # print(url)
        video_filename = download_from_youtube(url)
        youtube_id = url[32:]
        if video_filename == "":
            fail_cnt += 1
        else:
            success_cnt += 1
            base, ext = os.path.splitext(os.path.basename(video_filename))
            video_filename = shutil.move(video_filename, str(youtube_id) + ext)
            convert_to_wav(video_filename, output_dir)
            # os.remove(video_filename)

        time.sleep(10)


