from __future__ import annotations

import json
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Flowable,
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.utils import ImageReader


ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "GUIA_DE_USO.json").read_text(encoding="utf-8"))
OUT = ROOT / "output" / "pdf" / "guia-de-uso-cloud-project-pdv.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)

FONT_REG = Path(r"C:\Windows\Fonts\segoeui.ttf")
FONT_BOLD = Path(r"C:\Windows\Fonts\segoeuib.ttf")
if FONT_REG.exists() and FONT_BOLD.exists():
    pdfmetrics.registerFont(TTFont("Segoe", str(FONT_REG)))
    pdfmetrics.registerFont(TTFont("Segoe-Bold", str(FONT_BOLD)))
    FONT, BOLD = "Segoe", "Segoe-Bold"
else:
    FONT, BOLD = "Helvetica", "Helvetica-Bold"

NAVY = colors.HexColor("#0B2340")
BLUE = colors.HexColor("#1675C5")
CYAN = colors.HexColor("#20C3DF")
INK = colors.HexColor("#172B43")
MUTED = colors.HexColor("#60758E")
LINE = colors.HexColor("#CBD8E7")
PALE = colors.HexColor("#F2F7FB")
GOLD = colors.HexColor("#E8B85E")


def styles():
    base = getSampleStyleSheet()
    base.add(ParagraphStyle(
        name="TitleBrand", fontName=BOLD, fontSize=23, leading=28,
        textColor=INK, spaceAfter=6,
    ))
    base.add(ParagraphStyle(
        name="IntroBrand", fontName=FONT, fontSize=9.3, leading=14,
        textColor=MUTED, spaceAfter=9,
    ))
    base.add(ParagraphStyle(
        name="SectionBrand", fontName=BOLD, fontSize=8, leading=10,
        textColor=BLUE, tracking=1.1, spaceAfter=4,
    ))
    base.add(ParagraphStyle(
        name="BodyBrand", fontName=FONT, fontSize=8.8, leading=13,
        textColor=INK, spaceAfter=5,
    ))
    base.add(ParagraphStyle(
        name="StepBrand", fontName=FONT, fontSize=8.3, leading=12,
        textColor=INK, leftIndent=0, spaceAfter=5,
    ))
    base.add(ParagraphStyle(
        name="CalloutBrand", fontName=FONT, fontSize=8, leading=11,
        textColor=INK, borderColor=LINE, borderWidth=.6, borderRadius=6,
        borderPadding=8, backColor=PALE, spaceBefore=4, spaceAfter=5,
    ))
    base.add(ParagraphStyle(
        name="WarningBrand", fontName=FONT, fontSize=8, leading=11,
        textColor=colors.HexColor("#624D18"), borderColor=colors.HexColor("#E7D79E"),
        borderWidth=.6, borderRadius=6, borderPadding=8,
        backColor=colors.HexColor("#FFFBF0"), spaceBefore=3, spaceAfter=6,
    ))
    base.add(ParagraphStyle(
        name="CaptionBrand", fontName=FONT, fontSize=7, leading=9,
        textColor=MUTED, alignment=TA_CENTER, spaceBefore=4, spaceAfter=2,
    ))
    base.add(ParagraphStyle(
        name="TOCBrand", fontName=FONT, fontSize=7.4, leading=9.3,
        textColor=INK,
    ))
    base.add(ParagraphStyle(
        name="TOCSection", fontName=BOLD, fontSize=6.6, leading=8.5,
        textColor=BLUE,
    ))
    return base


class FlowDiagram(Flowable):
    def __init__(self, labels, width=510, height=60):
        super().__init__()
        self.labels = labels
        self.width = width
        self.height = height

    def draw(self):
        c = self.canv
        gap = 8
        n = max(1, len(self.labels))
        box_w = (self.width - gap * (n - 1)) / n
        for i, label in enumerate(self.labels):
            x = i * (box_w + gap)
            c.setFillColor(colors.HexColor("#F1F7FB"))
            c.setStrokeColor(colors.HexColor("#C9DCEC"))
            c.roundRect(x, 6, box_w, self.height - 12, 7, fill=1, stroke=1)
            c.setFillColor(BLUE if i % 2 == 0 else NAVY)
            c.circle(x + 13, self.height / 2, 7, fill=1, stroke=0)
            c.setFillColor(colors.white)
            c.setFont(BOLD, 6.2)
            c.drawCentredString(x + 13, self.height / 2 - 2.2, str(i + 1))
            c.setFillColor(INK)
            c.setFont(BOLD, 6.5)
            words = label.split()
            rows, row = [], ""
            max_chars = max(11, int((box_w - 29) / 3.3))
            for word in words:
                trial = (row + " " + word).strip()
                if len(trial) > max_chars and row:
                    rows.append(row)
                    row = word
                else:
                    row = trial
            if row:
                rows.append(row)
            rows = rows[:3]
            start_y = self.height / 2 + (len(rows) - 1) * 4
            for j, text in enumerate(rows):
                c.drawString(x + 25, start_y - j * 9 - 2, text)
            if i < n - 1:
                c.setFillColor(CYAN)
                c.setFont(BOLD, 11)
                c.drawCentredString(x + box_w + gap / 2, self.height / 2 - 3, "›")


def fit_image(path: Path, max_w: float, max_h: float) -> Image:
    img = Image(str(path))
    scale = min(max_w / img.imageWidth, max_h / img.imageHeight, 1.0)
    img.drawWidth = img.imageWidth * scale
    img.drawHeight = img.imageHeight * scale
    img.hAlign = "CENTER"
    return img


def page_chrome(canvas, doc):
    canvas.saveState()
    page_w, page_h = A4
    canvas.setFillColor(colors.HexColor("#E5EDF5"))
    canvas.rect(0, 0, page_w, page_h, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.rect(0, 0, page_w, page_h - 20, fill=1, stroke=0)
    logo = ROOT / "assets" / "brand" / "cloud-project-pdv-mark.png"
    canvas.drawImage(ImageReader(str(logo)), 42, page_h - 44, width=22, height=22, preserveAspectRatio=True, mask="auto", anchor="c")
    canvas.setFillColor(NAVY)
    canvas.setFont(BOLD, 7.6)
    canvas.drawString(70, page_h - 31, "CLOUD PROJECT PDV")
    canvas.setFillColor(MUTED)
    canvas.setFont(FONT, 7)
    canvas.drawRightString(page_w - 42, page_h - 31, f"MANUAL DO SISTEMA  ·  V{DATA['version']}")
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(.6)
    canvas.line(42, page_h - 53, page_w - 42, page_h - 53)
    canvas.line(42, 40, page_w - 42, 40)
    canvas.setFillColor(MUTED)
    canvas.setFont(FONT, 6.8)
    canvas.drawString(42, 27, "Guia de referência · Revisto em 15/10/2026")
    canvas.drawRightString(page_w - 42, 27, f"{doc.page:02d}")
    canvas.restoreState()


def first_page(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, w, h, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#10375D"))
    canvas.circle(w + 35, h - 30, 245, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#0D2D4D"))
    canvas.circle(w + 15, h - 17, 195, fill=1, stroke=0)
    canvas.setStrokeColor(colors.Color(.23, .69, .82, alpha=.28))
    canvas.setLineWidth(1)
    canvas.circle(w - 32, h - 24, 165, fill=0, stroke=1)
    canvas.circle(w - 32, h - 24, 142, fill=0, stroke=1)

    logo = ROOT / "assets" / "brand" / "cloud-project-pdv-mark.png"
    canvas.setFillColor(colors.white)
    canvas.roundRect(44, h - 131, 68, 68, 15, fill=1, stroke=0)
    canvas.drawImage(ImageReader(str(logo)), 50, h - 125, width=56, height=56, preserveAspectRatio=True, mask="auto", anchor="c")
    canvas.setFillColor(colors.white)
    canvas.setFont(BOLD, 13)
    canvas.drawString(126, h - 84, "CLOUD PROJECT PDV")
    canvas.setFillColor(colors.HexColor("#A9C3D9"))
    canvas.setFont(FONT, 7)
    canvas.drawString(126, h - 101, "GESTÃO COMERCIAL INTEGRADA")
    canvas.setFillColor(CYAN)
    canvas.setFont(BOLD, 7)
    canvas.drawString(46, h - 186, "MANUAL COMPLETO · VERSÃO DOCUMENTADA 0.1.47")
    canvas.setFillColor(colors.white)
    canvas.setFont(BOLD, 31)
    canvas.drawString(44, h - 234, "Guia de uso")
    canvas.drawString(44, h - 272, "completo e ilustrado")
    canvas.setFillColor(colors.HexColor("#C1D3E2"))
    canvas.setFont(FONT, 10)
    canvas.drawString(46, h - 302, "Do primeiro acesso às rotinas diárias do seu negócio.")

    x, y, iw, ih = 44, 270, w - 88, 242
    canvas.setFillColor(colors.Color(0, 0, 0, alpha=.26))
    canvas.roundRect(x - 4, y - 4, iw + 8, ih + 8, 12, fill=1, stroke=0)
    screen = ROOT / "assets" / "screenshots" / "dashboard.png"
    reader = ImageReader(str(screen))
    sw, sh = reader.getSize()
    scale = min(iw / sw, ih / sh)
    rw, rh = sw * scale, sh * scale
    canvas.setFillColor(colors.white)
    canvas.roundRect(x, y, iw, ih, 8, fill=1, stroke=0)
    canvas.saveState()
    clip = canvas.beginPath()
    clip.roundRect(x, y, iw, ih, 8)
    canvas.clipPath(clip, stroke=0)
    canvas.drawImage(reader, x + (iw - rw) / 2, y + (ih - rh) / 2, width=rw, height=rh, preserveAspectRatio=True, mask="auto")
    canvas.restoreState()
    canvas.setFillColor(CYAN)
    canvas.roundRect(46, y - 21, 134, 19, 9, fill=1, stroke=0)
    canvas.setFillColor(NAVY)
    canvas.setFont(BOLD, 6.5)
    canvas.drawCentredString(113, y - 15, "CAPTURA REAL DO SISTEMA")

    canvas.setFillColor(colors.HexColor("#E7F4FB"))
    canvas.setFont(BOLD, 8)
    canvas.drawString(46, 220, "UM GUIA PARA CADA ETAPA")
    steps = ["Preparar", "Cadastrar", "Operar", "Acompanhar", "Proteger"]
    sx = 46
    for i, label in enumerate(steps):
        bw = 83 if i == 3 else 75
        canvas.setStrokeColor(colors.Color(.65, .79, .91, alpha=.6))
        canvas.setFillColor(colors.Color(.07, .20, .34, alpha=.55))
        canvas.roundRect(sx, 182, bw, 24, 6, fill=1, stroke=1)
        canvas.setFillColor(colors.white)
        canvas.setFont(BOLD, 7)
        canvas.drawCentredString(sx + bw / 2, 191, label)
        sx += bw + 8
        if i < len(steps) - 1:
            canvas.setFillColor(CYAN)
            canvas.setFont(BOLD, 10)
            canvas.drawCentredString(sx - 4, 190, "›")
    canvas.setStrokeColor(colors.Color(.57, .73, .86, alpha=.3))
    canvas.line(44, 74, w - 44, 74)
    canvas.setFillColor(colors.HexColor("#A9C3D9"))
    canvas.setFont(FONT, 7)
    canvas.drawString(46, 56, "18 CAPÍTULOS  ·  TELAS REAIS  ·  FLUXOS E RESULTADOS ESPERADOS")
    canvas.drawRightString(w - 46, 56, "REVISADO EM 15/10/2026")
    canvas.restoreState()


def main():
    st = styles()
    page_w, page_h = A4
    doc = SimpleDocTemplate(
        str(OUT), pagesize=A4, rightMargin=42, leftMargin=42,
        topMargin=66, bottomMargin=52, title="Manual completo ilustrado - Cloud Project PDV",
        author="Cloud Project PDV", subject="Manual de uso do sistema",
    )
    story = [Spacer(1, 1), PageBreak()]

    story += [
        Paragraph("NAVEGAÇÃO", st["SectionBrand"]),
        Paragraph("Índice do guia", st["TitleBrand"]),
        Paragraph("Encontre o módulo e siga cada rotina sem pular conferências importantes.", st["IntroBrand"]),
    ]
    rows = []
    chapters = DATA["chapters"]
    for i in range(0, len(chapters), 2):
        row = []
        for j in (i, i + 1):
            if j < len(chapters):
                c = chapters[j]
                row.extend([
                    Paragraph(f"<b>{j + 1:02d}</b>", st["TOCSection"]),
                    Paragraph(f"<font color='#1675C5'><b>{escape(c['section'])}</b></font><br/>{escape(c['title'])}", st["TOCBrand"]),
                ])
            else:
                row.extend(["", ""])
        rows.append(row)
    toc = Table(rows, colWidths=[22, 230, 22, 237], hAlign="LEFT")
    toc.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("LINEBELOW", (0, 0), (-1, -1), .4, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story += [toc, Spacer(1, 15), Paragraph(
        "Versão de referência: 0.1.47. Menus podem variar conforme licença, permissões e configuração do terminal.",
        st["CalloutBrand"]), PageBreak()]

    story += [
        Paragraph("A JORNADA NO SISTEMA", st["SectionBrand"]),
        Paragraph("Do primeiro acesso ao fechamento", st["TitleBrand"]),
        Paragraph("O trabalho avança por etapas. Cada módulo recebe informações do anterior e ajuda a manter os dados consistentes.", st["IntroBrand"]),
        FlowDiagram(["Preparar conta e banco", "Cadastrar dados", "Registrar compras", "Vender e atender", "Acompanhar e proteger"], width=511, height=72),
        Spacer(1, 12),
        Paragraph("Antes de operar", st["Heading2"]),
        Paragraph("Confirme que o banco está conectado e estruturado, revise usuários e permissões, configure impressoras e mantenha um backup verificável. Se a tela indicar recuperação necessária, use Backups e restauração e confira o estado final.", st["BodyBrand"]),
        Paragraph("Como ler os capítulos", st["Heading2"]),
        Paragraph("Cada módulo apresenta o caminho, os passos, o resultado esperado e um ponto de atenção. As capturas marcadas como Interface real são imagens do programa; os diagramas mostram a sequência do processo.", st["BodyBrand"]),
        Paragraph("Recursos em implantação", st["Heading2"]),
        Paragraph("O Editor SQL aparece no guia para explicar sua localização e seu estado. Ele está identificado como EM IMPLANTAÇÃO e não deve ser tratado como disponível para uso operacional.", st["WarningBrand"]),
        PageBreak(),
    ]

    for i, c in enumerate(chapters, 1):
        story.append(Paragraph(f"{i:02d}  ·  {escape(c['section'])}", st["SectionBrand"]))
        story.append(Paragraph(escape(c["title"]), st["TitleBrand"]))
        if c.get("status"):
            story.append(Paragraph(f"<b>{escape(c['status'])}</b>", st["WarningBrand"]))
        story.append(Paragraph(escape(c["intro"]), st["IntroBrand"]))
        story.append(Paragraph("PASSO A PASSO", st["SectionBrand"]))
        for n, step in enumerate(c["steps"], 1):
            story.append(Paragraph(f"<font color='#1675C5'><b>{n:02d}</b></font>  {escape(step)}", st["StepBrand"]))
        story.append(Paragraph(f"<b>Resultado esperado:</b> {escape(c['result'])}", st["CalloutBrand"]))
        story.append(Paragraph(f"<b>Atenção:</b> {escape(c['attention'])}", st["WarningBrand"]))
        if c.get("screenshot"):
            asset = ROOT / c["screenshot"]
            story.append(Spacer(1, 3))
            story.append(Paragraph("INTERFACE REAL", st["SectionBrand"]))
            story.append(fit_image(asset, 505, 285))
            story.append(Paragraph(escape(c.get("screenshotCaption", "Captura real do Cloud Project PDV.")), st["CaptionBrand"]))
        else:
            story.append(Spacer(1, 4))
            story.append(Paragraph("FLUXO DO PROCESSO", st["SectionBrand"]))
            story.append(FlowDiagram(c["diagram"], width=511, height=64))
        if i < len(chapters):
            story.append(PageBreak())

    story += [
        PageBreak(),
        Paragraph("REFERÊNCIA", st["SectionBrand"]),
        Paragraph("Notas sobre as imagens e a versão", st["TitleBrand"]),
        Paragraph("As telas marcadas como Interface real vieram de capturas do Cloud Project PDV. Um aviso transitório do navegador foi retirado da captura do PDV para não cobrir a área de leitura. As imagens de fluxo são diagramas editoriais, não capturas.", st["BodyBrand"]),
        Paragraph("Este manual documenta a versão 0.1.47, revisada em 15/10/2026. Confirme nomes de menus, permissões e disponibilidade na instalação em uso. O Editor SQL permanece em implantação.", st["BodyBrand"]),
        Paragraph("Proteja a operação", st["Heading2"]),
        Paragraph("Não compartilhe senhas, códigos de ativação ou arquivos de certificado. Antes de ações que alteram estoque, vendas, contas ou banco de dados, confira os valores e as confirmações exibidos pelo sistema.", st["WarningBrand"]),
    ]

    doc.build(story, onFirstPage=first_page, onLaterPages=page_chrome)
    print(OUT)
    print(f"bytes={OUT.stat().st_size}")


if __name__ == "__main__":
    main()
