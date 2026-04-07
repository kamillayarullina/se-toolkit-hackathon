#!/usr/bin/env python3
"""Generate QueueLess 5-slide presentation PDF with elegant light-pink design."""

from fpdf import FPDF
import os, math, urllib.request, ssl

# ── colour palette ──────────────────────────────────────────────
BG       = (255, 245, 247)
PINK1    = (252, 228, 236)
PINK2    = (248, 187, 208)
PINK3    = (244, 143, 177)
PINK4    = (233, 30, 99)
ROSE     = (194, 24, 91)
WHITE    = (255, 255, 255)
CARD     = (255, 255, 255)
GRAY     = (120, 120, 130)
DIM      = (170, 170, 180)

URL_GH   = "https://github.com/kamillayarullina/se-toolkit-hackathon"
URL_LIVE = "http://10.93.25.100:8000"

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

W, H = 297, 210


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

    def _deco_circle(self, x, y, r, c):
        steps = 48
        pts = [(x + r * math.cos(a), y + r * math.sin(a))
               for a in [2 * math.pi * i / steps for i in range(steps + 1)]]
        self.set_fill_color(*c)
        self.polygon(pts, style="F")

    def _top_bar(self):
        self.set_fill_color(*PINK3)
        self.rect(0, 0, W, 3.5, "F")

    def _slide_num(self, n):
        self.set_font("D", "B", 9)
        self.set_text_color(*DIM)
        self.text(W - 18, H - 6, f"{n} / 5")

    def _title_bar(self, text):
        self.set_font("D", "B", 22)
        self.set_text_color(*ROSE)
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
        self.text(x, y, "\u2022")
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

    # ── text-in-card helper ─────────────────────────────────────
    def _text_in_card(self, x, y, w, lines, line_height=6, start_y_offset=14, font_size=9):
        """Write multiple lines of text inside a card, properly positioned."""
        cy = y + start_y_offset
        for line in lines:
            self.set_font("D", "", font_size)
            self.set_text_color(*GRAY)
            self.text(x + 10, cy, line)
            cy += line_height

    # ===================================================================
    # SLIDES
    # ===================================================================
    def slide_1(self):
        self.add_page()
        self._bg()
        self._top_bar()
        self._slide_num(1)

        # decorative circles
        self._deco_circle(260, 175, 95, PINK1)
        self._deco_circle(275, 195, 60, PINK2)
        self._deco_circle(45, 190, 75, PINK1)

        # title
        self.set_font("D", "B", 48)
        self.set_text_color(*ROSE)
        t = "QueueLess"
        self.text(W / 2 - self.get_string_width(t) / 2, 80, t)

        # underline
        self.set_fill_color(*PINK3)
        tw = self.get_string_width(t)
        self.rect(W / 2 - tw / 2, 85, tw, 1.5, "F")

        # subtitle
        self.set_font("D", "", 14)
        self.set_text_color(*GRAY)
        sub1 = "A modern TA office-hour booking system"
        sub2 = "with admin controls, notifications & full audit logging"
        self.text(W / 2 - self.get_string_width(sub1) / 2, 98, sub1)
        self.text(W / 2 - self.get_string_width(sub2) / 2, 108, sub2)

        # author card
        cx, cy, cw, ch = W / 2 - 80, 125, 160, 50
        self._card(cx, cy, cw, ch)
        # pink left stripe
        self.set_fill_color(*PINK4)
        self.rect(cx, cy, 4, ch, "F")

        self.set_font("D", "B", 18)
        self.set_text_color(*ROSE)
        self.text(cx + 18, cy + 17, "Kamilla Iarullina")

        self.set_font("D", "", 12)
        self.set_text_color(*GRAY)
        self.text(cx + 18, cy + 30, "k.iarullia@innopolis.university")
        self.text(cx + 18, cy + 41, "Group DSAI-03")

    def slide_2(self):
        self.add_page()
        self._bg()
        self._top_bar()
        self._slide_num(2)
        self._deco_circle(265, 185, 80, PINK1)
        self._title_bar("Context")

        lx, rx = 30, W / 2 + 5
        y = 58
        card_h = 72

        # --- Left card: End Users ---
        self._card(lx, y, W / 2 - 40, card_h)
        self.set_font("D", "B", 14)
        self.set_text_color(*ROSE)
        self.text(lx + 12, y + 14, "End Users")
        self.set_fill_color(*PINK1)
        self.rect(lx + 12, y + 17, 55, 0.8, "F")

        user_lines = [
            "\u2022  Students who need to book TA consultations",
            "   for course help and office hours",
            "",
            "\u2022  Teaching Assistants managing their",
            "   availability and schedules",
            "",
            "\u2022  Administrators configuring TA schedules,",
            "   blocking holidays & monitoring activity",
        ]
        uy = y + 24
        for line in user_lines:
            if line.startswith("\u2022"):
                self.set_font("D", "", 9)
                self.set_text_color(*PINK4)
                self.text(lx + 14, uy, "\u2022")
                self.set_text_color(*GRAY)
                self.text(lx + 21, uy, line[2:])
                uy += 7
            elif line.strip():
                self.set_font("D", "", 9)
                self.set_text_color(*GRAY)
                self.text(lx + 21, uy, line.strip())
                uy += 7
            else:
                uy += 2

        # --- Right card: The Problem ---
        self._card(rx, y, W / 2 - 40, card_h)
        self.set_font("D", "B", 14)
        self.set_text_color(*ROSE)
        self.text(rx + 12, y + 14, "The Problem")
        self.set_fill_color(*PINK1)
        self.rect(rx + 12, y + 17, 55, 0.8, "F")

        prob_lines = [
            "\u2022  No centralized system to find and book",
            "   TA office hours efficiently",
            "",
            "\u2022  TAs cannot define available hours or block",
            "   dates for holidays and days off",
            "",
            "\u2022  No notifications or audit trail for who",
            "   booked and cancelled time slots",
        ]
        py = y + 24
        for line in prob_lines:
            if line.startswith("\u2022"):
                self.set_font("D", "", 9)
                self.set_text_color(*PINK4)
                self.text(rx + 14, py, "\u2022")
                self.set_text_color(*GRAY)
                self.text(rx + 21, py, line[2:])
                py += 7
            elif line.strip():
                self.set_font("D", "", 9)
                self.set_text_color(*GRAY)
                self.text(rx + 21, py, line.strip())
                py += 7
            else:
                py += 2

        # --- Solution banner ---
        bx, by, bw, bh = 55, 144, W - 110, 38
        self._card(bx, by, bw, bh)
        self.set_fill_color(*PINK4)
        self.rect(bx, by, 4, bh, "F")
        self.set_font("D", "B", 14)
        self.set_text_color(*ROSE)
        self.text(bx + 16, by + 16, "Our Solution")
        self.set_fill_color(*PINK1)
        self.rect(bx + 16, by + 19, 60, 0.8, "F")
        self.set_font("D", "", 12)
        self.set_text_color(*GRAY)
        sol = "QueueLess is a self-hosted web app  \u2014  browse, book, and manage TA slots in one place."
        self.text(bx + 16, by + 30, sol)

    def slide_3(self):
        self.add_page()
        self._bg()
        self._top_bar()
        self._slide_num(3)
        self._deco_circle(260, 180, 85, PINK1)
        self._title_bar("Implementation")

        lx, rx = 30, W / 2 + 5
        y = 58
        card_h = 62

        # --- Tech Stack card ---
        self._card(lx, y, W / 2 - 40, card_h)
        self.set_font("D", "B", 14)
        self.set_text_color(*ROSE)
        self.text(lx + 12, y + 14, "Tech Stack")
        self.set_fill_color(*PINK1)
        self.rect(lx + 12, y + 17, 55, 0.8, "F")

        stack = [
            "\u2022  Backend: Node.js + Express.js 4",
            "\u2022  Database: SQLite3 (zero-config, file-based)",
            "\u2022  Frontend: Vanilla HTML / CSS / JavaScript",
            "\u2022  Email: Nodemailer (Gmail SMTP)",
            "\u2022  Messaging: Telegram Bot API",
            "\u2022  Deployment: Docker + Docker Compose",
        ]
        sy = y + 24
        for item in stack:
            self.set_font("D", "", 9)
            self.set_text_color(*PINK4)
            self.text(lx + 14, sy, "\u2022")
            self.set_text_color(*GRAY)
            self.text(lx + 21, sy, item[2:])
            sy += 7

        # --- V1 -> V2 card ---
        self._card(rx, y, W / 2 - 40, card_h)
        self.set_font("D", "B", 14)
        self.set_text_color(*ROSE)
        self.text(rx + 12, y + 14, "Version 1  \u2192  Version 2")
        self.set_fill_color(*PINK1)
        self.rect(rx + 12, y + 17, 55, 0.8, "F")

        self.set_font("D", "B", 8)
        self.set_text_color(*DIM)
        self.text(rx + 14, y + 24, "V1:")
        self.set_font("D", "", 8)
        self.set_text_color(*GRAY)
        v1 = ["Basic booking with overlap detection",
              "Single-week calendar view",
              "Email-only ownership for cancellation"]
        vy = y + 31
        for item in v1:
            self.text(rx + 14, vy, item)
            vy += 6

        self.set_font("D", "B", 8)
        self.set_text_color(*PINK4)
        self.text(rx + 14, vy + 1, "V2 added:")
        vy += 7
        v2 = ["Week / Month calendar toggle",
              "Admin authentication (login/logout/sessions)",
              "Available hours per day + blocked dates",
              "Email & Telegram notifications",
              "Full booking history audit log",
              "Admin password change from UI",
              "Docker Compose one-command deploy"]
        for item in v2:
            self.set_font("D", "", 8)
            self.set_text_color(*GRAY)
            self.text(rx + 14, vy, "\u2022  " + item)
            vy += 6

        # --- TA feedback banner ---
        bx, by, bw, bh = 40, 135, W - 80, 52
        self._card(bx, by, bw, bh)
        self.set_fill_color(*PINK4)
        self.rect(bx, by, 4, bh, "F")
        self.set_font("D", "B", 13)
        self.set_text_color(*ROSE)
        self.text(bx + 16, by + 14, "TA Feedback Points Addressed")
        self.set_fill_color(*PINK1)
        self.rect(bx + 16, by + 17, 60, 0.8, "F")

        fb = [
            "\u2713  Admin-definable hours per day",
            "\u2713  Block dates for holidays",
            "\u2713  Notifications on confirm & cancel",
            "\u2713  Full booking history log",
            "\u2713  Protected admin actions with auth",
        ]
        fx, fy = bx + 18, by + 26
        for item in fb:
            self.set_font("D", "", 11)
            self.set_text_color(*GRAY)
            self.text(fx, fy, item)
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
        self.text(30, 50, "Feature walkthrough of Version 2")

        # 2 rows x 4 cols of feature cards
        features = [
            ("1", "Browse TA list and navigate", "week / month calendar views"),
            ("2", "Create a booking with name,", "email, telegram, date, time"),
            ("3", "Admin login to access", "management panel"),
            ("4", "Set available hours per day", "of week for each TA"),
            ("5", "Block specific dates for", "holidays with reasons"),
            ("6", "View booking history log with", "full audit trail of actions"),
            ("7", "Configure email & Telegram", "notification settings in UI"),
            ("8", "Change admin password in the", "dedicated Security tab"),
        ]
        cols = 4
        rows = 2
        card_w = 64
        card_h = 38
        gap = 6
        total_w = cols * card_w + (cols - 1) * gap
        start_x = (W - total_w) / 2
        start_y = 58

        for idx, (num, line1, line2) in enumerate(features):
            c = idx % cols
            r = idx // cols
            cx = start_x + c * (card_w + gap)
            cy = start_y + r * (card_h + gap)
            self._card(cx, cy, card_w, card_h)

            # number badge
            self.set_fill_color(*PINK4)
            self.circle(cx + 7, cy + 7, 5.5, style="F")
            self.set_font("D", "B", 9)
            self.set_text_color(*WHITE)
            self.text(cx + 4.5, cy + 10, num)

            # text
            self.set_font("D", "", 9)
            self.set_text_color(*GRAY)
            self.text(cx + 16, cy + 15, line1)
            self.text(cx + 16, cy + 24, line2)

        # live note
        self.set_font("D", "B", 11)
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

        # --- GitHub card ---
        gx, gy, gw, gh = 50, 60, 85, 105
        self._card(gx, gy, gw, gh)
        self._qr(URL_GH, gx + gw / 2 - 18, gy + 10, 36)
        self.set_font("D", "B", 12)
        self.set_text_color(*ROSE)
        gh_label = "GitHub Repository"
        self.text(gx + gw / 2 - self.get_string_width(gh_label) / 2, gy + 58, gh_label)
        self.set_font("D", "", 6)
        self.set_text_color(*DIM)
        self.text(gx + 6, gy + 68, URL_GH)
        self.set_font("D", "", 8)
        self.set_text_color(*GRAY)
        scan_label = "Scan to open the repo"
        self.text(gx + gw / 2 - self.get_string_width(scan_label) / 2, gy + 92, scan_label)

        # --- Live product card ---
        lx_c = W - 50 - gw
        ly_c = 60
        self._card(lx_c, ly_c, gw, gh)
        self._qr(URL_LIVE, lx_c + gw / 2 - 18, ly_c + 10, 36)
        self.set_font("D", "B", 12)
        self.set_text_color(*ROSE)
        live_label = "Deployed Product"
        self.text(lx_c + gw / 2 - self.get_string_width(live_label) / 2, ly_c + 58, live_label)
        self.set_font("D", "", 6)
        self.set_text_color(*DIM)
        self.text(lx_c + 10, ly_c + 68, URL_LIVE)
        self.set_font("D", "", 8)
        self.set_text_color(*GRAY)
        scan2_label = "Scan to open the app"
        self.text(lx_c + gw / 2 - self.get_string_width(scan2_label) / 2, ly_c + 92, scan2_label)

        # --- Presentation card (center) ---
        px, py, pw, ph = W / 2 - 40, 60, 80, 105
        self._card(px, py, pw, ph)
        self.set_fill_color(*PINK4)
        self.rect(px, py, 4, ph, "F")
        self.set_font("D", "B", 12)
        self.set_text_color(*ROSE)
        pres_label = "Presentation"
        self.text(px + 14, py + 16, pres_label)
        self.set_fill_color(*PINK1)
        self.rect(px + 14, py + 19, 50, 0.8, "F")
        self.set_font("D", "", 9)
        self.set_text_color(*GRAY)
        pres_lines = [
            "5-slide PDF with:",
            "",
            "  1. Title & author info",
            "  2. Context & problem",
            "  3. Implementation",
            "  4. Demo walkthrough",
            "  5. Links & QR codes",
            "",
            "File: presentation.pdf",
            "Source: gen_pdf.py",
        ]
        ply = py + 30
        for line in pres_lines:
            if line:
                self.set_font("D", "", 9)
                self.set_text_color(*GRAY)
                self.text(px + 14, ply, line)
            ply += 6.5

        # thank you
        self.set_font("D", "B", 24)
        self.set_text_color(*ROSE)
        ty_text = "Thank you!"
        self.text(W / 2 - self.get_string_width(ty_text) / 2, 188, ty_text)


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
