class CreateBotsSandboxAllowlist < ActiveRecord::Migration[8.1]
  def change
    # Hosts que a sandbox da instância pode acessar via HTTP/HTTPS.
    # Match: exato (api.openai.com) ou wildcard de subdomínio (*.openai.com).
    # IPs privados (RFC1918, link-local, metadata) são sempre bloqueados pelo proxy.
    create_table "bots.sandbox_allowlist", force: :cascade do |t|
      t.string  :instance_id,  null: false
      t.string  :host_pattern, null: false                  # ex: "api.openai.com" ou "*.openai.com"
      t.string  :note                                        # descrição opcional do admin
      t.timestamps null: false
    end

    add_index "bots.sandbox_allowlist", :instance_id
    add_index "bots.sandbox_allowlist", [ :instance_id, :host_pattern ], unique: true
  end
end
