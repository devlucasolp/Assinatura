module Api
  module V1
    class AppSettingsController < ApplicationController
      before_action :require_admin!

      def index
        settings = AppSetting.order(:key).map do |s|
          { key: s.key, value: s.display_value, is_secret: s.is_secret?, updated_at: s.updated_at }
        end
        render json: settings
      end

      def show
        setting = AppSetting.find(params[:key])
        render json: { key: setting.key, value: setting.display_value, is_secret: setting.is_secret? }
      end

      # PUT /api/v1/app_settings — upsert em lote
      # Body: { app_settings: [{ key:, value:, is_secret: }] }
      def bulk_upsert
        rows = params[:app_settings] || []
        rows.each do |row|
          AppSetting.find_or_initialize_by(key: row[:key]).tap do |s|
            s.value     = row[:value]
            s.is_secret = row[:is_secret] || false
            s.save!
          end
        end
        render json: { updated: rows.size }
      end
    end
  end
end
