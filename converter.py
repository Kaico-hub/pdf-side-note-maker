from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import RectangleObject
from reportlab.pdfgen import canvas
from reportlab.lib.colors import lightgrey
import io


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


