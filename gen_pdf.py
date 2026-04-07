#!/usr/bin/env python3
"""Generate QueueLess 5-slide presentation PDF with elegant light-pink design."""

from fpdf import FPDF
import os, math, urllib.request, ssl

# ── colour palette ──────────────────────────────────────────────
BG       = (255, 245, 247)   # very light pink background
PINK1    = (252, 228, 236)   # soft pink
PINK2    = (248, 187, 208)   # medium pink
PINK3    = (244, 143, 177)   # accent pink
PINK4    = (233, 30, 99)     # deep pink
ROSE     = (194, 24, 91)     # dark rose
WHITE    = (255, 255, 255)
CARD     = (255, 255, 255)   # white card bg
GRAY     = (120, 120, 130)
DIM      = (170, 170, 180)
ACCENT   = PINK4
ACCENT2  = ROSE

# ── QR URLs ─────────────────────────────────────────────────────
URL_GH   = "https://github.com/kamillayarullina/se-toolkit-hackathon"
URL_LIVE = "http://10.93.25.100:8000"

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

W, H = 297, 210  # A4 landscape mm


class PDF(FPDF):
    def __init__(self):
        super().__init__("L", "mm", "A4")
        self.set_auto_page_break(False)
        self.add_font("D", "", FONT)
        self.add_font("D", "B", FONTB)

    # ── background helpers ──────────────────────────────────────
    def _bg(self):
        self.set_fill_color(*BG)
        self.rect(0, 0, W, H, "F")

    def _deco_circle(self, x, y, r, c, alpha=20):
        """Draw a semi-transparent circle for decoration."""
        self.set_fill_color(*c)
        steps = 48
        pts = [(x + r * math.cos(a), y + r * math.sin(a)) for a in [2 * math.pi * i / steps for i in range(steps + 1)]]
        self.polygon(pts, style="F")

    def _top_bar(self):
        """Thin pink accent bar at top."""
        self.set_fill_color(*PINK3)
        self.rect(0, 0, W, 3.5, "F")

    def _slide_num(self, n):
        self.set_font("D", "B", 9)
        self.set_text_color(*DIM)
        self.text(W - 18, H - 6, f"{n} / 5")

    def _title_bar(self, text):
        """Section title with pink underline."""
        self.set_font("D", "B", 22)
        self.set_text_color(*ACCENT2)
        self.text(30, 38, text)
        tw = self.get_string_width(text)
        self.set_fill_color(*PINK3)
        self.rect(30, 42, tw, 1.5, "F")

    # ── content helpers ─────────────────────────────────────────
    def _card(self, x, y, w, h):
        self.set_fill_color(*CARD)
        self.set_draw_color(*PINK2)
        self.set_line_width(0.4)
        self.rect(x, y, w, h, "DF")
        self.set_line_width(0.2)

    def _bullet(self, x, y, text, size=10):
        self.set_font("D", "B", size)
        self.set_text_color(*PINK4)
        self.text(x, y, "●")
        self.set_font("D", "", size)
        self.set_text_color(*GRAY)
        self.text(x + 6, y, text)
        return y + 7

    def _qr(self, url, x, y, sz=32):
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size={sz*3}x{sz*3}&data={url}"
        p = f"/tmp/qr_{hash(url) & 0xFFFFFF:06x}.png"
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            urllib.request.urlretrieve(qr_url, p, context=ctx)
            self.image(p, x, y, sz, sz)
        except Exception:
            self.set_draw_color(*DIM)
            self.rect(x, y, sz, sz)

    # ===================================================================
    # SLIDES
    # ===================================================================
    def slide_1(self):
        self.add_page()
        self._bg()
        self._top_bar()
        self._slide_num(1)

        # decorative circles
        self._deco_circle(250, 180, 90, PINK1)
        self._deco_circle(270, 195, 55, PINK2)
        self._deco_circle(40, 190, 70, PINK1)

        # big emoji
        self.set_font("D", "", 56)
        self.set_text_color(*PINK4)
        self.set_text_color(*PINK4); self.text(W/2 - 25, 82, "QUEUE")

        # title
        self.set_font("D", "B", 44)
        self.set_text_color(*ROSE)
        t = "QueueLess"
        self.text(W / 2 - self.get_string_width(t) / 2, 100, t)

        # subtitle
        self.set_fill_color(*PINK3)
        self.rect(W / 2 - 55, 106, 110, 1.2, "F")

        self.set_font("D", "", 13)
        self.set_text_color(*GRAY)
        sub = "A modern TA office-hour booking system with admin controls,"
        self.text(W / 2 - self.get_string_width(sub) / 2, 116, sub)
        sub2 = "notifications & full audit logging"
        self.text(W / 2 - self.get_string_width(sub2) / 2, 125, sub2)

        # author card
        cx, cy, cw, ch = W / 2 - 75, 142, 150, 40
        self._card(cx, cy, cw, ch)
        self.set_font("D", "B", 16)
        self.set_text_color(*ROSE)
        self.text(cx + 15, cy + 15, "Kamilla Iarullina")
        self.set_font("D", "", 11)
        self.set_text_color(*GRAY)
        self.text(cx + 15, cy + 27, "k.iarullia@innopolis.university")
        self.text(cx + 15, cy + 36, "Group DSAI-03")

        # small pink dot decoration left of card
        self._deco_circle(cx - 8, cy + ch / 2, 5, PINK3)

    def slide_2(self):
        self.add_page()
        self._bg()
        self._top_bar()
        self._slide_num(2)
        self._deco_circle(265, 185, 80, PINK1)
        self._title_bar("Context")

        # two-column layout
        lx, rx = 30, W / 2 + 5
        y = 58
        # left card: End Users
        self._card(lx, y, W / 2 - 40, 70)
        self.set_font("D", "B", 14)
        self.set_text_color(*ROSE)
        self.text(lx + 10, y + 14, "End Users")
        self.set_fill_color(*PINK1)
        self.rect(lx + 10, y + 17, 50, 0.8, "F")
        users = [
            "Students who need to book TA consultations",
            "for course help and office hours",
            "",
            "Teaching Assistants managing their",
            "availability and schedules",
            "",
            "Administrators configuring TA schedules,",
            "blocking holidays & monitoring activity",
        ]
        uy = y + 24
        for line in users:
            if line:
                uy = self._bullet(lx + 12, uy + (uy > y + 24 and 1 or 0), line, 9)
            else:
                uy += 3

        # right card: The Problem
        self._card(rx, y, W / 2 - 40, 70)
        self.set_font("D", "B", 14)
        self.set_text_color(*ROSE)
        self.text(rx + 10, y + 14, "The Problem")
        self.set_fill_color(*PINK1)
        self.rect(rx + 10, y + 17, 50, 0.8, "F")
        problems = [
            "No centralized system to find and book TA",
            "office hours efficiently",
            "",
            "TAs cannot define available hours or block",
            "dates for holidays and days off",
            "",
            "No notifications or audit trail for who",
            "booked and cancelled time slots",
        ]
        py = y + 24
        for line in problems:
            if line:
                py = self._bullet(rx + 12, py + (py > y + 24 and 1 or 0), line, 9)
            else:
                py += 3

        # solution banner
        bx, by, bw, bh = 55, 142, W - 110, 38
        self._card(bx, by, bw, bh)
        # left pink accent stripe
        self.set_fill_color(*PINK4)
        self.rect(bx, by, 4, bh, "F")
        self.set_font("D", "B", 14)
        self.set_text_color(*ROSE)
        self.text(bx + 14, by + 14, "Our Solution")
        self.set_font("D", "", 12)
        self.set_text_color(*GRAY)
        sol = "QueueLess is a self-hosted web app \u2014 browse, book, and manage TA slots in one place."
        self.text(bx + 14, by + 28, sol)

    def slide_3(self):
        self.add_page()
        self._bg()
        self._top_bar()
        self._slide_num(3)
        self._deco_circle(260, 180, 85, PINK1)
        self._title_bar("Implementation")

        lx, rx = 30, W / 2 + 5
        y = 58

        # Tech Stack card
        self._card(lx, y, W / 2 - 40, 60)
        self.set_font("D", "B", 14)
        self.set_text_color(*ROSE)
        self.text(lx + 10, y + 14, "Tech Stack")
        self.set_fill_color(*PINK1)
        self.rect(lx + 10, y + 17, 50, 0.8, "F")
        stack = [
            "Backend: Node.js + Express.js 4",
            "Database: SQLite3 (zero-config, file-based)",
            "Frontend: Vanilla HTML / CSS / JavaScript",
            "Email: Nodemailer (Gmail SMTP)",
            "Messaging: Telegram Bot API",
            "Deployment: Docker + Docker Compose",
        ]
        sy = y + 24
        for item in stack:
            sy = self._bullet(lx + 12, sy + (sy > y + 24 and 1 or 0), item, 9)

        # V1 -> V2 card
        self._card(rx, y, W / 2 - 40, 60)
        self.set_font("D", "B", 14)
        self.set_text_color(*ROSE)
        self.text(rx + 10, y + 14, "Version 1  \u2192  Version 2")
        self.set_fill_color(*PINK1)
        self.rect(rx + 10, y + 17, 50, 0.8, "F")
        v1 = [
            "Basic booking with overlap detection",
            "Single-week calendar view",
            "Email-only ownership for cancellation",
        ]
        vy = y + 24
        self.set_font("D", "B", 9)
        self.set_text_color(*DIM)
        self.text(rx + 12, vy, "V1:")
        vy += 6
        for item in v1:
            self.set_font("D", "", 9)
            self.set_text_color(*GRAY)
            self.text(rx + 20, vy, item)
            vy += 6
        vy += 3
        self.set_font("D", "B", 9)
        self.set_text_color(*PINK4)
        self.text(rx + 12, vy, "V2 added:")
        vy += 6
        v2 = [
            "Week / Month calendar toggle",
            "Admin authentication (login/logout/sessions)",
            "Available hours per day + blocked dates",
            "Email & Telegram notifications",
            "Full booking history audit log",
            "Admin password change from UI",
            "Docker Compose one-command deploy",
        ]
        for item in v2:
            vy = self._bullet(rx + 12, vy, item, 8)

        # TA feedback banner
        bx, by, bw, bh = 40, 135, W - 80, 50
        self._card(bx, by, bw, bh)
        self.set_fill_color(*PINK4)
        self.rect(bx, by, 4, bh, "F")
        self.set_font("D", "B", 13)
        self.set_text_color(*ROSE)
        self.text(bx + 14, by + 14, "TA Feedback Points Addressed")
        self.set_fill_color(*PINK1)
        self.rect(bx + 14, by + 17, 50, 0.8, "F")
        fb = [
            "Admin-definable hours per day",
            "Block dates for holidays",
            "Notifications on confirm & cancel",
            "Full booking history log",
            "Protected admin actions with auth",
        ]
        fx, fy = bx + 16, by + 26
        for item in fb:
            self.set_font("D", "", 10)
            self.set_text_color(*GRAY)
            self.set_text_color(*PINK4)
            self.text(fx, fy, "\u2713  ")
            self.set_text_color(*GRAY)
            self.text(fx + 7, fy, item)
            fy += 7

    def slide_4(self):
        self.add_page()
        self._bg()
        self._top_bar()
        self._slide_num(4)
        self._deco_circle(260, 185, 80, PINK1)
        self._title_bar("Demo")

        self.set_font("D", "", 11)
        self.set_text_color(*GRAY)
        desc = "Feature walkthrough of Version 2"
        self.text(30, 50, desc)

        # 2x4 grid of feature cards
        features = [
            "Browse TA list and navigate",
            "week / month calendar views",
            "",
            "Create a booking with name,",
            "email, telegram, date, time",
            "",
            "Admin login (admin / admin123)",
            "to access management panel",
            "",
            "Set available hours per day",
            "of week for each TA",
            "",
            "Block specific dates for",
            "holidays with optional reasons",
            "",
            "View booking history log with",
            "full audit trail of all actions",
            "",
            "Configure email & Telegram",
            "notification settings in UI",
            "",
            "Change admin password in the",
            "dedicated Security tab",
        ]
        cols = 4
        rows = 2
        card_w = 65
        card_h = 38
        gap_x = 6
        gap_y = 6
        total_w = cols * card_w + (cols - 1) * gap_x
        start_x = (W - total_w) / 2
        start_y = 58

        for idx in range(cols * rows):
            c = idx % cols
            r = idx // cols
            cx = start_x + c * (card_w + gap_x)
            cy = start_y + r * (card_h + gap_y)
            self._card(cx, cy, card_w, card_h)
            # number badge
            self.set_fill_color(*PINK4)
            self.set_draw_color(*PINK4)
            bx_c = cx + 5
            by_c = cy + 4
            self.circle(bx_c + 4.5, by_c + 4.5, 4.5, "F")
            self.set_font("D", "B", 8)
            self.set_text_color(*WHITE)
            self.text(bx_c + 2.5, by_c + 7, str(idx + 1))

            # text
            line1 = features[idx * 2] if idx * 2 < len(features) else ""
            line2 = features[idx * 2 + 1] if idx * 2 + 1 < len(features) else ""
            self.set_font("D", "", 8)
            self.set_text_color(*GRAY)
            self.text(cx + 14, cy + 14, line1)
            self.text(cx + 14, cy + 23, line2)

        # live note
        self.set_font("D", "B", 10)
        self.set_text_color(*ROSE)
        note = "Live: http://10.93.25.100:8000"
        self.text(W / 2 - self.get_string_width(note) / 2, 195, note)

    def slide_5(self):
        self.add_page()
        self._bg()
        self._top_bar()
        self._slide_num(5)
        self._deco_circle(260, 185, 85, PINK1)
        self._deco_circle(40, 180, 70, PINK2)
        self._title_bar("Links")

        # GitHub card
        gx, gy, gw, gh = 40, 60, 100, 110
        self._card(gx, gy, gw, gh)
        self._qr(URL_GH, gx + gw / 2 - 20, gy + 15, 40)
        self.set_font("D", "B", 12)
        self.set_text_color(*ROSE)
        self.text(gx + 10, gy + 68, "GitHub Repository")
        self.set_font("D", "", 7)
        self.set_text_color(*DIM)
        self.text(gx + 10, gy + 78, URL_GH)
        self.set_font("D", "", 8)
        self.set_text_color(*GRAY)
        self.text(gx + 20, gy + 95, "Scan to open the repo")

        # Live card
        lx_c, ly_c = W - 140, 60
        self._card(lx_c, ly_c, gw, gh)
        self._qr(URL_LIVE, lx_c + gw / 2 - 20, ly_c + 15, 40)
        self.set_font("D", "B", 12)
        self.set_text_color(*ROSE)
        self.text(lx_c + 10, ly_c + 68, "Deployed Product")
        self.set_font("D", "", 7)
        self.set_text_color(*DIM)
        self.text(lx_c + 10, ly_c + 78, URL_LIVE)
        self.set_font("D", "", 8)
        self.set_text_color(*GRAY)
        self.text(lx_c + 22, ly_c + 95, "Scan to open the app")

        # thank you
        self.set_font("D", "B", 26)
        self.set_text_color(*ROSE)
        ty = "Thank you!"
        self.text(W / 2 - self.get_string_width(ty) / 2, 190, ty)
        self.set_font("D", "", 10)
        self.set_text_color(*GRAY)
        cred = "Admin: admin / admin123"
        self.text(W / 2 - self.get_string_width(cred) / 2, 200, cred)


# ── generate ─────────────────────────────────────────────────────
pdf = PDF()
pdf.slide_1()
pdf.slide_2()
pdf.slide_3()
pdf.slide_4()
pdf.slide_5()

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "presentation.pdf")
pdf.output(out)
print(f"PDF written to {out}  ({os.path.getsize(out) / 1024:.0f} KB)")
