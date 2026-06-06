class InstanceSkill < ApplicationRecord
  self.table_name = "bots.instance_skills"

  validates :instance_id, presence: true
  validates :skill_id,    presence: true, inclusion: { in: ->(_) { Skill::CATALOG.map { |s| s[:id] } } }
  validates :instance_id, uniqueness: { scope: :skill_id }
end
