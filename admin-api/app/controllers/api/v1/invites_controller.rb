module Api
  module V1
    class InvitesController < ApplicationController
      before_action :require_admin!, except: [ :show ]
      skip_before_action :authenticate!, only: [ :show ]

      # GET /api/v1/invites — lista pendentes
      def index
        render json: Invite.pending.order(created_at: :desc).map { |i| serialize(i) }
      end

      # POST /api/v1/invites — cria convite
      # Body: { invite: { email:, role: } }
      def create
        params_in = invite_params
        invite = Invite.create!(
          email:      params_in[:email],
          role:       params_in[:role].presence || "viewer",
          invited_by: @current_user,
        )
        render json: serialize(invite), status: :created
      rescue ActiveRecord::RecordInvalid => e
        render json: { error: e.message }, status: :unprocessable_entity
      end

      # DELETE /api/v1/invites/:id — revoga
      def destroy
        invite = Invite.find(params[:id])
        invite.destroy!
        head :no_content
      end

      # GET /api/v1/invites/:token — público, valida token antes do registro
      # Note: rota usa :id como param, mas tratamos como token (string)
      def show
        invite = Invite.find_by(token: params[:id])
        return render json: { error: "Convite inválido ou expirado" }, status: :not_found unless invite&.active?

        render json: { email: invite.email, role: invite.role, expires_at: invite.expires_at }
      end

      private

      def invite_params
        params.require(:invite).permit(:email, :role)
      end

      def serialize(invite)
        {
          id:          invite.id,
          token:       invite.token,
          email:       invite.email,
          role:        invite.role,
          invited_by:  invite.invited_by.name,
          expires_at:  invite.expires_at,
          created_at:  invite.created_at,
        }
      end
    end
  end
end
