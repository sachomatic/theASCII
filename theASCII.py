import os
from tqdm import tqdm
import store
import logging
import multiprocessing
from multiprocessing import Pool, Manager, Queue, cpu_count, Process
from decord import VideoReader,cpu
import cv2
from numpy import ndarray

def progress(count,max:int,div:int):
    import math
    pr = count * div / max
    pr = math.floor(pr)
    end = '\r'
    full = pr*"#" 
    empty = (div-pr)*"-"
    print(f"[{full}{empty}]" + f"{count}/{max}",end=end)
    if count == max:
        print("")

def opposite_color(rgb):
    r, g, b = rgb
    return (max(0, r-50), max(0, g-50), max(0, b-50))

def save_frame_worker(queue):
    while True:
        item = queue.get()
        if item is None:
            break
        frame_number, frame, output_folder = item
        frame_filename = os.path.join(output_folder, f"frame_{frame_number:05d}.png")
        cv2.imwrite(frame_filename, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

def extract_frames_with_progress(video_path, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    video_capture = VideoReader(video_path, ctx=cpu(0))

    frame_count = len(video_capture)
    fps = video_capture.get_avg_fps()
    frame_interval = 1 / fps

    queue = Queue(maxsize=cpu_count() * 2)

    # Create worker processes
    num_workers = cpu_count()
    processes = []
    for _ in range(num_workers):
        p = Process(target=save_frame_worker, args=(queue,))
        p.start()
        processes.append(p)

    with tqdm(total=frame_count, desc="Extracting frames") as pbar:
        frames = range(frame_count)
        for frame_number in frames:
            frame = video_capture[frame_number].asnumpy()
            queue.put((frame_number, frame, output_folder))
            pbar.update(1)

    # Tell workers to stop
    for _ in processes:
        queue.put(None)

    # Wait for workers to finish
    for p in processes:
        p.join()

    print("Done extracting frames.")
    return frame_interval, frame_count

def get_terminal_size():
    import shutil
    modificator = 0.95
    modificator = 0.95
    size = shutil.get_terminal_size((80, 20))  # Fallback size if unable to get terminal size
    return int(size.columns * modificator), int(size.lines * modificator)
    return int(size.columns * modificator), int(size.lines * modificator)

def image_to_ascii(image_path, dimension):
    from PIL import Image
    from colorama import Fore, Style
    from blessed import Terminal
    t = Terminal()
    from blessed import Terminal
    t = Terminal()

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
        opposite = opposite_color(pixel)
        fn_col = t.color_rgb(opposite[0],opposite[1],opposite[2])
        bg_col = t.on_color_rgb(pixel[0],pixel[1],pixel[2])
        if pixel == (0,0,0):
            col = ""
            ascii_char = " "
        else:
            col = fn_col + bg_col
            ascii_char = ASCII_CHARS[min(len(ASCII_CHARS) - 1, g_pixels[index] // (256 // len(ASCII_CHARS)))]
        opposite = opposite_color(pixel)
        fn_col = t.color_rgb(opposite[0],opposite[1],opposite[2])
        bg_col = t.on_color_rgb(pixel[0],pixel[1],pixel[2])
        if pixel == (0,0,0):
            col = ""
            ascii_char = " "
        else:
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
    from pynput import keyboard as k
    from pynput import keyboard as k
    import time
    keyboard = k.Controller()
    keyboard = k.Controller()
    while True:
        x,y = get_terminal_size()
        print(f"Actual setting : {x}x{y}")
        ch = input("Increase or decrease quality (+/- , enter to exit) : ")
        if ch == "-":
            with keyboard.pressed(k.Key.ctrl):
                keyboard.press("+")
        elif ch == "+":
            with keyboard.pressed(k.Key.ctrl):
                minus = "\u2013"
                keyboard.press(minus)
        ch = input("Increase or decrease quality (+/- , enter to exit) : ")
        if ch == "-":
            with keyboard.pressed(k.Key.ctrl):
                keyboard.press("+")
        elif ch == "+":
            with keyboard.pressed(k.Key.ctrl):
                minus = "\u2013"
                keyboard.press(minus)
        elif ch == "":
            break
        else:
            print("unknown command")
            print("unknown command")

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
    video_path = store.get_video()
    video_path = store.get_video()
    video_capture = cv2.VideoCapture(video_path)
    frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

    try:
        lenght = len(os.listdir("Converter/frames"))
        fps = video_capture.get(cv2.CAP_PROP_FPS)
        frame_interval = 1 / fps
        if lenght == frame_count:
            return (True,frame_interval,frame_count)
        else:
            print(frame_count,lenght)
            return (False,None,None)
    except:
        return (False,None,None)

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

def single_convert(dimension,lock,path_waiting_list,add_wt_dict:multiprocessing.Queue,maximum):
    while True:
        with lock:
            if len(path_waiting_list) == 0:
                break
            filename = path_waiting_list[0]
            path_waiting_list.pop(0)
        progress((maximum-len(path_waiting_list)),maximum,30)
        progress((maximum-len(path_waiting_list)),maximum,30)
        ascii = image_to_ascii(f"Converter/frames/{filename}",dimension)
        new = [filename,ascii]
        add_wt_dict.put(new)

def convert():
    import json
    import json

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
            frames_interval,frame_count = extract_frames_with_progress(store.get_video(),"Converter/frames")
            frames_interval,frame_count = extract_frames_with_progress(store.get_video(),"Converter/frames")
        for filename in os.listdir("Converter/frames"):
            path_waiting_list.append(filename)

        with Manager() as manager, open("Converter/temp/.~lock.temp.json#","w") as output_file:
            path_waiting_list2 =  manager.list(path_waiting_list)
            queue = manager.Queue(frame_count)
            lock = manager.Lock()
            args = [(dimension,lock,path_waiting_list2,queue,frame_count) for _ in path_waiting_list2]
            args = [(dimension,lock,path_waiting_list2,queue,frame_count) for _ in path_waiting_list2]
            with Pool(processes=multiprocessing.cpu_count()) as pool:
                pool.starmap(single_convert, args)

            output_file.write("{\n")
            first_entry = True

            output_file.write("{\n")
            first_entry = True

            while not queue.empty():
                filename, ascii_art = queue.get()
                store.frames_dict[filename] = ascii_art
                if not first_entry:
                    output_file.write(",\n")
                json_entry = json.dumps({filename: ascii_art})
                output_file.write(json_entry[1:-1])  # Strip the outer braces

                first_entry = False
            output_file.write("\n}")

        with open("Converter/temp/.~lock.temp.json#", "r+") as output_file:
            frames_dict = json.load(output_file)
            sorted_keys = sorted(frames_dict.keys(), key=lambda x: int(x.split('_')[1].replace(".png", "")))
            sorted_dict = {key: frames_dict[key] for key in sorted_keys}

            # Rewrite the file with the sorted dictionary
            output_file.seek(0)
            json.dump(sorted_dict, output_file, indent=4)
            output_file.truncate()
        convert_mp4_to_mp3(store.get_video(), "Converter/music.mp3")
        print("Done converting")
        try:
            store.save_movie(frames_interval)
            if input("Delete frames (this will save up a lot of space) Y/N : ").upper() == "Y":
                delete_all_files("Converter/frames")
        except:
            print("Unable to store film:")
            logging.exception("")
    
        open("Converter/temp/.~lock.temp.json#", "w").close()
        return sorted_dict
    except Exception:
        logging.exception("")

def view(ASCII_movie:dict,frames_interval:int):
    import threading
    import time
    from blessed import Terminal
    t = Terminal()
    from rich.console import Console
    clear = Console()
    from sys import stdout

    ready_event = threading.Event()
    music_path = "Converter/music.mp3"
    player = store.Player(music_path,ready_event)
    music_path = "Converter/music.mp3"
    player = store.Player(music_path,ready_event)

    Music_thread = threading.Thread(target=player.play)
    Music_thread = threading.Thread(target=player.play)
    
    start_time = time.perf_counter()
    Music_thread.start()
    print("Waiting for music player...")
    skip_frame = False

    ready_event.wait()
    with t.location(), t.hidden_cursor():
        clear.clear()
        while not player.state:
            pass
        for index, element in enumerate(ASCII_movie.items()):
            # Calculate the expected time for the current frame
            expected_time = start_time + index * frames_interval
            
            # Clear the console and print the frame
            if not skip_frame:
                stdout.write(t.move_xy(0,0)+element[1])
            else:
                skip_frame = False
            if not skip_frame:
                stdout.write(t.move_xy(0,0)+element[1])
            else:
                skip_frame = False

            # Calculate how much time to sleep
            current_time = time.perf_counter()
            time_to_sleep = expected_time - current_time

            # Only sleep if there is time left
            if time_to_sleep > 0:
                time.sleep(time_to_sleep)
            else:
                skip_frame = True                    

    Music_thread.join()
    clear.clear()

def browse():
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
        movie = store.extract_movie(dict[ch])
        data = movie["data"]
        interval = movie["interval"]

        input("Start")
        view(data,interval)
    except KeyError:
        print("Invalid number")

if __name__ == "__main__":
    setting_quality()
    inp = input("Browse / Convert : B/C : ").upper()

    if inp == "C":
        dict = convert()
        input("Start")
        view(dict, frames_interval)
    else:
        browse()