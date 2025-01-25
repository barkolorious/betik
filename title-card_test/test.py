from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ListStyle, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('Times', 'times.ttf'))
pdfmetrics.registerFont(TTFont('TimesBd', 'timesbd.ttf'))
pdfmetrics.registerFont(TTFont('TimesIt', 'timesi.ttf'))
pdfmetrics.registerFont(TTFont('TimesBI', 'timesbi.ttf'))
registerFontFamily('Times', normal='Times', bold='TimesBd', italic='TimesIt', boldItalic='TimesBI')

stiller = {
  'Paragraf':      ParagraphStyle(name='paragraf', fontName='Times',   fontSize=12, leading=12, firstLineIndent=inch/4, alignment=TA_JUSTIFY, uriWasteReduce=0.3, allowWidows=0),
  'Metin':         ParagraphStyle(name='metin',    fontName='Times',   fontSize=12, leading=18,                         alignment=TA_LEFT,    uriWasteReduce=0.3, allowWidows=0),
  'KalinMetin':    ParagraphStyle(name='metin',    fontName='TimesBd', fontSize=12, leading=18,                         alignment=TA_LEFT, uriWasteReduce=0.3, allowWidows=0),
  'Baslik':        ParagraphStyle(name='baslik',   fontName='TimesBd', fontSize=12, leading=18, leftIndent=inch/4,      alignment=TA_LEFT),
  'Madde':    ListStyle(name='madde', leftIndent=inch/4, rightIndent=0, bulletAlign='center', bulletType='bullet', bulletColor='black', bulletFontName='Times',   bulletFontSize=12, bulletDedent=inch/8, start='bulletchar'),
  'Liste':    ListStyle(name='liste', leftIndent=inch/4, rightIndent=0, bulletAlign='right',  bulletType='1',      bulletColor='black', bulletFontName='TimesBd', bulletFontSize=12, bulletDedent=inch/8, bulletFormat='%s.')
}

page_width, page_height = A4
page_margin = 2.5 * cm
avaliable_width = page_width - 2 * page_margin
avaliable_height = page_height - 2 * page_margin
bosluk = Spacer(width=page_width, height=inch/8)

sample_text = "Buradaki $(n-k)!$'i sanki seçmediğimiz <b>aaa</b> <i>iiii</i> <b><i>aaaaa</i></b> elemanların farklı sıralamalarını eliyormuş gibi düşünebiliriz \\[a^2 + b^2 = c^2\\] <b>Görsel <seq template=\"%(FigureNo+)s\"/></b> <i>Multi-level templates</i> this is a bullet point.  Spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam , öçşığüÖÇŞİĞÜ"

ana_alan = "Yazılım"
tematik_alan = "Yapay Zekâ"
baslik = "Merkeziyetsiz Drone Sürüleri Davranışlarının Deep Reinforcement Learning ile Kontrolü"

ozet_metin = ["Drone uygulamalarında drone’ların tekil kullanımı, kapsamlı görevler için yetersiz kalmaktadır. Bu durum drone’ların sürü halinde kullanımlarının ortaya çıkmasına ve yaygınlaşmasına yol açmıştır. Drone sürülerinin enerji verimliliği ve görev performansı bakımından optimizasyonu karmaşık bir problemdir. Bu problemin çözümlenmesinde formasyonun uygunluğu, değişen koşullara adaptasyon, ölçeklenebilirlik ve merkeziyetsiz karar verme becerisi önemli rol oynamaktadır.",
"Bu çalışmada; verilen probleme Deep Reinforcement Learning (DRL) tabanlı bir mimari ile yaklaşılmış, literatürdeki çalışmaların aksine tek bir görev türü için yapılan implementasyonlar yerine kullanıcı tarafından verilen bir ödül fonksiyonuna bağlı esnek bir yazılım iskeleti (İng.: framework) geliştirilmiştir. Ayrıca kullanıcının seçtiği ödül fonksiyonlarının yanı sıra sürünün çıkarını gözeten destekleyici ödül fonksiyonları da kullanılmıştır.",
"Drone’ların, hedeflerin ve engellerin etkileşimleri ve fiziğinin simüle edildiği sanal çevrede; gerçek sürü uygulamaları esas alınarak tasarlanan örnek görevlerde elde edilen sonuçlar ve test sırasında yapılan gözlemler değerlendirildiğinde çalışmanın amacına ulaştığı net bir şekilde görülmektedir. Çalışma; var olan literatüre katkı sağlamakla birlikte, drone sürüleri uygulamaları için hızlı ve esnek bir çözüm de sunmaktadır."]

anahtar_kelimeler = ["Reinforcement Learning", "Merkeziyetsiz Drone Sürüleri"]
anahtar_kelimeler_metin = "<b>Anahtar kelimeler:</b> "
for i, kelime in enumerate(anahtar_kelimeler):
  anahtar_kelimeler_metin += kelime
  if i != len(anahtar_kelimeler) - 1:
    anahtar_kelimeler_metin += ", "

P_ana_alan = Paragraph(text=ana_alan, style=stiller['KalinMetin'])
P_tematik_alan = Paragraph(text=tematik_alan, style=stiller['KalinMetin'])
P_baslik = Paragraph(text=baslik, style=stiller['KalinMetin'])

P_ozet_baslik = Paragraph(text="Özet", style=stiller['Baslik'])
P_ozet = [Paragraph(text=prg, style=stiller['Paragraf']) for prg in ozet_metin]

P_anahtar_kelime = Paragraph(text=anahtar_kelimeler_metin, style=stiller['Paragraf'])

proje_baslik=[['Proje Ana Alanı',     ':', P_ana_alan    ],  
              ['Proje Tematik Alanı', ':', P_tematik_alan],
              ['Proje Adı (Başlığı)', ':', P_baslik      ]]
T_proje_baslik=Table(proje_baslik, 
                     style=[('ALIGN',         (0, 0), (-1, -1), 'LEFT'), 
                            ('FONT',          (0, 0), (-1, -1), 'TimesBd'), 
                            ('FONTSIZE',      (0, 0), (-1, -1), 12), 
                            ('LEADING',       (0, 0), (-1, -1), 18),
                            ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
                            ('TOPPADDING',    (0, 0), (-1, -1), 0),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING',  (0, 0), (-1, -1), 0),
                            ('LEFTPADDING',   (0, 0), (-1, -1), 0)],
                     colWidths=[106, 6, avaliable_width - 122]
                    )
T_proje_baslik.hAlign = TA_LEFT

liste = ListFlowable(
  [
    Paragraph("Item no. 1", style=stiller['Metin']),
    Paragraph("Item no. 2", style=stiller['Metin']),
    ListItem(ListFlowable([
                            Paragraph("sublist item 1", style=stiller['Metin']), 
                            Paragraph('sublist item 2', style=stiller['Metin'])
                          ], style=stiller['Liste']
                         ), bulletColor='white'),
    Paragraph("Item no. 4", style=stiller['Metin']),
  ],
  style=stiller['Madde']
)

story = []

story.append(T_proje_baslik)
story.append(P_ozet_baslik)
for prg in P_ozet:
  story.append(prg)
story.append(P_anahtar_kelime)
story.append(Paragraph(sample_text, style=stiller['Paragraf']))
story.append(liste)
doc = SimpleDocTemplate('doc.pdf', pagesize = A4, leftMargin=page_margin, rightMargin=page_margin, topMargin=page_margin, bottomMargin=page_margin, allowSplitting=1)

doc.build(story)