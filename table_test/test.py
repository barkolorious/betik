from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, Image
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont

from PIL import Image as PILImg

pdfmetrics.registerFont(TTFont('Times', 'times.ttf'))
pdfmetrics.registerFont(TTFont('TimesBd', 'timesbd.ttf'))
pdfmetrics.registerFont(TTFont('TimesIt', 'timesi.ttf'))
pdfmetrics.registerFont(TTFont('TimesBI', 'timesbi.ttf'))
registerFontFamily('Times', normal='Times', bold='TimesBd', italic='TimesIt', boldItalic='TimesBI')

stiller = {
  'Paragraf':    ParagraphStyle(name='metin',  fontName='Times',   fontSize=12, leading=12, leftIndent=0,      rightIndent=0, firstLineIndent=inch/2, alignment=TA_JUSTIFY, uriWasteReduce=0.3, allowWidows=0, spaceAfter=inch/16, spaceBefore=inch/16),
  'Metin':       ParagraphStyle(name='metin',  fontName='Times',   fontSize=12, leading=12, leftIndent=0,      rightIndent=0, firstLineIndent=0,      alignment=TA_LEFT,    uriWasteReduce=0.3, allowWidows=0, spaceAfter=0, spaceBefore=0),
  'OrtaliMetin': ParagraphStyle(name='metin',  fontName='Times',   fontSize=12, leading=12, leftIndent=0,      rightIndent=0, firstLineIndent=0,      alignment=TA_CENTER,  uriWasteReduce=0.3, allowWidows=0, spaceAfter=0, spaceBefore=0),
  'Baslik':      ParagraphStyle(name='baslik', fontName='TimesBd', fontSize=12, leading=18, leftIndent=inch/4, rightIndent=0, firstLineIndent=0,      alignment=TA_LEFT,    uriWasteReduce=0.3, allowWidows=0, spaceAfter=inch/16, spaceBefore=inch/16),
  'KalinMetin':  ParagraphStyle(name='metin',  fontName='TimesBd', fontSize=12, leading=12, leftIndent=0,      rightIndent=0, firstLineIndent=0,      alignment=TA_LEFT,    uriWasteReduce=0.3, allowWidows=0, spaceAfter=0, spaceBefore=0),
  'ItalikMetin': ParagraphStyle(name='metin',  fontName='TimesIt', fontSize=12, leading=12, leftIndent=0,      rightIndent=0, firstLineIndent=0,      alignment=TA_LEFT,    uriWasteReduce=0.3, allowWidows=0, spaceAfter=0, spaceBefore=0),
}

page_width, page_height = A4
page_margin = 2.5 * cm
avaliable_width = page_width - 2 * page_margin
avaliable_height = page_height - 2 * page_margin
bosluk = Spacer(width=page_width, height=inch/8)

sample_text = "Buradaki $(n-k)!$'i sanki seçmediğimiz <b>aaa</b> <i>iiii</i> <b><i>aaaaa</i></b> elemanların farklı sıralamalarını eliyormuş gibi düşünebiliriz \\[a^2 + b^2 = c^2\\] <b>Görsel <seq template=\"%(FigureNo+)s\"/></b> <i>Multi-level templates</i> this is a bullet point.  Spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam , öçşığüÖÇŞİĞÜ"

tablo=[[Paragraph(text="Ödül", style=stiller['OrtaliMetin']),          Paragraph(text="Fonksiyon", style=stiller['OrtaliMetin'])],
       [Paragraph(text="Kohezyon",               style=stiller['Metin']), Paragraph(text="R = -\\gamma_1 \\cdot \\max ...", style=stiller['Metin'])],
       [Paragraph(text="Çarpışma Miktarı",       style=stiller['Metin']), Paragraph(text="R = -\\gamma_1 \\cdot \\max ...", style=stiller['Metin'])],
       [Paragraph(text="Harcanan Toplam Enerji", style=stiller['Metin']), Paragraph(text="R = -\\gamma_1 \\cdot \\max ...", style=stiller['Metin'])]]
T_tablo=Table(tablo,style=[('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                           ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                           ('LINEABOVE', (0,  0), (-1,  0), 1, 'black'),
                           ('LINEBELOW', (0,  0), (-1,  0), 1, 'black'),
                           ('LINEBELOW', (0, -1), (-1, -1), 1, 'black')], spaceAfter=0, spaceBefore=0)
P_tablo_metin=Paragraph(text="bişiler işte", style=stiller['ItalikMetin'])
P_tablo_baslik=Paragraph(text="Tablo <seq template=\"%(TableNo+)s\"/>", style=stiller['KalinMetin'])
tablo_tum=[[P_tablo_baslik], [P_tablo_metin], [T_tablo]]
T_tablo_tum=Table(tablo_tum,style=[('ALIGN', (0, 0), (-1, -1), 'CENTER'),('BOTTOMPADDING', (0, 0), (0, 0), 0)], spaceAfter=inch/16, spaceBefore=inch/16)

story = []

story.append(T_tablo)
story.append(Paragraph(sample_text, style=stiller['Paragraf']))
story.append(T_tablo_tum)
story.append(Paragraph(sample_text, style=stiller['Paragraf']))
story.append(Paragraph(sample_text, style=stiller['Paragraf']))
story.append(Paragraph(sample_text, style=stiller['Paragraf']))
story.append(Paragraph(sample_text, style=stiller['Paragraf']))

doc = SimpleDocTemplate('doc.pdf', pagesize=A4, leftMargin=page_margin, rightMargin=page_margin, topMargin=page_margin, bottomMargin=page_margin, allowSplitting=1)
doc.build(story)

print("Saved to doc.pdf")