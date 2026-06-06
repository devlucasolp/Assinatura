class ConnectorToken < ApplicationRecord
  self.table_name = "bots.connector_tokens"

  validates :connector,   presence: true
  validates :instance_id, presence: true
  validates :token_data,  presence: true

  GLOBAL = "__global__"
end
