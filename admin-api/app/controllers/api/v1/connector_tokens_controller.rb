module Api
  module V1
    class ConnectorTokensController < ApplicationController
      before_action :require_admin!

      def index
        tokens = ConnectorToken.select(:id, :connector, :instance_id, :scope, :updated_at).order(:connector)
        render json: tokens
      end

      # DELETE /api/v1/connector_tokens/:connector
      # O frontend envia o nome do conector (ex: "google_drive"), não o ID numérico.
      def destroy
        token = ConnectorToken.find_by(connector: params[:id], instance_id: ConnectorToken::GLOBAL)
        token ||= ConnectorToken.find_by(id: params[:id].to_i) if params[:id].match?(/\A\d+\z/)

        return render json: { error: "Token não encontrado" }, status: :not_found unless token

        token.destroy!
        head :no_content
      end
    end
  end
end
