class CreateBotsUsers < ActiveRecord::Migration[8.1]
  def change
    execute "CREATE SCHEMA IF NOT EXISTS bots"

    create_table "bots.users", force: :cascade do |t|
      t.string  :name,            null: false
      t.string  :email,           null: false
      t.string  :password_digest
      t.string  :google_sub                         # ID único da conta Google OAuth
      t.string  :role,            null: false, default: "viewer"
      t.boolean :active,          null: false, default: true
      t.timestamps null: false
    end

    add_index "bots.users", :email,      unique: true
    add_index "bots.users", :google_sub, unique: true, where: "google_sub IS NOT NULL"
  end
end
