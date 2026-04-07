const express = require("express");
const cors = require("cors");
const nodemailer = require("nodemailer");
const crypto = require("crypto");
const db = require("./db");

// Catch unhandled rejections to prevent crashes
process.on("unhandledRejection", (err) => {
  console.error("Unhandled Promise Rejection:", err);
});

const app = express();
const PORT = parseInt(process.env.PORT, 10) || 8000;
const HOST = process.env.HOST || "0.0.0.0";

app.use(cors({ credentials: true, origin: true }));
app.use(express.json());
app.use(express.static(__dirname));

// ==================== SESSION MANAGEMENT ====================

const sessions = new Map(); // token -> { username, createdAt }
const SESSION_TTL = 24 * 60 * 60 * 1000; // 24 hours

// Clean expired sessions every hour
setInterval(() => {
  const now = Date.now();
  for (const [token, sess] of sessions) {
    if (now - sess.createdAt > SESSION_TTL) sessions.delete(token);
  }
}, 60 * 60 * 1000);

function generateToken() {
  return crypto.randomBytes(32).toString("hex");
}

function requireAuth(req, res, next) {
  const header = req.headers["authorization"] || "";
  const token = header.startsWith("Bearer ") ? header.slice(7) : null;

  if (!token || !sessions.has(token)) {
    return res.status(401).json({ error: "Admin authentication required." });
  }

  const sess = sessions.get(token);
  if (Date.now() - sess.createdAt > SESSION_TTL) {
    sessions.delete(token);
    return res.status(401).json({ error: "Session expired. Please login again." });
  }

  req.adminUser = sess.username;
  next();
}

// ==================== ADMIN TABLE INIT ====================

db.run(
  `CREATE TABLE IF NOT EXISTS admin_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
  )`,
  (err) => {
    if (err) {
      console.error("Error creating admin_users table:", err.message);
      return;
    }
    console.log("Admin users table is ready.");
    // Seed default admin if table is empty
    db.get("SELECT COUNT(*) as count FROM admin_users", [], (err, row) => {
      if (!err && row.count === 0) {
        const hash = crypto.createHash("sha256").update("admin123").digest("hex");
        db.run(
          "INSERT INTO admin_users (username, password_hash) VALUES (?, ?)",
          ["admin", hash],
          (err) => {
            if (err) console.error("Error seeding admin user:", err.message);
            else console.log("Default admin user seeded (username: admin).");
          }
        );
      }
    });
  }
);

// ==================== AUTH ENDPOINTS ====================

// POST /admin/login
app.post("/admin/login", (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ error: "Username and password are required." });
  }

  const hash = crypto.createHash("sha256").update(password).digest("hex");

  db.get(
    "SELECT * FROM admin_users WHERE username = ? AND password_hash = ?",
    [username, hash],
    (err, row) => {
      if (err) {
        console.error(err);
        return res.status(500).json({ error: "Server error." });
      }
      if (!row) {
        return res.status(401).json({ error: "Invalid username or password." });
      }
      const token = generateToken();
      sessions.set(token, { username: row.username, createdAt: Date.now() });
      res.json({ message: "Login successful.", token, username: row.username });
    }
  );
});

// POST /admin/logout
app.post("/admin/logout", (req, res) => {
  const header = req.headers["authorization"] || "";
  const token = header.startsWith("Bearer ") ? header.slice(7) : null;
  if (token) sessions.delete(token);
  res.json({ message: "Logged out." });
});

// GET /admin/me
app.get("/admin/me", requireAuth, (req, res) => {
  res.json({ username: req.adminUser });
});

// POST /admin/change-password (authenticated)
app.post("/admin/change-password", requireAuth, (req, res) => {
  const { current_password, new_password } = req.body;
  if (!current_password || !new_password) {
    return res.status(400).json({ error: "Current and new password are required." });
  }
  if (new_password.length < 6) {
    return res.status(400).json({ error: "New password must be at least 6 characters." });
  }

  const currentHash = crypto.createHash("sha256").update(current_password).digest("hex");

  db.get(
    "SELECT * FROM admin_users WHERE username = ? AND password_hash = ?",
    [req.adminUser, currentHash],
    (err, row) => {
      if (err) return res.status(500).json({ error: "Server error." });
      if (!row) return res.status(401).json({ error: "Current password is incorrect." });

      const newHash = crypto.createHash("sha256").update(new_password).digest("hex");
      db.run(
        "UPDATE admin_users SET password_hash = ? WHERE username = ?",
        [newHash, req.adminUser],
        function (err) {
          if (err) return res.status(500).json({ error: "Failed to update password." });
          res.json({ message: "Password updated successfully." });
        }
      );
    }
  );
});

// ==================== NOTIFICATION SERVICE ====================

let mailTransporter = null;

function getMailTransporter(from, password) {
  if (mailTransporter) return mailTransporter;
  mailTransporter = nodemailer.createTransport({
    service: "gmail",
    auth: { user: from, pass: password },
  });
  return mailTransporter;
}

async function sendEmailNotification(subject, text) {
  const config = await getAllNotificationConfig();
  if (config.email_enabled !== "true") return;
  if (!config.email_from || !config.email_password || !config.email_to) return;

  try {
    const transporter = getMailTransporter(config.email_from, config.email_password);
    await transporter.sendMail({
      from: `"QueueLess" <${config.email_from}>`,
      to: config.email_to,
      subject,
      text,
    });
    console.log("[Email] Notification sent:", subject);
  } catch (err) {
    console.error("[Email] Failed to send notification:", err.message);
  }
}

async function sendTelegramNotification(text) {
  const config = await getAllNotificationConfig();
  if (config.telegram_enabled !== "true") return;
  if (!config.telegram_bot_token || !config.telegram_chat_id) return;

  try {
    const url = `https://api.telegram.org/bot${config.telegram_bot_token}/sendMessage`;
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chat_id: config.telegram_chat_id, text }),
    });
    const data = await res.json();
    if (data.ok) {
      console.log("[Telegram] Notification sent.");
    } else {
      console.error("[Telegram] Failed:", data.description);
    }
  } catch (err) {
    console.error("[Telegram] Error sending notification:", err.message);
  }
}

async function sendNotifications(action, booking, taName) {
  const dateStr = booking.start ? booking.start.split("T")[0] : "";
  const timeStr = booking.start ? booking.start.split("T")[1].substring(0, 5) : "";

  if (action === "created") {
    await sendEmailNotification(
      "QueueLess — Booking Confirmed",
      `Booking confirmed!\n\nName: ${booking.name}\nEmail: ${booking.email}\nTelegram: ${booking.telegram}\nTA: ${taName}\nDate: ${dateStr}\nTime: ${timeStr}\nDuration: ${booking.duration} min\nBooking ID: ${booking.id}`
    );
    await sendTelegramNotification(
      `📅 *Booking Confirmed*\n\n👤 Name: ${booking.name}\n📧 Email: ${booking.email}\n✈️ Telegram: ${booking.telegram}\n👨\u200d🏫 TA: ${taName}\n📆 Date: ${dateStr}\n🕐 Time: ${timeStr}\n⏱ Duration: ${booking.duration} min`
    );
  } else if (action === "cancelled") {
    await sendEmailNotification(
      "QueueLess — Booking Cancelled",
      `Booking cancelled.\n\nName: ${booking.name}\nEmail: ${booking.email}\nTA: ${taName}\nDate: ${dateStr}\nTime: ${timeStr}\nDuration: ${booking.duration} min\nBooking ID: ${booking.id}`
    );
    await sendTelegramNotification(
      `❌ *Booking Cancelled*\n\n👤 Name: ${booking.name}\n📧 Email: ${booking.email}\n👨\u200d🏫 TA: ${taName}\n📆 Date: ${dateStr}\n🕐 Time: ${timeStr}\n⏱ Duration: ${booking.duration} min`
    );
  }
}

function getAllNotificationConfig() {
  return new Promise((resolve, reject) => {
    db.all("SELECT key, value FROM notification_config", [], (err, rows) => {
      if (err) return reject(err);
      const config = {};
      rows.forEach((r) => { config[r.key] = r.value; });
      resolve(config);
    });
  });
}

// ==================== HISTORY LOGGING ====================

function logBookingHistory(action, booking, taName, performedBy) {
  return new Promise((resolve, reject) => {
    const now = new Date().toISOString();
    db.run(
      `INSERT INTO booking_history (booking_id, action, name, email, telegram, start, duration, ta_id, ta_name, performed_by, performed_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [
        booking.id || null,
        action,
        booking.name,
        booking.email,
        booking.telegram,
        booking.start || null,
        booking.duration || null,
        booking.ta_id || null,
        taName || "",
        performedBy || "",
        now,
      ],
      function (err) {
        if (err) {
          console.error("[History] Failed to log:", err.message);
          reject(err);
        } else {
          console.log(`[History] Logged: ${action} for booking ${booking.id || "unknown"}`);
          resolve(this.lastID);
        }
      }
    );
  });
}

// ==================== ADMIN HELPER: Check if a date/time is within admin hours ====================

function isWithinAdminHours(taId, dateStr, timeStr, duration, callback) {
  const d = new Date(`${dateStr}T${timeStr}:00Z`);
  const dayOfWeek = d.getUTCDay();
  const timeMinutes = parseInt(timeStr.split(":")[0], 10) * 60 + parseInt(timeStr.split(":")[1], 10);
  const endMinutes = timeMinutes + duration;

  db.get(
    "SELECT * FROM blocked_dates WHERE (ta_id = ? OR ta_id = 0) AND date = ?",
    [taId, dateStr],
    (err, blocked) => {
      if (err) return callback(err);
      if (blocked) return callback(null, { allowed: false, reason: "This date is blocked." });

      db.all(
        "SELECT * FROM admin_hours WHERE ta_id = ? AND day_of_week = ?",
        [taId, dayOfWeek],
        (err, hours) => {
          if (err) return callback(err);
          if (!hours || hours.length === 0) {
            return callback(null, { allowed: true });
          }

          const withinSlot = hours.some((h) => {
            const hStart = parseInt(h.start_time.split(":")[0], 10) * 60 + parseInt(h.start_time.split(":")[1], 10);
            const hEnd = parseInt(h.end_time.split(":")[0], 10) * 60 + parseInt(h.end_time.split(":")[1], 10);
            return timeMinutes >= hStart && endMinutes <= hEnd;
          });

          if (withinSlot) {
            callback(null, { allowed: true });
          } else {
            callback(null, { allowed: false, reason: "This time is outside the available hours." });
          }
        }
      );
    }
  );
}

function getAdminHoursForTA(taId) {
  return new Promise((resolve, reject) => {
    db.all("SELECT * FROM admin_hours WHERE ta_id = ? ORDER BY day_of_week, start_time", [taId], (err, rows) => {
      if (err) return reject(err);
      resolve(rows);
    });
  });
}

function getBlockedDatesForTA(taId) {
  return new Promise((resolve, reject) => {
    db.all("SELECT * FROM blocked_dates WHERE ta_id = ? OR ta_id = 0 ORDER BY date", [taId], (err, rows) => {
      if (err) return reject(err);
      resolve(rows);
    });
  });
}

// ==================== TA ENDPOINTS (public) ====================

app.get("/tas", (req, res) => {
  db.all("SELECT * FROM tas ORDER BY name ASC", [], (err, rows) => {
    if (err) {
      console.error(err);
      return res.status(500).json({ error: "Error retrieving TAs." });
    }
    res.json(rows);
  });
});

app.get("/tas/:id/bookings", (req, res) => {
  const taId = parseInt(req.params.id, 10);
  db.all(
    "SELECT * FROM bookings WHERE ta_id = ? ORDER BY start ASC",
    [taId],
    (err, rows) => {
      if (err) {
        console.error(err);
        return res.status(500).json({ error: "Error retrieving bookings." });
      }
      res.json(rows);
    }
  );
});

// ==================== BOOKING ENDPOINTS (public) ====================

function hasOverlap(taId, newStart, newDuration, callback) {
  const newStartTime = new Date(newStart).getTime();
  const newEndTime = newStartTime + newDuration * 60000;

  db.all(
    "SELECT start, duration FROM bookings WHERE ta_id = ?",
    [taId],
    (err, rows) => {
      if (err) return callback(err);
      const overlap = rows.some((row) => {
        const existStart = new Date(row.start).getTime();
        const existEnd = existStart + row.duration * 60000;
        return newStartTime < existEnd && newEndTime > existStart;
      });
      callback(null, overlap);
    }
  );
}

function checkAdminHours(taId, dateStr, timeStr, duration) {
  return new Promise((resolve, reject) => {
    isWithinAdminHours(taId, dateStr, timeStr, duration, (err, result) => {
      if (err) return reject(err);
      resolve(result);
    });
  });
}

function checkOverlap(taId, startISO, dur) {
  return new Promise((resolve, reject) => {
    hasOverlap(taId, startISO, dur, (err, result) => {
      if (err) return reject(err);
      resolve(result);
    });
  });
}

function getTAName(taId) {
  return new Promise((resolve, reject) => {
    db.get("SELECT name FROM tas WHERE id = ?", [taId], (err, row) => {
      if (err) return reject(err);
      resolve(row ? row.name : "Unknown");
    });
  });
}

// POST /book
app.post("/book", async (req, res) => {
  const { name, email, telegram, date, time, duration, ta_id } = req.body;

  if (!name || !email || !telegram || !date || !time || !duration || !ta_id) {
    return res.status(400).json({ error: "All fields are required." });
  }

  if (!email.endsWith("@innopolis.university")) {
    return res.status(400).json({ error: "Email must end with @innopolis.university" });
  }

  const startISO = `${date}T${time}:00.000Z`;
  const dur = parseInt(duration, 10);
  const taId = parseInt(ta_id, 10);

  try {
    const check = await checkAdminHours(taId, date, time, dur);
    if (!check.allowed) {
      return res.status(400).json({ error: check.reason });
    }

    const overlap = await checkOverlap(taId, startISO, dur);
    if (overlap) {
      return res.status(409).json({ error: "This time slot is already booked. Please choose another." });
    }

    db.run(
      "INSERT INTO bookings (name, email, telegram, start, duration, ta_id) VALUES (?, ?, ?, ?, ?, ?)",
      [name, email, telegram, startISO, dur, taId],
      async function (err) {
        if (err) {
          console.error(err);
          return res.status(500).json({ error: "Error saving the booking." });
        }

        const booking = { id: this.lastID, name, email, telegram, start: startISO, duration: dur, ta_id: taId };

        try {
          const taName = await getTAName(taId);
          await logBookingHistory("created", booking, taName, email);
          sendNotifications("created", booking, taName).catch((e) => console.error("[Notification] Error:", e.message));
        } catch (histErr) {
          console.error("[History] Error:", histErr.message);
        }

        res.status(201).json({ message: "Booking created successfully!", booking });
      }
    );
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Server error while checking availability." });
  }
});

// DELETE /bookings/:id
app.delete("/bookings/:id", async (req, res) => {
  const id = parseInt(req.params.id, 10);
  const { email } = req.body || {};

  db.get("SELECT * FROM bookings WHERE id = ?", [id], async (err, row) => {
    if (err) {
      console.error(err);
      return res.status(500).json({ error: "Server error." });
    }
    if (!row) {
      return res.status(404).json({ error: "Booking not found." });
    }
    if (row.email !== email) {
      return res.status(403).json({ error: "You can only cancel your own bookings." });
    }

    const booking = { ...row };

    db.run("DELETE FROM bookings WHERE id = ?", [id], async function (err) {
      if (err) {
        console.error(err);
        return res.status(500).json({ error: "Error deleting the booking." });
      }

      try {
        const taName = await getTAName(row.ta_id);
        await logBookingHistory("cancelled", booking, taName, email);
        sendNotifications("cancelled", booking, taName).catch((e) => console.error("[Notification] Error:", e.message));
      } catch (histErr) {
        console.error("[History] Error:", histErr.message);
      }

      res.json({ message: "Booking cancelled successfully." });
    });
  });
});

// ==================== ADMIN ENDPOINTS (all require auth) ====================

// GET /admin/hours/:taId
app.get("/admin/hours/:taId", requireAuth, async (req, res) => {
  const taId = parseInt(req.params.taId, 10);
  try {
    const hours = await getAdminHoursForTA(taId);
    res.json(hours);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Error retrieving admin hours." });
  }
});

// POST /admin/hours
app.post("/admin/hours", requireAuth, (req, res) => {
  const { ta_id, day_of_week, start_time, end_time } = req.body;
  if (!ta_id || day_of_week === undefined || !start_time || !end_time) {
    return res.status(400).json({ error: "All fields required: ta_id, day_of_week, start_time, end_time" });
  }

  db.run(
    "INSERT INTO admin_hours (ta_id, day_of_week, start_time, end_time) VALUES (?, ?, ?, ?)",
    [ta_id, parseInt(day_of_week, 10), start_time, end_time],
    function (err) {
      if (err) return res.status(500).json({ error: "Error saving admin hours." });
      res.status(201).json({ message: "Admin hour added.", id: this.lastID });
    }
  );
});

// DELETE /admin/hours/:id
app.delete("/admin/hours/:id", requireAuth, (req, res) => {
  const id = parseInt(req.params.id, 10);
  db.run("DELETE FROM admin_hours WHERE id = ?", [id], function (err) {
    if (err) return res.status(500).json({ error: "Error deleting admin hour." });
    res.json({ message: "Admin hour deleted." });
  });
});

// GET /admin/blocked/:taId
app.get("/admin/blocked/:taId", requireAuth, async (req, res) => {
  const taId = parseInt(req.params.taId, 10);
  try {
    const blocked = await getBlockedDatesForTA(taId);
    res.json(blocked);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Error retrieving blocked dates." });
  }
});

// POST /admin/blocked
app.post("/admin/blocked", requireAuth, (req, res) => {
  const { ta_id, date, reason } = req.body;
  if (!ta_id || !date) {
    return res.status(400).json({ error: "ta_id and date are required." });
  }

  db.run(
    "INSERT INTO blocked_dates (ta_id, date, reason) VALUES (?, ?, ?)",
    [ta_id, date, reason || ""],
    function (err) {
      if (err) return res.status(500).json({ error: "Error saving blocked date." });
      res.status(201).json({ message: "Blocked date added.", id: this.lastID });
    }
  );
});

// DELETE /admin/blocked/:id
app.delete("/admin/blocked/:id", requireAuth, (req, res) => {
  const id = parseInt(req.params.id, 10);
  db.run("DELETE FROM blocked_dates WHERE id = ?", [id], function (err) {
    if (err) return res.status(500).json({ error: "Error deleting blocked date." });
    res.json({ message: "Blocked date deleted." });
  });
});

// GET /admin/history
app.get("/admin/history", requireAuth, (req, res) => {
  const { ta_id, limit, offset } = req.query;
  const lim = parseInt(limit, 10) || 200;
  const off = parseInt(offset, 10) || 0;

  let sql = "SELECT * FROM booking_history";
  const params = [];

  if (ta_id) {
    sql += " WHERE ta_id = ?";
    params.push(parseInt(ta_id, 10));
  }

  sql += " ORDER BY performed_at DESC LIMIT ? OFFSET ?";
  params.push(lim, off);

  db.all(sql, params, (err, rows) => {
    if (err) {
      console.error(err);
      return res.status(500).json({ error: "Error retrieving booking history." });
    }
    res.json(rows);
  });
});

// GET /admin/notifications
app.get("/admin/notifications", requireAuth, async (req, res) => {
  try {
    const config = await getAllNotificationConfig();
    res.json(config);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Error retrieving notification config." });
  }
});

// POST /admin/notifications
app.post("/admin/notifications", requireAuth, (req, res) => {
  const entries = Object.entries(req.body);
  if (entries.length === 0) {
    return res.status(400).json({ error: "No config entries provided." });
  }

  let completed = 0;
  let hasError = false;

  entries.forEach(([key, value]) => {
    db.run(
      "INSERT INTO notification_config (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = ?",
      [key, String(value), String(value)],
      (err) => {
        completed++;
        if (err) {
          hasError = true;
          console.error(`Error updating notification config [${key}]:`, err.message);
        }
        if (completed === entries.length) {
          if (hasError) {
            res.status(500).json({ error: "Some config entries failed to update." });
          } else {
            res.json({ message: "Notification config updated." });
          }
        }
      }
    );
  });
});

// GET /tas/:id/info
app.get("/tas/:id/info", async (req, res) => {
  const taId = parseInt(req.params.id, 10);
  try {
    const [ta, hours, blocked] = await Promise.all([
      new Promise((resolve, reject) => {
        db.get("SELECT * FROM tas WHERE id = ?", [taId], (err, row) => err ? reject(err) : resolve(row));
      }),
      getAdminHoursForTA(taId),
      getBlockedDatesForTA(taId),
    ]);

    if (!ta) return res.status(404).json({ error: "TA not found." });
    res.json({ ta, hours, blocked });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Error retrieving TA info." });
  }
});

// ==================== Start Server ====================
app.listen(PORT, HOST, () => {
  console.log(`Server started: http://10.93.25.100:${PORT}`);
});
