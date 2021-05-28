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

def add_noise(target_dir, noise_dir, output_dir, signature_text="", sampling_rate=16000, process_ratio=0.3, original_volume=1.0, noise_volume=1.0):
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

    ''' Process for selected input files '''
    wav_path_list = glob.glob(target_dir + "/*.wav")
    random.shuffle(wav_path_list)
    wav_path_list = wav_path_list[:int(len(wav_path_list) * process_ratio)]
    for wav_path in wav_path_list:
        basename, ext = os.path.splitext(os.path.basename(wav_path))
        output_path = output_dir + "/" + basename + "_" + signature_text + ".wav"

        data, sr = librosa.core.load(wav_path, sr=sampling_rate, mono=True)
        duration_sample = len(data)

        noise = random.choice(noise_list)
        start_sample = int(random.uniform(0, len(noise) - duration_sample - 1))
        data = data * original_volume + noise[start_sample:start_sample + duration_sample] * noise_volume

        soundfile.write(output_path, data, samplerate=sampling_rate, subtype="PCM_16")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Download AudioSet")
    parser.add_argument("-t", "--target_dir", type=str, required=False, default="./talking")
    parser.add_argument("-n", "--noise_dir", type=str, required=False, default="./noise")
    parser.add_argument("-o", "--output_dir", type=str, required=False, default="./")
    parser.add_argument("-s", "--signature_text", type=str, required=False, default="")
    parser.add_argument("-r", "--sampling_rate", type=int, required=False, default="16000")
    parser.add_argument("-p", "--process_ratio", type=float, required=False, default="0.5")
    parser.add_argument("-u", "--original_volume", type=float, required=False, default="1.0")
    parser.add_argument("-v", "--noise_volume", type=float, required=False, default="1.0")

    args = parser.parse_args()
    target_dir = args.target_dir
    noise_dir = args.noise_dir
    output_dir = args.output_dir
    signature_text = args.signature_text
    sampling_rate = args.sampling_rate
    process_ratio = args.process_ratio
    original_volume = args.original_volume
    noise_volume = args.noise_volume

    os.makedirs(output_dir, exist_ok=True)

    add_noise(target_dir, noise_dir, output_dir, signature_text, sampling_rate, process_ratio, original_volume, noise_volume)

