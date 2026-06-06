module JwtAuthenticatable
  extend ActiveSupport::Concern

  SECRET = ENV.fetch("JWT_SECRET") { Rails.application.secret_key_base }
  TTL    = 24 * 60 * 60 # 24h

  module ClassMethods
    def encode_token(payload)
      JWT.encode(payload.merge(exp: Time.now.to_i + TTL), SECRET, "HS256")
    end
  end

  included do
    before_action :authenticate!
  end

  def authenticate!
    token = bearer_token
    return render_unauthorized("Token ausente") unless token

    begin
      decoded = JWT.decode(token, SECRET, true, algorithm: "HS256").first
      @current_user = User.find_by(id: decoded["user_id"], active: true)
      render_unauthorized("Usuário inativo ou não encontrado") unless @current_user
    rescue JWT::ExpiredSignature
      render_unauthorized("Token expirado")
    rescue JWT::DecodeError
      render_unauthorized("Token inválido")
    end
  end

  def require_admin!
    render json: { error: "Acesso restrito a administradores" }, status: :forbidden unless @current_user&.admin?
  end

  private

  def bearer_token
    header = request.headers["Authorization"]
    header&.split(" ")&.last
  end

  def render_unauthorized(message)
    render json: { error: message }, status: :unauthorized
  end
end
