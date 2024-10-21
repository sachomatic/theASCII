import sqlite3
import json
import gzip

frames_dict = {}
frames_interval = 0

conn = sqlite3.connect("Converter/saves.db")
cursor = conn.cursor()

cursor.execute("""
                CREATE TABLE IF NOT EXISTS saves (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    data TEXT,
                    interval INTEGER,
                    music BLOB
                )
                """)

def save_movie(data: dict, interval, save_to_json=True):
    import os
    import json
    import base64

    # Get the name of the movie from the user
    name = input("Name: ")

    # Convert the movie data list to JSON format
    data_json = json.dumps(data)

    # Read the .mp3 file as binary data and convert to Base64
    with open(os.path.join("Converter", "music.mp3"), 'rb') as file:
        blob_data = file.read()
        blob_data_base64 = base64.b64encode(blob_data).decode('utf-8')

    # Create a dictionary to store all the data
    movie_data = {
        'name': name,
        'data': data_json,
        'interval': interval,
        'music': blob_data_base64
    }

    # Save to either a .json or .txt file
    file_extension = 'json' if save_to_json else 'txt'
    file_name = f"{name}.{file_extension}"

    d = compress_json(json.dumps(movie_data,indent=4))

    # Write the dictionary to the desired file format
    with open(os.path.join("Converter/saves",file_name), 'wb') as file:
        file.write(d)

    print(f"Movie saved to {file_name}")

def compress_json(data):
    json_bytes = data.encode('utf-8')  # Convert string to bytes
    compressed_data = gzip.compress(json_bytes)
    return compressed_data

# Decompress JSON data
def decompress_json(compressed_data):
    decompressed_bytes = gzip.decompress(compressed_data)
    decompressed_data = decompressed_bytes.decode('utf-8')  # Convert bytes back to string
    return json.loads(decompressed_data)

def get_all():
    import os
    lst = []
    for filemane in os.listdir("Converter/saves"):
        lst.append(filemane)
    return lst

def view_extract_movie(json_file_path):
    import json
    import base64
    import os

    print("Beginning extraction")

    with open(f"Converter/saves/{json_file_path}", 'rb') as file:
        movie_data = decompress_json(file.read())

    print("Done, getting Data...")

    # Extract the movie data
    name = movie_data['name']
    data_json = movie_data['data']
    interval = movie_data['interval']
    music_base64 = movie_data['music']

    print("Done. Decoding music")
    # Convert the Base64-encoded music back to binary data
    music_data = base64.b64decode(music_base64)

    # Recreate the .mp3 file from the binary data
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
        'name': name,
        'data': movie_data_list,
        'interval': interval,
        'music': music_file_path
    }

def extract_movie(json_file_path):
    import json
    import base64
    import os

    print("Beginning extraction")

    with open(f"Converter/saves/{json_file_path}", 'rb') as file:
        movie_data = decompress_json(file.read())

    print("Done, getting Data...")

    # Extract the movie data
    name = movie_data['name']
    data_json = movie_data['data']
    interval = movie_data['interval']
    music_base64 = movie_data['music']

    print("Done. Decoding music")
    # Convert the Base64-encoded music back to binary data
    music_data = base64.b64decode(music_base64)

    # Recreate the .mp3 file from the binary data
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
        'name': name,
        'data': movie_data_list,
        'interval': interval,
        'music': music_file_path
    }

def delete_all():
    cursor.execute("DROP TABLE saves")

def change_name(new_name,old_name):
    cursor.execute("UPDATE saves SET name=? WHERE NAME=?",(new_name,old_name))
    conn.commit()

"""class bitch():
            def __init__(self) -> None:
                self.btch = []
            
            def put(self,element):
                self.btch.append(element)

            def prnt(self):
                for i in self.btch:
                    print(i)

        print(image_to_ascii("Converter/frames/frame_0000.png",get_terminal_size()))
        h = bitch()
        l = threading.Lock()
        lst = ["frame_0000.png","frame_0001.png"]
        single_convert(get_terminal_size(),l,lst,h)"""