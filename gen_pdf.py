from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Frame, PageTemplate, BaseDocTemplate
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus.flowables import Flowable
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics import renderPDF
import qrcode
import io
import os

# Colors
BG_PINK = HexColor("#FFF0F5")        # Lavender Blush
PINK_ACCENT = HexColor("#FFB6C1")    # Light Pink
PINK_DARK = HexColor("#DB7093")      # Pale Violet Red
PINK_MEDIUM = HexColor("#FF69B4")    # Hot Pink
TEXT_DARK = HexColor("#4A4A4A")
TEXT_LIGHT = HexColor("#FFFFFF")
WHITE = HexColor("#FFFFFF")
LIGHT_PINK_BG = HexColor("#FFE4E1")  # Misty Rose

class PageBackground(Flowable):
    """Draw pink background on each page"""
    def __init__(self, width, height):
        Flowable.__init__(self)
        self.width = 0
        self.height = 0
        self.page_width = width
        self.page_height = height
    
    def draw(self):
        self.canv.setFillColor(BG_PINK)
        self.canv.rect(0, 0, self.page_width, self.page_height, fill=1, stroke=0)
        # Decorative top border
        self.canv.setFillColor(PINK_ACCENT)
        self.canv.rect(0, self.page_height - 8*mm, self.page_width, 8*mm, fill=1, stroke=0)
        # Decorative bottom border  
        self.canv.rect(0, 0, self.page_width, 8*mm, fill=1, stroke=0)

def generate_qr_code(data, size=80):
    """Generate QR code and return as Drawing"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="#4A4A4A", back_color="#FFFFFF")
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    from reportlab.platypus import Image
    qr_img = Image(img_buffer, width=size, height=size)
    return qr_img

def create_slide_0(width, height, styles):
    """Title Slide"""
    elements = []
    elements.append(PageBackground(width, height))
    elements.append(Spacer(1, 60*mm))
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=36,
        textColor=PINK_DARK,
        alignment=TA_CENTER,
        spaceAfter=10*mm,
        fontName='Helvetica-Bold'
    )
    elements.append(Paragraph("QueueLess", title_style))
    
    # Subtitle
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=18,
        textColor=TEXT_DARK,
        alignment=TA_CENTER,
        spaceAfter=20*mm,
        fontName='Helvetica-Oblique'
    )
    elements.append(Paragraph("Smart Online Queue Management", subtitle_style))
    
    # Info
    info_style = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        fontSize=14,
        textColor=TEXT_DARK,
        alignment=TA_CENTER,
        spaceAfter=5*mm,
        fontName='Helvetica'
    )
    elements.append(Paragraph("<b>Kamilla Iarullina</b>", info_style))
    elements.append(Paragraph("k.iarullina@innopolis.university", info_style))
    elements.append(Paragraph("Group: DSAI-03", info_style))
    
    return elements

def create_slide_1(width, height, styles):
    """Context Slide"""
    elements = []
    elements.append(PageBackground(width, height))
    elements.append(Spacer(1, 25*mm))
    
    # Section title
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Title'],
        fontSize=28,
        textColor=PINK_DARK,
        alignment=TA_CENTER,
        spaceAfter=15*mm,
        fontName='Helvetica-Bold'
    )
    elements.append(Paragraph("Context", section_style))
    
    # Content box
    content_style = ParagraphStyle(
        'Content',
        parent=styles['Normal'],
        fontSize=13,
        textColor=TEXT_DARK,
        alignment=TA_LEFT,
        spaceAfter=8*mm,
        fontName='Helvetica',
        leading=16
    )
    
    # End User
    user_label = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=15,
        textColor=PINK_MEDIUM,
        alignment=TA_LEFT,
        spaceAfter=4*mm,
        spaceBefore=5*mm,
        fontName='Helvetica-Bold'
    )
    
    elements.append(Paragraph("👤 End-User", user_label))
    elements.append(Paragraph(
        "Customers of small businesses with queues<br/>"
        "(e.g., barbershops, clinics, cafes)",
        content_style
    ))
    
    elements.append(Paragraph("❓ Problem We Solve", user_label))
    elements.append(Paragraph(
        "It reduces time wasted in physical queues by letting users<br/>"
        "join remotely and see real-time queue status with<br/>"
        "estimated waiting time.",
        content_style
    ))
    
    elements.append(Paragraph("💡 Product Idea", user_label))
    elements.append(Paragraph(
        "A website that lets users join a queue online<br/>"
        "and come at the right time.",
        content_style
    ))
    
    return elements

def create_slide_2(width, height, styles):
    """Stakeholders Slide"""
    elements = []
    elements.append(PageBackground(width, height))
    elements.append(Spacer(1, 25*mm))
    
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Title'],
        fontSize=28,
        textColor=PINK_DARK,
        alignment=TA_CENTER,
        spaceAfter=20*mm,
        fontName='Helvetica-Bold'
    )
    elements.append(Paragraph("Stakeholders", section_style))
    
    content_style = ParagraphStyle(
        'Content',
        parent=styles['Normal'],
        fontSize=14,
        textColor=TEXT_DARK,
        alignment=TA_CENTER,
        spaceAfter=10*mm,
        fontName='Helvetica',
        leading=18
    )
    
    elements.append(Paragraph(
        "🎓 Students and staff at Innopolis University<br/>"
        "who need to book time slots<br/>"
        "for example for consultations",
        content_style
    ))
    
    elements.append(Spacer(1, 15*mm))
    
    # Highlight box
    highlight_style = ParagraphStyle(
        'Highlight',
        parent=styles['Normal'],
        fontSize=13,
        textColor=TEXT_DARK,
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique',
        leading=16
    )
    elements.append(Paragraph(
        '"No more waiting in line —<br/>book your spot and arrive just in time!"',
        highlight_style
    ))
    
    return elements

def create_slide_3(width, height, styles):
    """Implementation Slide"""
    elements = []
    elements.append(PageBackground(width, height))
    elements.append(Spacer(1, 20*mm))
    
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Title'],
        fontSize=26,
        textColor=PINK_DARK,
        alignment=TA_CENTER,
        spaceAfter=10*mm,
        fontName='Helvetica-Bold'
    )
    elements.append(Paragraph("Implementation", section_style))
    
    # How we built it
    label_style = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=14,
        textColor=PINK_MEDIUM,
        alignment=TA_LEFT,
        spaceAfter=3*mm,
        spaceBefore=5*mm,
        fontName='Helvetica-Bold'
    )
    
    content_style = ParagraphStyle(
        'Content',
        parent=styles['Normal'],
        fontSize=11,
        textColor=TEXT_DARK,
        alignment=TA_LEFT,
        spaceAfter=4*mm,
        fontName='Helvetica',
        leading=14
    )
    
    elements.append(Paragraph("🛠️ How We Built It", label_style))
    elements.append(Paragraph(
        "Node.js backend with Express • SQLite database<br/>"
        "Real-time updates with JavaScript frontend",
        content_style
    ))
    
    elements.append(Paragraph("📦 Version 1", label_style))
    elements.append(Paragraph(
        "• Booking with overlap prevention<br/>"
        "• User fills form (name, email, date, time, duration)<br/>"
        "• Server validates email, checks slot availability<br/>"
        "• Sidebar shows all current bookings<br/>"
        "• Users can cancel only their own booking",
        content_style
    ))
    
    elements.append(Paragraph("🚀 Version 2", label_style))
    elements.append(Paragraph(
        "• View bookings by week/month calendar<br/>"
        "• Admin view: define available hours & block dates<br/>"
        "• Booking history log (who booked/cancelled, when)",
        content_style
    ))
    
    elements.append(Paragraph("💬 TA Feedback Addressed", label_style))
    elements.append(Paragraph(
        "• Added support for multiple queues",
        content_style
    ))
    
    return elements

def create_slide_4(width, height, styles, github_url, deployed_url):
    """Demo & Links Slide"""
    elements = []
    elements.append(PageBackground(width, height))
    elements.append(Spacer(1, 18*mm))
    
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Title'],
        fontSize=26,
        textColor=PINK_DARK,
        alignment=TA_CENTER,
        spaceAfter=8*mm,
        fontName='Helvetica-Bold'
    )
    elements.append(Paragraph("Demo & Links", section_style))
    
    demo_style = ParagraphStyle(
        'Demo',
        parent=styles['Normal'],
        fontSize=12,
        textColor=TEXT_DARK,
        alignment=TA_CENTER,
        spaceAfter=10*mm,
        fontName='Helvetica-Oblique'
    )
    elements.append(Paragraph(
        "Pre-recorded video demonstration of Version 2<br/>"
        "with voice-over (≤ 2 minutes)",
        demo_style
    ))
    
    # Generate QR codes
    qr_github = generate_qr_code(github_url, 70)
    qr_deployed = generate_qr_code(deployed_url, 70)
    
    # Links table
    link_style = ParagraphStyle(
        'Link',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor("#0066CC"),
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    # Create QR codes as images
    qr1_path = "/tmp/qr_github.png"
    qr2_path = "/tmp/qr_deployed.png"
    
    qr1 = qrcode.make(github_url)
    qr1.save(qr1_path)
    
    qr2 = qrcode.make(deployed_url)
    qr2.save(qr2_path)
    
    from reportlab.platypus import Image
    
    # Table with QR codes and links
    qr_img1 = Image(qr1_path, width=65, height=65)
    qr_img2 = Image(qr2_path, width=65, height=65)
    
    data = [
        [qr_img1, qr_img2],
        [Paragraph("GitHub Repository", link_style), 
         Paragraph("Deployed Product", link_style)],
        [Paragraph(github_url, ParagraphStyle('small', fontSize=8, textColor=TEXT_DARK, alignment=TA_CENTER)),
         Paragraph(deployed_url, ParagraphStyle('small2', fontSize=8, textColor=TEXT_DARK, alignment=TA_CENTER))]
    ]
    
    table = Table(data, colWidths=[width/2, width/2])
    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(Spacer(1, 10*mm))
    elements.append(table)
    
    return elements

def build_presentation():
    """Build the complete presentation"""
    output_path = "/root/QueueLess/presentation.pdf"
    
    # URLs for QR codes (update these as needed)
    GITHUB_URL = "https://github.com/yourusername/QueueLess"
    DEPLOYED_URL = "https://queueless.yourdomain.com"
    
    doc = BaseDocTemplate(
        output_path,
        pagesize=A4,
        title="QueueLess Presentation",
        author="Kamilla Iarullina",
        showBoundary=0
    )
    
    # Page dimensions
    width, height = A4
    
    # Create frame for content
    frame = Frame(
        15*mm, 15*mm,  # x, y
        width - 30*mm, height - 30*mm,  # width, height
        id='normal'
    )
    
    # Add page template
    doc.addPageTemplates([
        PageTemplate(id='all', frames=frame),
    ])
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Build all slides
    story = []
    story.extend(create_slide_0(width, height, styles))
    story.append(PageBreak())
    story.extend(create_slide_1(width, height, styles))
    story.append(PageBreak())
    story.extend(create_slide_2(width, height, styles))
    story.append(PageBreak())
    story.extend(create_slide_3(width, height, styles))
    story.append(PageBreak())
    story.extend(create_slide_4(width, height, styles, GITHUB_URL, DEPLOYED_URL))
    
    doc.build(story)
    print(f"Presentation saved to {output_path}")

if __name__ == "__main__":
    build_presentation()
