module Api
  module V1
    class SkillsController < ApplicationController
      before_action :require_admin!, only: [ :update, :destroy ]

      # GET /api/v1/skills
      # Catálogo completo das skills built-in com customizações aplicadas.
      def index
        render json: Skill.catalog_with_overrides
      end

      # PATCH /api/v1/skills/:id
      # Body: { skill: { name?, description? } }
      # Aceita só `nil` (volta ao default) ou string não vazia.
      def update
        skill_id = params[:id]
        return render json: { error: "Skill desconhecida" }, status: :not_found unless Skill.find(skill_id)

        attrs = params.require(:skill).permit(:name, :description).to_h
        return render json: { error: "Nada para atualizar" }, status: :unprocessable_entity if attrs.empty?

        record = SkillCustomization.find_or_initialize_by(skill_id: skill_id)
        record.custom_name        = attrs["name"]        if attrs.key?("name")
        record.custom_description = attrs["description"] if attrs.key?("description")

        # Se ambos voltaram a vazio, deleta para "voltar ao default"
        if record.custom_name.blank? && record.custom_description.blank?
          record.destroy if record.persisted?
        else
          record.save!
        end

        render json: skill_payload(skill_id)
      end

      # DELETE /api/v1/skills/:id  → restaura defaults
      def destroy
        SkillCustomization.where(skill_id: params[:id]).destroy_all
        render json: skill_payload(params[:id])
      end

      private

      def skill_payload(skill_id)
        Skill.catalog_with_overrides.find { |s| s[:id] == skill_id }
      end
    end
  end
end
