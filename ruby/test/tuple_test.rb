# frozen_string_literal: true

require "test_helper"

# A tuple: a list whose places differ and whose length is closed. A transcript line is [who, what],
# and the whole point of the kind is that neither place may go missing without the reader noticing.
class TupleTest < Minitest::Test
  def test_a_line_of_a_transcript_is_who_and_what
    golden = Pinecall::Protocol::Validate.call!(
      "ExtractionGolden",
      { name: "la alergia", said: [["caller", "Soy alergica"], ["agent", "Anotado"]] },
      where: "case"
    )

    assert_equal 2, golden[:said].length
  end

  def test_a_line_missing_its_second_place_says_how_long_a_line_is
    refusal = assert_raises(Pinecall::Protocol::ProtocolError) do
      Pinecall::Protocol::Validate.call!(
        "ExtractionGolden", { name: "media linea", said: [["caller"]] }, where: "case"
      )
    end

    assert_includes refusal.message, "2 things"
    assert_includes refusal.message, "said[0]"
  end

  def test_a_place_of_the_wrong_type_is_named_by_its_own_index
    refusal = assert_raises(Pinecall::Protocol::ProtocolError) do
      Pinecall::Protocol::Validate.call!(
        "ExtractionGolden", { name: "un numero", said: [["caller", 7]] }, where: "case"
      )
    end

    assert_includes refusal.message, "said[0][1]"
  end

  def test_a_line_that_is_not_a_list_at_all_is_refused
    refusal = assert_raises(Pinecall::Protocol::ProtocolError) do
      Pinecall::Protocol::Validate.call!(
        "ExtractionGolden", { name: "una frase", said: ["caller: hola"] }, where: "case"
      )
    end

    assert_includes refusal.message, "said[0]"
  end
end
