class ApplicationController < ActionController::API
  include JwtAuthenticatable

  rescue_from ActiveRecord::RecordNotFound do
    render json: { error: "Não encontrado" }, status: :not_found
  end

  rescue_from ActiveRecord::RecordInvalid do |e|
    render json: { error: e.message }, status: :unprocessable_entity
  end
end
