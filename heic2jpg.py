import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import pillow_heif
import os
import threading

# HEIFサポートの登録
pillow_heif.register_heif_opener()

class HeicToJpgConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("HEIC to JPG Converter Pro")
        self.root.geometry("600x450")
        
        self.files_to_convert = []
        
        self.setup_ui()

    def setup_ui(self):
        # メインフレーム
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ファイル選択セクション
        self.btn_select = tk.Button(main_frame, text="HEICファイルを選択 (複数可)", command=self.select_files, height=2)
        self.btn_select.pack(fill=tk.X, pady=5)

        self.lbl_count = tk.Label(main_frame, text="選択されたファイル: 0 件")
        self.lbl_count.pack(pady=5)

        # 設定セクション
        config_frame = tk.LabelFrame(main_frame, text="変換設定", padx=10, pady=10)
        config_frame.pack(fill=tk.X, pady=10)

        tk.Label(config_frame, text="画質 (1-100):").grid(row=0, column=0, sticky="w")
        self.quality_scale = tk.Scale(config_frame, from_=1, to=100, orient=tk.HORIZONTAL)
        self.quality_scale.set(90)
        self.quality_scale.grid(row=0, column=1, sticky="ew", padx=10)

        self.keep_exif = tk.BooleanVar(value=True)
        tk.Checkbutton(config_frame, text="EXIFデータ(位置情報など)を保持", variable=self.keep_exif).grid(row=1, column=0, columnspan=2, sticky="w")

        # 進捗状況
        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress.pack(fill=tk.X, pady=10)

        self.status_label = tk.Label(main_frame, text="待機中", fg="blue")
        self.status_label.pack(pady=5)

        # 実行ボタン
        self.btn_convert = tk.Button(main_frame, text="変換を開始", command=self.start_conversion_thread, bg="#4CAF50", fg="white", height=2, state=tk.DISABLED)
        self.btn_convert.pack(fill=tk.X, pady=10)

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="HEICファイルを選択",
            filetypes=[("HEIC files", "*.heic"), ("All files", "*.*")]
        )
        if files:
            self.files_to_convert = list(files)
            self.lbl_count.config(text=f"選択されたファイル: {len(self.files_to_convert)} 件")
            self.btn_convert.config(state=tk.NORMAL)
            self.status_label.config(text="変換の準備ができました", fg="black")

    def start_conversion_thread(self):
        # 変換中にUIをフリーズさせないためにスレッドを使用
        threading.Thread(target=self.convert_files, daemon=True).start()

    def convert_files(self):
        if not self.files_to_convert:
            return

        # 保存先フォルダの選択
        save_dir = filedialog.askdirectory(title="保存先フォルダを選択")
        if not save_dir:
            return

        self.btn_convert.config(state=tk.DISABLED)
        self.btn_select.config(state=tk.DISABLED)
        
        total = len(self.files_to_convert)
        self.progress["maximum"] = total
        
        success_count = 0
        error_count = 0

        for i, file_path in enumerate(self.files_to_convert):
            try:
                self.status_label.config(text=f"変換中: {os.path.basename(file_path)}")
                
                image = Image.open(file_path)
                
                # ファイル名の生成
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                target_path = os.path.join(save_dir, f"{base_name}.jpg")

                # 変換実行
                exif = image.info.get("exif") if self.keep_exif.get() else None
                
                if exif:
                    image.save(target_path, "JPEG", quality=self.quality_scale.get(), exif=exif)
                else:
                    image.save(target_path, "JPEG", quality=self.quality_scale.get())
                
                success_count += 1
            except Exception as e:
                print(f"Error converting {file_path}: {e}")
                error_count += 1
            
            self.progress["value"] = i + 1
            self.root.update_idletasks()

        # 完了後のリセット処理
        self.status_label.config(text=f"完了! 成功: {success_count}件 / 失敗: {error_count}件", fg="green")
        messagebox.showinfo("完了", f"すべての処理が終わりました。\n成功: {success_count}件\n失敗: {error_count}件")
        
        # 次の変換のためにUIを有効化（リストはクリアしない）
        self.btn_convert.config(state=tk.NORMAL)
        self.btn_select.config(state=tk.NORMAL)
        self.progress["value"] = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = HeicToJpgConverter(root)
    root.mainloop()