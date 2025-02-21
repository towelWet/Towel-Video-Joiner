import os
import tkinter as tk
from tkinter import filedialog, messagebox
import moviepy.editor as mpy

def select_input_folder():
    folder = filedialog.askdirectory()
    if folder:
        input_var.set(folder)

def select_output_folder():
    folder = filedialog.askdirectory()
    if folder:
        output_var.set(folder)

def join_videos():
    in_dir = input_var.get()
    out_dir = output_var.get()
    fmt = format_var.get().strip('.').lower()  # e.g., "mp4"
    if not in_dir or not out_dir or not fmt:
        messagebox.showerror("Error", "Please select folders and format.")
        return
    
    clips = []
    for f in sorted(os.listdir(in_dir)):
        path = os.path.join(in_dir, f)
        if os.path.isfile(path):
            try:
                clip = mpy.VideoFileClip(path)
                clips.append(clip)
            except:
                pass
    
    if not clips:
        messagebox.showerror("Error", "No valid video files found.")
        return
    
    final_clip = mpy.concatenate_videoclips(clips, method="compose")
    out_file = os.path.join(out_dir, f"joined_video.{fmt}")
    final_clip.write_videofile(out_file)
    
    for c in clips:
        c.close()
    messagebox.showinfo("Done", f"Joined video saved as:\n{out_file}")

root = tk.Tk()
root.title("Towel Video Joiner")

input_var = tk.StringVar()
output_var = tk.StringVar()
format_var = tk.StringVar(value="mp4")

tk.Label(root, text="Input Folder:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
tk.Entry(root, textvariable=input_var, width=40).grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=select_input_folder).grid(row=0, column=2, padx=5)

tk.Label(root, text="Output Folder:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
tk.Entry(root, textvariable=output_var, width=40).grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=select_output_folder).grid(row=1, column=2, padx=5)

tk.Label(root, text="Output Format:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
tk.Entry(root, textvariable=format_var, width=10).grid(row=2, column=1, padx=5, pady=5, sticky="w")

tk.Button(root, text="Join Videos", command=join_videos).grid(row=3, column=0, columnspan=3, pady=10)

root.mainloop()
