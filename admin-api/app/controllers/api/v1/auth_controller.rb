module Api
  module V1
    class AuthController < ApplicationController
      skip_before_action :authenticate!, only: [ :create, :register ]

      # POST /api/v1/auth/sessions
      # Body: { email:, password: } OU { google_token: }
      def create
        user = authenticate_by_credentials || authenticate_by_google
        return render json: { error: "Credenciais inválidas" }, status: :unauthorized unless user
        return render json: { error: "Conta inativa" }, status: :forbidden unless user.active?

        token = ApplicationController.encode_token(jwt_payload(user))
        render json: { token:, user: user_payload(user) }
      end

      # POST /api/v1/auth/register
      # Sem invite_token: exige domínio @assinaturamarcapropria.com.br
      # Com invite_token válido: usa email e role do convite (bypass domínio)
      def register
        return render json: { error: "Nome é obrigatório" }, status: :unprocessable_entity if params[:name].blank?
        return render json: { error: "Senha é obrigatória" }, status: :unprocessable_entity if params[:password].blank?

        invite = nil
        if params[:invite_token].present?
          invite = Invite.find_by(token: params[:invite_token])
          return render json: { error: "Convite inválido ou expirado" }, status: :unprocessable_entity unless invite&.active?
        end

        email = (invite&.email || params[:email]).to_s.downcase
        role  = invite&.role || default_role

        user = build_user_skipping_domain_check_if_invited(
          name:     params[:name],
          email:    email,
          password: params[:password],
          role:     role,
          invited:  invite.present?,
        )
        user.save!

        invite&.consume!

        token = ApplicationController.encode_token(jwt_payload(user))
        render json: { token:, user: user_payload(user) }, status: :created
      rescue ActiveRecord::RecordInvalid => e
        render json: { error: e.message }, status: :unprocessable_entity
      end

      # DELETE /api/v1/auth/sessions — stateless JWT: apenas sinaliza ao cliente para descartar
      def destroy
        render json: { message: "Sessão encerrada" }
      end

      # GET /api/v1/auth/me
      def me
        render json: user_payload(@current_user)
      end

      private

      def authenticate_by_credentials
        return unless params[:email].present? && params[:password].present?

        user = User.find_by(email: params[:email].downcase)
        user&.authenticate(params[:password]) ? user : nil
      end

      def authenticate_by_google
        return unless params[:google_token].present?

        info = fetch_google_userinfo(params[:google_token])
        return unless info

        user = User.find_or_initialize_by(google_sub: info["sub"])
        user.email  = info["email"]
        user.name   = info["name"].presence || info["email"]
        user.role   = user.new_record? ? default_role : user.role
        user.active = true
        user.save!
        user
      rescue ActiveRecord::RecordInvalid
        nil
      end

      def fetch_google_userinfo(token)
        uri = URI("https://www.googleapis.com/oauth2/v3/userinfo")
        req = Net::HTTP::Get.new(uri)
        req["Authorization"] = "Bearer #{token}"
        res = Net::HTTP.start(uri.host, uri.port, use_ssl: true) { |h| h.request(req) }
        Rails.logger.info("GOOGLE USERINFO: #{res.code} - #{res.body}")
        res.is_a?(Net::HTTPSuccess) ? JSON.parse(res.body) : nil
      rescue StandardError => e
        Rails.logger.error("GOOGLE USERINFO ERROR: #{e.message}")
        nil
      end

      def default_role
        User.exists? ? "viewer" : "admin"
      end

      def build_user_skipping_domain_check_if_invited(name:, email:, password:, role:, invited:)
        user = User.new(name:, email:, password:, role:, active: true)
        user.skip_domain_check = true if invited
        user
      end

      def jwt_payload(user)
        {
          "user_id" => user.id,
          "name"    => user.name,
          "email"   => user.email,
          "role"    => user.role,
        }
      end

      def user_payload(user)
        { id: user.id, name: user.name, email: user.email, role: user.role }
      end
    end
  end
end
