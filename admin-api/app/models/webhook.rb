class Webhook < ApplicationRecord
  self.table_name = "bots.webhooks"

  validates :instance_id, presence: true
  validates :slug, presence: true, uniqueness: { scope: :instance_id }
  validates :code, presence: true
end
