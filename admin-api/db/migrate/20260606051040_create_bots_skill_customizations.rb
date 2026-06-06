class CreateBotsSkillCustomizations < ActiveRecord::Migration[8.1]
  def change
    # Overrides do catálogo de skills built-in.
    # O conjunto de skill_ids válidos vem do Skill::CATALOG (código).
    # Esta tabela só guarda o que o admin renomeou/editou.
    create_table "bots.skill_customizations", force: :cascade do |t|
      t.string :skill_id,            null: false
      t.string :custom_name
      t.text   :custom_description
      t.timestamps null: false
    end

    add_index "bots.skill_customizations", :skill_id, unique: true
  end
end
