class CustomSkill < ApplicationRecord
  self.table_name = "bots.custom_skills"

  validates :instance_id,       presence: true
  validates :name,              presence: true, length: { maximum: 80 }
  validates :keywords,          presence: true
  validates :response_template, presence: true, length: { maximum: 4000 }
  validate  :keywords_not_empty
  validate  :name_unique_per_instance

  before_validation :normalize_keywords

  private

  def normalize_keywords
    return unless keywords.is_a?(Array)
    self.keywords = keywords
      .map { |k| k.to_s.strip.downcase }
      .reject(&:blank?)
      .uniq
  end

  def keywords_not_empty
    errors.add(:keywords, "precisa ter ao menos uma palavra-chave") if keywords.blank? || keywords.compact.reject(&:blank?).empty?
  end

  def name_unique_per_instance
    return if instance_id.blank? || name.blank?
    scope = CustomSkill.where(instance_id: instance_id).where("lower(name) = ?", name.downcase)
    scope = scope.where.not(id: id) if persisted?
    errors.add(:name, "já existe nesta instância") if scope.exists?
  end
end
