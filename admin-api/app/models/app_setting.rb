class AppSetting < ApplicationRecord
  self.table_name = "bots.app_settings"
  self.primary_key = "key"

  validates :key, presence: true, uniqueness: true

  SECRET_MASK = "••••••••"

  def display_value
    is_secret? ? SECRET_MASK : value
  end
end
