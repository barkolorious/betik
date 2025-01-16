import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm, inch


import textwrap
import io
import fitz  # PyMuPDF
import tempfile
import os


class TextToPDFConverter:
  def __init__(self, root):
    self.root = root
    self.root.title("Text to PDF Converter")
    self.root.geometry("1000x600")

    main_frame = ttk.Frame(root, padding="10")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    left_frame = ttk.Frame(main_frame)
    left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
    
    toolbar = ttk.Frame(left_frame)
    toolbar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
    
    self.bold_btn = ttk.Button(toolbar, text="Bold", command=lambda: self.insert_markup('*'))
    self.bold_btn.grid(row=0, column=0, padx=2)
    
    self.italic_btn = ttk.Button(toolbar, text="Italic", command=lambda: self.insert_markup('_'))
    self.italic_btn.grid(row=0, column=1, padx=2)
    
    self.help_btn = ttk.Button(toolbar, text="?", width=3, command=self.show_help)
    self.help_btn.grid(row=0, column=2, padx=2)
    
    self.text_area = tk.Text(left_frame, height=15, width=40, wrap=tk.WORD)
    self.text_area.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    example_text = "Regular text\n*Bold text*\n_Italic text_\n*_Bold and italic text_*"
    self.text_area.insert("1.0", example_text)
    
    text_scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.text_area.yview)
    text_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
    self.text_area['yscrollcommand'] = text_scrollbar.set
    
    format_frame = ttk.LabelFrame(left_frame, text="Formatting", padding="5")
    format_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=10)
    
    self.indent_var = tk.BooleanVar(value=True)
    self.indent_check = ttk.Checkbutton(
        format_frame, 
        text="Indent Paragraphs", 
        variable=self.indent_var
    )
    self.indent_check.grid(row=0, column=0, padx=5)
    
    button_frame = ttk.Frame(left_frame)
    button_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
    
    self.export_button = ttk.Button(button_frame, text="Export to PDF", command=self.export_to_pdf)
    self.export_button.grid(row=0, column=0, padx=5)
    
    self.preview_button = ttk.Button(button_frame, text="Update Preview", command=self.update_preview)
    self.preview_button.grid(row=0, column=1, padx=5)
    
    right_frame = ttk.Frame(main_frame)
    right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    preview_label = ttk.Label(right_frame, text="Preview:")
    preview_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
    
    self.preview_canvas = tk.Canvas(right_frame, bg='white', width=400, height=500)
    self.preview_canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    preview_scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.preview_canvas.yview)
    preview_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
    self.preview_canvas.configure(yscrollcommand=preview_scrollbar.set)
    
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)
    main_frame.rowconfigure(0, weight=1)
    left_frame.columnconfigure(0, weight=1)
    left_frame.rowconfigure(1, weight=1)
    right_frame.columnconfigure(0, weight=1)
    right_frame.rowconfigure(1, weight=1)

  def show_help(self):
    help_text = """Text Formatting Guide:
        
*bold text* - Makes text bold
_italic text_ - Makes text italic
*_bold and italic text_* - Makes text both bold and italic

You can also use the Bold and Italic buttons to insert the markup."""
        
    messagebox.showinfo("Formatting Help", help_text)

  def insert_markup(self, markup):
    try:
      try:
        start = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
        self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
        self.text_area.insert(tk.INSERT, f"{markup}{start}{markup}")
      except tk.TclError:  # No selection
        self.text_area.insert(tk.INSERT, markup + markup)
        # Move cursor between markup
        current_pos = self.text_area.index(tk.INSERT)
        self.text_area.mark_set(tk.INSERT, f"{current_pos}-{len(markup)}c")
    except Exception as e:
      messagebox.showerror("Error", f"Error inserting markup: {str(e)}")

  def create_pdf(self, output_path):
    text_content = self.text_area.get("1.0", tk.END).strip()
    paragraphs = text_content.split('\n')
      
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
      
    margin = 2.5 * cm
    y = height - margin
    font_size = 12
    line_height = font_size
    paragraph_spacing = font_size * 1.5
    indent_size = inch / 2
      
    available_width = width - (2 * margin)
    chars_per_line = int(available_width / (font_size * 0.5))
      
    for paragraph in paragraphs:
      wrapped_lines = textwrap(paragraph, width=chars_per_line)

      first_flag = True

      for line in wrapped_lines:
        if y < margin:
          c.showPage()
          y = height - margin
          
        x = margin

        if first_flag:
          first_flag = False
          x += indent_size
          
          # Parse the line for formatting
        parts = []
        current_text = ''
        is_bold = False
        is_italic = False
            
        i = 0
        while i < len(line):
          if line[i] in '*_':
            if current_text:
              parts.append((current_text, is_bold, is_italic))
              current_text = ''
            if line[i] == '*':
              is_bold = not is_bold
            else:
              is_italic = not is_italic
            i += 1
            continue
          current_text += line[i]
          i += 1
            
        if current_text:
          parts.append((current_text, is_bold, is_italic))
          
        for text, bold, italic in parts:
          if bold and italic:
            font = 'Times-BoldItalic'
          elif bold:
            font = 'Times-Bold'
          elif italic:
            font = 'Times-Italic'
          else:
            font = 'Times-Roman'
            
          c.setFont(font, font_size, leading=font_size)
          c.drawString(x, y, text)
          x += c.stringWidth(text, font, font_size)
        
        # Add paragraph spacing
        y -= paragraph_spacing - line_height
        
        if y < margin + line_height:
          c.showPage()
          y = height - margin
      
    c.save()

  def export_to_pdf(self):
    if not self.text_area.get("1.0", tk.END).strip():
      messagebox.showwarning("Warning", "Please enter some text before exporting.")
      return
    
    file_path = filedialog.asksaveasfilename(
      defaultextension=".pdf",
      filetypes=[("PDF files", "*.pdf")],
      title="Save PDF As"
    )
    
    if file_path:
      try:
        self.create_pdf(file_path)
        messagebox.showinfo("Success", "PDF exported successfully!")
      except Exception as e:
        messagebox.showerror("Error", f"An error occurred while creating the PDF:\n{str(e)}")

  def update_preview(self):
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
      tmp_pdf_path = tmp_pdf.name
    
    try:
      self.create_pdf(tmp_pdf_path)
      
      doc = fitz.open(tmp_pdf_path)
      page = doc[0]
      pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
      
      img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
      photo = ImageTk.PhotoImage(img)
      
      self.preview_canvas.delete("all")
      self.preview_canvas.create_image(0, 0, anchor=tk.NW, image=photo)
      self.preview_canvas.image = photo
      
      self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))
      
      doc.close()
        
    except Exception as e:
      messagebox.showerror("Error", f"An error occurred while generating preview:\n{str(e)}")
    
    finally:
      try:
        os.unlink(tmp_pdf_path)
      except:
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = TextToPDFConverter(root)
    root.mainloop()