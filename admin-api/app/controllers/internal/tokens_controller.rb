module Internal
  class TokensController < BaseController
    # GET /internal/tokens
    # Retorna todos os tokens ativos, com refresh automático se expirado.
    def index
      tokens = ConnectorToken.all.map { |t| serialize(t) }
      render json: { tokens: }
    end

    # GET /internal/tokens/:connector
    # Retorna o token global de um conector específico, com refresh automático.
    def show
      token = ConnectorToken.find_by!(connector: params[:connector], instance_id: ConnectorToken::GLOBAL)
      render json: serialize(token)
    end

    # GET /internal/tokens/:connector/:instance_id
    # Retorna o token de um conector para uma instância específica.
    def show_instance
      token = ConnectorToken.find_by!(connector: params[:connector], instance_id: params[:instance_id])
      render json: serialize(token)
    end

    # GET /internal/sandbox_allowlist/:instance_id
    # Lista hosts permitidos para a sandbox da instância. Consumido pelo egress-proxy.
    def sandbox_allowlist
      entries = SandboxAllowlistEntry
                  .where(instance_id: params[:instance_id])
                  .pluck(:host_pattern)
      render json: { instance_id: params[:instance_id], allow: entries }
    end

    # POST /internal/connector_tokens
    # Recebe token do Python após OAuth e persiste no banco.
    def upsert
      connector   = params.require(:connector)
      instance_id = params.fetch(:instance_id, ConnectorToken::GLOBAL)
      token_data  = params.require(:token_data).to_unsafe_h
      scope       = params[:scope]

      token = ConnectorToken.find_or_initialize_by(connector:, instance_id:)
      token.update!(token_data:, scope:, updated_at: Time.current)

      Rails.logger.info "[INTERNAL] Token salvo | connector: #{connector} | instance: #{instance_id}"
      render json: { status: "ok", connector:, instance_id: }, status: :created
    rescue ActionController::ParameterMissing => e
      render json: { error: e.message }, status: :unprocessable_entity
    end

    private

    def serialize(token)
      data = token.token_data
      data = refresh_if_expired(token, data) if google_connector?(token.connector)

      {
        id:          token.id,
        connector:   token.connector,
        instance_id: token.instance_id,
        scope:       token.scope,
        updated_at:  token.updated_at,
        token_data:  data,
      }
    end

    def refresh_if_expired(token, data)
      expiry = data["expiry"] || data["token_expiry"]
      return data if expiry.nil?

      expires_at = Time.at(expiry.to_f)
      return data if expires_at > 1.minute.from_now

      refreshed = google_refresh(data)
      return data unless refreshed

      token.update!(token_data: refreshed, updated_at: Time.current)
      refreshed
    rescue StandardError => e
      Rails.logger.warn "[INTERNAL] Falha ao renovar token #{token.connector}/#{token.instance_id}: #{e.message}"
      data
    end

    def google_connector?(connector)
      connector.start_with?("google_")
    end

    def google_refresh(data)
      refresh_token = data["refresh_token"]
      return nil if refresh_token.blank?

      client_id     = AppSetting.find_by(key: "google.client_id")&.value     || ENV["GOOGLE_CLIENT_ID"]
      client_secret = AppSetting.find_by(key: "google.client_secret")&.value || ENV["GOOGLE_CLIENT_SECRET"]
      return nil if client_id.blank? || client_secret.blank?

      uri = URI("https://oauth2.googleapis.com/token")
      res = Net::HTTP.post_form(uri, {
        client_id:,
        client_secret:,
        refresh_token:,
        grant_type: "refresh_token",
      })

      return nil unless res.is_a?(Net::HTTPSuccess)

      body = JSON.parse(res.body)
      return nil if body["error"].present?

      data.merge(
        "access_token" => body["access_token"],
        "expiry"       => (Time.current + body["expires_in"].to_i).to_f,
      )
    end
  end
end
