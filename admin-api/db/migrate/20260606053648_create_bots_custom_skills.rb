class CreateBotsCustomSkills < ActiveRecord::Migration[8.1]
  def change
    # Skills criadas pelo admin sem código: keywords disparam um template de resposta.
    # Match: se mensagem (case-insensitive) contém qualquer keyword → responde com template.
    create_table "bots.custom_skills", force: :cascade do |t|
      t.string  :instance_id,        null: false                        # FK lógico
      t.string  :name,               null: false
      t.string  :keywords,           array: true, null: false, default: []
      t.boolean :match_whole_word,   null: false, default: false
      t.text    :response_template,  null: false
      t.boolean :enabled,            null: false, default: true
      t.timestamps null: false
    end

    add_index "bots.custom_skills", :instance_id
    add_index "bots.custom_skills", "instance_id, lower(name)", unique: true, name: "idx_custom_skills_unique_name_per_instance"
  end
end
