module Api
  module V1
    class SandboxAllowlistController < ApplicationController
      before_action :require_admin!, except: [ :index ]
      before_action :set_instance

      # GET /api/v1/instances/:instance_id/sandbox_allowlist
      def index
        entries = SandboxAllowlistEntry
                    .where(instance_id: @instance.id)
                    .order(:host_pattern)
                    .map { |e| serialize(e) }
        render json: entries
      end

      # POST /api/v1/instances/:instance_id/sandbox_allowlist
      def create
        entry = SandboxAllowlistEntry.new(entry_params.merge(instance_id: @instance.id))
        entry.save!
        render json: serialize(entry), status: :created
      rescue ActiveRecord::RecordInvalid => e
        render json: { error: e.message }, status: :unprocessable_entity
      end

      # DELETE /api/v1/instances/:instance_id/sandbox_allowlist/:id
      def destroy
        entry = SandboxAllowlistEntry.find_by!(id: params[:id], instance_id: @instance.id)
        entry.destroy!
        head :no_content
      end

      private

      def set_instance
        @instance = Instance.find(params[:instance_id])
      end

      def entry_params
        params.require(:entry).permit(:host_pattern, :note)
      end

      def serialize(e)
        { id: e.id, host_pattern: e.host_pattern, note: e.note, created_at: e.created_at }
      end
    end
  end
end
