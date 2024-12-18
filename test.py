from PIL import Image
import os

# Get list of HEIF and HEIC files in directory
directory = '/Users/marshallraubenheimer/Downloads/TotalNinja/'
os.chdir(directory)
files = os.listdir(directory)

# Convert each file to JPEG
for filename in files:
    image = Image.open(os.path.join(directory, filename.lower()))

    # image.convert('RGB').save(os.path.join(directory, os.path.splitext(filename)[0] + '.jpg'))