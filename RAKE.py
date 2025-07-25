from tkinter import *
from tkinter import filedialog
import os
import customtkinter as ctk
import pygame
import random
import eyed3, io
from PIL import Image, ImageTk
from io import BytesIO

pygame.mixer.pre_init(buffer=4096)
pygame.mixer.init()
pygame.init()
pygame.mixer.music.fadeout(2000)

paused = False
shuffled = False
song_end = False
song_slider_pressed = False
pygame.mixer.music.set_volume(50)
pressed = False
new_pos = 0
songs_hidden = False
songs_played = []

def import_songs():
    global file_path, song
    try: 
        pause_unpause_btn.config(text="⏸️")
        file_path = filedialog.askdirectory() + '/'
        songs_list.delete(0, END)
        for song in os.listdir(file_path):
            songs_list.insert(END, song)
        playlist_name = file_path.split('/')[-2]
        playlist_label.config(text=playlist_name)
    except:
        pass
    
def delay(event):
    root.after(150, play_song)

def play_song():
    global paused, image_stream, new_pos, song_name
    try:
        paused = False
        new_pos = 0
        pause_unpause_btn.config(text="⏸️")
        song = songs_list.get(ACTIVE)
        pygame.mixer.music.load(file_path + song)
        pygame.mixer.music.play(fade_ms=1700)
        sound = pygame.mixer.Sound(file_path + song)
        song_len = int((sound.get_length()))
        min, sec = divmod(song_len, 60)
        time2 = '%02d:%02d' % (min, sec)
        song_length.config(text=time2)
        song_slider.config(to_=song_len)
        song_name.config(text=song[:-4])
        songfile = eyed3.load(file_path+song)
        artist = songfile.tag.artist
        artist_label.config(text=artist)

        artwork_data = songfile.tag.images[0].image_data
        image_stream = BytesIO(artwork_data)
        pil_image = Image.open(image_stream)
        resized_image = pil_image.resize((420,240), Image.LANCZOS)
        tk_image = ImageTk.PhotoImage(resized_image)
        artwork_label = Label(root, image=tk_image, bd=0)
        artwork_label.place(x=14, y=6)
        artwork_label.image = tk_image

  
    except:
        pass
    
def pause_unpause_song():
    global paused
    try:
        if paused == True:
                pygame.mixer.music.unpause()
                paused = False
                pause_unpause_btn.config(text="⏸️")
        elif paused == False:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.pause()
                    paused = True
                    pause_unpause_btn.config(text="▶️")
    except:
        pass

def next_song():
    try:
        if shuffled == True:
            next_selection = random.randint(0, songs_list.size() - 1)            
        elif songs_list.curselection()[0] == songs_list.size() - 1:
            next_selection = 0
        else:
            next_selection = (songs_list.curselection()[0] + 1)
        if next_selection == songs_list.curselection()[0]:
            next_song()
        else:
            songs_list.selection_clear(0, END)
            songs_list.selection_set(next_selection)
            songs_list.activate(next_selection)
            play_song()
    except:
        pass
    

def prev_song():
    try:
        if float(pygame.mixer.music.get_pos())/1000 > 2:
            play_song()
        else:
            if shuffled == True:
                next_selection = random.randint(0, songs_list.size()-1)
            elif songs_list.curselection()[0] == 0:
                next_selection = songs_list.size()-1
            else:
                next_selection = (songs_list.curselection()[0] - 1)
            if next_selection == songs_list.curselection()[0]:
                next_song()
            else:
                songs_list.selection_clear(0, END)
                songs_list.selection_set(next_selection)
                songs_list.activate(next_selection)
                play_song()
    except:
        pass

def shuffle_songs():
    global shuffled
    try:
        if shuffled == False:
            shuffled = True
            shuffle_btn.config(fg='gold')
        else:
            shuffled = False
            shuffle_btn.config(fg='gray')
    except:
        pass

def change_volume(value):
    global music_volume
    try:
        if int(value) > 0:
            music_volume = int(value)/100
            pygame.mixer.music.set_volume(int(value)/100)
            mute_btn.config(text='🔊', fg='gray')
        else:
            mute_btn.config(text='🔇', fg='red')
    except:
        pass
def check_song_end():
    global time
    try:
        for event in pygame.event.get():
            if event.type == MUSIC_END:
                next_song()
        if pressed == False:
            min, sec = divmod(int(pygame.mixer.music.get_pos()/1000) + new_pos, 60)
            time = '%02d:%02d' % (min, sec)
            song_pos.config(text=time)
            song_slider.set(int(pygame.mixer.music.get_pos()/1000) + new_pos)
        root.after(50, check_song_end)
    except:
        pass
                

def mute_song():
    try:
        volume_slider.set(0)
        mute_btn.config(text='🔇')
        mute_btn.config(fg='red')
        pygame.mixer.music.set_volume(0)
    except:
        pass

def slider_pressed(event):
    global pressed
    pressed = True

def slider_released(event):
    global pressed, new_pos
    pressed = False
    try:
        pygame.mixer.music.play(fade_ms=2000)
        new_pos = int(song_slider.get())
        pygame.mixer.music.set_pos(new_pos)
    except:
        pass

def hide_songs():
    global songs_hidden
    try:
        if songs_hidden == False:
            root.geometry("450x350")
            songs_hidden = True
            hide_songs_button.config(text='>')
        elif songs_hidden == True:
            root.geometry("700x350")
            songs_hidden = False
            hide_songs_button.config(text='<')
    except:
        pass

MUSIC_END = pygame.USEREVENT+1
pygame.mixer.music.set_endevent(MUSIC_END)

root = ctk.CTk()
root.title("RAKE")
root.geometry("700x350")
root.resizable(True, True)
root.config(background='black')
root.resizable(0, 0)
root.iconbitmap("Stuff\\rake_logo.ico")



songs_list = Listbox(root, width=40, background='gray10', selectforeground='gold', selectbackground='gray10', activestyle='none', height=17, bd=0, highlightthickness=0, foreground="White")
songs_list.place(x=450,y=32)
songs_list.bind("<<ListboxSelect>>", delay)

next_btn = Button(root, text="⏭️", bg='black', fg='gray', width=5, height=2, relief='flat', command=next_song)
next_btn.place(x=250, y=307)

prev_btn = Button(root, text="⏮️", bg='black', fg='gray', width=5, height=2, command=prev_song, relief='flat')
prev_btn.place(x=150, y=307)

pause_unpause_btn = Button(root, text='⏸️', bg='black', fg='white', width=5, height=2, relief='flat', command=pause_unpause_song)
pause_unpause_btn.place(x=200, y=307)

shuffle_btn = Button(root, text="RAKE", bg='black', fg='gray', width=5, height=2, relief='flat', command=shuffle_songs)
shuffle_btn.place(x=5, y=307)

volume_slider = Scale(root, from_=0, to_=100, bd=0, highlightthickness=0, troughcolor='gray', bg='white', length=220, relief='flat', orient=HORIZONTAL, showvalue=False, command=change_volume)
volume_slider.set(50)
volume_slider.place(x=470, y=317)

mute_btn = Button(root, relief='flat', bg='black', fg='gray', text='🔊', command=mute_song)
mute_btn.place(x=445, y=311)

song_pos = Label(root, text='00:00', bg='black', fg='gray')
song_pos.place(x=10, y=287)

song_length = Label(root, text='00:00', bg='black', fg='gray')
song_length.place(x=400, y=287)

song_name = Label(root, bg='black', fg='white')
song_name.place(x=10, y=248)

artist_label = Label(root, bg='black', fg='gray')
artist_label.place(x=10, y=266)

song_slider = Scale(root,orient=HORIZONTAL, highlightthickness=0, fg='white', bd=0, troughcolor='gray', from_=0, length=350, showvalue=False)
song_slider.place(x=47, y=290)
song_slider.bind("<ButtonPress-1>", slider_pressed)
song_slider.bind("<ButtonRelease-1>", slider_released)

add_playlist_button = Button(root, text='+', relief='flat', command=import_songs, bg='black', fg='white')
add_playlist_button.place(x=670, y=5)

playlist_label = Label(root, bg='black', fg='white', )
playlist_label.place(x=450, y=5)

hide_songs_button = Button(root, text='<', relief='flat', command=hide_songs, bg='black', fg='gray')
hide_songs_button.place(x=419, y=313)


background_path = "Stuff\\rake_background.png"
original_image = Image.open(background_path)
resized = original_image.resize((420, 240), Image.LANCZOS)
new_image = ImageTk.PhotoImage(resized)
artwork_background = Canvas(root, bg='white', highlightthickness=0, height=235, width=415)
artwork_background.place(x=14, y=6)
artwork_background.create_image(0, 0, anchor=NW, image=new_image)

check_song_end()
root.mainloop()
