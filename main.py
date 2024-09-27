import tkinter as tk
from tkinter import filedialog
from pygame import mixer
import os
import json
from mutagen.easyid3 import EasyID3 
from mutagen.mp3 import MP3  

mixer.init()


root = tk.Tk()
root.title("opwip`s music player")
root.geometry("800x800")

song_progress_current = tk.StringVar
song_progress_full = tk.StringVar
song_length = tk.IntVar()
current_song_index = tk.IntVar()
paused = tk.BooleanVar()

first = tk.BooleanVar()
first.set(True)

# Functions!!!

def play_music(song_info):
    """Play the selected music file."""
    label_file.config(text=song_info["name"])
    song_path = song_info["path"]
    audio = mixer.Sound(song_path)
    song_length.set(audio.get_length()) 
    if song_path:
        paused.set(False)
        stop_music()
        mixer.music.load(song_path)
        mixer.music.play()
        label_status.config(text="Playing")
        if first.get():
            update_progress()
            first.set(False)

def pause_music():
    """Pause the currently playing music."""
    mixer.music.pause()
    paused.set(True)
    label_status.config(text="Paused")

def resume_music():
    """Resume the paused music."""
    mixer.music.unpause()
    paused.set(False)
    label_status.config(text="Playing")

def stop_music():
    """Stop the music playback."""
    paused.set(True)
    mixer.music.stop()
    label_status.config(text="Stopped")

def play_next():
    if list(music_list.keys())[current_song_index.get()] ==  list(music_list.keys())[-1]:
        current_song_index.set(0)
        song_id = list(music_list.keys())[current_song_index.get()]
        song_info = music_list[song_id]
        stop_music()
        play_music(song_info)
    else:
        song_id = list(music_list.keys())[current_song_index.get() + 1]
        song_info = music_list[song_id]
        current_song_index.set(current_song_index.get() + 1)
        stop_music()
        play_music(song_info)

def play_previous():
    if list(music_list.keys())[current_song_index.get()] ==  list(music_list.keys())[0]:
        song_id = list(music_list.keys())[-1]
        song_info = music_list[song_id]
        current_song_index.set(len(list(music_list.keys())) - 1)
        stop_music()
        play_music(song_info)
    else:
        song_id = list(music_list.keys())[current_song_index.get() - 1]
        song_info = music_list[song_id]
        current_song_index.set(current_song_index.get() - 1)
        stop_music()
        play_music(song_info)

def music_load():
    music_folder_path = 'music/'
    try:
        with open(f"{music_folder_path}/music.json", "r" ) as music_file:
            data = json.load(music_file)
            if data:
                music = data
            else:
                music = {
                0 : {"name" : "lalala",
                    "path" : 'unknown'}
                }
    except FileNotFoundError:
        print(f"Error: The file {music_folder_path}/music.json was not found.")
        with open(f"{music_folder_path}/music.json", "w" ) as music_file:
            music = {
                0 : {"name" : "lalala",
                    "path" : 'unknown'}
                }
    except json.JSONDecodeError as e:
        music = {
                0 : {"name" : "lalala",
                    "path" : 'unknown'}
                }
        print(f"JSONDecodeError: {e}")  # This will show the specific error message

        

    return music

music_list = music_load()

def add_music():
    file = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])

    def get_name(filet):
        try:
            audio = MP3(filet, ID3=EasyID3)

            # Retrieve artist and title from the metadata
            artist = audio.get('artist', ['Unknown Artist'])[0]
            title = audio.get('title', ['Unknown Title'])[0]

            print(f"Artist: {artist}")
            print(f"Title: {title}")
            if title == 'Unknown Title' and artist == 'Unknown Artist':
                if os.path.basename(filet.title()).lower() == "audio.mp3" or len(os.path.basename(filet.title()).lower().split('.')[0]) < 4 :
                    print(os.path.dirname(filet))
                    return os.path.dirname(filet).split("/")[-1]
                return os.path.basename(filet.title())
            return f"{title} by {artist}"
        except NameError:
            return os.path.basename(filet.title())
        
    song_info = {'name' : get_name(file),
                "path" : file.title()}

    for key,value in music_list.items():
        if value['path'] == song_info['path']:
            return 0

    music_list[int(list(music_list.keys())[-1]) + 1] = song_info
    
    loaded_music.insert(tk.END, song_info["name"])

    with open("music/music.json", "w" ) as music_file:
        json.dump(music_list, music_file, indent=4)

def delete_music():
    selected_index = loaded_music.curselection()
    if selected_index:
        song_id = list(music_list.keys())[selected_index[0]]
        del music_list[song_id]
        stop_music()
        loaded_music.delete(selected_index[0])
        with open("music/music.json", "w" ) as music_file:
            json.dump(music_list, music_file, indent=4)

def on_select(event):
    # Get the selected item index
    selected_index = loaded_music.curselection()
    if selected_index:
        current_song_index.set(selected_index[0])
        # Get the ID of the selected song
        song_id = list(music_list.keys())[selected_index[0]]
        song_info = music_list[song_id]
        # Load the song using the path
        try:
            play_music(song_info)
        except FileNotFoundError:
            delete_music()

# Buttons to press and not only them !!!!
frame_controls = tk.Frame(root)
frame_controls.pack(pady=20)


button_pause = tk.Button(frame_controls, text="Pause", command=pause_music)
button_resume = tk.Button(frame_controls, text="Resume", command=resume_music)

volume_scale = tk.Scale(root, from_=0, to=100, orient="horizontal", label="Volume", command=lambda v: mixer.music.set_volume(int(v) / 100))
volume_scale.pack(pady=20)
volume_scale.set(25)  # Set default volume to 25%

button_music_add = tk.Button(frame_controls, text="add_music", command=add_music)
button_music_add.grid(row=2, column=0, padx=20, pady=20)

button_delete_music = tk.Button(frame_controls, text="delete_music", command=delete_music)
button_delete_music.grid(row=2, column=6, padx=20, pady=20)

button_play_next = tk.Button(frame_controls, text="play next", command=play_next)
button_play_next.grid(row=2, column=4, padx=20, pady=20)

button_play_next = tk.Button(frame_controls, text="play next", command=play_next)
button_play_next.grid(row=2, column=4, padx=20, pady=20)

button_play_prev = tk.Button(frame_controls, text="play prev", command=play_previous)
button_play_prev.grid(row=2, column=2, padx=20, pady=20)

loaded_music = tk.Listbox(root, width=50, height=10)
loaded_music.pack(pady=10)

for song_id, song_info in music_list.items():
    loaded_music.insert(tk.END, song_info["name"])

loaded_music.bind('<<ListboxSelect>>', on_select)

button_pause.grid(row=0, column=2, padx=10)
button_resume.grid(row=0, column=3, padx=10)

music_progress = tk.Label(root)
music_progress.pack(pady=10)

label_file = tk.Label(root, text="No file loaded", font=("Arial", 12))
label_file.pack(pady=10)

label_status = tk.Label(root, text="Welcome to opwip`s music player", font=("Arial", 12), fg="green")
label_status.pack(pady=10)

def format_time_display(seconds):
    if seconds < 10:
        return f"0{seconds}"
    return seconds

def update_progress():
    if mixer.music.get_busy():
        # ВАЖНО ВАЖНО 💀💀💀💀💀💀💀💀💀💀 !!!!!!! ЗДЕЛАЙ ЄТО НА ДРУГОЙ ПОТОК ЕБЛАН
        # ⬆⬆⬆⬆⬆👆👆👆👆 НЕТ НЕ НАДО ДИБИЛОИД ЕБУЧИЙ
        # Да я БиЛичностная личность, проблемы?
        music_progress.config(text=f'{int(mixer.music.get_pos() / 1000 // 60)}:{format_time_display(int(round(mixer.music.get_pos() / 1000 % 60, 0)))} / {int(song_length.get() // 60)}:{format_time_display(int(round(song_length.get() % 60, 0)))}')
    elif not paused.get():
        play_next()
    root.after(1000, update_progress)


root.mainloop()

mixer.quit()