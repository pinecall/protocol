# frozen_string_literal: true

require "minitest/autorun"
require "pinecall/protocol"

# The goldens live in the Python package's own directory — hatchling cannot pack a file from
# outside the project it builds — and every language reads those same bytes rather than a copy.
FIXTURES = File.expand_path("../../python/pinecall_protocol/fixtures", __dir__)
