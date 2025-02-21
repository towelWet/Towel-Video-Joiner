import sys
import os
import traceback
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import moviepy.editor as mpy

def setup_ffmpeg_path():
    """Ensure ffmpeg is accessible by setting the absolute path."""
    ffmpeg_path = r"C:\ffmpeg\bin\ffmpeg.exe"  # Adjust this path to your ffmpeg installation
    os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)
    log_message(f"Updated PATH with ffmpeg: {os.environ['PATH']}")

def select_input_folder():
    folder = filedialog.askdirectory()
    if folder:
        input_var.set(folder)
        log_message(f"Selected input folder: {folder}")

def select_output_folder():
    folder = filedialog.askdirectory()
    if folder:
        output_var.set(folder)
        log_message(f"Selected output folder: {folder}")

def join_videos():
    """Function to start the video joining in a separate thread."""
    threading.Thread(target=process_videos, daemon=True).start()

def process_videos():
    in_dir = input_var.get()
    out_dir = output_var.get()
    fmt = format_var.get().strip('.').lower()  # e.g., "mp4"
    log_message(f"Input directory: {in_dir}")
    log_message(f"Output directory: {out_dir}")
    log_message(f"Output format: {fmt}")

    if not in_dir or not out_dir or not fmt:
        messagebox.showerror("Error", "Please select folders and format.")
        return

    all_files = []
    try:
        all_files = sorted(os.listdir(in_dir))
        log_message(f"Files found in directory: {all_files}")
    except Exception as e:
        messagebox.showerror("Error", f"Cannot list directory '{in_dir}': {e}")
        return

    video_paths = [os.path.join(in_dir, f) for f in all_files if os.path.isfile(os.path.join(in_dir, f))]
    log_message(f"Video paths: {video_paths}")

    if not video_paths:
        messagebox.showerror("Error", "No valid video files found.")
        return

    clips = []
    for path in video_paths:
        try:
            clip = mpy.VideoFileClip(path)
            clips.append(clip)
            log_message(f"Loaded video: {path}")
        except Exception as e:
            log_message(f"Failed to load video {path}: {e}")

    if not clips:
        messagebox.showerror("Error", "No valid video files to process.")
        return

    final_clip = mpy.concatenate_videoclips(clips, method="compose")
    out_file = os.path.join(out_dir, f"joined_video.{fmt}")
    try:
        final_clip.write_videofile(out_file)
        log_message(f"Final video saved at {out_file}")
        messagebox.showinfo("Success", f"Video successfully joined: {out_file}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to write video file: {e}")
    finally:
        for clip in clips:
            clip.close()

def log_message(message):
    """Log messages to the scrolled text widget."""
    if console:
        console.config(state='normal')
        console.insert(tk.END, message + '\n')
        console.config(state='disabled')
        console.yview(tk.END)

def main():
    global input_var, output_var, format_var, console
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

    # Console log area
    console = scrolledtext.ScrolledText(root, state='disabled', height=10)
    console.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="we")

    setup_ffmpeg_path()
    root.mainloop()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        tk.Tk().withdraw()
        messagebox.showerror("Fatal Error", f"Error: {e}\nSee console for details.")
        sys.exit(1)
