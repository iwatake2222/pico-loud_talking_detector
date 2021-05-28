#-- coding: utf-8 --

import os
import glob
import shutil
import time
import argparse
import random
import librosa
import soundfile

def separate_wav(target_dir, output_dir, sampling_rate=16000, output_duration_time=5,delete_original=False):
    output_duration_sample = int(sampling_rate * output_duration_time)

    ''' Process for selected input files '''
    wav_path_list = glob.glob(target_dir + "/*.wav")
    for wav_path in wav_path_list:
        basename, ext = os.path.splitext(os.path.basename(wav_path))

        try:
            data, sr = librosa.core.load(wav_path, sr=sampling_rate, mono=True)
        except:
            continue
        duration_sample = len(data)
        index = 0
        while (index + 0.5) * output_duration_sample <= duration_sample:
            if (index + 1) * output_duration_sample <= duration_sample:
                data_out = data[index * output_duration_sample : (index + 1) * output_duration_sample]
            else:
                data_out = data[duration_sample - output_duration_sample : duration_sample]
            output_path = output_dir + "/" + basename + "_" + f"{index:02}" + ".wav"
            soundfile.write(output_path, data_out, samplerate=sampling_rate, subtype="PCM_16")
            index += 1
        if delete_original:
            os.remove(wav_path)
        rest_data_sample = duration_sample - (index * output_duration_sample)
        if rest_data_sample > 0:
            print(f"Warning: data dropped, {basename}, {str(rest_data_sample)}")



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Download AudioSet")
    parser.add_argument("-t", "--target_dir", type=str, required=False, default="./talking")
    parser.add_argument("-n", "--noise_dir", type=str, required=False, default="./noise")
    parser.add_argument("-o", "--output_dir", type=str, required=False, default="./")
    parser.add_argument("-r", "--sampling_rate", type=int, required=False, default="16000")
    parser.add_argument("-p", "--output_duration_time", type=int, required=False, default="5")

    args = parser.parse_args()
    target_dir = args.target_dir
    output_dir = args.output_dir
    sampling_rate = args.sampling_rate
    output_duration_time = args.output_duration_time

    os.makedirs(output_dir, exist_ok=True)

    separate_wav(target_dir, output_dir, sampling_rate=16000, output_duration_time=5, delete_original=False)

