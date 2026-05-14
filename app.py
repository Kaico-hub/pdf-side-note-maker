import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from converter import add_note_area


class PdfNoteMarginApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("PDF Note Margin Maker")
        self.geometry("680x360")
        self.minsize(620, 340)

        self.input_pdf = tk.StringVar()
        self.output_pdf = tk.StringVar()
        self.note_ratio = tk.StringVar(value="1.0")
        self.ruled = tk.BooleanVar(value=True)
        self.status = tk.StringVar(value="")

        self._build_ui()

    def _build_ui(self):
        root = ttk.Frame(self, padding=16)
        root.pack(fill=tk.BOTH, expand=True)

        root.columnconfigure(1, weight=1)

        ttk.Label(root, text="入力PDF").grid(row=0, column=0, sticky=tk.W, pady=6)
        ttk.Entry(root, textvariable=self.input_pdf).grid(row=0, column=1, sticky=tk.EW, padx=8)
        ttk.Button(root, text="選択", command=self.choose_input_pdf).grid(row=0, column=2, sticky=tk.E)

        ttk.Label(root, text="出力PDF").grid(row=1, column=0, sticky=tk.W, pady=6)
        ttk.Entry(root, textvariable=self.output_pdf).grid(row=1, column=1, sticky=tk.EW, padx=8)
        ttk.Button(root, text="保存先", command=self.choose_output_pdf).grid(row=1, column=2, sticky=tk.E)

        ttk.Label(root, text="ノート欄の比率").grid(row=2, column=0, sticky=tk.W, pady=6)
        ratio_frame = ttk.Frame(root)
        ratio_frame.grid(row=2, column=1, sticky=tk.W, padx=8)
        ttk.Entry(ratio_frame, textvariable=self.note_ratio, width=10).pack(side=tk.LEFT)
        ttk.Label(ratio_frame, text="例: 0.5 / 1.0 / 1.2").pack(side=tk.LEFT, padx=(12, 0))

        ttk.Label(
            root,
            text="元PDFの横幅に対する割合です。0.5=半分、1.0=同じ幅、1.2=少し広め",
        ).grid(
            row=3,
            column=1,
            columnspan=2,
            sticky=tk.W,
            padx=8,
            pady=(0, 6),
        )

        ttk.Checkbutton(
            root,
            text="ノート欄に横罫線を入れる",
            variable=self.ruled,
        ).grid(row=4, column=1, sticky=tk.W, padx=8, pady=6)

        cat_art = "（＞ω＜）"
        ttk.Label(root, text=cat_art, font=("MS Gothic", 12), justify=tk.CENTER).grid(
            row=4,
            column=2,
            rowspan=2,
            sticky=tk.E,
            padx=(8, 0),
            pady=(0, 6),
        )

        self.run_button = ttk.Button(root, text="変換開始", command=self.start_conversion)
        self.run_button.grid(row=5, column=1, sticky=tk.W, padx=8, pady=(16, 6))

        ttk.Label(root, textvariable=self.status, wraplength=560).grid(
            row=6,
            column=0,
            columnspan=3,
            sticky=tk.W,
            pady=(12, 0),
        )

    def choose_input_pdf(self):
        path = filedialog.askopenfilename(
            title="入力PDFを選択",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        )
        if not path:
            return

        self.input_pdf.set(path)
        if not self.output_pdf.get():
            base, _ = os.path.splitext(path)
            self.output_pdf.set(base + "_with_notes.pdf")
        self.status.set("")

    def choose_output_pdf(self):
        initial = self.output_pdf.get()
        path = filedialog.asksaveasfilename(
            title="出力PDFの保存先を選択",
            defaultextension=".pdf",
            initialfile=os.path.basename(initial) if initial else "",
            initialdir=os.path.dirname(initial) if initial else "",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        )
        if path:
            self.output_pdf.set(path)

    def start_conversion(self):
        try:
            input_pdf, output_pdf, note_ratio = self.validate_inputs()
        except ValueError as exc:
            messagebox.showerror("入力エラー", str(exc))
            return

        self.run_button.config(state=tk.DISABLED)
        self.status.set("変換中です。PDFが大きい場合は少し時間がかかります。")

        thread = threading.Thread(
            target=self.convert_pdf,
            args=(input_pdf, output_pdf, note_ratio, self.ruled.get()),
            daemon=True,
        )
        thread.start()

    def validate_inputs(self):
        input_pdf = self.input_pdf.get().strip()
        output_pdf = self.output_pdf.get().strip()

        if not input_pdf:
            raise ValueError("入力PDFを選択してください。")

        if not os.path.exists(input_pdf):
            raise ValueError("入力PDFが見つかりません。")

        if not input_pdf.lower().endswith(".pdf"):
            raise ValueError("入力PDFにはPDFファイルを指定してください。")

        if not output_pdf:
            raise ValueError("出力PDFの保存先を指定してください。")

        if not output_pdf.lower().endswith(".pdf"):
            output_pdf += ".pdf"
            self.output_pdf.set(output_pdf)

        try:
            note_ratio = float(self.note_ratio.get())
        except ValueError as exc:
            raise ValueError("ノート欄の比率は数値で入力してください。") from exc

        if note_ratio <= 0:
            raise ValueError("ノート欄の比率は0より大きい数値にしてください。")

        return input_pdf, output_pdf, note_ratio

    def convert_pdf(self, input_pdf, output_pdf, note_ratio, ruled):
        try:
            add_note_area(
                input_pdf=input_pdf,
                output_pdf=output_pdf,
                note_ratio=note_ratio,
                ruled=ruled,
            )
        except Exception as exc:
            self.after(0, self.on_conversion_failed, exc)
            return

        self.after(0, self.on_conversion_finished, output_pdf)

    def on_conversion_finished(self, output_pdf):
        self.run_button.config(state=tk.NORMAL)
        self.status.set(f"完了しました: {output_pdf}")
        messagebox.showinfo("完了", "PDFの変換が完了しました。")

    def on_conversion_failed(self, exc):
        self.run_button.config(state=tk.NORMAL)
        self.status.set("変換に失敗しました。")
        messagebox.showerror("変換エラー", str(exc))


if __name__ == "__main__":
    app = PdfNoteMarginApp()
    app.mainloop()
