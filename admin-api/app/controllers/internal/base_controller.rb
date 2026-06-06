module Internal
  class BaseController < ActionController::API
    before_action :authenticate_bot!

    private

    def authenticate_bot!
      key = request.headers["X-Bot-Service-Key"]
      unless BotServiceKey.matches?(key)
        render json: { error: "Acesso não autorizado" }, status: :unauthorized
      end
    end
  end
end
