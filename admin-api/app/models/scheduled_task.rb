class ScheduledTask < ApplicationRecord
  self.table_name = "bots.scheduled_tasks"

  validates :instance_id, presence: true
  validates :name, presence: true
  validates :cron_expression, presence: true
  validates :code, presence: true
end
