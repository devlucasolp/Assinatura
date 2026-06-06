module Api
  module V1
    class InstanceSkillsController < ApplicationController
      before_action :require_admin!, only: [ :update ]
      before_action :set_instance

      # GET /api/v1/instances/:instance_id/skills
      # Retorna o catálogo completo + estado por instância (default: enabled=true)
      def index
        toggles = InstanceSkill.where(instance_id: @instance.id).index_by(&:skill_id)

        skills = Skill.catalog_with_overrides.map do |s|
          toggle = toggles[s[:id]]
          s.merge(enabled: s[:always_on] || toggle.nil? || toggle.enabled)
        end

        render json: { instance_id: @instance.id, skills: skills }
      end

      # PUT /api/v1/instances/:instance_id/skills
      # Body: { skills: { "asana_delete": false, "ata": true, ... } }
      # Aceita qualquer subset; valores faltantes não mudam.
      def update
        updates = params.require(:skills).to_unsafe_h
        toggleable = Skill.toggleable_ids

        updates.each do |skill_id, enabled|
          next unless toggleable.include?(skill_id.to_s)

          record = InstanceSkill.find_or_initialize_by(
            instance_id: @instance.id, skill_id: skill_id.to_s,
          )
          record.enabled = ActiveModel::Type::Boolean.new.cast(enabled)
          record.save!
        end

        index
      end

      private

      def set_instance
        @instance = Instance.find(params[:instance_id] || params[:id])
      end
    end
  end
end
