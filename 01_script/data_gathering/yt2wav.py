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

# ffmpeg_path = "C:/iwatake/tool/ffmpeg-20170827-ef0c6d9-win64-static/bin/ffmpeg.exe"
ffmpeg_path = "ffmpeg"

talking_id_list = [
    # "/m/0dgw9r",
    # "/m/09l8g",
    # "/m/09x0r",
    "/m/05zppz",
    "/m/02zsn",
    "/m/0ytgt",
    "/m/01h8n0",
    # "/m/02qldy",
    # "/m/0261r1",
    # "/m/0brhx",
    # "/m/07p6fty",
    # "/m/07q4ntr",
    # "/m/07rwj3x",
    # "/m/07sr1lc",
    # "/m/04gy_2",
    # "/t/dd00135",
    # "/m/03qc9zr",
    # "/m/02rtxlg",
    # "/m/01j3sz",
    # "/t/dd00001",
    # "/m/07r660_",
    # "/m/07s04w4",
    # "/m/07sq110",
    # "/m/07rgt08",
    # "/m/0463cq4",
    # "/t/dd00002",
    # "/m/07qz6j3",
    # "/m/07qw_06",
    # "/m/07plz5l",
    # "/m/015lz1",
    # "/m/0l14jd",
    # "/m/01swy6",
    # "/m/02bk07",
    # "/m/01c194",
    # "/t/dd00003",
    # "/t/dd00004",
    # "/t/dd00005",
    # "/t/dd00006",
    # "/m/06bxc",
    # "/m/02fxyj",
    # "/m/07s2xch",
    # "/m/07r4k75",
    # "/m/01j423",
]

human_any_sound_id_list = [
    "/m/0dgw9r",
    "/m/09l8g",
    "/m/09x0r",
    "/m/05zppz",
    "/m/02zsn",
    "/m/0ytgt",
    "/m/01h8n0",
    "/m/02qldy",
    "/m/0261r1",
    "/m/0brhx",
    "/m/07p6fty",
    "/m/07q4ntr",
    "/m/07rwj3x",
    "/m/07sr1lc",
    "/m/04gy_2",
    "/t/dd00135",
    "/m/03qc9zr",
    "/m/02rtxlg",
    "/m/01j3sz",
    "/t/dd00001",
    "/m/07r660_",
    "/m/07s04w4",
    "/m/07sq110",
    "/m/07rgt08",
    "/m/0463cq4",
    "/t/dd00002",
    "/m/07qz6j3",
    "/m/07qw_06",
    "/m/07plz5l",
    "/m/015lz1",
    "/m/0l14jd",
    "/m/01swy6",
    "/m/02bk07",
    "/m/01c194",
    "/t/dd00003",
    "/t/dd00004",
    "/t/dd00005",
    "/t/dd00006",
    "/m/06bxc",
    "/m/02fxyj",
    "/m/07s2xch",
    "/m/07r4k75",
    "/m/01j423",
    "/m/01w250",
    "/m/079vc8",
    "/m/09hlz4",
    "/m/0lyf6",
    "/m/07mzm6",
    "/m/01d3sd",
    "/m/07s0dtb",
    "/m/07pyy8b",
    "/m/07q0yl5",
    "/m/01b_21",
    "/m/0dl9sf8",
    "/m/01hsr_",
    "/m/07ppn3j",
]

def export_details(str):
    data = str.split(",")
    youtube_id = data[0].strip()
    start_seconds = int(float(data[1].strip()))
    end_seconds = int(float(data[2].strip()))
    positive_labels = data[3:]
    positive_labels = list(map(lambda x: x.strip().strip('"'), positive_labels))
    # print(youtube_id, start_seconds, end_seconds, positive_labels)
    return youtube_id, start_seconds, end_seconds, positive_labels

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
    ffmpeg_cmd = f'{ffmpeg_path} -y -loglevel quiet -i "{video_filename}" -ss {start_seconds} -t {duration} -ac 1 -ar 16000 -acodec pcm_s16le "{output_dir}/{base}.wav"'
    ffmpeg_cmd = ffmpeg_cmd.replace(os.sep, "/")
    # print(f"{ffmpeg_cmd}") 
    os.system(f"{ffmpeg_cmd}") 


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Download AudioSet")
    # parser.add_argument("list_filename", help="Segment list filename", type=str)
    parser.add_argument("-i", "--input", help="list filename", type=str, required=False, default="./balanced_train_segments.csv")
    parser.add_argument("-o", "--output_dir", help="output directory", type=str, required=False, default="./balanced_train_segments")
    parser.add_argument("-s", "--start_num", help="start num", type=int, required=False, default=0)
    args = parser.parse_args()
    list_filename = args.input
    output_dir = args.output_dir
    start_num = args.start_num
    print(f"list_filename = {list_filename}, output_dir = {output_dir}, start_num = {start_num}")
    dir_talking = f"{output_dir}/talking"
    dir_not_talking = f"{output_dir}/not_talking"
    dir_ambiguous = f"{output_dir}/ambiguous"
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(dir_talking, exist_ok=True)
    os.makedirs(dir_not_talking, exist_ok=True)
    os.makedirs(dir_ambiguous, exist_ok=True)

    total_file_num = len(open(list_filename).readlines())
    success_cnt = 0
    fail_cnt = 0
    skip_cnt = 0
    read_file_cnt = start_num
    with open(list_filename) as f:
        for header_line in range(3 + start_num):
            line = f.readline()

        for line in f.readlines():
            print("Progress: " + str(read_file_cnt) + " / " + str(total_file_num) + ". Success cnt: " + str(success_cnt) + ". Fail cnt: " + str(fail_cnt) + ". Skip cnt: " + str(skip_cnt))
            read_file_cnt = read_file_cnt + 1

            youtube_id, start_seconds, end_seconds, positive_labels = export_details(line)
            duration = end_seconds - start_seconds
            is_talking = False
            is_human_any_sound = False
            for label in positive_labels:
                if label in talking_id_list:
                    is_talking = True
                if label in human_any_sound_id_list:
                    is_human_any_sound = True

            url = f"https://www.youtube.com/watch?start={start_seconds}&end={end_seconds}&v={youtube_id}&feature=youtu.be"
            # print(url)
            video_filename = download_from_youtube(url)
            if video_filename == "":
                fail_cnt = fail_cnt + 1
            else:
                base, ext = os.path.splitext(os.path.basename(video_filename))
                video_filename = shutil.move(video_filename, str(youtube_id) + ext)
                success_cnt = success_cnt + 1
                dir_to_save = dir_talking if is_talking else dir_not_talking
                dir_to_save = dir_ambiguous if (is_talking == False) and (is_human_any_sound == True) else dir_to_save

                convert_to_wav(video_filename, dir_to_save)
                os.remove(video_filename)

            time.sleep(10)


