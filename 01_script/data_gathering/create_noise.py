#-- coding: utf-8 --

import os
import glob
import shutil
import time
import argparse
import random
import librosa
import soundfile

def clear_last_sep(dir):
    dir.replace(os.sep,'/')
    if dir[-1] == "/":
        dir = dir[:-1]
    return dir

def create_noise(noise_dir, output_dir, signature_text="", sampling_rate=16000, duration_time=10, output_number_of_file=10, noise_volume=1.0):
    if signature_text == "":
        signature_text = os.path.splitext(os.path.basename(clear_last_sep(noise_dir)))[0]

    ''' Make sure the shuffling is deterministic for reproduce '''
    random.seed(1234)

    ''' Read noise data as array '''
    noise_list = []
    noise_wav_path_list = glob.glob(noise_dir + "/*.wav")
    for noise_wav_path in noise_wav_path_list:
        data, sr = librosa.core.load(noise_wav_path, sr=sampling_rate, mono=True)
        noise_list.append(data)

    duration_sample = duration_time * sampling_rate 
    ''' Process to create files'''
    for i in range(output_number_of_file):
        noise = random.choice(noise_list)
        start_sample = int(random.uniform(0, len(noise) - duration_sample - 1))
        data = noise[start_sample:start_sample + duration_sample] * noise_volume
        output_path = output_dir + "/" + signature_text + f"_{i:05}.wav"
        soundfile.write(output_path, data, samplerate=sampling_rate, subtype="PCM_16")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Download AudioSet")
    parser.add_argument("-n", "--noise_dir", type=str, required=False, default="./noise")
    parser.add_argument("-o", "--output_dir", type=str, required=False, default="./")
    parser.add_argument("-s", "--signature_text", type=str, required=False, default="")
    parser.add_argument("-r", "--sampling_rate", type=int, required=False, default="16000")
    parser.add_argument("-d", "--duration_time", type=int, required=False, default="10")
    parser.add_argument("-m", "--output_number_of_file", type=int, required=False, default="10")
    parser.add_argument("-v", "--noise_volume", type=float, required=False, default="1.0")

    args = parser.parse_args()
    noise_dir = args.noise_dir
    output_dir = args.output_dir
    signature_text = args.signature_text
    sampling_rate = args.sampling_rate
    duration_time = args.duration_time
    output_number_of_file = args.output_number_of_file
    noise_volume = args.noise_volume

    os.makedirs(output_dir, exist_ok=True)

    create_noise(noise_dir, output_dir, signature_text, sampling_rate, duration_time, output_number_of_file, noise_volume)

