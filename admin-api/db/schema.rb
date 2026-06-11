# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `bin/rails
# db:schema:load`. When creating a new database, `bin/rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema[8.1].define(version: 2026_06_11_064548) do
  create_schema "bots"

  # These are extensions that must be enabled in order to support this database
  enable_extension "pg_catalog.plpgsql"

  create_table "bots.app_settings", primary_key: "key", id: { type: :string, limit: 200 }, force: :cascade do |t|
    t.boolean "is_secret", default: false, null: false
    t.timestamptz "updated_at", default: -> { "now()" }, null: false
    t.text "value", default: "", null: false
  end

  create_table "bots.connector_tokens", id: :serial, force: :cascade do |t|
    t.string "connector", limit: 50, null: false
    t.timestamptz "created_at", default: -> { "now()" }, null: false
    t.text "instance_id", default: "__global__", null: false
    t.text "scope"
    t.jsonb "token_data", null: false
    t.timestamptz "updated_at", default: -> { "now()" }, null: false

    t.unique_constraint ["connector", "instance_id"], name: "connector_tokens_connector_instance_id_key"
  end

  create_table "bots.custom_skills", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.boolean "enabled", default: true, null: false
    t.string "instance_id", null: false
    t.string "keywords", default: [], null: false, array: true
    t.boolean "match_whole_word", default: false, null: false
    t.string "name", null: false
    t.text "response_template", null: false
    t.datetime "updated_at", null: false
    t.index "instance_id, lower((name)::text)", name: "idx_custom_skills_unique_name_per_instance", unique: true
    t.index ["instance_id"], name: "index_custom_skills_on_instance_id"
  end

  create_table "bots.instance_skills", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.boolean "enabled", default: true, null: false
    t.string "instance_id", null: false
    t.string "skill_id", null: false
    t.datetime "updated_at", null: false
    t.index ["instance_id", "skill_id"], name: "index_instance_skills_on_instance_id_and_skill_id", unique: true
    t.index ["instance_id"], name: "index_instance_skills_on_instance_id"
  end

  create_table "bots.instances", id: :text, force: :cascade do |t|
    t.text "asana_access_token", default: "", null: false
    t.text "asana_project_gid", default: "", null: false
    t.text "asana_section_gid", default: "", null: false
    t.text "asana_user_gid", default: "", null: false
    t.text "asana_workspace_gid", default: "", null: false
    t.string "assistant_name", default: "", null: false
    t.string "briefing_afternoon"
    t.string "briefing_evening"
    t.string "briefing_morning"
    t.string "briefing_timezone", default: "America/Sao_Paulo", null: false
    t.timestamptz "created_at", default: -> { "now()" }, null: false
    t.text "evolution_instance", null: false
    t.text "gemini_api_key", default: "", null: false
    t.boolean "is_active", default: true, null: false
    t.text "msg_auto_reply_event", default: "", null: false
    t.text "msg_auto_reply_meeting", default: "", null: false
    t.text "msg_greeting", default: "", null: false
    t.text "msg_status_event_on", default: "", null: false
    t.text "msg_status_meeting_on", default: "", null: false
    t.text "msg_status_off", default: "", null: false
    t.text "name", null: false
    t.integer "new_tasks_poll_minutes"
    t.text "openai_api_key", default: "", null: false
    t.text "openai_model", default: "gpt-4o", null: false
    t.text "phone_primary", default: "", null: false
    t.text "phone_secondary", default: "", null: false
    t.text "system_prompt", default: "", null: false
    t.timestamptz "updated_at", default: -> { "now()" }, null: false
    t.index ["evolution_instance"], name: "idx_bots_instances_evolution", where: "(is_active = true)"
    t.unique_constraint ["evolution_instance"], name: "instances_evolution_instance_key"
  end

  create_table "bots.invites", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.string "email", null: false
    t.datetime "expires_at", null: false
    t.bigint "invited_by_id", null: false
    t.string "role", default: "viewer", null: false
    t.string "token", null: false
    t.datetime "updated_at", null: false
    t.datetime "used_at"
    t.index ["email"], name: "index_invites_on_email"
    t.index ["invited_by_id"], name: "index_invites_on_invited_by_id"
    t.index ["token"], name: "index_invites_on_token", unique: true
  end

  create_table "bots.sandbox_allowlist", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.string "host_pattern", null: false
    t.string "instance_id", null: false
    t.string "note"
    t.datetime "updated_at", null: false
    t.index ["instance_id", "host_pattern"], name: "index_sandbox_allowlist_on_instance_id_and_host_pattern", unique: true
    t.index ["instance_id"], name: "index_sandbox_allowlist_on_instance_id"
  end

  create_table "bots.sandbox_runs", force: :cascade do |t|
    t.text "code", null: false
    t.datetime "created_at", null: false
    t.integer "duration_ms"
    t.integer "exit_code"
    t.string "instance_id", null: false
    t.string "kill_reason"
    t.boolean "killed", default: false, null: false
    t.integer "memory_peak_mb"
    t.string "origin"
    t.text "stderr"
    t.text "stdout"
    t.index ["created_at"], name: "index_sandbox_runs_on_created_at"
    t.index ["instance_id", "created_at"], name: "index_sandbox_runs_on_instance_id_and_created_at"
    t.index ["instance_id"], name: "index_sandbox_runs_on_instance_id"
  end

  create_table "bots.scheduled_tasks", force: :cascade do |t|
    t.text "code", null: false
    t.datetime "created_at", null: false
    t.string "cron_expression", null: false
    t.boolean "enabled", default: true, null: false
    t.string "instance_id", null: false
    t.string "name", null: false
    t.datetime "updated_at", null: false
    t.index ["instance_id"], name: "index_scheduled_tasks_on_instance_id"
  end

  create_table "bots.skill_customizations", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.text "custom_description"
    t.string "custom_name"
    t.string "skill_id", null: false
    t.datetime "updated_at", null: false
    t.index ["skill_id"], name: "index_skill_customizations_on_skill_id", unique: true
  end

  create_table "bots.users", force: :cascade do |t|
    t.boolean "active", default: true, null: false
    t.datetime "created_at", null: false
    t.string "email", null: false
    t.string "google_sub"
    t.string "name", null: false
    t.string "password_digest"
    t.string "role", default: "viewer", null: false
    t.datetime "updated_at", null: false
    t.index ["email"], name: "index_users_on_email", unique: true
    t.index ["google_sub"], name: "index_users_on_google_sub", unique: true, where: "(google_sub IS NOT NULL)"
  end

  create_table "bots.webhooks", force: :cascade do |t|
    t.text "code", null: false
    t.datetime "created_at", null: false
    t.boolean "enabled", default: true, null: false
    t.string "instance_id", null: false
    t.string "slug", null: false
    t.datetime "updated_at", null: false
    t.index ["instance_id", "slug"], name: "index_webhooks_on_instance_id_and_slug", unique: true
  end

end
