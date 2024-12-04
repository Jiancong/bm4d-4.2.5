import os
import glob
import argparse
import re

parser = argparse.ArgumentParser(description='This is a demo for list files in folder')

parser.add_argument('input', help='images folder for input')
parser.add_argument('format', help='file format')

args = parser.parse_args()

directory = args.input

entries = glob.glob(os.path.join(directory, '*.' + args.format))

pattern = r"tif"
match = re.search(pattern, args.format)

for file_path in entries:
    print(file_path)
    if match:
        # convert to mat file
        os.system('python3 convertTIFF2.py ' + file_path)
        os.system('python3 bm4d_denoising.py ' + file_path[:-4] + ".mat")
    else:
        os.system('python3 bm4d_denoising_png.py ' + file_path[:-4] + ".png")

