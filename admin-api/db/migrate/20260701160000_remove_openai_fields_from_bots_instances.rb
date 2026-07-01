class RemoveOpenaiFieldsFromBotsInstances < ActiveRecord::Migration[8.1]
  def change
    remove_column "bots.instances", :openai_api_key, :text, default: "", null: false
    remove_column "bots.instances", :openai_model, :text, default: "gpt-4o", null: false
  end
end
