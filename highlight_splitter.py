import matplotlib.pyplot as plt
import numpy as np
from os.path import dirname, join as pjoin
from scipy.io import wavfile
import subprocess
import os.path
from pathlib import Path
import datetime
import sys
from scipy import stats


def reformat_sound_data(_new_x_data, _amplitude_channel, _sample_rate):
    """
    :param _new_x_data: length of sound (in second)
    :param _amplitude_channel: left channel data or right channel data
    :param _sample_rate: hz
    :return: array new data (one second, one element)
    """
    current_point = 0
    _new_y_data = []
    for index in _new_x_data:
        # chia khoảng audio ra theo mỗi giây
        next_point = current_point + _sample_rate
        array_amplitude_per_second = _amplitude_channel[current_point:next_point]
        # ở mỗi giây đó, lấy max và min (tương ứng dương và âm)
        max_in_second = np.max(array_amplitude_per_second)
        min_in_second = np.min(array_amplitude_per_second)
        current_point = next_point
        # newYData là array [[1,1], [2,2]] dùng để vẽ biểu đồ
        _new_y_data.append([max_in_second, min_in_second])
    return _new_y_data


def get_avg_amplitude(_new_y_data):
    """
    :param _new_y_data: array data return by function reformat_sound_data
    :return: array with average top and bot sound signal
    """
    top_amplitude = np.array(_new_y_data)[:, 0]
    bot_amplitude = np.array(_new_y_data)[:, 1]
    return [np.mean(top_amplitude), np.mean(bot_amplitude)]


def detect_highlight(_new_x_data, new_y_data):
    """
    :param _new_x_data: array data return by function reformat_sound_data
    :param new_y_data: array data return by function reformat_sound_data
    :return: array highlight data, from second to second [[from_second, to_second]]
    """
    min_highlight_length = 8
    max_highlight_length = 40
    is_start = False
    highlight_from = 0
    highlight_to = 0
    list_highlight = []
    top_avg_amplitude, bot_avg_amplitude = get_avg_amplitude(new_y_data)
    print("List highlight zone n:-------------------------")
    for index in _new_x_data:
        _top_value = new_y_data[index][0]
        _bot_value = new_y_data[index][1]
        if _top_value >= top_avg_amplitude and not is_start:
            # 2 lai bắt đầu ở điểm đầu tiên có biên độ CAO hơn avg và CHƯA start
            is_start = True
            highlight_from = index
        if _bot_value <= bot_avg_amplitude and is_start:
            # 2 lai kết thức ở điểm đầu tiên có biên độ THẤP hơn avg và ĐÃ start
            is_start = False
            highlight_to = index
            highlight_length = highlight_to - highlight_from
            # nếu 2lai > 5s mới tính
            if min_highlight_length < highlight_length < max_highlight_length:
                txt = "start {}p {}s end {}p {}s"
                print(txt.format(highlight_from // 60, highlight_from % 60, highlight_to // 60, highlight_to % 60))
                list_highlight.append([highlight_from, highlight_to])
    print("END List highlight zone n:-------------------------")
    return list_highlight


def assign_plot_data(_new_x_data, _new_y_data, _label="Channel"):
    plt.plot(_new_x_data, _new_y_data, label=_label)
    plt.xlabel("Time [s]")
    plt.ylabel("Amplitude")
    # plt.show()


def intersect_2d_array(a, b):
    """
    Find row intersection between 2D numpy arrays, a and b.
    Returns another numpy array with shared rows
    """
    return np.array([x for x in set(tuple(x) for x in a) & set(tuple(x) for x in b)])


def get_audio_wav_from_video(video_path, output_path="split_to.wav"):
    if not os.path.isfile(video_path):
        print("not found " + video_path)
        return False
    command = "ffmpeg -i " + video_path + " -ab 160k -ac 2 -ar 44100 -vn " + output_path
    # subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("CMD execute: " + command)
    subprocess.call(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def cut_video(video_path, from_h_m_s, to_h_m_s, output_path="split_video.mp4"):
    if not os.path.isfile(video_path):
        print("not found "+video_path)
        return False
    output_sub_folder = "my_split"
    Path(output_sub_folder).mkdir(parents=True, exist_ok=True)
    full_path_output = output_sub_folder + "/" + output_path
    Path(full_path_output).unlink(missing_ok=True)
    command = "ffmpeg -ss " + from_h_m_s + " -i " + video_path + " -t " + to_h_m_s + " -c copy " + full_path_output
    # subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("CMD execute: "+command)
    subprocess.call(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def main():
    video_path = "../lollong.mp4"
    wav_after_extract = "extract_video_to_2.wav"
    if not os.path.isfile(wav_after_extract):
        get_audio_wav_from_video(video_path, wav_after_extract)
    if not os.path.isfile(wav_after_extract):
        print("not found " + wav_after_extract)
        return False
    sample_rate, data = wavfile.read(wav_after_extract)
    # sample_rate, data = wavfile.read('../sound.wav')
    # biên độ left, right channel
    left_amplitude = data[:, 0]
    right_amplitude = data[:, 1]
    # sound length in second
    length_in_second = data.shape[0] / sample_rate
    new_x_data = range(0, int(length_in_second))

    left_new_y_data = reformat_sound_data(new_x_data, left_amplitude, sample_rate)
    assign_plot_data(new_x_data, left_new_y_data, "Left channel")

    right_new_y_data = reformat_sound_data(new_x_data, right_amplitude, sample_rate)
    assign_plot_data(new_x_data, right_new_y_data, "Right channel")
    plt.show()

    list_highlight_left = detect_highlight(new_x_data, left_new_y_data)
    list_highlight_right = detect_highlight(new_x_data, right_new_y_data)
    # list_highlight = intersect_2d_array(list_highlight_left, list_highlight_right)
    list_highlight = list_highlight_left
    list_highlight.extend(list_highlight_right)
    print(list_highlight)
    for item in list_highlight:
        _second_from = item[0]
        _second_to = item[1]
        _time_from = "0" + str(datetime.timedelta(seconds=int(_second_from)))
        _time_to = "0" + str(datetime.timedelta(seconds=int(_second_to-_second_from)))
        _output_file_name = "_{}_{}.mp4"
        _output_file_name = _output_file_name.format(str(_second_from), str(_second_to))
        cut_video(video_path, _time_from, _time_to, _output_file_name)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
