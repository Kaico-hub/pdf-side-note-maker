from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import RectangleObject
from reportlab.pdfgen import canvas
from reportlab.lib.colors import lightgrey
import io
import os


def create_note_background(width, height, note_x, ruled=True):
    """
    右側ノート欄の背景PDFを1ページ分作る
    width, height: 変換後ページ全体のサイズ
    note_x: ノート欄の開始位置
    ruled: 横罫線を入れるか
    """
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(width, height))

    # PDF本文とノート欄の境界線
    c.setStrokeColor(lightgrey)
    c.setLineWidth(1)
    c.line(note_x, 0, note_x, height)

    if ruled:
        c.setStrokeColor(lightgrey)
        c.setLineWidth(0.5)

        line_spacing = 24
        margin_top = 36
        margin_bottom = 36
        margin_right = 24
        margin_left = 24

        y = height - margin_top
        while y > margin_bottom:
            c.line(note_x + margin_left, y, width - margin_right, y)
            y -= line_spacing

    c.save()
    packet.seek(0)
    return PdfReader(packet).pages[0]


def add_note_area(input_pdf, output_pdf, note_ratio=1.0, ruled=True):
    """
    input_pdf: 元PDF
    output_pdf: 出力PDF
    note_ratio: ノート欄の幅。元PDF幅に対する倍率
                1.0なら、右側に元PDFと同じ幅のメモ欄を追加
    ruled: Trueなら罫線あり、Falseなら無地
    """
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for page in reader.pages:
        original_width = float(page.mediabox.width)
        original_height = float(page.mediabox.height)

        note_width = original_width * note_ratio
        new_width = original_width + note_width
        new_height = original_height

        background = create_note_background(
            width=new_width,
            height=new_height,
            note_x=original_width,
            ruled=ruled
        )

        page.add_transformation(Transformation().translate(tx=0, ty=0))
        background.merge_page(page)

        background.mediabox = RectangleObject([0, 0, new_width, new_height])
        background.cropbox = RectangleObject([0, 0, new_width, new_height])

        writer.add_page(background)

    with open(output_pdf, "wb") as f:
        writer.write(f)


def ask_input_pdf():
    while True:
        input_pdf = input("入力PDFファイル名を入力してください: ").strip().strip('"')

        if not input_pdf:
            print("ファイル名が空です。もう一度入力してください。")
            continue

        if not os.path.exists(input_pdf):
            print(f"ファイルが見つかりません: {input_pdf}")
            continue

        if not input_pdf.lower().endswith(".pdf"):
            print("PDFファイルを指定してください。")
            continue

        return input_pdf


def ask_output_pdf(input_pdf):
    default_name = os.path.splitext(input_pdf)[0] + "_with_notes.pdf"

    output_pdf = input(f"出力PDFファイル名を入力してください [{default_name}]: ").strip().strip('"')

    if not output_pdf:
        output_pdf = default_name

    if not output_pdf.lower().endswith(".pdf"):
        output_pdf += ".pdf"

    return output_pdf


def ask_note_ratio():
    while True:
        value = input("ノート欄の比率を入力してください [1.0]: ").strip()

        if not value:
            return 1.0

        try:
            note_ratio = float(value)
        except ValueError:
            print("数値を入力してください。例: 1.0")
            continue

        if note_ratio <= 0:
            print("0より大きい数値を入力してください。")
            continue

        return note_ratio


if __name__ == "__main__":
    input_pdf = ask_input_pdf()
    output_pdf = ask_output_pdf(input_pdf)
    note_ratio = ask_note_ratio()

    print()
    print("変換を開始します。")
    print(f"入力PDF: {input_pdf}")
    print(f"出力PDF: {output_pdf}")
    print(f"ノート欄の比率: {note_ratio}")
    print()

    add_note_area(
        input_pdf=input_pdf,
        output_pdf=output_pdf,
        note_ratio=note_ratio,
        ruled=True
    )

    print("完了しました。")