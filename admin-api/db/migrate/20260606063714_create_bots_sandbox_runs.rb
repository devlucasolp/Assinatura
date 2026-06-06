class CreateBotsSandboxRuns < ActiveRecord::Migration[8.1]
  def change
    create_table "bots.sandbox_runs", force: :cascade do |t|
      t.string  :instance_id,         null: false                    # FK lógico para bots.instances
      t.text    :code,                null: false                    # código executado (truncado em 8KB)
      t.text    :stdout                                               # truncado em 64KB
      t.text    :stderr                                               # truncado em 64KB
      t.integer :exit_code
      t.integer :duration_ms                                          # tempo total worker→worker
      t.integer :memory_peak_mb                                       # pico do container (cgroup stat)
      t.boolean :killed,              null: false, default: false    # true se atingiu timeout ou OOM
      t.string  :kill_reason                                          # "timeout" | "oom" | "manual"
      t.string  :origin                                               # "gemini" | "admin" | "test"
      t.datetime :created_at,         null: false
    end

    add_index "bots.sandbox_runs", :instance_id
    add_index "bots.sandbox_runs", :created_at
    add_index "bots.sandbox_runs", [ :instance_id, :created_at ]
  end
end
