module Api
  module V1
    class SandboxRunsController < ApplicationController
      before_action :require_admin!

      # GET /api/v1/sandbox_runs?instance_id=&status=&limit=&offset=
      def index
        scope = SandboxRun.recent
        scope = scope.for_instance(params[:instance_id]) if params[:instance_id].present?

        case params[:status]
        when "success" then scope = scope.where(exit_code: 0, killed: false)
        when "error"   then scope = scope.where.not(exit_code: 0).or(scope.where(killed: true))
        when "killed"  then scope = scope.where(killed: true)
        end

        limit  = [ params.fetch(:limit, 50).to_i, 200 ].min
        offset = params.fetch(:offset, 0).to_i

        total = scope.count
        rows  = scope.limit(limit).offset(offset).map { |r| serialize(r) }

        render json: { total: total, limit: limit, offset: offset, runs: rows }
      end

      def show
        run = SandboxRun.find(params[:id])
        render json: serialize(run, full: true)
      end

      private

      def serialize(r, full: false)
        base = {
          id:              r.id,
          instance_id:     r.instance_id,
          exit_code:       r.exit_code,
          duration_ms:     r.duration_ms,
          memory_peak_mb:  r.memory_peak_mb,
          killed:          r.killed,
          kill_reason:     r.kill_reason,
          origin:          r.origin,
          created_at:      r.created_at,
        }
        if full
          base[:code]   = r.code
          base[:stdout] = r.stdout
          base[:stderr] = r.stderr
        end
        base
      end
    end
  end
end
