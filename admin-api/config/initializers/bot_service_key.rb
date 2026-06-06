module BotServiceKey
  def self.value
    @value ||= from_env || from_db || generate_and_save!
  end

  def self.reset!
    @value = nil
  end

  def self.matches?(candidate)
    return false if candidate.blank?
    ActiveSupport::SecurityUtils.secure_compare(value, candidate)
  end

  private_class_method def self.from_env
    key = ENV["BOT_SERVICE_KEY"]
    key.presence
  end

  private_class_method def self.from_db
    AppSetting.find_by(key: "system.bot_service_key")&.value
  rescue StandardError
    nil
  end

  private_class_method def self.generate_and_save!
    key = SecureRandom.hex(32)
    AppSetting.find_or_create_by!(key: "system.bot_service_key") do |s|
      s.value     = key
      s.is_secret = true
    end
    Rails.logger.info <<~MSG

      ╔══════════════════════════════════════════════════════╗
      ║  BOT_SERVICE_KEY gerada automaticamente              ║
      ║  Copie para o .env do Python:                        ║
      ║  RAILS_BOT_SERVICE_KEY=#{key}  ║
      ╚══════════════════════════════════════════════════════╝

    MSG
    key
  end
end
