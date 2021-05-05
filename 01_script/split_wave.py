#-- coding: utf-8 --
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
import wave
import math
import random

def binary2float(frames, length, sampwidth):
    # binary to int
    if sampwidth==1:
        data = np.frombuffer(frames, dtype=np.uint8)
        data = data - 128
    elif sampwidth==2:
        data = np.frombuffer(frames, dtype=np.int16)
    elif sampwidth==3:
        a8 = np.fromstring(frames, dtype=np.uint8)
        tmp = np.empty([length, 4], dtype=np.uint8)
        tmp[:, :sampwidth] = a8.reshape(-1, sampwidth)
        tmp[:, sampwidth:] = (tmp[:, sampwidth-1:sampwidth] >> 7) * 255
        data = tmp.view("int32")[:, 0]
    elif sampwidth==4:
        data = np.frombuffer(frames, dtype=np.int32)
    # Normalize (int to float)
    # data = data.astype(float)/(2*(sampwidth-1))
    return data
 
def float2binary(data, sampwidth):
    # Normalize (float to int)
    # data = (data(2 * (sampwidth-1)-1)).reshape(data.size, 1)
    # int to binary
    if sampwidth==1:
        data = data+128
        frames = data.astype(np.uint8).tobytes()
    elif sampwidth==2:
        frames = data.astype(np.int16).tobytes()
    elif sampwidth==3:
        a32 = np.asarray(data, dtype = np.int32)
        a8 = (a32.reshape(a32.shape + (1,)) >> np.array([0, 8, 16])) & 255
        frames = a8.astype(np.uint8).tobytes()
    elif sampwidth==4:
        frames = data.astype(np.int32).tobytes()
    return frames
 
def read_wave(file_name, start=0, end=0):
    file = wave.open(file_name, "rb") # open file
    sampwidth = file.getsampwidth()
    nframes = file.getnframes()
    fs = file.getframerate()
    file.setpos(start)
    if end == 0:
        length = nframes-start
    else:
        length = end-start+1
    frames = file.readframes(length)
    file.close() # close file
    return nframes, fs, binary2float(frames, length, sampwidth) # binary to float
 
def write_wave(file_name, data, sampwidth=3, fs=48000):
    file = wave.open(file_name, "wb") # open file
    # setting parameters
    file.setnchannels(1)
    file.setsampwidth(sampwidth)
    file.setframerate(fs)
    frames = float2binary(data, sampwidth) # float to binary
    file.writeframes(frames)
    file.close() # close file
 
def getParams(file_name):
    file = wave.open(file_name) # open file
    params = file.getparams()
    file.close() # close file
    return params

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create wave file using sin wav")
    parser.add_argument("wav_filename", help="Input wav filename", type=str)
    parser.add_argument("-i", "--interval", help="interval[ms]", type=int, required=True, default=10)
    parser.add_argument("-d", "--duration", help="duration[ms]", type=int, required=False, default=1000)
    parser.add_argument("-r", "--random", help="random fluctuation[ms]", type=int, required=False, default=0)
    parser.add_argument("-o", "--out_dir", help="output directory", type=str, required=False, default="./")
    args = parser.parse_args()
    wav_filename = args.wav_filename
    interval = args.interval
    duration = args.duration
    random_fluctuation = args.random
    out_dir = args.out_dir
    print(f"Input = {wav_filename}, interval = {interval} ms, duration = {duration} ms. random_fluctuation = {random_fluctuation}. out_dir = {out_dir}")
    base, ext = os.path.splitext(os.path.basename(wav_filename))
    os.makedirs(out_dir, exist_ok=True)
    
    nframes, fs, input_data = read_wave(wav_filename)
    plt.plot(input_data)
    plt.show()

    t = 0
    while t <= nframes - int(duration*fs/1000):
        output_filename = os.path.join(out_dir, base + f"_{t:08} .wav")
        output_data = input_data[t:t + duration * int(fs/1000)]
        t += (interval + random.randint(-random_fluctuation, random_fluctuation)) * int(fs/1000)
        write_wave(output_filename, output_data, 2, fs)
