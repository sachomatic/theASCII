from multiprocessing import Pool,cpu_count
import zstandard as zstd
import sys
import termios
import tty

frames_dict = {}
frames_interval = 0

class Player():
    def __init__(self,path,ready_event):
        import pygame
        
        self.state = False

        self.mixer = pygame.mixer
        self.mixer.init()
        self.path = path

        self.ready_event = ready_event
        self.mixer.music.load(self.path)

        self.ready_event.set()

    def play(self):
        self.state = True
        self.mixer.music.play()

def get_video():
    import os

    path_list = os.listdir("Converter/video")
    result = "Converter/video/" + path_list[0]

    return result

def delete_video():
    import os

    try:
        path = get_video()
        os.remove(path)
        
        return True
    except:
        return False


def save_movie(interval):
    import os
    import json
    import base64

    # Get the name of the movie from the user
    name = input("Name: ")

    # Read the .mp3 file as binary data and convert to Base64
    print("Encoding music")
    with open(os.path.join("Converter", "music.mp3"), 'rb') as file:
        blob_data = file.read()
        blob_data_base64 = base64.b64encode(blob_data).decode('utf-8')

    # Create a dictionary to store all the data
    print("Creating storage for data")
    with open("Converter/temp/.~lock.temp.json#","r") as file:
        movie_data = {
            'name': name,
            'data': file.read(),
            'interval': interval,
            'music': blob_data_base64
        }

    # Save to either a .json or .txt file
    print("Creating file")
    file_extension = 'zst'
    file_name = f"{name}.{file_extension}"

    print("Compressing")
    ideal_level = ideal_ratio(len(movie_data["data"]))
    level = choose_compression_level(ideal_level)
    print("")
    d = parallel_zstd_compress(json.dumps(movie_data,indent=4),level)

    # Write the dictionary to the desired file format
    print("Saving")
    with open(os.path.join("Converter/saves",file_name), 'wb') as file:
        file.write(d)

    print(f"Movie saved to {file_name}")

def ideal_ratio(char_numbers) -> int:
    import math
    # Define file size ranges (in bytes) and corresponding target compression ratios.
    # These values are rough estimates and may vary with the data type.
    size_to_ratio = [
        (1_000, 0.9),        # Files ~1KB: 90% of original size (minimal compression)
        (10_000, 0.75),      # Files ~10KB: 75% of original size
        (100_000, 0.6),      # Files ~100KB: 60% of original size
        (1_000_000, 0.5),    # Files ~1MB: 50% of original size
        (10_000_000, 0.4),   # Files ~10MB: 40% of original size
        (100_000_000, 0.3),  # Files ~100MB: 30% of original size
        (1_000_000_000, 0.25) # Files ~1GB or more: 25% of original size
    ]

    file_size = char_numbers//16
    
    # If file size is below the smallest threshold, return the highest ratio (least compression)
    if file_size < size_to_ratio[0][0]:
        return size_to_ratio[0][1]
    
    # Iterate over ranges to find where the file size fits and interpolate ratio
    for i in range(1, len(size_to_ratio)):
        size_low, ratio_low = size_to_ratio[i - 1]
        size_high, ratio_high = size_to_ratio[i]
        
        if size_low <= file_size < size_high:
            # Interpolate ratio based on file size within the current range
            interpolation = (file_size - size_low) / (size_high - size_low)
            target_ratio = ratio_low + interpolation * (ratio_high - ratio_low)
            target_level = math.floor(target_ratio * 24)
            target_level = int(target_level)
            return target_level
    
    # If the file size exceeds the largest defined range, use the lowest target ratio
    ratio = size_to_ratio[-1][1]
    target_level = math.floor(ratio * 24)
    target_level = int(target_level)
    return target_level

# Main function to compress JSON data in parallel using LZMA
def parallel_zstd_compress(data,level:int):    
    compressor = zstd.ZstdCompressor(level=level, threads=cpu_count()-1)
    compressed_data = compressor.compress(data.encode('utf-8'))

    return compressed_data

# Function to decompress a single LZMA-compressed chunk
def decompress_chunk(compressed_data):
    try:
        decompressor = zstd.ZstdDecompressor()
        data = decompressor.decompress(compressed_data)
        return data
    except zstd.ZstdError as error:
        print(f"Warning: {error}")
        return None

def get_key():
    """Read a single keypress from stdin and return it."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)   # raw mode = no line buffering
        ch = sys.stdin.read(3)  # arrows send 3 chars like "\x1b[D"
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def choose_compression_level(default_level:int=3):
    import time
    print(f"Ideal level : {default_level} Hit q to quit")
    global level,stop
    level = default_level

    ui = "[{}{}{}]"
    while True:
        key = get_key()
        if key == "\x1b[D":
            level -= 1
        elif key == "\x1b[C":
            level += 1
        elif key == "q":
            return level
        empty1 = (level-1)*"-"
        cursor = "|"
        empty2 = (24-level)*"-"
        print("Compression level (enter to save): "+ui.format(empty1,cursor,empty2)+f"{level}/24",end='\r')
            

def get_all():
    import os
    lst = []
    for filemane in os.listdir("Converter/saves"):
        lst.append(filemane)
    return lst

def extract_movie(json_file_path):
    import json
    import base64
    import os

    print("Beginning extraction")

    with open(f"Converter/saves/{json_file_path}", 'rb') as file:
        movie_data = decompress_chunk(file.read())

    print("Done, getting Data...")

    movie_data = movie_data.decode('utf-8')
    movie_data = json.loads(movie_data)

    # Extract the movie data
    name = movie_data['name']
    data_json = movie_data['data']
    interval = movie_data['interval']
    music_base64 = movie_data['music']

    print("Done. Decoding music")
    # Convert the Base64-encoded music back to binary data
    print("-Decoding music")
    music_data = base64.b64decode(music_base64)

    # Recreate the .mp3 file from the binary data
    print("-Saving music")
    music_file_path = "Converter/music.mp3"
    os.makedirs(os.path.dirname(music_file_path), exist_ok=True)

    with open(music_file_path, 'wb') as music_file:
        music_file.write(music_data)

    print("Done, preparing movie...")

    # Convert the JSON movie data back to a Python list
    movie_data_list = json.loads(data_json)

    print(f"Movie '{name}' extracted.")

    # Return the extracted data
    return {
        'data': movie_data_list,
        'interval': interval,
    }