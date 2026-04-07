#!/usr/bin/env python3
"""Generate QueueLess 5-slide presentation PDF using fpdf2."""

from fpdf import FPDF
import os

QR_GH = "https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://github.com/kamillayarullina/se-toolkit-hackathon"
QR_LIVE = "https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=http://10.93.25.100:8000"

BG_DARK = (26, 26, 46)
BG_BLUE = (15, 52, 96)
BG_PURPLE = (83, 52, 131)
ACCENT = (233, 69, 96)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DIM = (140, 140, 160)
CARD_BG = (35, 35, 60)


class Presentation(FPDF):
    def __init__(self):
        super().__init__("L", "mm", "A4")
        self.set_auto_page_break(False)
        self.add_font("DejaVu", "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
        self.add_font("DejaVu", "B", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")

    # ---------- helpers ----------
    def _bg(self, r, g, b):
        self.set_fill_color(r, g, b)
        self.rect(0, 0, self.w, self.h, "F")

    def _grad_horiz(self, c1, c2):
        for i in range(int(self.w)):
            r = c1[0] + (c2[0] - c1[0]) * i / self.w
            g = c1[1] + (c2[1] - c1[1]) * i / self.w
            b = c1[2] + (c2[2] - c1[2]) * i / self.w
            self.set_draw_color(r, g, b)
            self.line(i, 0, i, self.h)

    def _accent_line(self, x, y, w):
        self.set_draw_color(*ACCENT)
        self.set_line_width(2)
        self.line(x, y, x + w, y)
        self.set_line_width(0.2)

    def _title(self, text):
        self.set_font("DejaVu", "B", 28)
        self.set_text_color(*ACCENT)
        self.text(25, 38, text)

    def _heading(self, text, y=32):
        self.set_font("DejaVu", "B", 24)
        self.set_text_color(*ACCENT)
        self.text(25, y, text)
        self._accent_line(25, y + 4, 60)

    def _bullet(self, text, x, y, size=12):
        self.set_font("DejaVu", "", size)
        self.set_text_color(*GRAY)
        self.set_text_color(*ACCENT)
        self.text(x, y, "▸ ")
        self.set_text_color(*GRAY)
        self.text(x + 6, y, text)
        return y + 8

    def _card(self, x, y, w, h):
        self.set_fill_color(*CARD_BG)
        self.set_draw_color(*ACCENT)
        self.rect(x, y, w, h, "DF")

    def _qr(self, url, x, y, label, w=150):
        import urllib.request, ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size={w}x{w}&data={url}"
        qr_path = f"/tmp/qr_{label.replace(' ', '_')}.png"
        try:
            urllib.request.urlretrieve(qr_url, qr_path, context=ctx)
            self.image(qr_path, x, y, w, w)
        except Exception:
            self.set_draw_color(*DIM)
            self.rect(x, y, w, w)
            self.set_font("DejaVu", "", 8)
            self.set_text_color(*DIM)
            self.text(x + 15, y + w / 2, "QR")

    # ---------- slide backgrounds ----------
    def slide_1_bg(self):
        self._grad_horiz(BG_DARK, BG_BLUE)

    def slide_2_bg(self):
        self._grad_horiz(BG_BLUE, BG_PURPLE)

    def slide_3_bg(self):
        self._grad_horiz(BG_PURPLE, BG_BLUE)

    def slide_4_bg(self):
        self._grad_horiz(BG_DARK, (15, 52, 96))

    def slide_5_bg(self):
        self._grad_horiz(BG_BLUE, BG_DARK)

    # ---------- slide drawing ----------
    def draw_slide_1(self):
        self.slide_1_bg()
        # Big emoji
        self.set_font("DejaVu", "", 52)
        self.set_text_color(*WHITE)
        self.text(self.w / 2 - 22, 55, "\U0001f4cb")
        # Title
        self.set_font("DejaVu", "B", 42)
        self.set_text_color(*WHITE)
        w_txt = "QueueLess"
        self.text(self.w / 2 - self.get_string_width(w_txt) / 2, 82, w_txt)
        # Subtitle
        self._accent_line(self.w / 2 - 50, 90, 100)
        self.set_font("DejaVu", "", 16)
        self.set_text_color(*ACCENT)
        sub = "A modern TA office-hour booking system with admin controls, notifications & full audit logging"
        self.text(self.w / 2 - self.get_string_width(sub) / 2, 105, sub)
        # Author info
        self.set_font("DejaVu", "", 15)
        self.set_text_color(*DIM)
        y = 130
        for line in ["Kamilla Iarullina", "k.iarullia@innopolis.university", "Group DSAI-03"]:
            self.text(self.w / 2 - self.get_string_width(line) / 2, y, line)
            y += 11

    def draw_slide_2(self):
        self.slide_2_bg()
        self._heading("Context")
        # Two columns
        x_left, x_right = 25, self.w / 2 + 10
        y = 50
        self.set_font("DejaVu", "B", 17)
        self.set_text_color(*WHITE)
        self.text(x_left, y, "End Users")
        self.text(x_right, y, "The Problem")
        y += 14
        users = [
            "Students at Innopolis University who need to",
            "book TA consultations for course help",
            "",
            "Teaching Assistants who manage their",
            "availability and office-hour schedules",
            "",
            "Administrators who configure TA schedules,",
            "block holidays, and monitor activity",
        ]
        problems = [
            "No centralized system to find and book TA",
            "office hours efficiently",
            "",
            "TAs cannot define their available hours or",
            "block dates for holidays and days off",
            "",
            "No notifications or audit trail for who",
            "booked and cancelled time slots",
        ]
        for i, line in enumerate(users):
            if line:
                y = self._bullet(line, x_left, y + 10 if i > 0 else y + 2, 11)
            else:
                y += 4
        y = 56
        for i, line in enumerate(problems):
            if line:
                y = self._bullet(line, x_right, y + 10 if i > 0 else y + 2, 11)
            else:
                y += 4
        # Solution box
        self._card(60, 155, self.w - 120, 30)
        self.set_font("DejaVu", "", 14)
        self.set_text_color(*ACCENT)
        sol = "QueueLess solves this with a self-hosted web app \u2014 browse, book, and manage TA slots in one place."
        self.text(self.w / 2 - self.get_string_width(sol) / 2, 173, sol)

    def draw_slide_3(self):
        self.slide_3_bg()
        self._heading("Implementation")
        # Left column: Tech Stack
        x_left, x_right = 25, self.w / 2 + 10
        y = 52
        self.set_font("DejaVu", "B", 16)
        self.set_text_color(*WHITE)
        self.text(x_left, y, "Tech Stack")
        y += 12
        stack = [
            "Backend: Node.js + Express.js 4",
            "Database: SQLite3 (zero-config, file-based)",
            "Frontend: Vanilla HTML / CSS / JavaScript",
            "Email: Nodemailer (Gmail SMTP)",
            "Messaging: Telegram Bot API",
            "Deployment: Docker + Docker Compose",
        ]
        for item in stack:
            y = self._bullet(item, x_left, y + 1, 11)
        # Right column: V1 -> V2
        y = 52
        self.set_font("DejaVu", "B", 16)
        self.set_text_color(*WHITE)
        self.text(x_right, y, "Version 1  \u2192  Version 2")
        y += 12
        v1 = [
            "Basic booking with overlap detection",
            "Single-week calendar view",
            "Email-only ownership for cancellation",
        ]
        for item in v1:
            y = self._bullet(item, x_right, y + 1, 11)
        y += 4
        self.set_font("DejaVu", "B", 14)
        self.set_text_color(*ACCENT)
        self.text(x_right, y, "Version 2 added:")
        y += 10
        v2 = [
            "Week / Month calendar toggle views",
            "Admin authentication (login / logout / sessions)",
            "Available hours per day + blocked dates",
            "Email & Telegram notifications",
            "Full booking history audit log",
            "Admin password change from UI",
            "Docker Compose one-command deployment",
        ]
        for item in v2:
            y = self._bullet(item, x_right, y + 1, 11)
        # TA feedback box
        self._card(40, 155, self.w - 80, 32)
        self.set_font("DejaVu", "B", 13)
        self.set_text_color(*ACCENT)
        self.text(50, 167, "TA Feedback Points Addressed")
        self.set_font("DejaVu", "", 10)
        self.set_text_color(*GRAY)
        fb = "\u2705 Admin-definable hours per day   \u2705 Block dates for holidays   \u2705 Notifications on confirm & cancel   \u2705 Full booking history log   \u2705 Protected admin actions"
        self.text(45, 180, fb)

    def draw_slide_4(self):
        self.slide_4_bg()
        self._heading("Demo")
        self.set_font("DejaVu", "B", 16)
        self.set_text_color(*WHITE)
        self.text(25, 52, "Pre-recorded video demonstration of Version 2 (with voice-over)")
        y = 66
        # Feature boxes
        features = [
            ("1.", "Browse TA list and navigate week / month calendar views"),
            ("2.", "Create a booking with name, email, telegram, date, time, duration"),
            ("3.", "Admin login (username: admin, password: admin123)"),
            ("4.", "Set available hours per day of week for each TA"),
            ("5.", "Block specific dates for holidays with optional reasons"),
            ("6.", "View booking history log with full audit trail"),
            ("7.", "Configure email & Telegram notification settings"),
            ("8.", "Change admin password in the Security tab"),
        ]
        col1_y = 66
        col2_y = 66
        for i, (num, desc) in enumerate(features):
            x = 25 if i < 4 else self.w / 2 + 5
            y = col1_y if i < 4 else col2_y
            self._card(x, y, self.w / 2 - 35, 22)
            self.set_font("DejaVu", "B", 14)
            self.set_text_color(*ACCENT)
            self.text(x + 5, y + 13, num)
            self.set_font("DejaVu", "", 11)
            self.set_text_color(*GRAY)
            self.text(x + 20, y + 13, desc)
            if i < 4:
                col1_y += 28
            else:
                col2_y += 28
        # Note
        self.set_font("DejaVu", "", 12)
        self.set_text_color(*DIM)
        note = "Live demo at http://10.93.25.100:8000  |  Admin: admin / admin123"
        self.text(self.w / 2 - self.get_string_width(note) / 2, 185, note)

    def draw_slide_5(self):
        self.slide_5_bg()
        self._heading("Links")
        # GitHub card
        self._card(25, 55, 120, 110)
        self.set_font("DejaVu", "B", 14)
        self.set_text_color(*ACCENT)
        self.text(35, 72, "GitHub Repository")
        self.set_font("DejaVu", "", 9)
        self.set_text_color(*DIM)
        url1 = "https://github.com/kamillayarullina/se-toolkit-hackathon"
        self.text(30, 84, url1)
        self._qr(url1, 70, 95, "github")
        self.set_font("DejaVu", "", 9)
        self.set_text_color(*DIM)
        self.text(35, 158, "Scan to open the repo")
        # Live product card
        self._card(165, 55, 120, 110)
        self.set_font("DejaVu", "B", 14)
        self.set_text_color(*ACCENT)
        self.text(175, 72, "Deployed Product")
        self.set_font("DejaVu", "", 9)
        self.set_text_color(*DIM)
        url2 = "http://10.93.25.100:8000"
        self.text(185, 84, url2)
        self._qr(url2, 220, 95, "live")
        self.set_font("DejaVu", "", 9)
        self.set_text_color(*DIM)
        self.text(185, 158, "Scan to open the app")
        # Thank you
        self.set_font("DejaVu", "B", 22)
        self.set_text_color(*WHITE)
        ty = "Thank you!"
        self.text(self.w / 2 - self.get_string_width(ty) / 2, 185, ty)
        self.set_font("DejaVu", "", 11)
        self.set_text_color(*DIM)
        cred = "Admin credentials: admin / admin123"
        self.text(self.w / 2 - self.get_string_width(cred) / 2, 198, cred)


# ---------- generate ----------
pdf = Presentation()

# Slide 1
pdf.add_page()
pdf.draw_slide_1()

# Slide 2
pdf.add_page()
pdf.draw_slide_2()

# Slide 3
pdf.add_page()
pdf.draw_slide_3()

# Slide 4
pdf.add_page()
pdf.draw_slide_4()

# Slide 5
pdf.add_page()
pdf.draw_slide_5()

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "presentation.pdf")
pdf.output(out)
print(f"PDF written to {out}  ({os.path.getsize(out) / 1024:.0f} KB)")
