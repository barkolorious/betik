import os, tempfile, shutil, logging, re
from subprocess import Popen, PIPE, DEVNULL
from PIL import Image

from reportlab.lib.styles import ParagraphStyle, ListStyle
from reportlab.lib.units import cm, inch
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont

class LaTeXConverter:
  """A class to convert LaTeX equations to PNG images."""
    
  def __init__(self, dpi=300):
    """
    Initialize the converter with specified DPI.
    
    Args:
        dpi (int): Dots per inch for the output PNG image
    """
    self.dpi = dpi
    self.required_programs = ['latex', 'dvipng']
    self._check_dependencies()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    self.logger = logging.getLogger(__name__)
    
  def _check_dependencies(self):
    """Check if required programs are installed."""
    missing = []
    for program in self.required_programs:
      if shutil.which(program) is None:
        missing.append(program)
    
    if missing:
      raise RuntimeError(
        f"Required programs are missing: {', '.join(missing)}. "
        "Please install them using your package manager."
      )
    
  def _create_latex_document(self, equation, inline=False):
    """
    Create a complete LaTeX document containing the equation.
    
    Args:
        equation (str): The LaTeX equation to convert
        inline (bool): Whether the equation should be rendered inline
    """
    # Remove any \begin{equation} or \[ or $ if they exist
    equation = equation.strip()
    # Remove delimiters only from start and end of equation
    equation = re.sub(r'^(\$|\\\[|\\begin\{equation\})', '', equation)  # Remove opening delimiters
    equation = re.sub(r'(\$|\\\]|\\end\{equation\})$', '', equation)    # Remove closing delimiters
        
    if inline:
      # For inline equations, wrap in $
      wrapped_equation = f"${equation}$"
    else:
      # For display equations, wrap in \[ \]
      wrapped_equation = f"\\[{equation}\\]"
            
    return r"""
\documentclass[12pt]{article}
\special{papersize=3in,5in}
\usepackage{amsmath,amsfonts,amssymb}
\pagestyle{empty}
\setlength{\parindent}{0in}
\begin{document}
%s
\end{document}
""" % wrapped_equation

  def convert_equation(self, equation, output_path, inline=False):
    """
    Convert a LaTeX equation to PNG.
    
    Args:
        equation (str): The LaTeX equation to convert
        output_path (str): Path where the PNG should be saved
        inline (bool): Whether to render the equation inline
        
    Returns:
        bool: True if conversion was successful, False otherwise
    """
    try:
      # Create temporary directory
      with tempfile.TemporaryDirectory() as temp_dir:
        # Create and write LaTeX file
        tex_path = os.path.join(temp_dir, 'equation.tex')
        with open(tex_path, 'w', encoding='utf-8') as f:
          f.write(self._create_latex_document(equation, inline))
        
        # Run latex to create DVI
        self.logger.info("Running latex...")
        latex_process = Popen(
          ['latex', '-interaction=nonstopmode', 'equation.tex'],
          cwd=temp_dir,
          stdout=DEVNULL,
          stderr=PIPE
        )
        _, stderr = latex_process.communicate()
        
        if latex_process.returncode != 0:
          self.logger.error(f"LaTeX error: {stderr.decode()}")
          return False
        
        # Convert DVI to PNG
        self.logger.info("Converting to PNG...")
        dvi_path = os.path.join(temp_dir, 'equation.dvi')
        dvipng_process = Popen(
          [
            'dvipng',
            '-D', str(self.dpi),
            '-T', 'tight',
            '-bg', 'Transparent',
            '-o', output_path,
            dvi_path
          ],
          stdout=DEVNULL,
          stderr=PIPE
        )
        _, stderr = dvipng_process.communicate()
        
        if dvipng_process.returncode != 0:
          self.logger.error(f"dvipng error: {stderr.decode()}")
          return False
        
        self.logger.info(f"Successfully created PNG at {output_path}")
        return True
                
    except Exception as e:
      self.logger.error(f"Conversion failed: {str(e)}")
      return False

def render_latex (text):
  converter = LaTeXConverter(dpi=1600)

  sections = []
  i = 0
  current_text = ''
  is_latex = False
  latex_counter = 0
  while i < len(text):
    if text[i] == '$':
      if is_latex:
        latex_file_name = "eq{id}.png".format(id=latex_counter)
        print(current_text)
        converter.convert_equation(current_text, latex_file_name, inline=True)
        latex_counter += 1
      sections.append((current_text, is_latex))
      current_text = ''
      is_latex = not is_latex
    else:
      current_text += text[i]
    i += 1
  
  if current_text:
    sections.append((current_text, is_latex))

  text_to_be_rendered = ''

  latex_counter = 0
  for section, latex in sections:
    if latex:
      image_path = "eq{id}.png".format(id=latex_counter)
      with Image.open(image_path) as img:
          img_width, img_height = img.size
      text_to_be_rendered += "<img src=\"{src}\" valign=\"-1.5\" height=\"{resized_height}\" width=\"{resized_width}\"/>".format(src=image_path, resized_width=img_width/25, resized_height=img_height/25)
      latex_counter += 1
    else:
      text_to_be_rendered += section

  return text_to_be_rendered

pdfmetrics.registerFont(TTFont('Times', 'times.ttf'))
pdfmetrics.registerFont(TTFont('TimesBd', 'timesbd.ttf'))
pdfmetrics.registerFont(TTFont('TimesIt', 'timesi.ttf'))
pdfmetrics.registerFont(TTFont('TimesBI', 'timesbi.ttf'))
registerFontFamily('Times', normal='Times', bold='TimesBd', italic='TimesIt', boldItalic='TimesBI')

stiller = {
  'Paragraf': ParagraphStyle(name='paragraf', fontName='Times', fontSize=12, leading=12, leftIndent=0, rightIndent=0, firstLineIndent=inch/2, alignment=TA_JUSTIFY, textColor="black", uriWasteReduce=0.3, allowWidows=0),
  'Madde': ListStyle(name='madde', leftIndent=inch/4, rightIndent=0, bulletAlign='center', bulletType='bullet', bulletColor='black', bulletFontName='Times', bulletFontSize=12, bulletDedent=inch/8, start='bulletchar'),
  'Liste': ListStyle(name='madde', leftIndent=inch/4, rightIndent=0, bulletAlign='right', bulletType='1', bulletColor='black', bulletFontName='Times', bulletFontSize=12, bulletDedent=inch/8, bulletFormat='%s.'),
  'Kaynakca': ParagraphStyle(name='kaynakca', fontName='Times', fontSize=12, leading=12, leftIndent=inch/2, rightIndent=0, firstLineIndent=-inch/2, alignment=TA_JUSTIFY, textColor="black", uriWasteReduce=0.3, allowWidows=0)
}


sample_text = "Buradaki $(n-k)!$'i sanki seçmediğimiz <b>aaa</b> <i>iiii</i> <b><i>aaaaa</i></b> elemanların farklı sıralamalarını eliyormuş gibi düşünebiliriz \\[a^2 + b^2 = c^2\\] <b>Görsel <seq template=\"%(FigureNo+)s\"/></b> <i>Multi-level templates</i> this is a bullet point.  Spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam spam , öçşığüÖÇŞİĞÜ"
render_text = render_latex(sample_text).encode("utf-8")
bullet_text = "<bullet>&bull;</bullet>this is a bullet point. | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | | |"
bib_text = "Akgül, B., Yaşa, S., & Hergül, B. (2018). Unmanned aerial vehicles for gathering the news media industry fast development of methods. <i>Innovation and Global Issues 3: Congress Book</i>, 72-87."
bib_text2 = """Alkouz, B., & Bouguettaya, A. (2021). Formation-based selection of drone swarm services. <i>MobiQuitous 2020 - 17th EAI International Conference on Mobile and Ubiquitous Systems: Computing, Networking and Services</i>, 386-394. <link href="https://doi.org/10.1145/3448891.3448899">https://doi.org/10.1145/3448891.3448899</link>"""

story = []

page_width, page_height = A4
bosluk = Spacer(width=page_width, height=inch/8)
story.append(Paragraph(sample_text, style=stiller['Paragraf']))
story.append(bosluk)
story.append(Paragraph(sample_text, style=stiller['Paragraf']))
story.append(bosluk)
story.append(Paragraph(sample_text, style=stiller['Paragraf']))
story.append(bosluk)
story.append(Paragraph(sample_text, style=stiller['Paragraf']))
story.append(bosluk)
story.append(Paragraph(render_text, style=stiller['Paragraf']))
story.append(bosluk)
story.append(Paragraph(render_text, style=stiller['Paragraf']))
story.append(bosluk)
story.append(Paragraph(render_text, style=stiller['Paragraf']))
story.append(bosluk)
story.append(Paragraph(render_text, style=stiller['Paragraf']))
story.append(bosluk)
story.append(Paragraph(render_text, style=stiller['Paragraf']))
story.append(bosluk)
# story.append(Paragraph(bullet_text, style=stiller['Madde']))
# story.append(Paragraph(bullet_text, style=stiller['Madde']))
# story.append(bosluk)
story.append(Paragraph(bib_text, style=stiller['Kaynakca']))
story.append(Paragraph(bib_text2, style=stiller['Kaynakca']))
story.append(bosluk)
story.append(Paragraph(render_text, style=stiller['Paragraf']))
story.append(bosluk)
story.append(Paragraph(render_text, style=stiller['Paragraf']))
story.append(bosluk)
story.append(Paragraph(bib_text2, style=stiller['Kaynakca']))

# canv = Canvas('doc.pdf')
doc = SimpleDocTemplate('doc.pdf', pagesize = A4, leftMargin=inch, rightMargin=inch, topMargin=inch, bottomMargin=inch, allowSplitting=1,)

doc.build(story)