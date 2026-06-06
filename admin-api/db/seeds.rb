# ── Admin especial ────────────────────────────────────────────────────────────
User.find_or_initialize_by(email: "brtzolkin@gmail.com").tap do |u|
  u.name     = "Gustavo (Tzolkin)"
  u.role     = "admin"
  u.active   = true
  u.password = "Tzolkin@2026" unless u.password_digest.present?
  u.save!
end
puts "Seed: admin brtzolkin@gmail.com garantido."

