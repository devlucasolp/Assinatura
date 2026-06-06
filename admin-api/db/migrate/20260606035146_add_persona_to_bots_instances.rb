class AddPersonaToBotsInstances < ActiveRecord::Migration[8.1]
  def change
    add_column "bots.instances", :assistant_name, :string, null: false, default: ""
    add_column "bots.instances", :system_prompt,  :text,   null: false, default: ""
  end
end
