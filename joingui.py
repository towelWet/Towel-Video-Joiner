import sys
import os
import traceback
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import moviepy.editor as mp

def get_ffmpeg_path():
    """Get the ffmpeg path from either the environment or a local directory."""
    if os.path.exists("ffmpeg.exe"):
        return os.path.abspath("ffmpeg.exe")
    elif os.path.exists(r"C:\ffmpeg\bin\ffmpeg.exe"):
        return r"C:\ffmpeg\bin\ffmpeg.exe"
    return None

def setup_ffmpeg_path():
    """Configure ffmpeg path in the environment."""
    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        log_message("Warning: ffmpeg.exe not found. Please ensure it's in the application directory or C:\\ffmpeg\\bin\\")
        return False
    os.environ["IMAGEIO_FFMPEG_EXE"] = ffmpeg_path
    log_message(f"Found ffmpeg at: {ffmpeg_path}")
    return True

def select_input_folder():
    """Open folder selection dialog for input directory."""
    folder = filedialog.askdirectory()
    if folder:
        input_var.set(folder)
        log_message(f"Selected input folder: {folder}")

def select_output_folder():
    """Open folder selection dialog for output directory."""
    folder = filedialog.askdirectory()
    if folder:
        output_var.set(folder)
        log_message(f"Selected output folder: {folder}")

def join_videos():
    """Start video joining process in a separate thread."""
    if not setup_ffmpeg_path():
        messagebox.showerror("Error", "ffmpeg not found. Please install ffmpeg or place ffmpeg.exe in the application directory.")
        return
    threading.Thread(target=process_videos, daemon=True).start()

def process_videos():
    """Main video processing function."""
    try:
        in_dir = input_var.get()
        out_dir = output_var.get()
        fmt = format_var.get().strip('.').lower()
        
        if not all([in_dir, out_dir, fmt]):
            messagebox.showerror("Error", "Please select input folder, output folder, and format.")
            return
        
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
            log_message(f"Created output directory: {out_dir}")

        video_files = [f for f in os.listdir(in_dir) if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]
        if not video_files:
            messagebox.showerror("Error", "No video files found in input directory.")
            return
        
        log_message(f"Found {len(video_files)} video files")
        
        # Sort files by name to ensure consistent order
        video_files.sort()
        clips = []
        
        for filename in video_files:
            filepath = os.path.join(in_dir, filename)
            try:
                clip = mp.VideoFileClip(filepath)
                clips.append(clip)
                log_message(f"Loaded: {filename}")
            except Exception as e:
                log_message(f"Error loading {filename}: {str(e)}")
                for loaded_clip in clips:
                    loaded_clip.close()
                messagebox.showerror("Error", f"Failed to load {filename}")
                return

        if not clips:
            messagebox.showerror("Error", "No videos could be loaded")
            return

        try:
            log_message("Joining videos...")
            final_clip = mp.concatenate_videoclips(clips)
            output_path = os.path.join(out_dir, f"joined_video.{fmt}")
            
            log_message("Writing final video...")
            final_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            log_message(f"Successfully created: {output_path}")
            messagebox.showinfo("Success", "Videos joined successfully!")
            
        except Exception as e:
            log_message(f"Error during video processing: {str(e)}")
            messagebox.showerror("Error", f"Failed to process videos: {str(e)}")
            
        finally:
            for clip in clips:
                clip.close()
            if 'final_clip' in locals():
                final_clip.close()
                
    except Exception as e:
        log_message(f"Unexpected error: {str(e)}")
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

def log_message(message):
    """Add message to the console widget."""
    if console:
        console.configure(state='normal')
        console.insert(tk.END, f"{message}\n")
        console.configure(state='disabled')
        console.see(tk.END)
        root.update_idletasks()

def create_gui():
    """Create the main GUI window and widgets."""
    global root, input_var, output_var, format_var, console
    
    root = tk.Tk()
    root.title("Towel Video Joiner")
    
    # Make window resizable
    root.resizable(True, True)
    root.minsize(500, 300)
    
    # Configure grid weights
    root.grid_columnconfigure(1, weight=1)
    root.grid_rowconfigure(4, weight=1)
    
    # Create StringVars
    input_var = tk.StringVar()
    output_var = tk.StringVar()
    format_var = tk.StringVar(value="mp4")
    
    # Input folder row
    tk.Label(root, text="Input Folder:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    tk.Entry(root, textvariable=input_var).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    tk.Button(root, text="Browse", command=select_input_folder).grid(row=0, column=2, padx=5)
    
    # Output folder row
    tk.Label(root, text="Output Folder:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    tk.Entry(root, textvariable=output_var).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
    tk.Button(root, text="Browse", command=select_output_folder).grid(row=1, column=2, padx=5)
    
    # Format row
    tk.Label(root, text="Output Format:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    format_entry = tk.Entry(root, textvariable=format_var, width=10)
    format_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
    
    # Join button
    join_button = tk.Button(root, text="Join Videos", command=join_videos)
    join_button.grid(row=3, column=0, columnspan=3, pady=10)
    
    # Console
    console = scrolledtext.ScrolledText(root, height=10, wrap=tk.WORD)
    console.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
    console.configure(state='disabled')
    
    return root

def main():
    """Main application entry point."""
    try:
        root = create_gui()
        setup_ffmpeg_path()
        root.mainloop()
    except Exception as e:
        traceback.print_exc()
        messagebox.showerror("Fatal Error", f"Application failed to start: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
