# frozen_string_literal: true

require_relative "lib/pinecall/protocol/version"

Gem::Specification.new do |spec|
  spec.name = "pinecall-protocol"
  spec.version = Pinecall::Protocol::VERSION
  spec.authors = ["Pinecall"]
  spec.email = ["hello@pinecall.io"]

  spec.summary = "The Pinecall wire: the shapes, the codec and the log reducer, generated from one schema"
  spec.description = "Ruby's side of the Pinecall protocol. The tables under generated/ are written " \
                     "from protocol/schema by the same generator that writes the Python and " \
                     "TypeScript packages, so the three never disagree about a field."
  spec.homepage = "https://github.com/pinecall/protocol"
  spec.license = "Apache-2.0"
  spec.required_ruby_version = ">= 3.2.0"

  spec.metadata = {
    "homepage_uri" => spec.homepage,
    "source_code_uri" => spec.homepage,
    "rubygems_mfa_required" => "true"
  }

  spec.files = Dir["lib/**/*.rb", "sig/**/*.rbs", "LICENSE", "README.md"]
  spec.require_paths = ["lib"]
end
