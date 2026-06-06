class SandboxAllowlistEntry < ApplicationRecord
  self.table_name = "bots.sandbox_allowlist"

  # Hostname válido OU "*.hostname" (wildcard de 1 nível)
  HOST_PATTERN = /\A(\*\.)?([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)(\.[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)+\z/i

  validates :instance_id,  presence: true
  validates :host_pattern, presence: true,
                           format: { with: HOST_PATTERN, message: "deve ser hostname ou *.hostname" },
                           uniqueness: { scope: :instance_id, case_sensitive: false }

  before_validation { self.host_pattern = host_pattern.to_s.downcase.strip }
end
