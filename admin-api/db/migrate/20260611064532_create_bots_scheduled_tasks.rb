class CreateBotsScheduledTasks < ActiveRecord::Migration[8.1]
  def change
    create_table "bots.scheduled_tasks" do |t|
      t.string :instance_id, null: false
      t.string :name, null: false
      t.string :cron_expression, null: false
      t.text :code, null: false
      t.boolean :enabled, null: false, default: true

      t.timestamps
    end
    add_index "bots.scheduled_tasks", :instance_id
  end
end
