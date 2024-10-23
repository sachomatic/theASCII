import multiprocessing.queues
import cv2,os
from tqdm import tqdm
import store
import threading
import math
from colorama import Fore,Back,Style
import logging
import multiprocessing
from multiprocessing import Pool, Manager, Value
from Custom_drv import Press,KEYPAD_MINUS,KEYPAD_PLUS

def euclidean_distance(c1, c2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))

def opposite(q):
    col = {
        'BLACK': 'WHITE',
        'BLUE': 'BLACK',
        'CYAN': 'BLACK',
        'GREEN': 'BLACK',
        'MAGENTA': 'BLACK',
        'LIGHTRED': 'BLACK',
        'WHITE': 'BLACK',
        'YELLOW': 'BLACK',
        'GRAY': 'BLACK',
        'LIGHTBLUE': 'BLACK',
        'LIGHTGREEN': 'BLACK',
        'PURPLE': 'BLACK',
        'RED': 'BLACK'
        }

    try:
        r = col[q]

        match r:
            case "WHITE":
                result = Fore.WHITE
            case "YELLOW":
                result = Fore.YELLOW
            case "RED":
                result = Fore.RED
            case "MAGENTA":
                result = Fore.MAGENTA
            case "GREEN":
                result = Fore.GREEN
            case "CYAN":
                result = Fore.CYAN
            case "BLACK":
                result = Fore.BLACK
            case "BLUE":
                result = Fore.BLUE
            case "GRAY":
                result = Fore.LIGHTBLACK_EX
    except:
        result = False
    finally:
        return result

def closest_color(rgb):
    # Initialize variables to store the closest color and minimum distance
    colors = {
    "BLACK": (0, 0, 0),
    "BLUE": (0, 0, 255),
    "CYAN": (0, 255, 255),
    "GREEN": (0, 255, 0),
    "MAGENTA": (255, 0, 255),
    "LIGHTRED": (200, 0, 0),
    "WHITE": (255,255,255),
    "YELLOW": (255, 255, 0),
    "GRAY":(128, 128, 128),
    "LIGHTBLUE":(0, 0, 128),
    "LIGHTGREEN":(0,128,0),
    "PURPLE":(128,0,128),
    "RED":(255,0,0)  
    }

    closest = None
    min_dist = float('inf')
    
    # Iterate through the predefined colors
    for color_name, color_rgb in colors.items():
        # Calculate the Euclidean distance between the input RGB and the current color
        dist = euclidean_distance(rgb, color_rgb)
        
        # If the distance is the smallest found so far, update the closest color
        if dist < min_dist:
            min_dist = dist
            closest = color_name
            
    return closest

global frames_interval
global path_waiting_list

def extract_frames_with_progress(video_path, output_folder):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Open the video file
    video_capture = cv2.VideoCapture(video_path)
    
    # Check if video opened successfully
    if not video_capture.isOpened():
        print("Error: Could not open video.")
        return
    
    # Get the total number of frames
    frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = video_capture.get(cv2.CAP_PROP_FPS)
    frame_interval = 1 / fps
    print(f"Frame rate: {fps} frames per second")
    print(f"Time interval between frames: {frame_interval} seconds")

    frame_number = 0
    
    with tqdm(total=frame_count, desc="Extracting frames") as pbar:
        while True:
            # Read the next frame
            success, frame = video_capture.read()
            
            # If the frame was not read successfully, break the loop
            if not success:
                break
            
            # Save the frame as an image file
            frame_filename = os.path.join(output_folder, f"frame_{frame_number:04d}.png")
            cv2.imwrite(frame_filename, frame)
            
            frame_number += 1
            pbar.update(1)
    
    # Release the video capture object
    video_capture.release()
    print("Done extracting frames.")
    return frame_interval,frame_count

def get_terminal_size():
    import shutil

    size = shutil.get_terminal_size((80, 20))  # Fallback size if unable to get terminal size
    return size.columns, size.lines

def image_to_ascii(image_path, dimension):
    from PIL import Image
    from colorama import Fore, Style

    # ASCII characters used to build the output text
    ASCII_CHARS = "@%#*+=-:. "

    # Open image
    image = Image.open(image_path)
    
    # Get terminal size
    term_width, term_height = dimension
    # Adjust the image size to fit the terminal
    aspect_ratio = image.width / image.height
    new_width = term_width
    # Multiply the height by 1.8 to compensate for the character aspect ratio
    new_height = int(term_width / aspect_ratio / 1.8)

    # If new height is greater than terminal height, adjust both width and height
    if new_height > term_height:
        new_height = term_height
        new_width = int(term_height * aspect_ratio * 1.8)

    image = image.resize((new_width, new_height))

    gray_image = image.convert("L")
    
    # Convert pixels to ASCII
    g_pixels = gray_image.getdata()
    pixels = image.getdata()
    ascii_img_parts = []
    for index,pixel in enumerate(pixels):
        color = closest_color(pixel)
        fn_col = opposite(color)
        match color:
            case "BLACK":
                bg_col = Back.BLACK
            case "BLUE":
                bg_col = Back.BLUE
            case "CYAN":
                bg_col = Back.CYAN
            case "GREEN":
                bg_col = Back.GREEN
            case 'MAGENTA':
                bg_col = Back.MAGENTA
            case "RED":
                bg_col = Back.RED
            case "WHITE":
                bg_col = Back.WHITE
            case "YELLOW":
                bg_col = Back.YELLOW
            case "LIGHTRED":
                bg_col = Back.LIGHTRED_EX
            case "LIGHTBLUE":
                bg_col = Back.LIGHTBLUE_EX
            case "LIGHTGREEN":
                bg_col = Back.LIGHTGREEN_EX
            case "PURPLE":
                bg_col = Back.LIGHTMAGENTA_EX
            case "GRAY":
                bg_col = Back.LIGHTBLACK_EX
            case _:
                print(color)
        col = fn_col + bg_col
        ascii_char = ASCII_CHARS[min(len(ASCII_CHARS) - 1, g_pixels[index] // (256 // len(ASCII_CHARS)))]
        ascii_img_parts.append(col + ascii_char + Style.RESET_ALL)
    
    # Split string into multiple lines
    ascii_img = ""
    for i in range(0, len(ascii_img_parts), new_width):
        ascii_img += ''.join(ascii_img_parts[i:i + new_width]) + "\n"
    
    return ascii_img

def set_font_size(size):
    # ANSI escape codes for font size (not universally supported)
    print(f"\033[{size}m", end='')

def setting_quality():
    from pynput.keyboard import Controller, Key
    import time
    keyboard = Controller()
    while True:
        x,y = get_terminal_size()
        print(f"Actual setting : {x}x{y}")
        ch = input("Increase or decrease quality (+/-)(enter to exit) : ")
        if ch == "+":
            set_font_size(50)
        elif ch == "-":
            with keyboard.pressed(Key.ctrl):
                Press(KEYPAD_PLUS)
        elif ch == "":
            break
        else:
            print("")

def delete_all_files(directory):
    if not os.path.exists(directory):
        print(f"The directory {directory} does not exist.")
        return

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            os.unlink(file_path)
            print(f"Deleted file: {file_path}")
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

def check_if_already_extracted_footage():
    video_path = "Converter/video.mp4"
    video_capture = cv2.VideoCapture(video_path)
    frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

    try:
        for index,filename in enumerate(os.listdir("Converter/frames")):
            pass
        fps = video_capture.get(cv2.CAP_PROP_FPS)
        frame_interval = 1 / fps
        if index+1 == frame_count:
            return (True,frame_interval,frame_count)
        else:
            print(frame_count,index)
            return (False,None,None)
    except:
        return (False,None,None)
    
def play(play_event:threading.Event,ready_event:threading.Event):
        import time
        import pygame

        pygame.mixer.init()
        movie_player = pygame.mixer

        music_path = f"Converter/music.mp3"
        if os.path.isfile(music_path):
            movie_player.music.load(music_path)
            ready_event.set()
            while not play_event.is_set:
                pass
            movie_player.music.play()
        else:
            print("Music not found")

def convert_mp4_to_mp3(input_file, output_file=None):
    from moviepy.editor import VideoFileClip
    import os

    if output_file is None:
        base, _ = os.path.splitext(input_file)
        output_file = base + '.mp3'

    video_clip = VideoFileClip(input_file)
    audio_clip = video_clip.audio

    audio_clip.write_audiofile(output_file)

    audio_clip.close()
    video_clip.close()

def single_convert(dimension,lock,path_waiting_list,add_wt_dict:multiprocessing.Queue):
    while True:
        with lock:
            if len(path_waiting_list) == 0:
                break
            filename = path_waiting_list[0]
            path_waiting_list.pop(0)
        print(f" {len(path_waiting_list)} frames left        ",end="\r")
        ascii = image_to_ascii(f"Converter/frames/{filename}",dimension)
        new = [filename,ascii]
        add_wt_dict.put(new)

def convert():
    import time

    global frames_interval
    global path_waiting_list

    path_waiting_list = []
    
    try:
        al_extracted,frames_interval,frame_count = check_if_already_extracted_footage()
        if al_extracted == True:
            print("Similar file already exctracted. Use?")
            choice = input("Y/N : ")
        dimension = get_terminal_size()
        if al_extracted == False or choice.upper() == "N":
            delete_all_files("Converter/frames")
            print("Starting...")
            frames_interval,frame_count = extract_frames_with_progress("Converter/video.mp4","Converter/frames")
        for filename in os.listdir("Converter/frames"):
            path_waiting_list.append(filename)

        with Manager() as manager:
            path_waiting_list2 =  manager.list(path_waiting_list)
            queue = manager.Queue(frame_count)
            lock = manager.Lock()
            args = [(dimension,lock,path_waiting_list2,queue) for _ in path_waiting_list2]
            print(f" {len(path_waiting_list)} frames left",end="\r")
            with Pool(processes=multiprocessing.cpu_count()) as pool:
                pool.starmap(single_convert, args)

            while not queue.empty():
                filename, ascii_art = queue.get()
                store.frames_dict[filename] = ascii_art
                #store.frames_dict.append(queue.get())

        sorted_keys = sorted(store.frames_dict.keys(), key=lambda x: int(x.split('_')[1].replace(".png", "")))
        sorted_dict = {key: store.frames_dict[key] for key in sorted_keys}
        store.frames_dict = sorted_dict
        #list_fls = [value[1] for value in store.frames_dict.values()]

        convert_mp4_to_mp3("Converter/video.mp4", "Converter/music.mp3")
        print("Done converting")
        choice = input("Save movie for later? : Y/N")
        try:
            if choice.upper() == "Y":
                store.save_movie(store.frames_dict,frames_interval)
        except:
            print("Unable to store film")
        return sorted_dict
    except Exception as error:
        logging.exception("")

def view_decompression(compressed_movie,frames_interval):
    buffer = None

def view(ASCII_movie:dict,frames_interval:int):
    import threading
    from rich.console import Console
    term = Console()
    import time
    from blessed import Terminal
    t = Terminal()
    play_event = threading.Event()
    ready_event = threading.Event()

    Music_thread = threading.Thread(target=play,args=(play_event,ready_event))
    a = 0
    
    start_time = time.perf_counter()
    Music_thread.start()
    print("Waiting for music player...")
    #print(ASCII_movie.items())
    while not ready_event.is_set():
        pass
    with t.location():
        play_event.set()
        for index, element in enumerate(ASCII_movie.items()):
            # Calculate the expected time for the current frame
            expected_time = start_time + index * frames_interval
            
            # Clear the console and print the frame
            print(t.move_xy(0,0)+element[1])

            # Calculate how much time to sleep
            current_time = time.perf_counter()
            time_to_sleep = expected_time - current_time

            # Only sleep if there is time left
            if time_to_sleep > 0:
                time.sleep(time_to_sleep)

    Music_thread.join()
    term.clear()

def browse():
    import json

    lib = store.get_all()
    if lib == []:
        print("No movies saved")
        return
    dict = {}
    for index,element in enumerate(lib):
        print(f"{index+1} : {element}")
        dict[str(index+1)] = element
    ch = input("View (number) : ")
    try:
        dict[ch]
        movie = store.extract_movie(dict[ch])
        name = movie["name"]
        data = movie["data"]
        interval = movie["interval"]
        music_path = movie["music"]

        input("Start")
        view(data,interval)
    except KeyError:
        print("Invalid number")

if __name__ == "__main__":
    setting_quality()
    inp = input("Browse / Convert : B/C : ").upper()

    if inp == "ERASE":
        store.delete_all()
    elif inp == "CHANGE":
        lib = store.get_all()
        dict = {}
        for index, element in enumerate(lib):
            print(f"{index + 1} : {element[1]}")
            dict[str(index + 1)] = element
        inp2 = input("Change name of (number) :")
        try:
            dict[inp2]
            name = dict[inp2][1]
            new_name = input("New name : ")
            store.change_name(new_name, name)
        except:
            print("Invalid number")
    elif inp == "C":
        dict = convert()
        input("Start")
        view(dict, frames_interval)
    else:
        browse()