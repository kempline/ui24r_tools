import os
import glob
import subprocess
import json


IN_FOLDER = "/Users/sbg/Music/Partyteufel/BackingTracks/categories_single_tracks"
OUT_FOLDER = "/Users/sbg/Downloads/Multitrack"
SOX_BIN = "/Users/sbg/Documents/Homebrew-brew-bfe9693/bin/sox"
SOXI_BIN = "/Users/sbg/Documents/Homebrew-brew-bfe9693/bin/soxi"


def get_extended_env():
    current_environment = os.environ.copy()
    if os.name == 'posix':
        # copy current environment and add /usr/local/bin: since mediainfo is
        # usually installed at this location on macOS
        current_environment['PATH'] = '/usr/local/bin:' + current_environment['PATH']
    return current_environment


def get_metadata(source_file, soxi_switch):
    if os.path.exists(source_file) is False:
        print("Given source file does not exist: " + source_file)
        return -1

    cmd = '"' + SOXI_BIN + '" "' + soxi_switch + '" "' + source_file + '"'
    result = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True, env=get_extended_env())
    if result.returncode != 0:
        print("Error while trying to execute cmd: " + str(cmd))
        print("stderr: " + str(result.stderr))
        return -1

    return result.stdout


def write_ui_rec_session(folder):
    # pick first .flac file in folder
    in_flac_files = glob.glob(os.path.join(folder, "*.flac"))

    if len(in_flac_files) == 0:
        print("No flac-files found in directory: " + folder)
        return -1

    in_flac_files = sorted(in_flac_files)

    in_files_names_only = list()
    for in_flac_file in in_flac_files:
        tmp = os.path.basename(in_flac_file)
        tmp = tmp.replace('.flac', '')
        in_files_names_only.append(tmp)

    sample_rate = get_metadata(in_flac_files[0], '-r')
    if sample_rate == -1:
        return -1

    length_samples = get_metadata(in_flac_files[0], '-s')
    if length_samples == -1:
        return -1

    length_seconds = get_metadata(in_flac_files[0], '-D')
    if length_samples == -1:
        return -1

    mapping_list = list()
    for i in range(0, len(in_flac_files)):
        mapping_list.append('i.' + str(i))

    ui_rec_session_data = dict()
    ui_rec_session_data["complete"] = True
    ui_rec_session_data["ext"] = ".flac"
    ui_rec_session_data["files"] = in_files_names_only
    ui_rec_session_data["lengthSamples"] = int(length_samples)
    ui_rec_session_data["lengthSeconds"] = float(length_seconds)
    ui_rec_session_data["mapping"] = mapping_list
    ui_rec_session_data["names"] = in_files_names_only
    ui_rec_session_data["sampleRate"] = int(sample_rate)

    with open(os.path.join(folder, '.uirecsession'), 'w') as f:
        json.dump(ui_rec_session_data, f, indent=4)

    return 0


def generate_ui_recording_session(in_folder, multitrack_out_folder):
    if os.path.exists(in_folder) is False:
        print("Source folder does not exists: " + in_folder)
        return

    if os.path.isdir(in_folder) is False:
        print("Given source folder not a directory: " + in_folder)
        return

    in_wav_files = glob.glob(os.path.join(in_folder, "*.wav"))

    if len(in_wav_files) == 0:
        print("No wave-files found in directory: " + in_folder)
        return

    # check if out folder is called "Multitrack"
    if "Multitrack" != os.path.basename(multitrack_out_folder):
        print("Output folder must end with 'Multitrack' folder!")
        return -1

    if os.path.exists(multitrack_out_folder) is False:
        print("Destination folder does not exists: " + multitrack_out_folder)
        return

    session_name = os.path.basename(in_folder)
    out_folder = os.path.join(multitrack_out_folder, session_name)
    os.mkdir(out_folder)

    for in_wav_file in in_wav_files:

        filename = os.path.basename(in_wav_file)
        '''
        if filename.endswith('backing_vocals.wav'):
            filename = '8_backing_vocals.wav'
        elif filename.endswith('bass.wav'):
            filename = '3_bass.wav'
        elif filename.endswith('bed.wav'):
            filename = '6_bed.wav'
        elif filename.endswith('click.wav'):
            filename = '1_click.wav'
        elif filename.endswith('drums.wav'):
            filename = '2_drums.wav'
        elif filename.endswith('guitars.wav'):
            filename = '5_guitars.wav'
        elif filename.endswith('keyboard.wav'):
            filename = '4_keyboard.wav'
        elif filename.endswith('main_voice.wav'):
            filename = '7_main_voice.wav'
        '''
        filename_l = filename.replace('.wav', ' L.flac')
        filename_l = filename_l.replace('_', ' ')
        filename_l = filename_l.replace('\'', '')
        filename_r = filename.replace('.wav', ' R.flac')
        filename_r = filename_r.replace('_', ' ')
        filename_r = filename_r.replace('\'', '')

        # left channel
        cmd = SOX_BIN + ' "' + in_wav_file + '" "' + os.path.join(out_folder, filename_l) + '" remix 1'
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE, shell=True, env=get_extended_env())

        if result.returncode != 0:
            print("Error while trying to execute cmd: " + str(cmd))
            print("stderr: " + str(result.stderr))
            return -1
        print("Converted: " + os.path.join(out_folder, filename_l))

        # right channel
        cmd = SOX_BIN + ' "' + in_wav_file + '" "' + os.path.join(out_folder, filename_r) + '" remix 2'
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE, shell=True, env=get_extended_env())

        if result.returncode != 0:
            print("Error while trying to execute cmd: " + str(cmd))
            print("stderr: " + str(result.stderr))
            return -1
        print("Converted: " + os.path.join(out_folder, filename_l))

    ret_val = write_ui_rec_session(out_folder)
    if ret_val != 0:
        return -1

    return 0


if __name__ == '__main__':
    multi_track_dirs = glob.glob(IN_FOLDER + '/*')
    multi_track_dirs = sorted(multi_track_dirs)
    for multi_track_dir in multi_track_dirs:
        if os.path.isdir(multi_track_dir):
            generate_ui_recording_session(multi_track_dir, OUT_FOLDER)


