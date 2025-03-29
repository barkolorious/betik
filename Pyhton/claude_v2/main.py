import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import markdown
import os
import tempfile
from tkinter import font
import webbrowser
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.units import inch
import io
from PIL import Image as PILImage, ImageTk
from html.parser import HTMLParser
import re
import fitz  # PyMuPDF library for PDF rendering

class MarkdownToPDFConverter(HTMLParser):
    """Convert HTML to ReportLab elements for PDF generation"""
    
    def __init__(self):
        super().__init__()
        self.styles = getSampleStyleSheet()
        # Add some custom styles
        self.styles.add(ParagraphStyle(
            name='CodeBlock',
            parent=self.styles['Code'],
            backColor=colors.lightgrey,
            borderPadding=5,
            borderWidth=0.5,
            borderColor=colors.grey,
            fontName='Courier',
            fontSize=9,
            leading=12
        ))
        
        self.current_style = self.styles['Normal']
        self.elements = []
        self.in_list = False
        self.list_items = []
        self.list_type = None
        self.in_table = False
        self.table_data = []
        self.current_row = []
        self.current_cell = []
        self.text_buffer = ""
        
    def handle_starttag(self, tag, attrs):
        # Flush any pending text
        if self.text_buffer and not (self.in_list or self.in_table):
            self.elements.append(Paragraph(self.text_buffer, self.current_style))
            self.text_buffer = ""
            
        if tag == 'h1':
            self.current_style = self.styles['Heading1']
        elif tag == 'h2':
            self.current_style = self.styles['Heading2']
        elif tag == 'h3':
            self.current_style = self.styles['Heading3']
        elif tag == 'h4':
            self.current_style = self.styles['Heading4']
        elif tag == 'h5':
            self.current_style = self.styles['Heading5']
        elif tag == 'h6':
            self.current_style = self.styles['Heading6']
        elif tag == 'p':
            self.current_style = self.styles['Normal']
        elif tag == 'strong' or tag == 'b':
            self.current_style = self.styles['BodyText']
        elif tag == 'em' or tag == 'i':
            self.current_style = self.styles['Italic']
        elif tag == 'code':
            self.current_style = self.styles['Code']
        elif tag == 'pre':
            self.current_style = self.styles['CodeBlock']
        elif tag == 'ul':
            self.in_list = True
            self.list_type = 'unordered'
            self.list_items = []
        elif tag == 'ol':
            self.in_list = True
            self.list_type = 'ordered'
            self.list_items = []
        elif tag == 'li' and self.in_list:
            pass  # We'll handle this in handle_data
        elif tag == 'table':
            self.in_table = True
            self.table_data = []
        elif tag == 'tr' and self.in_table:
            self.current_row = []
        elif (tag == 'td' or tag == 'th') and self.in_table:
            self.current_cell = []
        elif tag == 'br':
            self.text_buffer += '<br/>'
    
    def handle_endtag(self, tag):
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'strong', 'b', 'em', 'i', 'code', 'pre']:
            # Add the paragraph with the current style
            if self.text_buffer:
                self.elements.append(Paragraph(self.text_buffer, self.current_style))
                self.text_buffer = ""
            # Add some space after headings and paragraphs
            if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']:
                self.elements.append(Spacer(1, 0.1 * inch))
            # Reset to normal style
            self.current_style = self.styles['Normal']
        
        elif tag == 'ul' or tag == 'ol':
            # Process the list items
            bullet_type = 'bullet' if self.list_type == 'unordered' else 'number'
            for item in self.list_items:
                # Add bullet or number
                bullet_text = '• ' if bullet_type == 'bullet' else f"{self.list_items.index(item) + 1}. "
                self.elements.append(Paragraph(f"{bullet_text}{item}", self.styles['Normal']))
            
            self.in_list = False
            self.list_items = []
            self.list_type = None
            self.elements.append(Spacer(1, 0.1 * inch))
        
        elif tag == 'li' and self.in_list:
            if self.text_buffer:
                self.list_items.append(self.text_buffer)
                self.text_buffer = ""
        
        elif tag == 'table':
            # Process the table
            if self.table_data:
                # Create a ReportLab Table
                table_style = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ])
                
                table = Table(self.table_data)
                table.setStyle(table_style)
                self.elements.append(table)
                self.elements.append(Spacer(1, 0.2 * inch))
            
            self.in_table = False
            self.table_data = []
        
        elif tag == 'tr' and self.in_table:
            if self.current_row:
                self.table_data.append(self.current_row)
        
        elif (tag == 'td' or tag == 'th') and self.in_table:
            if self.text_buffer:
                self.current_row.append(Paragraph(self.text_buffer, self.styles['Normal']))
                self.text_buffer = ""
    
    def handle_data(self, data):
        self.text_buffer += data
    
    def get_elements(self):
        # Flush any remaining text
        if self.text_buffer:
            self.elements.append(Paragraph(self.text_buffer, self.current_style))
        
        return self.elements

class MarkdownEditor:
    def __init__(self, root):
        """Initialize the Markdown Editor application"""
        self.root = root
        self.root.title("Markdown Editor with PDF Export")
        self.root.geometry("1200x800")
        
        self.current_file = None
        self.temp_html_path = None
        self.temp_pdf_path = None
        
        self.setup_ui()
        self.bind_events()
        
    def setup_ui(self):
        """Setup the user interface components"""
        # Main paned window for editor and preview
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Editor frame (left side)
        self.editor_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(self.editor_frame, weight=1)
        
        # Editor toolbar
        self.editor_toolbar = ttk.Frame(self.editor_frame)
        self.editor_toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # File operations
        ttk.Button(self.editor_toolbar, text="New", command=self.new_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.editor_toolbar, text="Open", command=self.open_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.editor_toolbar, text="Save", command=self.save_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.editor_toolbar, text="Save As", command=self.save_file_as).pack(side=tk.LEFT, padx=2)
        
        # Markdown shortcuts
        ttk.Separator(self.editor_toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        ttk.Button(self.editor_toolbar, text="Bold", command=lambda: self.insert_markdown("**", "**")).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.editor_toolbar, text="Italic", command=lambda: self.insert_markdown("*", "*")).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.editor_toolbar, text="H1", command=lambda: self.insert_markdown("# ", "")).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.editor_toolbar, text="H2", command=lambda: self.insert_markdown("## ", "")).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.editor_toolbar, text="Link", command=lambda: self.insert_markdown("[", "](url)")).pack(side=tk.LEFT, padx=2)
        
        # Export buttons
        ttk.Separator(self.editor_toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        ttk.Button(self.editor_toolbar, text="Export HTML", command=self.export_html).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.editor_toolbar, text="Export PDF", command=self.export_pdf).pack(side=tk.LEFT, padx=2)
        
        # Text editor with line numbers
        self.editor_area = tk.Frame(self.editor_frame)
        self.editor_area.pack(fill=tk.BOTH, expand=True)
        
        # Line numbers
        self.line_numbers = tk.Text(self.editor_area, width=4, padx=3, takefocus=0, border=0,
                               background='#f0f0f0', state='disabled', wrap='none')
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Text editor with scrollbar
        self.text_frame = tk.Frame(self.editor_area)
        self.text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Use a monospace font for the editor
        editor_font = font.Font(family="Courier", size=10)
        self.editor = tk.Text(self.text_frame, wrap="word", undo=True, font=editor_font)
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.scrollbar = ttk.Scrollbar(self.text_frame, command=self.editor.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.editor.config(yscrollcommand=self.scrollbar.set)
        
        # Status bar
        self.status_bar = ttk.Label(self.editor_frame, text="Ready", anchor=tk.W)
        self.status_bar.pack(fill=tk.X, padx=5, pady=2)
        
        # Preview frame (right side)
        self.preview_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(self.preview_frame, weight=1)
        
        # Preview toolbar
        self.preview_toolbar = ttk.Frame(self.preview_frame)
        self.preview_toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.preview_toolbar, text="PDF Preview").pack(side=tk.LEFT, padx=5)
        ttk.Button(self.preview_toolbar, text="Refresh", command=self.update_preview).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.preview_toolbar, text="Open in PDF Viewer", command=self.open_in_pdf_viewer).pack(side=tk.LEFT, padx=2)
        
        # PDF preview canvas with scrollbar
        self.preview_frame_inner = ttk.Frame(self.preview_frame)
        self.preview_frame_inner.pack(fill=tk.BOTH, expand=True)
        
        # Canvas for PDF preview
        self.preview_canvas = tk.Canvas(self.preview_frame_inner, bg="white")
        self.preview_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbars for the canvas
        self.preview_x_scrollbar = ttk.Scrollbar(self.preview_frame, orient=tk.HORIZONTAL, command=self.preview_canvas.xview)
        self.preview_x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.preview_y_scrollbar = ttk.Scrollbar(self.preview_frame_inner, orient=tk.VERTICAL, command=self.preview_canvas.yview)
        self.preview_y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.preview_canvas.config(
            xscrollcommand=self.preview_x_scrollbar.set,
            yscrollcommand=self.preview_y_scrollbar.set
        )
        
        # Initialize with some default content
        self.editor.insert("1.0", "# Markdown Editor\n\nThis is a simple **Markdown** editor with *PDF* export using ReportLab.\n\n## Features\n\n- Edit markdown\n- See PDF preview\n- Export to HTML or PDF\n\n")
        
        # Update the preview
        self.update_preview()
        self.update_line_numbers()
    
    def bind_events(self):
        """Bind all necessary events for the editor"""
        # Bind events for line numbers and preview updates
        self.editor.bind("<<Modified>>", self.on_text_modified)
        self.editor.bind("<Configure>", self.update_line_numbers)
        self.editor.bind("<KeyRelease>", self.update_line_numbers)
        self.editor.bind("<MouseWheel>", self.update_line_numbers)
        self.editor.bind("<Key>", self.on_key_press)
    
    def on_key_press(self, event):
        """Handle key press events in the editor"""
        # Update preview after a small delay (can be added for real-time updates)
        self.root.after(1000, self.update_preview)  # Update preview after 1 second of inactivity
    
    def on_text_modified(self, event):
        """Handle text modified event"""
        self.editor.edit_modified(False)  # Reset the modified flag
        self.update_status("Modified")
    
    def update_line_numbers(self, event=None):
        """Update the line numbers in the editor"""
        # Update the line numbers text widget
        line_count = self.editor.get("1.0", tk.END).count('\n')
        if line_count == 0:
            line_count = 1
            
        line_number_content = "\n".join(str(i) for i in range(1, line_count + 1))
        
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', tk.END)
        self.line_numbers.insert('1.0', line_number_content)
        self.line_numbers.config(state='disabled')
        
        # Make sure the scrolls align
        top = self.editor.yview()[0]
        self.line_numbers.yview_moveto(top)
    
    def update_status(self, message):
        """Update the status bar with a message"""
        self.status_bar.config(text=message)
    
    def insert_markdown(self, prefix, suffix):
        """Insert markdown formatting at cursor position or around selected text"""
        # Get the selected text or current position
        try:
            selection = self.editor.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.editor.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.editor.insert(tk.INSERT, f"{prefix}{selection}{suffix}")
        except tk.TclError:  # No selection
            self.editor.insert(tk.INSERT, f"{prefix}{suffix}")
            # Move cursor between tags if there's a suffix
            if suffix:
                self.editor.mark_set(tk.INSERT, f"{tk.INSERT} - {len(suffix)}c")
    
    def new_file(self):
        """Create a new file, discarding current changes"""
        if messagebox.askyesno("New File", "Discard current changes?"):
            self.editor.delete("1.0", tk.END)
            self.current_file = None
            self.update_preview()
            self.update_status("New file created")
    
    def open_file(self):
        """Open a markdown file from disk"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Markdown Files", "*.md"), ("Text Files", "*.txt"), ("All Files", "*.*")])
        
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                self.editor.delete("1.0", tk.END)
                self.editor.insert("1.0", content)
                self.current_file = file_path
                self.update_preview()
                self.update_status(f"Opened: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")
    
    def save_file(self):
        """Save the current file to disk"""
        if self.current_file:
            try:
                content = self.editor.get("1.0", tk.END)
                with open(self.current_file, "w", encoding="utf-8") as file:
                    file.write(content)
                self.update_status(f"Saved: {os.path.basename(self.current_file)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
        else:
            self.save_file_as()
    
    def save_file_as(self):
        """Save the current file with a new name"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown Files", "*.md"), ("Text Files", "*.txt"), ("All Files", "*.*")])
        
        if file_path:
            self.current_file = file_path
            self.save_file()
    
    def export_html(self):
        """Export the markdown content as HTML file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML Files", "*.html"), ("All Files", "*.*")])
        
        if file_path:
            try:
                # Convert markdown to HTML
                markdown_text = self.editor.get("1.0", tk.END)
                html = markdown.markdown(markdown_text, extensions=['tables', 'fenced_code'])
                
                # Add some basic CSS for better appearance
                styled_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>{os.path.basename(file_path) if self.current_file else 'Markdown Document'}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
                        h1, h2, h3, h4, h5, h6 {{ color: #333; margin-top: 20px; }}
                        code {{ background-color: #f4f4f4; padding: 2px 4px; border-radius: 4px; font-family: monospace; }}
                        pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 4px; overflow-x: auto; }}
                        blockquote {{ border-left: 4px solid #ddd; padding-left: 15px; color: #777; }}
                        table {{ border-collapse: collapse; width: 100%; }}
                        th, td {{ border: 1px solid #ddd; padding: 8px; }}
                        th {{ background-color: #f2f2f2; }}
                        img {{ max-width: 100%; }}
                        a {{ color: #0066cc; }}
                    </style>
                </head>
                <body>
                    {html}
                </body>
                </html>
                """
                
                # Write to file
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(styled_html)
                
                self.update_status(f"HTML exported to: {os.path.basename(file_path)}")
                
                # Ask if user wants to open the exported file
                if messagebox.askyesno("Open File", "Would you like to open the exported HTML file?"):
                    webbrowser.open(file_path)
                    
            except Exception as e:
                messagebox.showerror("Error", f"Could not export HTML: {e}")
    
    def export_pdf(self):
        """Export the current markdown as PDF using ReportLab"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")])
        
        if file_path:
            try:
                # Generate PDF using our helper method
                self.generate_pdf(file_path)
                
                self.update_status(f"PDF exported to: {os.path.basename(file_path)}")
                
                # Ask if user wants to open the exported file
                if messagebox.askyesno("Open File", "Would you like to open the exported PDF file?"):
                    # Use the appropriate method to open PDF based on platform
                    if os.name == 'nt':  # Windows
                        os.startfile(file_path)
                    elif os.name == 'posix':  # macOS or Linux
                        import subprocess
                        subprocess.call(('open' if os.uname().sysname == 'Darwin' else 'xdg-open', file_path))
            
            except Exception as e:
                messagebox.showerror("Error", f"Could not export PDF: {e}")
    
    def generate_pdf(self, output_path=None):
        """Generate a PDF from the current markdown content
        
        Args:
            output_path: If provided, saves the PDF to this path.
                         If None, creates a temp file for preview.
                         
        Returns:
            Path to the generated PDF file
        """
        # Convert markdown to HTML
        markdown_text = self.editor.get("1.0", tk.END)
        html = markdown.markdown(markdown_text, extensions=['tables', 'fenced_code'])
        
        # Create a PDF document
        if output_path is None:
            # Create a temporary file for preview
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as pdf_file:
                output_path = pdf_file.name
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            title=os.path.basename(self.current_file) if self.current_file else 'Markdown Document'
        )
        
        # Parse the HTML and convert to ReportLab elements
        parser = MarkdownToPDFConverter()
        parser.feed(html)
        elements = parser.get_elements()
        
        # Build the PDF
        doc.build(elements)
        
        return output_path
    
    def update_preview(self):
        """Update the PDF preview in the right panel"""
        try:
            # Clean up previous temp files
            if self.temp_pdf_path and os.path.exists(self.temp_pdf_path):
                try:
                    os.unlink(self.temp_pdf_path)
                except:
                    pass
            
            # Generate a new PDF for preview
            self.temp_pdf_path = self.generate_pdf()
            
            # Render the first page of the PDF
            self.display_pdf(self.temp_pdf_path)
            
            self.update_status("PDF preview updated")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generating PDF preview: {e}")
    
    def display_pdf(self, pdf_path):
        """Display a PDF file in the preview canvas
        
        Args:
            pdf_path: Path to the PDF file to display
        """
        # Clear the canvas
        self.preview_canvas.delete("all")
        
        try:
            # Open the PDF with PyMuPDF
            doc = fitz.open(pdf_path)
            
            # Get the first page
            page = doc[0]
            
            # Determine the scale factor (fit to canvas width)
            canvas_width = self.preview_canvas.winfo_width()
            if canvas_width <= 1:  # Canvas not yet realized
                canvas_width = 400  # Default width
            
            # Calculate zoom factor to fit the page width
            zoom_factor = canvas_width / page.rect.width
            
            # Get the pixmap (rasterize the page)
            mat = fitz.Matrix(zoom_factor, zoom_factor)
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image and then to ImageTk
            img = PILImage.frombytes("RGB", [pix.width, pix.height], pix.samples)
            tk_img = ImageTk.PhotoImage(image=img)
            
            # Save the reference to prevent garbage collection
            self.tk_img = tk_img
            
            # Add the image to the canvas
            canvas_img = self.preview_canvas.create_image(0, 0, anchor="nw", image=tk_img)
            
            # Configure the scrollregion
            self.preview_canvas.config(scrollregion=(0, 0, pix.width, pix.height))
            
            # Close the document
            doc.close()
            
        except Exception as e:
            error_message = f"Unable to render PDF preview: {e}"
            self.preview_canvas.create_text(200, 200, text=error_message, fill="red")
    
    def open_in_pdf_viewer(self):
        """Open the current PDF preview in an external viewer"""
        if self.temp_pdf_path and os.path.exists(self.temp_pdf_path):
            # Use the appropriate method to open PDF based on platform
            if os.name == 'nt':  # Windows
                os.startfile(self.temp_pdf_path)
            elif os.name == 'posix':  # macOS or Linux
                import subprocess
                subprocess.call(('open' if os.uname().sysname == 'Darwin' else 'xdg-open', self.temp_pdf_path))
        else:
            self.update_preview()  # Generate the preview first
            if self.temp_pdf_path:
                # Use the appropriate method to open PDF
                if os.name == 'nt':  # Windows
                    os.startfile(self.temp_pdf_path)
                elif os.name == 'posix':  # macOS or Linux
                    import subprocess
                    subprocess.call(('open' if os.uname().sysname == 'Darwin' else 'xdg-open', self.temp_pdf_path))
    
    def cleanup(self):
        """Clean up temporary files before application exit"""
        # Clean up HTML temp file
        if self.temp_html_path and os.path.exists(self.temp_html_path):
            try:
                os.unlink(self.temp_html_path)
            except:
                pass
        
        # Clean up PDF temp file
        if self.temp_pdf_path and os.path.exists(self.temp_pdf_path):
            try:
                os.unlink(self.temp_pdf_path)
            except:
                pass

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = MarkdownEditor(root)
    
    def on_closing():
        """Handle window closing event"""
        app.cleanup()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()