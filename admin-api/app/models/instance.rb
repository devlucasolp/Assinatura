class Instance < ApplicationRecord
  self.table_name = "bots.instances"

  TIME_FORMAT = /\A([01]\d|2[0-3]):[0-5]\d\z/

  validates :id,                 presence: true
  validates :name,               presence: true
  validates :evolution_instance, presence: true, uniqueness: true

  validates :briefing_morning,   format: { with: TIME_FORMAT, message: "deve ser HH:MM" }, allow_blank: true
  validates :briefing_afternoon, format: { with: TIME_FORMAT, message: "deve ser HH:MM" }, allow_blank: true
  validates :briefing_evening,   format: { with: TIME_FORMAT, message: "deve ser HH:MM" }, allow_blank: true
  validates :new_tasks_poll_minutes, numericality: { only_integer: true, greater_than_or_equal_to: 1, less_than_or_equal_to: 1440 }, allow_nil: true

  before_validation :set_defaults

  private

  def set_defaults
    self.openai_model = "gpt-4o" if openai_model.blank?
  end
end
