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
  'Paragraf':      ParagraphStyle(name='paragraf', fontName='Times',   fontSize=12, leading=12, leftIndent=0,      rightIndent=0, firstLineIndent=inch/4, alignment=TA_JUSTIFY, uriWasteReduce=0.3, allowWidows=0),
  'Metin':         ParagraphStyle(name='metin',    fontName='Times',   fontSize=12, leading=12, leftIndent=0,      rightIndent=0, firstLineIndent=0,      alignment=TA_LEFT,    uriWasteReduce=0.3, allowWidows=0),
  'GorselMetin':   ParagraphStyle(name='metin',    fontName='Times',   fontSize=12, leading=12, leftIndent=0,      rightIndent=0, firstLineIndent=0,      alignment=TA_CENTER,  uriWasteReduce=0.3, allowWidows=0),
  'KalinMetin':    ParagraphStyle(name='metin',    fontName='TimesBd', fontSize=12, leading=18, leftIndent=0,      rightIndent=0, firstLineIndent=0,      alignment=TA_LEFT,    uriWasteReduce=0.3, allowWidows=0),
  'Baslik':        ParagraphStyle(name='baslik',   fontName='TimesBd', fontSize=12, leading=18, leftIndent=inch/4, rightIndent=0, firstLineIndent=0,      alignment=TA_LEFT)
}

page_width, page_height = A4
page_margin = 2.5 * cm
avaliable_width = page_width - 2 * page_margin
avaliable_height = page_height - 2 * page_margin
bosluk = Spacer(width=page_width, height=inch/8)

sample_text = "Buradaki $(n-k)!$'i sanki seçmediğimiz <b>aaa</b> <i>iiii</i> <b><i>aaaaa</i></b> elemanların farklı sıralamalarını eliyormuş gibi düşünebiliriz \\[a^2 + b^2 = c^2\\] <b>Görsel <seq template=\"%(FigureNo+)s\"/></b> <i>Multi-level templates</i> this is a bullet point.  Spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam , öçşığüÖÇŞİĞÜ"

image_path = "img1.png"
with PILImg.open(image_path) as img:
  img_width, img_height = img.size
  if img_width > img_height:
    resized_width = avaliable_width * .5
    resized_height = img_height / img_width * resized_width
  else:
    resized_height = avaliable_height * .33
    resized_width = img_width / img_height * resized_height
I_gorsel_1=Image(image_path, width=resized_width, height=resized_height)
P_gorsel_metin_1=Paragraph(text="<b>Görsel <seq template=\"%(FigureNo+)s\"/></b> <i>barkolorious</i>", style=stiller['GorselMetin'])
gorsel_1=[[I_gorsel_1], [P_gorsel_metin_1]]
T_gorsel_1=Table(gorsel_1,style=[('ALIGN', (0, 0), (-1, -1), 'CENTER'),('TOPPADDING', (0, 1), (0, 1), 0), ('BOTTOMPADDING', (0, 0), (0, 0), 0)])
T_gorsel_1.hAlign = TA_JUSTIFY


image_path = "img2.png"
with PILImg.open(image_path) as img:
  img_width, img_height = img.size
  if img_width > img_height:
    resized_width = avaliable_width * .5
    resized_height = img_height / img_width * resized_width
  else:
    resized_height = avaliable_height * .33
    resized_width = img_width / img_height * resized_height
I_gorsel_2 = Image(image_path, width=resized_width, height=resized_height)
P_gorsel_metin_2 = Paragraph(text="<b>Görsel <seq template=\"%(FigureNo+)s\"/></b> <i>AEROP</i>", style=stiller['GorselMetin'])
gorsel_2=[[I_gorsel_2], [P_gorsel_metin_2]]
T_gorsel_2=Table(gorsel_2,style=[('ALIGN', (0, 0), (-1, -1), 'CENTER'),('TOPPADDING', (0, 1), (0, 1), 0), ('BOTTOMPADDING', (0, 0), (0, 0), 0)])
T_gorsel_2.hAlign = TA_JUSTIFY



story = []

# story.append(I_gorsel_1)
story.append(T_gorsel_1)
story.append(Paragraph(sample_text, style=stiller['Paragraf']))
story.append(T_gorsel_2)

doc = SimpleDocTemplate('doc.pdf', pagesize=A4, leftMargin=page_margin, rightMargin=page_margin, topMargin=page_margin, bottomMargin=page_margin, allowSplitting=1)
doc.build(story)

print("Saved to doc.pdf")