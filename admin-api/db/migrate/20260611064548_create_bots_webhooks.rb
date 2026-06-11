class CreateBotsWebhooks < ActiveRecord::Migration[8.1]
  def change
    create_table "bots.webhooks" do |t|
      t.string :instance_id, null: false
      t.string :slug, null: false
      t.text :code, null: false
      t.boolean :enabled, null: false, default: true

      t.timestamps
    end
    add_index "bots.webhooks", [:instance_id, :slug], unique: true
  end
end
