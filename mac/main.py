import sys
import os

# Force the PATH in Python.
if sys.platform == "darwin":
    new_path = "/usr/local/bin:/opt/homebrew/bin:" + os.environ.get("PATH", "")
    os.environ["PATH"] = new_path
    print(f"Python script PATH: {os.environ['PATH']}")

    # macOS Tcl/Tk setup.
    os.environ["TCL_LIBRARY"] = "/usr/local/opt/tcl-tk/lib/tcl8.6"
    os.environ["TK_LIBRARY"] = "/usr/local/opt/tcl-tk/lib/tk8.6"
    os.environ["TK_SILENCE_DEPRECATION"] = "1"

import traceback
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import moviepy.config as mpc
import moviepy.editor as mpy
# Force MoviePy to use absolute ffmpeg path
mpc.change_settings({"FFMPEG_BINARY": "/usr/local/bin/ffmpeg"})
# Check if ffmpeg is on PATH.
if not shutil.which("ffmpeg"):
    sys.exit("Error: ffmpeg not found on PATH. Please install it and ensure 'ffmpeg' is accessible on PATH.")
# For macOS frozen apps, override sys.executable (IF needed)
if getattr(sys, 'frozen', False) and sys.platform == "darwin":
    sys.executable = '/usr/local/bin/python3'
# --------------------------------------------------------------------
# CHUNK_SIZE: how many videos to process at once.
CHUNK_SIZE = 20
def select_input_folder():
    folder = filedialog.askdirectory()
    if folder:
        input_var.set(folder)
def select_output_folder():
    folder = filedialog.askdirectory()
    if folder:
        output_var.set(folder)
def join_videos():
    """Concatenate videos in chunks and merge them into a final output."""
    in_dir = input_var.get()
    out_dir = output_var.get()
    fmt = format_var.get().strip('.').lower()  # e.g., "mp4"
    if not in_dir or not out_dir or not fmt:
        messagebox.showerror("Error", "Please select folders and format.")
        return
    try:
        all_files = sorted(os.listdir(in_dir))
    except Exception as e:
        messagebox.showerror("Error", f"Cannot list directory '{in_dir}': {e}")
        return
    video_paths = []
    for f in all_files:
        path = os.path.join(in_dir, f)
        if os.path.isfile(path):
            video_paths.append(path)
    if not video_paths:
        messagebox.showerror("Error", "No valid video files found.")
        return
    temp_files = []
    chunk_counter = 0
    for start_index in range(0, len(video_paths), CHUNK_SIZE):
        chunk = video_paths[start_index : start_index + CHUNK_SIZE]
        chunk_clips = []
        try:
            for p in chunk:
                try:
                    clip = mpy.VideoFileClip(p)
                    chunk_clips.append(clip)
                except Exception as e:
                    print(f"Skipping {p}: {e}")
            if not chunk_clips:
                continue
            chunk_clip = mpy.concatenate_videoclips(chunk_clips, method="compose")
            chunk_file = os.path.join(out_dir, f"chunk_{chunk_counter}.mp4")
            chunk_counter += 1
            chunk_clip.write_videofile(chunk_file, threads=1)
            temp_files.append(chunk_file)
        except Exception as e:
            messagebox.showerror("Error", f"Error while processing chunk: {e}")
            return
        finally:
            for c in chunk_clips:
                c.close()
    if len(temp_files) == 0:
        messagebox.showerror("Error", "No chunks produced; possibly no valid videos.")
        return
    if len(temp_files) == 1:
        final_file = os.path.join(out_dir, f"joined_video.{fmt}")
        os.rename(temp_files[0], final_file)
        messagebox.showinfo("Done", f"Joined video saved as:\n{final_file}")
        return
    final_clips = []
    try:
        for tmp in temp_files:
            try:
                c = mpy.VideoFileClip(tmp)
                final_clips.append(c)
            except Exception as e:
                print(f"Skipping temp file {tmp}: {e}")
        if not final_clips:
            messagebox.showerror("Error", "No chunk files to merge. Possibly no valid videos.")
            return
        final_clip = mpy.concatenate_videoclips(final_clips, method="compose")
        final_file = os.path.join(out_dir, f"joined_video.{fmt}")
        final_clip.write_videofile(final_file, threads=1)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to join final chunks: {e}")
        return
    finally:
        for c in final_clips:
            c.close()
        for tmp in temp_files:
            try:
                os.remove(tmp)
            except Exception:
                pass
    messagebox.showinfo("Done", f"Joined video saved as:\n{final_file}")
def main():
    global input_var, output_var, format_var
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
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        tk.Tk().withdraw()
        messagebox.showerror("Fatal Error", f"Error: {e}\nSee console for details.")
        sys.exit(1)