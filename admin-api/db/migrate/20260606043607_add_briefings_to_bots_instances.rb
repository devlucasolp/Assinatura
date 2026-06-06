class AddBriefingsToBotsInstances < ActiveRecord::Migration[8.1]
  def change
    # Horários no formato "HH:MM" (string). NULL = briefing desligado naquele período.
    add_column "bots.instances", :briefing_morning,        :string                            # ex: "10:00"
    add_column "bots.instances", :briefing_afternoon,      :string                            # ex: "15:00"
    add_column "bots.instances", :briefing_evening,        :string                            # ex: "18:00"
    add_column "bots.instances", :new_tasks_poll_minutes,  :integer                           # ex: 10 (intervalo) — NULL = desligado
    add_column "bots.instances", :briefing_timezone,       :string, default: "America/Sao_Paulo", null: false
  end
end
