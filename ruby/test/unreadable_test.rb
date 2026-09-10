# frozen_string_literal: true

require "test_helper"

# A log outlives the shape of its entries: `prompt.changed` carried `region` before it carried
# `name`, and those rows are still in the table. A reader that raised on one refused the call.
class UnreadableTest < Minitest::Test
  FROM_ANOTHER_VERSION = {
    seq: 7, ts: 1.0, call: "CA_8f4a2c", agent: "clinica-norte",
    type: "prompt.changed", ephemeral: false,
    data: { region: "static", hash: "abc", chars: 10 }
  }.freeze

  def an_entry(**changed)
    Pinecall::Protocol::Entry.new(**FROM_ANOTHER_VERSION.merge(changed))
  end

  def folded(entry)
    Pinecall::Protocol::Reduce.apply(Pinecall::Protocol::State.initial, entry)
  end

  def test_an_entry_this_reader_cannot_read_is_one_line_of_the_errors_list
    state = folded(an_entry)
    assert_equal 1, state[:errors].length
    assert_equal Pinecall::Protocol::Reduce::UNREADABLE, state[:errors].first[:code]
    assert_includes state[:errors].first[:message], "prompt.changed at seq 7"
    assert_empty state[:prompt]
  end

  def test_the_fold_still_moves_to_the_seq_it_could_not_read
    state = folded(an_entry)
    assert_equal 7, state[:seq]
    assert_equal "clinica-norte", state[:agent]
    assert_equal "CA_8f4a2c", state[:call]
  end

  def test_an_entry_of_a_type_nobody_knows_is_refused_the_same_way
    state = folded(an_entry(type: "nobody.knows"))
    assert_includes state[:errors].first[:message], "nobody.knows at seq 7"
  end
end
