import os
import glob
import subprocess


IN_FOLDER = "/Users/sbg/Downloads/wav_in"
OUT_FOLDER = "/Users/sbg/Downloads/mp3_out"
SOX_BIN = "/Users/sbg/Documents/Homebrew-brew-bfe9693/bin/sox"
SOXI_BIN = "/Users/sbg/Documents/Homebrew-brew-bfe9693/bin/soxi"


def get_extended_env():
    current_environment = os.environ.copy()
    if os.name == 'posix':
        # copy current environment and add /usr/local/bin: since mediainfo is
        # usually installed at this location on macOS
        current_environment['PATH'] = '/usr/local/bin:' + current_environment['PATH']
    return current_environment


def conv(source_file, dest_file):
    if os.path.exists(source_file) is False:
        print("Given source file does not exist: " + source_file)
        return -1

    # sox -r 8000 <wavfilename> <mp3filename> --norm
    cmd = '"' + SOX_BIN + '" "' + source_file + '" "' + dest_file + '" --norm'
    result = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True, env=get_extended_env())
    if result.returncode != 0:
        print("Error while trying to execute cmd: " + str(cmd))
        print("stderr: " + str(result.stderr))
        return -1

    return result.stdout


if __name__ == '__main__':
    input_files = glob.glob(IN_FOLDER + '/*.wav')
    input_files = sorted(input_files)
    for input_file in input_files:
        basename = os.path.basename(input_file)
        conv(input_file, os.path.join(OUT_FOLDER, basename + '.mp3'))




