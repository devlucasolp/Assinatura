module Api
  module V1
    class UsersController < ApplicationController
      before_action :require_admin!
      before_action :set_user, only: [ :show, :update, :destroy ]

      def index
        render json: User.order(:name).map { |u| serialize(u) }
      end

      def show
        render json: serialize(@user)
      end

      def update
        @user.update!(user_params)
        render json: serialize(@user)
      end

      def destroy
        return render json: { error: "Não é possível remover sua própria conta" }, status: :unprocessable_entity if @user.id == @current_user.id
        @user.destroy!
        head :no_content
      end

      private

      def set_user
        @user = User.find(params[:id])
      end

      def user_params
        params.require(:user).permit(:name, :role, :active)
      end

      def serialize(user)
        {
          id:         user.id,
          name:       user.name,
          email:      user.email,
          role:       user.role,
          active:     user.active,
          google_sub: user.google_sub.present?,
          created_at: user.created_at,
        }
      end
    end
  end
end
