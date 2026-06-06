class Invite < ApplicationRecord
  self.table_name = "bots.invites"

  belongs_to :invited_by, class_name: "User"

  TTL = 7.days

  validates :email, presence: true, format: { with: URI::MailTo::EMAIL_REGEXP }
  validates :role,  inclusion: { in: User::ROLES }
  validates :token, presence: true, uniqueness: true

  before_validation :set_defaults, on: :create

  scope :pending, -> { where(used_at: nil).where("expires_at > ?", Time.current) }

  def active?
    used_at.nil? && expires_at > Time.current
  end

  def consume!
    update!(used_at: Time.current)
  end

  private

  def set_defaults
    self.token       ||= SecureRandom.urlsafe_base64(32)
    self.expires_at  ||= Time.current + TTL
    self.email         = email.to_s.downcase
  end
end
