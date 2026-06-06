class CreateBotsInvites < ActiveRecord::Migration[8.1]
  def change
    create_table "bots.invites", force: :cascade do |t|
      t.string     :token,        null: false                        # URL-safe random
      t.string     :email,        null: false                        # email pré-aprovado para esse convite
      t.string     :role,         null: false, default: "viewer"
      t.references :invited_by,   null: false                        # FK para bots.users (admin que gerou)
      t.datetime   :expires_at,   null: false
      t.datetime   :used_at                                          # null = ainda válido
      t.timestamps null: false
    end

    add_index "bots.invites", :token, unique: true
    add_index "bots.invites", :email
  end
end
