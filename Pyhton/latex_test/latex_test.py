# +--------------------------------------------------------------------+
# |                          TEST SUCCESSFULL                          |
# +--------------------------------------------------------------------+

import os
import tempfile
import shutil
from subprocess import Popen, PIPE, DEVNULL
import logging
import re

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
\documentclass[preview]{standalone}
\usepackage{amsmath,amsfonts,amssymb}
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

# Example usage
if __name__ == "__main__":
  converter = LaTeXConverter(dpi=600)

  display_equation = r"\int_{0}^{\infty} e^{-x^2} dx = \frac{\sqrt{\pi}}{2}"
  converter.convert_equation(display_equation, "display_equation.png", inline=False)

  inline_equation = r"$a^2 + b^2 = c^2\$ $"
  converter.convert_equation(inline_equation, "inline_equation.png", inline=True)