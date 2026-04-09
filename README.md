# QueueLess

> **A modern TA office-hour booking system** with calendar views, admin controls, notifications, and full audit logging — built with Node.js, Express, and SQLite.

**🌐 Live Demo:** [http://10.93.25.100:8000](http://10.93.25.100:8000) *(also accessible at `http://localhost:8000` when running locally)*

---

## Demo

### Screenshots

#### Booking Calendar (Week View)
The week view shows a 7-day grid with booking slots per day, navigable with previous/next buttons. Blocked dates appear with an orange highlight.

#### Booking Calendar (Month View)
The month view provides an overview of the entire month, with dots indicating days that have bookings. Blocked dates are marked with a 🚫 icon.

#### Admin Panel
The admin panel (accessible after login) allows defining available hours per day of the week, blocking dates for holidays, and configuring email/Telegram notifications.

#### Booking History
The history log shows every booking creation and cancellation with timestamps, user details, and who performed the action.

---

## Product Context

### End Users
- **Students** at Innopolis University who need to book time slots with Teaching Assistants (TAs) for consultations, help sessions, or office hours.
- **Teaching Assistants** who manage their availability and need visibility into their schedule.
- **Administrators** who configure TA availability, block holidays, and monitor booking activity.

### Problem
Students currently struggle to find and book TA office hours efficiently. TAs have no easy way to define their availability, block holidays, or track who booked/cancelled slots. There is no notification system to confirm bookings or alert admins of changes.

### Solution
QueueLess is a self-hosted web application that provides a clean calendar interface for students to browse and book TA time slots, while giving TAs and admins full control over availability, blocked dates, notifications, and a complete audit trail of all booking activity.

---

## Features

### Implemented (v2)

| Feature | Description |
|---------|-------------|
| 📅 Week/Month Calendar View | Toggle between week and month calendar views to browse bookings |
| 👤 User Booking | Students can book, view, and cancel their own slots (email ownership) |
| 🔒 Admin Authentication | Login-based admin access with session management (default: `admin` / `admin123`) |
| ⏰ Available Hours | Admin can define per-day-of-week available hours per TA |
| 🚫 Block Dates | Admin can block specific dates (holidays, days off) |
| 📧 Email Notifications | Gmail-based email on booking confirmation and cancellation |
| ✈️ Telegram Notifications | Telegram bot notifications on booking confirmation and cancellation |
| 📜 Booking History Log | Full audit trail: who booked, who cancelled, when |
| 🔑 Admin Password Change | Admins can change their password from the UI |
| 🐳 Docker Support | One-command deployment with Docker Compose |

### Not Yet Implemented (Roadmap)

| Feature | Description |
|---------|-------------|
| 📊 Analytics Dashboard | Booking statistics, popular time slots, TA utilization |
| 🔔 User Reminders | Pre-appointment reminder notifications to students |
| 📱 Mobile App | Native mobile application |
| 🔄 Recurring Bookings | Weekly/bi-weekly recurring slot reservations |
| 👥 Multi-admin Roles | Separate TA-level and super-admin roles |
| 🌐 Multi-university Support | Email domain configuration per institution |

---

## Usage

### For Students
1. Open the QueueLess website in your browser.
2. Select a TA from the left sidebar.
3. Browse the week or month calendar to see available slots.
4. Fill in the booking form: Name, Email (`@innopolis.university`), Telegram, Date, Time, Duration.
5. Click **Book Now**. You will receive a confirmation (if notifications are configured).
6. To cancel, click the **✕** button on your booking.

### For Administrators
1. Click the **⚙️ Admin** tab in the sidebar.
2. Login with admin credentials (default: `admin` / `admin123`).
3. Select a TA to manage in the admin panel.
4. Use the tabs to:
   - **Available Hours**: Define time windows per day of week
   - **Blocked Dates**: Add/remove blocked dates with reasons
   - **Notifications**: Configure Gmail and Telegram bot settings
   - **Security**: Change the admin password
5. View the **📜 History** tab for a complete audit log.

---

## Deployment

### Operating System
- **Ubuntu 24.04 LTS** (recommended; same as university VMs)
- Also compatible with any Linux distribution that supports Docker

### Prerequisites

The following must be installed on the VM:

| Software | Minimum Version | Install Command |
|----------|----------------|-----------------|
| Docker | 24.0+ | See below |
| Docker Compose | 2.20+ | Included with Docker Desktop, or install separately |
| Git | 2.30+ | `sudo apt install git` |
| curl | Any | `sudo apt install curl` |

#### Install Docker on Ubuntu 24.04

```bash
# Remove any old versions
sudo apt-get remove docker docker-engine docker.io containerd runc 2>/dev/null || true

# Install prerequisites
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Enable Docker for current user (no sudo needed)
sudo usermod -aG docker $USER
# Log out and log back in for this to take effect

# Verify
docker --version
docker compose version
```

### Step-by-Step Deployment

#### Option 1: Quick Start with Deploy Script (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/<YOUR_USERNAME>/se-toolkit-hackathon.git
cd se-toolkit-hackathon/QueueLess

# 2. Run the deploy script
./deploy.sh up

# 3. Open in browser
# http://<YOUR_SERVER_IP>:8000
```

#### Option 2: Manual Docker Compose

```bash
# 1. Clone the repository
git clone https://github.com/<YOUR_USERNAME>/se-toolkit-hackathon.git
cd se-toolkit-hackathon/QueueLess

# 2. Build and start
docker compose up -d --build

# 3. Verify
docker compose ps
curl http://localhost:8000/tas

# 4. Access the app
# http://<YOUR_SERVER_IP>:8000
```

#### Option 3: Without Docker (Node.js directly)

```bash
# 1. Clone the repository
git clone https://github.com/<YOUR_USERNAME>/se-toolkit-hackathon.git
cd se-toolkit-hackathon/QueueLess

# 2. Install dependencies
npm install

# 3. Start the server
npm start

# 4. Access the app
# http://localhost:8000
```

### Docker Management Commands

```bash
# View logs
docker compose logs -f

# Stop containers
docker compose down

# Restart
docker compose down && docker compose up -d --build

# Reset database (deletes all data)
docker compose down
docker volume rm queueless_db-data
docker compose up -d

# Check container health
docker compose ps
```

### Configuration

#### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | Server port |
| `HOST` | `0.0.0.0` | Server bind address |
| `DB_PATH` | `./bookings.db` | Path to SQLite database file |
| `NODE_ENV` | `production` | Node environment |

#### Notification Setup

1. **Email**: Enable in Admin → Notifications. Use a Gmail account with an [App Password](https://support.google.com/accounts/answer/185833).
2. **Telegram**: Create a bot via [@BotFather](https://t.me/BotFather), get the token and your chat ID, then configure in Admin → Notifications.

### Default Admin Credentials

| Username | Password |
|----------|----------|
| `admin` | `admin123` |

> ⚠️ **Change the default password immediately** after first login via Admin → Security tab.

---

## Project Structure

```
QueueLess/
├── server.js          # Express server, all API routes, auth middleware
├── db.js              # SQLite setup, schema creation, seeding
├── index.html         # Frontend HTML + embedded CSS
├── script.js          # Frontend JavaScript (all client-side logic)
├── package.json       # Node.js dependencies
├── Dockerfile         # Docker image definition
├── docker-compose.yml # Docker Compose configuration
├── deploy.sh          # Deployment helper script
├── .dockerignore      # Docker build exclusions
├── .gitignore         # Git exclusions
├── LICENSE            # MIT License
└── README.md          # This file
```

---

## API Reference

### Public Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/tas` | None | List all TAs |
| `GET` | `/tas/:id/bookings` | None | Get all bookings for a TA |
| `POST` | `/book` | None | Create a new booking |
| `DELETE` | `/bookings/:id` | Email ownership | Cancel a booking |

### Admin Endpoints (require Bearer token)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/admin/login` | Authenticate admin |
| `POST` | `/admin/logout` | Invalidate admin session |
| `GET` | `/admin/me` | Get current admin session |
| `POST` | `/admin/change-password` | Change admin password |
| `GET` | `/admin/hours/:taId` | Get admin hours for TA |
| `POST` | `/admin/hours` | Add available hour |
| `DELETE` | `/admin/hours/:id` | Remove available hour |
| `GET` | `/admin/blocked/:taId` | Get blocked dates for TA |
| `POST` | `/admin/blocked` | Block a date |
| `DELETE` | `/admin/blocked/:id` | Unblock a date |
| `GET` | `/admin/history` | Get booking history log |
| `GET` | `/admin/notifications` | Get notification config |
| `POST` | `/admin/notifications` | Update notification config |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Runtime | Node.js 20 |
| Backend | Express.js 4 |
| Database | SQLite3 |
| Frontend | Vanilla HTML/CSS/JavaScript |
| Email | Nodemailer (Gmail) |
| Messaging | Telegram Bot API |
| Containerization | Docker + Docker Compose |

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Presentation

A 5-slide PDF presentation is included at [`presentationfinal2.0.pdf`](presentationfinal2.0.pdf). Open it with any PDF viewer. Slides cover:

1. **Title** — Product name, author (Kamilla Iarullina), email, group (DSAI-03)
2. **Context** — End users, problem, solution
3. **Implementation** — Tech stack, V1→V2, TA feedback addressed
4. **Demo** — Feature walkthrough description
5. **Links** — GitHub repo and deployed product with QR codes

