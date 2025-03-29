# +--------------------------------------------------------------------+
# |                          TEST SUCCESSFULL                          |
# +--------------------------------------------------------------------+

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm, inch
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_JUSTIFY

sample_text = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit. $Phasellus$ dapibus venenatis leo ac suscipit. Pellentesque ut nisl eu velit tempus gravida. Sed ut consectetur eros. Integer at hendrerit orci. Donec sagittis hendrerit elementum. Pellentesque sit amet libero nec lacus dictum aliquet quis a mi. Duis interdum nunc non lacus tempus ornare. <i>Etiam enim ante, <b>tincidunt eu nunc et,</b> scelerisque pretium purus. Fusce molestie pellentesque malesuada. Sed imperdiet lectus quam, id dignissim ligula convallis non.</i>
"""

styleSheet = getSampleStyleSheet()
# style = styleSheet['BodyText']
style = ParagraphStyle(
    name="paragraf", 
    fontName='Times', 
    fontSize=12, 
    leading=12,
    leftIndent=0,
    rightIndent=0,
    firstLineIndent=inch/2,
    alignment= TA_JUSTIFY, 
    textColor="black",
    hyphenationLang="tr_TR",
    embeddedHyphenation=1,
    uriWasteReduce=0.3  
)

P=Paragraph(sample_text,style)
canv = Canvas('doc.pdf')
width, height = A4
margin = 2.5 * cm

available_width = width - 2 * margin
available_height = height - 2 * margin

w,h = P.wrap(available_width, available_height)    # find required space
print(w, h, available_width, available_height)

y = (height - margin) - h
x = margin

if w<=available_width and h<=available_height:
    P.drawOn(canv, x, y)
    available_height = available_height - h         # reduce the available height
    canv.save()
else:
    raise ValueError("Not enough room")