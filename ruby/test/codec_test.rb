# frozen_string_literal: true

require "test_helper"

# What the codec refuses, and where it says the mistake is. A frame is checked on the way out,
# in the app's own process, because a gateway's 1008 with no sentence in it teaches nobody.
class CodecTest < Minitest::Test
  def test_a_command_is_built_from_the_shape_its_type_names
    command = Pinecall::Protocol.command(
      type: "agent.say",
      agent: "clinica-norte",
      call: "CA_1",
      data: { text: "Buenas tardes." }
    )

    assert_equal "agent.say", command.type
    assert_equal({ type: "agent.say", agent: "clinica-norte", call: "CA_1", data: { text: "Buenas tardes." } },
                 JSON.parse(Pinecall::Protocol.encode(command), symbolize_names: true))
  end

  def test_a_command_with_a_field_the_schema_never_declared_is_refused_by_name
    refusal = assert_raises(Pinecall::Protocol::ProtocolError) do
      Pinecall::Protocol.command(type: "agent.say", agent: "a", call: "c", data: { text: "hola", shout: true })
    end

    assert_includes refusal.message, "shout"
  end

  def test_a_command_missing_a_required_field_says_which_one
    refusal = assert_raises(Pinecall::Protocol::ProtocolError) do
      Pinecall::Protocol.command(type: "agent.say", agent: "a", call: "c", data: {})
    end

    assert_includes refusal.message, "agent.say.text"
  end

  def test_a_word_outside_a_closed_list_is_refused_with_the_list
    refusal = assert_raises(Pinecall::Protocol::ProtocolError) do
      Pinecall::Protocol.command(
        type: "call.transfer",
        agent: "a",
        call: "c",
        data: { to: "+34910000000", mode: "sideways" }
      )
    end

    assert_includes refusal.message, "cold"
    assert_includes refusal.message, "warm"
  end

  def test_an_unknown_command_type_is_refused_before_anything_is_sent
    assert_raises(Pinecall::Protocol::ProtocolError) do
      Pinecall::Protocol.command(type: "agent.sing", agent: "a", call: "c", data: {})
    end
  end

  def test_an_entry_of_a_type_this_protocol_does_not_declare_is_named_in_the_error
    entry = Pinecall::Protocol::Entry.new(
      seq: 1, ts: 1.0, call: "c", agent: "a", type: "turn.sideways", ephemeral: false, data: {}
    )
    refusal = assert_raises(Pinecall::Protocol::ProtocolError) { Pinecall::Protocol.event_of(entry) }

    assert_includes refusal.message, "turn.sideways"
  end

  def test_a_supervise_verb_is_told_apart_by_the_field_the_schema_discriminates_on
    Pinecall::Protocol::Validate.call!("Verb", { verb: "transfer", to: "+34910000000", mode: "cold" })

    assert_raises(Pinecall::Protocol::ProtocolError) do
      Pinecall::Protocol::Validate.call!("Verb", { verb: "improvise" })
    end
  end
end
