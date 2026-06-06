ENV["BUNDLE_GEMFILE"] ||= File.expand_path("../Gemfile", __dir__)

require "bundler/setup"
# Bootsnap desabilitado — tem bug com caminhos com espaços no Windows
# require "bootsnap/setup"
