module Api
  module V1
    class WebhooksController < ApplicationController
      before_action :require_admin!, except: [ :index, :show ]
      before_action :set_instance
      before_action :set_webhook, only: [ :show, :update, :destroy ]

      def index
        render json: Webhook.where(instance_id: @instance.id).order(created_at: :desc).map { |w| serialize(w) }
      end

      def show
        render json: serialize(@webhook)
      end

      def create
        webhook = Webhook.new(webhook_params.merge(instance_id: @instance.id))
        webhook.save!
        render json: serialize(webhook), status: :created
      rescue ActiveRecord::RecordInvalid => e
        render json: { error: e.message }, status: :unprocessable_entity
      end

      def update
        @webhook.update!(webhook_params)
        render json: serialize(@webhook)
      rescue ActiveRecord::RecordInvalid => e
        render json: { error: e.message }, status: :unprocessable_entity
      end

      def destroy
        @webhook.destroy!
        head :no_content
      end

      private

      def set_instance
        @instance = Instance.find(params[:instance_id])
      end

      def set_webhook
        @webhook = Webhook.find_by!(id: params[:id], instance_id: @instance.id)
      end

      def webhook_params
        params.require(:webhook).permit(:slug, :code, :enabled)
      end

      def serialize(w)
        {
          id: w.id,
          slug: w.slug,
          code: w.code,
          enabled: w.enabled,
          created_at: w.created_at,
          updated_at: w.updated_at
        }
      end
    end
  end
end
