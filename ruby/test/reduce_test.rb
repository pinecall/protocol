# frozen_string_literal: true

require "test_helper"

# `agent.transcript` is a delta — one word of a spoken reply, one token of a written one — so what
# is on screen is every delta of the reply in flight joined, until the finished turn clears it.
class ReduceTest < Minitest::Test
  def an_entry(seq, type, data)
    Pinecall::Protocol::Entry.new(
      seq: seq, ts: 1_786_537_500.0 + seq, call: "CA_1", agent: "clinica-norte",
      type: type, ephemeral: true, data: data
    )
  end

  def a_word(seq, text, start)
    an_entry(seq, "agent.transcript", { speech_id: "s1", text: text, final: false, start: start, end: start + 0.2 })
  end

  def a_token(seq, text)
    an_entry(seq, "agent.transcript", { speech_id: "s2", text: text, final: false })
  end

  def test_the_words_of_a_spoken_reply_are_set_a_space_apart
    state = Pinecall::Protocol::Reduce.reduce([a_word(1, "Buenos", 0), a_word(2, "días,", 0.3), a_word(3, "Clínica", 0.6)])
    assert_equal "Buenos días, Clínica", state[:live][:agent]
  end

  def test_the_tokens_of_a_written_reply_keep_their_own_spacing
    state = Pinecall::Protocol::Reduce.reduce(
      [a_token(1, "Buenos"), a_token(2, " días"), a_token(3, ","), a_token(4, " clean"), a_token(5, "ing")]
    )
    assert_equal "Buenos días, cleaning", state[:live][:agent]
  end

  def test_the_finished_turn_clears_the_words_on_screen
    turn = an_entry(2, "turn.agent", { speech_id: "s1", text: "Buenos días.", interrupted: false, metrics: {} })
    state = Pinecall::Protocol::Reduce.reduce([a_word(1, "Buenos", 0), turn])
    assert_nil state[:live][:agent]
  end
end
