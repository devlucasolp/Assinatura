Rails.application.routes.draw do
  get "up" => "rails/health#show", as: :rails_health_check

  # Rotas internas — acessíveis apenas pelo bot Python via X-Bot-Service-Key
  namespace :internal do
    get  "tokens",                          to: "tokens#index"
    get  "tokens/:connector",               to: "tokens#show",          constraints: { connector: /[^\/]+/ }
    get  "tokens/:connector/:instance_id",  to: "tokens#show_instance", constraints: { connector: /[^\/]+/, instance_id: /[^\/]+/ }
    post "connector_tokens",                to: "tokens#upsert"
  end

  namespace :api do
    namespace :v1 do
      # Auth
      post "auth/register",       to: "auth#register"
      post "auth/sessions",       to: "auth#create"
      delete "auth/sessions",     to: "auth#destroy"
      get "auth/me",              to: "auth#me"

      # Users
      resources :users, only: [ :index, :show, :update, :destroy ]

      # Invites
      resources :invites, only: [ :index, :create, :show, :destroy ]

      # Skills (catálogo built-in editável — nome/descrição overridable)
      resources :skills, only: [ :index, :update, :destroy ], constraints: { id: /[a-z_]+/ }

      # Instances
      resources :instances, except: [ :new, :edit ] do
        member do
          get  "skills", to: "instance_skills#index"
          put  "skills", to: "instance_skills#update"
        end

        resources :custom_skills, only: [ :index, :show, :create, :update, :destroy ]
      end

      # Connectors
      resources :connector_tokens, only: [ :index, :destroy ]

      # App Settings
      resources :app_settings, param: :key, only: [ :index, :show ] do
        collection { put "/" => "app_settings#bulk_upsert" }
      end
    end
  end
end
