module Api
  module V1
    class ScheduledTasksController < ApplicationController
      before_action :require_admin!, except: [ :index, :show ]
      before_action :set_instance
      before_action :set_task, only: [ :show, :update, :destroy ]

      def index
        render json: ScheduledTask.where(instance_id: @instance.id).order(created_at: :desc).map { |t| serialize(t) }
      end

      def show
        render json: serialize(@task)
      end

      def create
        task = ScheduledTask.new(task_params.merge(instance_id: @instance.id))
        task.save!
        render json: serialize(task), status: :created
      rescue ActiveRecord::RecordInvalid => e
        render json: { error: e.message }, status: :unprocessable_entity
      end

      def update
        @task.update!(task_params)
        render json: serialize(@task)
      rescue ActiveRecord::RecordInvalid => e
        render json: { error: e.message }, status: :unprocessable_entity
      end

      def destroy
        @task.destroy!
        head :no_content
      end

      private

      def set_instance
        @instance = Instance.find(params[:instance_id])
      end

      def set_task
        @task = ScheduledTask.find_by!(id: params[:id], instance_id: @instance.id)
      end

      def task_params
        params.require(:scheduled_task).permit(:name, :cron_expression, :code, :enabled)
      end

      def serialize(t)
        {
          id: t.id,
          name: t.name,
          cron_expression: t.cron_expression,
          code: t.code,
          enabled: t.enabled,
          created_at: t.created_at,
          updated_at: t.updated_at
        }
      end
    end
  end
end
