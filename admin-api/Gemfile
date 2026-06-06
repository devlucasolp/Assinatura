source "https://rubygems.org"

gem "rails", "~> 8.1.3"
gem "pg", "~> 1.1"
gem "puma", ">= 5.0"

gem "bcrypt", "~> 3.1.7"
gem "jwt", "~> 2.9"
gem "rack-cors"

# fiddle não é mais stdlib no Ruby 4.0 (dependência indireta de kamal/net-ssh)
gem "fiddle"

gem "dotenv-rails"
gem "bootsnap", require: false
gem "tzinfo-data", platforms: %i[ windows jruby ]

group :development, :test do
  gem "debug", platforms: %i[ mri windows ], require: "debug/prelude"
  gem "brakeman", require: false
  gem "rubocop-rails-omakase", require: false
end
