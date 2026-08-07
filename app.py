# app.py
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from formatter import format_transcript
from transcriber import LANGUAGES, MODEL_SIZES, Transcriber

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False


class App:
    def __init__(self, root):
        self.root = root
        root.title("视频转文字稿工具")
        root.geometry("560x420")

        self.file_path = None

        # 拖放区
        self.drop_label = tk.Label(
            root, text="把视频/音频文件拖到这里\n或点击下方按钮选择文件",
            bg="#e8f0fe", fg="#333333", font=("Microsoft YaHei", 12),
            relief="groove", height=5, cursor="hand2",
        )
        self.drop_label.pack(fill="both", expand=True, padx=20, pady=15)
        self.drop_label.bind("<Button-1>", lambda e: self.choose_file())
        if DND_AVAILABLE:
            self.drop_label.drop_target_register(DND_FILES)
            self.drop_label.dnd_bind("<<Drop>>", self.on_drop)
        else:
            self.drop_label.config(text="点击下方按钮选择文件")

        # 文件显示
        self.file_var = tk.StringVar(value="未选择文件")
        tk.Label(root, textvariable=self.file_var, fg="#555555",
                 font=("Microsoft YaHei", 10), wraplength=500).pack(pady=(0, 8))

        # 选项行
        opts = tk.Frame(root)
        opts.pack(pady=4)
        tk.Label(opts, text="精度:", font=("Microsoft YaHei", 10)).grid(row=0, column=0)
        self.model_var = tk.StringVar(value="高精度")
        ttk.Combobox(opts, textvariable=self.model_var, width=8,
                     values=list(MODEL_SIZES), state="readonly").grid(row=0, column=1, padx=8)
        tk.Label(opts, text="语言:", font=("Microsoft YaHei", 10)).grid(row=0, column=2)
        self.lang_var = tk.StringVar(value="中文")
        ttk.Combobox(opts, textvariable=self.lang_var, width=8,
                     values=list(LANGUAGES), state="readonly").grid(row=0, column=3, padx=8)
        ttk.Button(opts, text="选择文件", command=self.choose_file).grid(row=0, column=4, padx=8)

        # 开始按钮
        self.start_btn = ttk.Button(root, text="开始转文字", command=self.start)
        self.start_btn.pack(pady=10)

        # 进度条
        self.progress = ttk.Progressbar(root, mode="indeterminate")
        self.progress.pack(fill="x", padx=40)

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        tk.Label(root, textvariable=self.status_var, fg="#888888",
                 font=("Microsoft YaHei", 9)).pack(pady=6)

    def choose_file(self):
        path = filedialog.askopenfilename(
            title="选择视频或音频文件",
            filetypes=[("音视频文件", "*.mp4 *.mov *.mkv *.avi *.flv *.mp3 *.wav *.m4a *.aac *.flac *.ogg"), ("所有文件", "*.*")],
        )
        if path:
            self.file_path = path
            self.file_var.set(os.path.basename(path))

    def on_drop(self, event):
        raw = event.data
        # tkinterdnd2 返回的路径可能带花括号，去掉
        path = raw.strip("{}").strip()
        if os.path.isfile(path):
            self.file_path = path
            self.file_var.set(os.path.basename(path))

    def start(self):
        if not self.file_path:
            messagebox.showwarning("提示", "请先选择文件")
            return
        self.start_btn.config(state="disabled")
        self.progress.start(12)
        self.status_var.set("正在转写，请稍候…（首次运行需下载模型）")
        threading.Thread(target=self._work, daemon=True).start()

    def _work(self):
        try:
            model_size = self.model_var.get()
            language = LANGUAGES[self.lang_var.get()]
            tr = Transcriber(model_size, language)
            segments = tr.transcribe(self.file_path)
            text = format_transcript(segments)
            out_path = os.path.splitext(self.file_path)[0] + "_文字稿.txt"
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(text)
            self.root.after(0, self._done, out_path)
        except Exception as e:
            self.root.after(0, self._error, str(e))

    def _done(self, out_path):
        self.progress.stop()
        self.start_btn.config(state="normal")
        self.status_var.set("完成")
        messagebox.showinfo("完成", f"文字稿已生成：\n{out_path}")

    def _error(self, msg):
        self.progress.stop()
        self.start_btn.config(state="normal")
        self.status_var.set("出错")
        messagebox.showerror("出错", msg)


def main():
    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
