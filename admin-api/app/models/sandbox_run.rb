class SandboxRun < ApplicationRecord
  self.table_name = "bots.sandbox_runs"
  # Tabela é só leitura no Rails — escrita vem do worker via asyncpg.
  self.inheritance_column = nil

  scope :recent, -> { order(created_at: :desc) }
  scope :for_instance, ->(id) { where(instance_id: id) }

  def success?
    exit_code == 0 && !killed
  end
end
