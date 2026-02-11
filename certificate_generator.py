import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import black, darkblue, Color, red
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Config
from config import TEMPLATE_FILENAME, TEMPLATE_ICSSHR, OUTPUT_DIR

def get_wrapped_lines(text, font_name, font_size, max_width, canvas_obj):
    """
    Splits text into lines that fit within max_width using the given font.
    """
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        width = canvas_obj.stringWidth(test_line, font_name, font_size)
        
        if width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                # Provide handled word-break if a single word is too long?
                # For now just force break or let it overflow slightly?
                # Actually certificates rarely have super long single words.
                lines.append(word)
                current_line = []
    
    if current_line:
        lines.append(' '.join(current_line))
        
    return lines

def get_lines_by_char_limit(text, max_chars_per_line=40):
    """
    Wraps text so that each line has at most max_chars_per_line characters (word boundary).
    """
    words = text.split()
    lines = []
    current_line = []
    current_len = 0
    for word in words:
        need = len(word) + (1 if current_line else 0)
        if current_len + need <= max_chars_per_line:
            current_line.append(word)
            current_len += need
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
            current_len = len(word)
    if current_line:
        lines.append(' '.join(current_line))
    return lines


def author_display_name(name):
    """
    Ism-familiyani ko'rsatish uchun: har bir so'z bosh harf bilan, lekin apostrof (') dan
    keyingi harf kichik qoladi (masalan Ra'nokhon, Ra'Nokhon emas).
    """
    t = name.title()
    # Apostrofdan keyingi harfni kichik qil (O'zbek, Ra'nokhon)
    result = []
    for i, c in enumerate(t):
        if i > 0 and (t[i - 1] == "'" or t[i - 1] == "'"):
            result.append(c.lower())
        else:
            result.append(c)
    return "".join(result)


def draw_centered_field(c, text, x_center, y_center, max_width, initial_font_size, font_name, max_lines=3, min_font_size=10, fill_color=black):
    """
    Draws text centered at (x_center, y_center).
    Automatically reduces font size if text wraps into more than max_lines lines.
    """
    font_size = initial_font_size
    lines = []
    
    # Attempt to fit text
    while font_size >= min_font_size:
        lines = get_wrapped_lines(text, font_name, font_size, max_width, c)
        if len(lines) <= max_lines:
            break
        font_size -= 2
        
    # Set font
    c.setFont(font_name, font_size)
    c.setFillColor(fill_color)
    
    # Calculate block height
    line_height = font_size * 1.4  # Line spacing
    total_height = len(lines) * line_height
    
    # If y_center is the vertical center of the text block:
    start_y = y_center + (total_height / 2) - line_height * 0.8
    # 0.8 is roughly ascent/baseline adjustment. Reportlab draws at baseline.
    
    for i, line in enumerate(lines):
        text_width = c.stringWidth(line, font_name, font_size)
        x_draw = x_center - (text_width / 2)
        y_draw = start_y - (i * line_height)
        c.drawString(x_draw, y_draw, line)
        
    return font_size

def generate_certificate(author_name, article_title, publication_date, cert_id, doi=None, template=None, layout_shift_up=0,
                        author_color=None, author_shift_down=0, date_red_bold=False, date_x_ratio=None, date_y_ratio=None,
                        author_x_ratio=None, author_y_ratio=None, title_x_ratio=None, title_y_ratio=None, use_cert_id_only=False):
    """
    Generates a PDF certificate. Sertifikatda DOI ko'rsatiladi (agar bor bo'lsa); use_cert_id_only=True bo'lsa doim Certificate ID.
    template: None = Human Studies (template_human_studies.png);
              boshqa qiymat = shu fayl (masalan TEMPLATE_ICSSHR).
    layout_shift_up: 0..1 — author/title ni sahifa balandligining shu qismi tepaga siljitiradi (masalan 0.2 = 20%).
    author_x_ratio, author_y_ratio: muallif matnining markaz joyi (0..1, sahifa eni/balandligiga nisbatan). None = default.
    title_x_ratio, title_y_ratio: sarlavha markaz joyi (0..1). None = default.
    """
    project_dir = os.path.dirname(os.path.abspath(__file__)) or "."
    template_path = template or TEMPLATE_FILENAME
    if not os.path.isabs(template_path):
        template_path = os.path.join(project_dir, template_path)
    
    # Author font: loyiha papkasidagi yoki C:\Windows\Fonts dagi CORSIVA_BOLD_ITALIC
    font_name_author = "Helvetica-Bold"
    corsiva_paths = [
        os.path.join(project_dir, "CORSIVA_BOLD_ITALIC.TTF"),
        os.path.join(project_dir, "CORSIVA_BOLD_ITALIC.ttf"),
        os.path.join(project_dir, "unicode.corsiva.ttf"),
        r"C:\Windows\Fonts\CORSIVA_BOLD_ITALIC.ttf",
        r"C:\Windows\Fonts\CORSIVA_BOLD_ITALIC.otf",
    ]
    if "Corsiva" in pdfmetrics.getRegisteredFontNames():
        font_name_author = "Corsiva"
    else:
        try:
            for path in corsiva_paths:
                if path and os.path.exists(path):
                    try:
                        pdfmetrics.registerFont(TTFont("Corsiva", path))
                        font_name_author = "Corsiva"
                        break
                    except Exception:
                        continue
            if font_name_author != "Corsiva":
                print("CORSIVA_BOLD_ITALIC font not found, using Helvetica-Bold for author")
        except Exception as e:
            print(f"Error registering Corsiva font: {e}")
            font_name_author = "Helvetica-Bold"
    
    # 1. Output Filename
    safe_author = "".join([c for c in author_name if c.isalnum() or c in (' ', '-', '_')]).strip().replace(' ', '_')
    # If author name is too long for filename, truncate?
    if len(safe_author) > 50:
        safe_author = safe_author[:50]
        
    pdf_filename = f"certificate_{safe_author}_{cert_id}.pdf"
    output_path = os.path.join(OUTPUT_DIR, pdf_filename)
    
    # 2. Setup Canvas
    # A4 Landscape: 841.89 x 595.27 points
    page_width, page_height = landscape(A4)
    c = canvas.Canvas(output_path, pagesize=landscape(A4))
    
    # 3. Draw Template Image
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template image {template_path} not found.")

    try:
        c.drawImage(template_path, 0, 0, width=page_width, height=page_height, mask='auto')
    except Exception as e:
        raise e

    # 4. Text Configuration
    center_x = page_width / 2
    # Muallif va title joyi: agar author_x_ratio/author_y_ratio berilsa shu ishlatiladi, aks holda default
    author_x = page_width * author_x_ratio if author_x_ratio is not None else center_x
    author_y = page_height * author_y_ratio if author_y_ratio is not None else (page_height * (0.55 + layout_shift_up) - page_height * author_shift_down)
    title_x = page_width * title_x_ratio if title_x_ratio is not None else center_x
    title_y = page_height * title_y_ratio if title_y_ratio is not None else page_height * (0.40 + layout_shift_up)

    # Author Name (ism-familiya: faqat birinchi harf katta, qolgani kichik)
    author_display = author_display_name(author_name)
    draw_centered_field(c, author_display, author_x, author_y, 
                        max_width=page_width * 0.8, 
                        initial_font_size=26, 
                        font_name=font_name_author, 
                        max_lines=2, fill_color=author_color or black)
                        
    # Article Title (14 pt, bold, to'q ko'k; 60+ belgi bo'lsa ikkinchi, uchinchi qatorlarga tushadi)
    title_font_size = 14
    title_font_name = "Helvetica-Bold"
    if len(article_title) > 60:
        title_lines = get_lines_by_char_limit(article_title, max_chars_per_line=60)
        title_lines = title_lines[:5]  # maksimum 5 qator
        c.setFont(title_font_name, title_font_size)
        c.setFillColor(darkblue)
        line_height = title_font_size * 1.4
        total_height = len(title_lines) * line_height
        start_y = title_y + (total_height / 2) - line_height * 0.8
        for i, line in enumerate(title_lines):
            text_width = c.stringWidth(line, title_font_name, title_font_size)
            c.drawString(title_x - text_width / 2, start_y - (i * line_height), line)
    else:
        draw_centered_field(c, article_title, title_x, title_y, 
                            max_width=page_width * 0.7, 
                            initial_font_size=title_font_size, 
                            font_name=title_font_name, 
                            max_lines=2, fill_color=darkblue)
                        
    # Sana (o'ngroq va teparoq; konferensiyada: markazdan chapga, pastroq, qizil bold)
    date_y = page_height * (date_y_ratio if date_y_ratio is not None else 0.24)
    if date_x_ratio is not None:
        date_x = center_x - page_width * date_x_ratio  # chapga
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(date_red_bold and red or black)
        c.drawString(date_x, date_y, publication_date)
    else:
        date_x = center_x + page_width * 0.30
        c.setFont("Helvetica-Oblique", 16)
        c.setFillColor(black)
        c.drawRightString(date_x, date_y, publication_date)

    # DOI (o'ngroq, pastda, prozrachnost); konferensiyada doim maxsus Certificate ID
    id_x = center_x + page_width * 0.37
    id_y = 22
    c.setFont("Helvetica", 8)
    c.setFillColor(Color(0, 0, 0, alpha=0.5))
    if use_cert_id_only:
        display_id = f"Certificate ID: {cert_id}"
    else:
        display_id = f"DOI: {doi}" if doi else f"Certificate ID: {cert_id}"
    c.drawCentredString(id_x, id_y, display_id)
    c.setFillColor(black)
    
    c.save()
    return output_path


def generate_certificate_icsshr(author_name, article_title, publication_date, cert_id, doi=None):
    """
    International Conference on Social Sciences and Humanities Research uchun
    PDF sertifikat (template_human_studies2.png).
    """
    # Konferensiya: muallif va title joyi — x,y ni o'zingiz sozlang (0..1, sahifa eni/balandligiga nisbatan)
    # x: 0.5 = markaz, 0 = chap, 1 = o'ng. y: 0 = past, 1 = tepa.
    return generate_certificate(
        author_name, article_title, publication_date, cert_id, doi=doi, template=TEMPLATE_ICSSHR,
        use_cert_id_only=True,  # Konferensiyada DOI o'rniga maxsus sertifikat ID
        layout_shift_up=0.2,
        author_color=red,
        author_shift_down=0.04,
        date_red_bold=True,
        date_x_ratio=0.32,
        date_y_ratio=0.15,
        # Muallif ism-familiya joyi (x, y)
        author_x_ratio=0.5,
        author_y_ratio=0.63,
        # Sarlavha (title) joyi (x, y)
        title_x_ratio=0.5,
        title_y_ratio=0.51,
    )


if __name__ == "__main__":
    # Test: Human Studies (default template)
    try:
        path = generate_certificate("Test Author", "Test Article Title", "February 2026", "MIHS-2026-000000")
        print(f"Generated (Human Studies) at {path}")
    except Exception as e:
        print(f"Error: {e}")
    # Test: International Conference on Social Sciences and Humanities Research
    try:
        path2 = generate_certificate_icsshr("Test Author", "Test Article Title", "February 2026", "ICSSHR-2026-000001")
        print(f"Generated (ICSSHR) at {path2}")
    except Exception as e:
        print(f"Error ICSSHR: {e}")
