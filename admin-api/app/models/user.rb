class User < ApplicationRecord
  self.table_name = "bots.users"

  has_secure_password validations: false

  ROLES                = %w[admin viewer].freeze
  ALLOWED_DOMAIN       = "assinaturamarcapropria.com.br"
  ADMIN_BYPASS_EMAILS  = %w[brtzolkin@gmail.com].freeze

  # Virtual — quando true (registro via convite), pula a checagem de domínio
  attr_accessor :skip_domain_check

  validates :email, presence: true, uniqueness: { case_sensitive: false },
                    format: { with: URI::MailTo::EMAIL_REGEXP }
  validates :name,  presence: true
  validates :role,  inclusion: { in: ROLES }
  validate  :email_domain_allowed

  before_save { self.email = email.downcase }

  def admin?
    role == "admin"
  end

  private

  def email_domain_allowed
    return if skip_domain_check
    return if ADMIN_BYPASS_EMAILS.include?(email&.downcase)
    return if email&.downcase&.end_with?("@#{ALLOWED_DOMAIN}")
    errors.add(:email, "não autorizado — apenas @#{ALLOWED_DOMAIN} ou contas especiais")
  end
end
