# frozen_string_literal: true

require "test_helper"

# The golden fixture is the contract: what it decodes to, and what it folds to, is the same in
# Ruby as in TypeScript and in the runtime's Python. This file is where that stops being a claim.
class GoldenLogTest < Minitest::Test
  def setup
    @golden = Pinecall::Protocol.decode_entries(File.read("#{FIXTURES}/call-log-golden.json"))
  end

  def test_every_entry_decodes_to_the_shape_its_type_names
    @golden.each do |entry|
      event = Pinecall::Protocol.event_of(entry)
      assert_equal entry.type, event.type
      assert Pinecall::Protocol::Registry::EVENTS.key?(event.type), entry.type
    end
  end

  def test_it_reduces_to_the_state_the_other_two_languages_reach
    expected = JSON.parse(File.read("#{FIXTURES}/call-log-golden.state.json"), symbolize_names: true)
    assert_equal expected, Pinecall::Protocol.reduce(@golden)
  end

  def test_only_what_the_schema_lets_a_store_drop_is_marked_ephemeral
    @golden.select(&:ephemeral).each do |entry|
      assert Pinecall::Protocol::Codec.ephemeral?(entry.type) || entry.type == "user.transcript", entry.type
    end
  end

  def test_a_reader_that_folds_entry_by_entry_ends_where_the_whole_log_does
    one_at_a_time = @golden.reduce(Pinecall::Protocol.initial_state) do |state, entry|
      Pinecall::Protocol.apply(state, entry)
    end
    assert_equal Pinecall::Protocol.reduce(@golden), one_at_a_time
  end
end
