module Api
  module V1
    class InstancesController < ApplicationController
      before_action :require_admin!, only: [ :create, :update, :destroy ]
      before_action :set_instance,   only: [ :show, :update, :destroy ]

      def index
        render json: Instance.order(:created_at)
      end

      def show
        render json: @instance
      end

      def create
        instance = Instance.new(instance_params)
        instance.save!
        render json: instance, status: :created
      end

      def update
        @instance.update!(instance_params)
        render json: @instance
      end

      def destroy
        @instance.destroy!
        head :no_content
      end

      private

      def set_instance
        @instance = Instance.find(params[:id])
      end

      def instance_params
        params.require(:instance).permit(
          :id, :name, :evolution_instance,
          :phone_primary, :phone_secondary,
          :asana_access_token, :asana_workspace_gid, :asana_project_gid,
          :asana_section_gid, :asana_user_gid,
          :gemini_api_key, :openai_api_key, :openai_model,
          :msg_auto_reply_meeting, :msg_auto_reply_event,
          :msg_status_meeting_on, :msg_status_event_on, :msg_status_off, :msg_greeting,
          :assistant_name, :system_prompt,
          :briefing_morning, :briefing_afternoon, :briefing_evening,
          :new_tasks_poll_minutes, :briefing_timezone,
          :is_active
        )
      end
    end
  end
end
