# frozen_string_literal: true

# The Pinecall wire in Ruby: the tables the schema generated, a validator, the codec, the reducer.
#
# Nothing here is hand-copied from the other two languages. `protocol/scripts/generate` writes the
# tables under generated/ from schema/, and CI regenerates and diffs them, so a field added to the
# wire arrives in Ruby the same commit it arrives in Python and TypeScript.

require "json"
require "set"

require_relative "protocol/version"
require_relative "protocol/errors"
require_relative "protocol/generated/enums"
require_relative "protocol/generated/shapes"
require_relative "protocol/generated/registry"
require_relative "protocol/validate"
require_relative "protocol/codec"
require_relative "protocol/state"
require_relative "protocol/reduce"

module Pinecall
  # The vocabulary both sides of the socket share: what a gateway writes and what an app sends.
  module Protocol
    class << self
      # One log line from parsed JSON.
      def decode_entry(raw) = Codec.decode_entry(raw)

      # A whole log from the text of a JSON array.
      def decode_entries(text) = Codec.decode_entries(text)

      # The entry's data as the shape its type names.
      def event_of(entry) = Codec.event_of(entry)

      # One command frame, checked against the shape its type names.
      def command(...) = Codec.command(...)

      # A frame as JSON text.
      def encode(frame) = Codec.encode(frame)

      # Fold a log into the state it means.
      def reduce(entries) = Reduce.reduce(entries)

      # One entry folded into a state, for a reader following a log as it happens.
      def apply(state, entry) = Reduce.apply(state, entry)

      # What an empty log is.
      def initial_state = State.initial
    end
  end
end
