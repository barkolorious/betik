from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ListStyle, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('Times', 'times.ttf'))
pdfmetrics.registerFont(TTFont('TimesBd', 'timesbd.ttf'))
pdfmetrics.registerFont(TTFont('TimesIt', 'timesi.ttf'))
pdfmetrics.registerFont(TTFont('TimesBI', 'timesbi.ttf'))
registerFontFamily('Times', normal='Times', bold='TimesBd', italic='TimesIt', boldItalic='TimesBI')

stiller = {
  'Paragraf': ParagraphStyle(name='paragraf', fontName='Times', fontSize=12, leading=12, leftIndent=0, rightIndent=0, alignment=TA_JUSTIFY, textColor="black", uriWasteReduce=0.3, allowWidows=0),
  'Madde': ListStyle(name='madde', leftIndent=inch/4, rightIndent=0, bulletAlign='center', bulletType='bullet', bulletColor='black', bulletFontName='Times', bulletFontSize=12, bulletDedent=inch/8, start='bulletchar'),
  'Liste': ListStyle(name='madde', leftIndent=inch/4, rightIndent=0, bulletAlign='right', bulletType='1', bulletColor='black', bulletFontName='Times', bulletFontSize=12, bulletDedent=inch/8, bulletFormat='%s.')
}

sample_text = "Buradaki $(n-k)!$'i sanki seçmediğimiz <b>aaa</b> <i>iiii</i> <b><i>aaaaa</i></b> elemanların farklı sıralamalarını eliyormuş gibi düşünebiliriz \\[a^2 + b^2 = c^2\\] <b>Görsel <seq template=\"%(FigureNo+)s\"/></b> <i>Multi-level templates</i> this is a bullet point.  Spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam , öçşığüÖÇŞİĞÜ"

t = ListFlowable(
  [
    Paragraph("Item no. 1", style=stiller['Paragraf']),
    Paragraph("Item no. 2", style=stiller['Paragraf']),
    ListItem(ListFlowable([
                            Paragraph("sublist item 1", style=stiller['Paragraf']), 
                            Paragraph('sublist item 2', style=stiller['Paragraf'])
                          ], style=stiller['Liste']
                         ), bulletColor='white'),
    Paragraph("Item no. 4", style=stiller['Paragraf']),
  ],
  style=stiller['Madde']
)

story = []

page_width, page_height = A4
bosluk = Spacer(width=page_width, height=inch/8)
story.append(Paragraph(sample_text, style=stiller['Paragraf']))
story.append(t)
doc = SimpleDocTemplate('doc.pdf', pagesize = A4, leftMargin=2.5*cm, rightMargin=2.5*cm, topMargin=2.5*cm, bottomMargin=2.5*cm, allowSplitting=1)

doc.build(story)