# frozen_string_literal: true

require "test_helper"

# An ask for a person is open until a supervisor takes the line, the wait runs out, or the caller
# hangs up: the same three endings the TypeScript and Python reducers fold it into.
class AttentionTest < Minitest::Test
  def an_entry(seq, type, data)
    Pinecall::Protocol::Entry.new(
      seq: seq, ts: 1_786_537_500.0 + seq, call: "CA_1", agent: "clinica-norte",
      type: type, ephemeral: false, data: data
    )
  end

  def asked
    an_entry(1, "attention.requested", { reason: "wants a refund", wait_s: 60 })
  end

  def test_an_ask_is_open_until_somebody_answers_it
    state = Pinecall::Protocol::Reduce.reduce([asked])
    assert_equal "open", state[:attention][:status]
    assert_in_delta 1_786_537_501.0, state[:attention][:asked_at]
  end

  def test_a_supervisor_who_takes_the_line_answers_it
    by = { id: "sup_1", name: "Lucía" }
    state = Pinecall::Protocol::Reduce.reduce([asked, an_entry(2, "attention.answered", { ok: true, by: by })])
    assert_equal "answered", state[:attention][:status]
    assert_equal "sup_1", state[:attention][:by][:id]
  end

  def test_a_caller_who_hangs_up_while_waiting_was_never_answered
    ended = an_entry(2, "call.ended", { reason: "caller_hung_up", ended_by: "caller", ended_at: 2.0, duration_s: 1.0 })
    state = Pinecall::Protocol::Reduce.reduce([asked, ended])
    assert_equal "lapsed", state[:attention][:status]
  end
end
