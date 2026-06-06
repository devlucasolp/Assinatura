class SkillCustomization < ApplicationRecord
  self.table_name = "bots.skill_customizations"

  validates :skill_id, presence: true, uniqueness: true,
            inclusion: { in: ->(_) { Skill::CATALOG.map { |s| s[:id] } } }
end
