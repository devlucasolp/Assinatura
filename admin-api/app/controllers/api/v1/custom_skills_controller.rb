module Api
  module V1
    class CustomSkillsController < ApplicationController
      before_action :require_admin!, except: [ :index, :show ]
      before_action :set_instance
      before_action :set_skill, only: [ :show, :update, :destroy ]

      # GET /api/v1/instances/:instance_id/custom_skills
      def index
        render json: CustomSkill.where(instance_id: @instance.id).order(:name).map { |s| serialize(s) }
      end

      def show
        render json: serialize(@skill)
      end

      def create
        skill = CustomSkill.new(skill_params.merge(instance_id: @instance.id))
        skill.save!
        render json: serialize(skill), status: :created
      rescue ActiveRecord::RecordInvalid => e
        render json: { error: e.message }, status: :unprocessable_entity
      end

      def update
        @skill.update!(skill_params)
        render json: serialize(@skill)
      rescue ActiveRecord::RecordInvalid => e
        render json: { error: e.message }, status: :unprocessable_entity
      end

      def destroy
        @skill.destroy!
        head :no_content
      end

      private

      def set_instance
        @instance = Instance.find(params[:instance_id])
      end

      def set_skill
        @skill = CustomSkill.find_by!(id: params[:id], instance_id: @instance.id)
      end

      def skill_params
        permitted = params.require(:custom_skill).permit(:name, :response_template, :match_whole_word, :enabled, keywords: [])
        permitted[:keywords] ||= []
        permitted
      end

      def serialize(s)
        {
          id:                s.id,
          name:              s.name,
          keywords:          s.keywords,
          match_whole_word:  s.match_whole_word,
          response_template: s.response_template,
          enabled:           s.enabled,
          updated_at:        s.updated_at,
        }
      end
    end
  end
end
