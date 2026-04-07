const sqlite3 = require("sqlite3").verbose();
const path = require("path");

// Allow overriding the DB path via environment variable (useful for Docker volumes)
const DB_PATH = process.env.DB_PATH || path.join(__dirname, "bookings.db");

const db = new sqlite3.Database(DB_PATH, (err) => {
  if (err) {
    console.error("SQLite connection error:", err.message);
  } else {
    console.log("Connected to SQLite database.");
  }
});

db.run("PRAGMA journal_mode = WAL");

// ==================== TAs Table ====================
db.run(
  `CREATE TABLE IF NOT EXISTS tas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    subject TEXT NOT NULL
  )`,
  (err) => {
    if (err) {
      console.error("Error creating tas table:", err.message);
    } else {
      db.get("SELECT COUNT(*) as count FROM tas", [], (err, row) => {
        if (!err && row.count === 0) {
          const stmt = db.prepare("INSERT INTO tas (name, subject) VALUES (?, ?)");
          stmt.run("Alice Petrova", "CS101 — Intro to Computer Science");
          stmt.run("Bob Ivanov", "MATH201 — Linear Algebra");
          stmt.run("Charlie Sidorov", "CS202 — Data Structures");
          stmt.run("Diana Kuznetsova", "ENG101 — Academic English");
          stmt.finalize((err) => {
            if (err) console.error("Error seeding TAs:", err.message);
            else console.log("Default TAs seeded.");
          });
        }
      });
    }
  }
);

// ==================== Bookings Table ====================
db.run(
  `CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    telegram TEXT NOT NULL,
    start TEXT NOT NULL,
    duration INTEGER NOT NULL,
    ta_id INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (ta_id) REFERENCES tas(id)
  )`,
  (err) => {
    if (err) console.error("Error creating bookings table:", err.message);
    else console.log("Bookings table is ready.");
  }
);

// Migration: add ta_id column if it doesn't exist
db.all("PRAGMA table_info(bookings)", [], (err, rows) => {
  if (err) {
    console.error("Error checking bookings schema:", err.message);
    return;
  }
  const hasTaId = rows.some((r) => r.name === "ta_id");
  if (!hasTaId) {
    db.run("ALTER TABLE bookings ADD COLUMN ta_id INTEGER NOT NULL DEFAULT 1", (err) => {
      if (err) console.error("Migration error adding ta_id:", err.message);
      else console.log("Migration: added ta_id column to bookings.");
    });
  }
});

// ==================== Admin Available Hours Table ====================
// Stores per-day-of-week available hours. day_of_week: 0=Sun..6=Sat
// Each row defines a window like "Mon 09:00-17:00"
db.run(
  `CREATE TABLE IF NOT EXISTS admin_hours (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ta_id INTEGER NOT NULL DEFAULT 0,
    day_of_week INTEGER NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    FOREIGN KEY (ta_id) REFERENCES tas(id)
  )`,
  (err) => {
    if (err) console.error("Error creating admin_hours table:", err.message);
    else console.log("Admin hours table is ready.");
  }
);

// ==================== Blocked Dates Table ====================
db.run(
  `CREATE TABLE IF NOT EXISTS blocked_dates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ta_id INTEGER NOT NULL DEFAULT 0,
    date TEXT NOT NULL,
    reason TEXT DEFAULT ''
  )`,
  (err) => {
    if (err) console.error("Error creating blocked_dates table:", err.message);
    else console.log("Blocked dates table is ready.");
  }
);

// ==================== Booking History Log Table ====================
db.run(
  `CREATE TABLE IF NOT EXISTS booking_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER,
    action TEXT NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    telegram TEXT NOT NULL,
    start TEXT,
    duration INTEGER,
    ta_id INTEGER,
    ta_name TEXT,
    performed_by TEXT DEFAULT '',
    performed_at TEXT NOT NULL
  )`,
  (err) => {
    if (err) console.error("Error creating booking_history table:", err.message);
    else console.log("Booking history table is ready.");
  }
);

// ==================== Notification Config Table ====================
db.run(
  `CREATE TABLE IF NOT EXISTS notification_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL
  )`,
  (err) => {
    if (err) console.error("Error creating notification_config table:", err.message);
    else console.log("Notification config table is ready.");
  }
);

// Seed default notification config if empty
db.get("SELECT COUNT(*) as count FROM notification_config", [], (err, row) => {
  if (!err && row.count === 0) {
    const stmt = db.prepare("INSERT INTO notification_config (key, value) VALUES (?, ?)");
    stmt.run("email_enabled", "false");
    stmt.run("email_from", "");
    stmt.run("email_password", "");
    stmt.run("email_to", "");
    stmt.run("telegram_enabled", "false");
    stmt.run("telegram_bot_token", "");
    stmt.run("telegram_chat_id", "");
    stmt.finalize((err) => {
      if (err) console.error("Error seeding notification config:", err.message);
      else console.log("Notification config seeded.");
    });
  }
});

module.exports = db;
