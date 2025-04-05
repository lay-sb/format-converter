# -*- coding: utf-8 -*-
'''
作者：lay~sb
Github：https://github.com/lay~sb/format-converter
注：作者是萌新，代码写的很烂，欢迎大佬们指正
'''

import tkinter as tk
from tkinter import filedialog
import subprocess
from tkinter import ttk
import time
import os
import re

class VideoConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("格式转换器")
        self.input_file = tk.StringVar()
        self.output_format = tk.StringVar(value="mp3")
        self.folder_path = tk.StringVar()
        self.batch_output_format = tk.StringVar(value="mp3")
        single_frame = tk.LabelFrame(root, text="单个文件转换", font=('Arial', 12))
        single_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky='ew')
        tk.Label(single_frame, text="输入文件:", font=('Arial', 12)).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        tk.Entry(single_frame, textvariable=self.input_file, width=40, font=('Arial', 12)).grid(row=0, column=1, padx=10, pady=10)
        tk.Button(single_frame, text="浏览", command=self.select_file, width=10, font=('Arial', 12)).grid(row=0, column=2, padx=10, pady=10)
        tk.Label(single_frame, text="输出格式:", font=('Arial', 12)).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        tk.Entry(single_frame, textvariable=self.output_format, width=40, font=('Arial', 12)).grid(row=1, column=1, padx=10, pady=10)
        tk.Button(single_frame, text="转换", command=self.convert_video, width=10, font=('Arial', 12)).grid(row=1, column=2, padx=10, pady=10)
        batch_frame = tk.LabelFrame(root, text="批量转换", font=('Arial', 12))
        batch_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky='ew')
        tk.Label(batch_frame, text="批量转换:", font=('Arial', 12)).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        tk.Entry(batch_frame, textvariable=self.folder_path, width=40, font=('Arial', 12)).grid(row=0, column=1, padx=10, pady=10)
        tk.Button(batch_frame, text="浏览", command=self.select_folder, width=10, font=('Arial', 12)).grid(row=0, column=2, padx=10, pady=10)
        tk.Label(batch_frame, text="输出格式:", font=('Arial', 12)).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        tk.Entry(batch_frame, textvariable=self.batch_output_format, width=40, font=('Arial', 12)).grid(row=1, column=1, padx=10, pady=10)
        tk.Button(batch_frame, text="批量转换", command=self.batch_convert, width=10, font=('Arial', 12)).grid(row=1, column=2, padx=10, pady=10)
        self.status_label = tk.Label(root, text="等待开始转换", font=('Arial', 12), fg="blue")
        self.status_label.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky='w')
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Horizontal.TProgressbar", thickness=25, troughcolor='#f0f0f0', background='#4caf50', relief='flat')
        self.progress = ttk.Progressbar(root, orient="horizontal", length=450, mode="determinate", style="Horizontal.TProgressbar")
        self.progress.grid(row=4, column=0, columnspan=3, padx=20, pady=20)
        info_frame = tk.LabelFrame(root, text="文件信息", font=('Arial', 12))
        info_frame.grid(row=0, column=3, rowspan=5, padx=10, pady=10, sticky='ns')
        self.original_info = tk.Text(info_frame, height=10, width=40, font=('Arial', 12))
        self.original_info.grid(row=0, column=0, padx=10, pady=10)
        self.converted_info = tk.Text(info_frame, height=10, width=40, font=('Arial', 12))
        self.converted_info.grid(row=1, column=0, padx=10, pady=10)

    def select_file(self):
        file_path = filedialog.askopenfilename()
        self.input_file.set(file_path)
        self.update_file_info(file_path)

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        self.folder_path.set(folder_path)
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        self.original_info.delete(1.0, tk.END)
        if files:
            for file_name in files:
                file_path = os.path.join(folder_path, file_name)
                self.original_info.insert(tk.END, f"文件名: {file_name}\n")
                self.original_info.insert(tk.END, f"文件大小: {os.path.getsize(file_path) / 1024:.2f} KB\n")
                self.original_info.insert(tk.END, f"文件格式: {file_name.split('.')[-1]}\n\n")
        else:
            self.original_info.insert(tk.END, "文件夹中没有文件")

    def batch_convert(self):
        folder_path = self.folder_path.get()
        output_format = self.batch_output_format.get()
        if not folder_path:
            tk.messagebox.showerror("错误", "请先选择文件夹！")
            return
        try:
            files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            total_files = len(files)
            if total_files == 0:
                tk.messagebox.showerror("错误", "文件夹中没有文件！")
                return
            for file_name in files:
                output_file = os.path.join(folder_path, file_name.rsplit('.', 1)[0] + '.' + output_format)
                if os.path.exists(output_file):
                    tk.messagebox.showerror("错误", f"检测到同名文件 {output_file}，转换已终止！")
                    self.status_label.config(text='转换终止', fg='red')
                    return
            self.progress['value'] = 0
            self.status_label.config(text='批量转换中...', fg='orange')
            self.progress.update()
            for i, file_name in enumerate(files):
                input_file = os.path.join(folder_path, file_name)
                output_file = os.path.join(folder_path, file_name.rsplit('.', 1)[0] + '.' + output_format)
                if os.path.exists(output_file):
                    self.status_label.config(text=f'跳过已存在文件 {i+1}/{total_files}')
                    self.progress['value'] = (i+1)/total_files * 100
                    self.progress.update()
                    continue
                self.status_label.config(text=f'正在转换 {i+1}/{total_files}')
                self.progress['value'] = (i+1)/total_files * 100
                self.progress.update()
                subprocess.run(['ffmpeg', '-i', input_file, output_file], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.status_label.config(text='批量转换完成！', fg='green')
            self.update_file_info(output_file)
            tk.messagebox.showinfo("成功", f"成功转换了 {total_files} 个文件！")
        except subprocess.CalledProcessError as e:
            self.status_label.config(text='批量转换失败', fg='red')
            tk.messagebox.showerror("错误", f"批量转换失败: {str(e)}")

    def convert_video(self):
        input_file = self.input_file.get()
        output_format = self.output_format.get()
        if not output_format:
            tk.messagebox.showerror("错误", "请先指定输出格式！")
            return
        output_file = input_file.rsplit('.', 1)[0] + '.' + output_format
        if os.path.exists(output_file):
            tk.messagebox.showerror("错误", f"检测到同名文件 {output_file}，转换已终止！")
            self.status_label.config(text='转换终止', fg='red')
            return
        try:
            cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_file]
            duration = float(subprocess.check_output(cmd).decode().strip())
            self.progress['value'] = 0
            self.status_label.config(text='转换中...', fg='orange')
            self.progress.update()
            self.start_time = time.time()
            process = subprocess.Popen(['ffmpeg', '-i', input_file, output_file], stderr=subprocess.PIPE, encoding='utf-8')
            while True:
                output = process.stderr.readline().strip()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    time_match = re.search(r'time=(\d{2}):(\d{2}):(\d{2}).(\d{2})', output)
                    if time_match:
                        hours, minutes, seconds, milliseconds = map(int, time_match.groups())
                        total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 100
                        progress_value = min(total_seconds / duration * 100, 100)
                        self.progress['value'] = progress_value
                        self.status_label.config(text=f'转换中... {int(progress_value)}%')
                        self.progress.update()
                        self.root.update()
            process.wait()
            self.end_time = time.time()
            self.conversion_time = self.end_time - self.start_time
            self.status_label.config(text='转换完成！', fg='green')
            self.update_file_info(output_file)
            tk.messagebox.showinfo("成功", "视频转换完成！")
        except subprocess.CalledProcessError as e:
            self.status_label.config(text='转换失败', fg='red')
            tk.messagebox.showerror("错误", f"转换失败: {str(e)}")

    def update_file_info(self, output_file):
        input_file = self.input_file.get()
        self.original_info.delete(1.0, tk.END)
        if not input_file or not os.path.exists(input_file):
            self.original_info.insert(tk.END, "转化前文件信息：文件不存在或未选择\n")
            return
        self.original_info.insert(tk.END, "转化前文件信息如下：\n")
        self.original_info.insert(tk.END, f"文件名: {os.path.basename(input_file)}\n")
        self.original_info.insert(tk.END, f"文件大小: {os.path.getsize(input_file) / 1024:.2f} KB\n")
        try:
            cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_file]
            duration = float(subprocess.check_output(cmd).decode().strip())
            hours = int(duration // 3600)
            minutes = int((duration % 3600) // 60)
            seconds = int(duration % 60)
            self.original_info.insert(tk.END, f"文件时长: {hours:02d}:{minutes:02d}:{seconds:02d}\n")
        except:
            self.original_info.insert(tk.END, "文件时长: 无法获取\n")
        self.original_info.insert(tk.END, f"文件格式: {input_file.split('.')[-1]}\n")
        try:
            cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_file]
            duration = float(subprocess.check_output(cmd).decode().strip())
            hours = int(duration // 3600)
            minutes = int((duration % 3600) // 60)
            seconds = int(duration % 60)
        except:
            self.original_info.insert(tk.END, "文件时长: 无法获取\n")
        self.converted_info.delete(1.0, tk.END)
        if os.path.exists(output_file) and self.status_label.cget('text') == '转换完成！':
            self.converted_info.insert(tk.END, f"转化后文件信息如下:\n")
            self.converted_info.insert(tk.END, f"文件名: {os.path.basename(output_file)}\n")
            self.converted_info.insert(tk.END, f"文件大小: {os.path.getsize(output_file) / 1024:.2f} KB\n")
            self.converted_info.insert(tk.END, f"文件格式: {output_file.split('.')[-1]}\n")
            self.converted_info.insert(tk.END, f"转换耗时: {self.conversion_time:.2f} 秒\n")
        else:
            self.converted_info.insert(tk.END, "无法读取，文件未生成")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoConverter(root)
    root.mainloop()
