class CreateBotsInstanceSkills < ActiveRecord::Migration[8.1]
  def change
    # Armazena APENAS overrides — ausência de registro = skill habilitada (default).
    # Quando admin desliga uma skill, cria registro com enabled=false.
    create_table "bots.instance_skills", force: :cascade do |t|
      t.string  :instance_id, null: false        # FK lógico para bots.instances.id (TEXT)
      t.string  :skill_id,    null: false        # ID lógico da skill (ex: "asana_delete")
      t.boolean :enabled,     null: false, default: true
      t.timestamps null: false
    end

    add_index "bots.instance_skills", [ :instance_id, :skill_id ], unique: true
    add_index "bots.instance_skills", :instance_id
  end
end
