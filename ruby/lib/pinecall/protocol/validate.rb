# frozen_string_literal: true

module Pinecall
  module Protocol
    # Checks a payload against the generated shape table, and says which field is wrong.
    #
    # This is what zod does on the TypeScript side and pydantic on the Python one. Ruby has no
    # third-party schema library here on purpose: the schema already generated the table, and
    # walking it is thirty lines that never disagree with the other two languages.
    module Validate
      module_function

      # Check a payload against the named shape and return it. A shape is closed, so a key nobody
      # declared is refused: it is a message from a newer protocol, and silence would drop it.
      def call!(name, value, where: name)
        return union!(name, value, where) if Shapes::UNIONS.key?(name)
        return map!(Shapes::MAPS.fetch(name), value, where) if Shapes::MAPS.key?(name)

        shape = Shapes::SHAPES[name]
        raise ProtocolError, "#{where}: the protocol declares no shape called #{name}" if shape.nil?
        raise ProtocolError, "#{where}: expected the fields of #{name}, got #{named(value)}" unless value.is_a?(Hash)

        unknown = value.keys - shape.keys
        raise ProtocolError, "#{where}: #{name} has no field called #{unknown.join(", ")}" unless unknown.empty?

        shape.each { |field, spec| field_of!(shape: name, spec:, value:, field:, where:) }
        value
      end

      # One field of one shape: absent when it may be, and otherwise whatever its kind allows.
      def field_of!(shape:, spec:, value:, field:, where:)
        unless value.key?(field)
          raise ProtocolError, "#{where}.#{field}: #{shape} requires it" if spec[:required]

          return
        end
        field!(spec, value[field], "#{where}.#{field}")
      end

      # One value against one field's description. Every branch is a kind the generator emits.
      def field!(spec, value, where)
        if value.nil?
          return if spec[:null]

          raise ProtocolError, "#{where}: nothing is not one of the things it may be"
        end

        case spec[:kind]
        when :str then string!(spec, value, where)
        when :int then expect(value, Integer, where, "a whole number")
        when :float then expect(value, Numeric, where, "a number")
        when :bool then expect_boolean(value, where)
        when :json then expect(value, Hash, where, "an object")
        when :any then value
        when :list then list!(spec, value, where)
        when :map then map!(spec[:items], value, where)
        when :enum then one_of!(spec[:values], value, where)
        when :const then const!(spec[:const], value, where)
        when :ref then ref!(spec[:ref], value, where)
        else raise ProtocolError, "#{where}: the generator emitted a kind nobody reads: #{spec[:kind]}"
        end
      end

      # A union is told apart by the one field the schema's discriminator names.
      def union!(name, value, where)
        union = Shapes::UNIONS.fetch(name)
        on = union[:on]
        said = value.is_a?(Hash) ? value[on] : nil
        member = union[:members].find { |one| Shapes::SHAPES.dig(one, on, :const) == said }
        if member.nil?
          allowed = union[:members].filter_map { |one| Shapes::SHAPES.dig(one, on, :const) }
          raise ProtocolError, "#{where}: #{on} #{said.inspect} is not one of #{allowed.join(", ")}"
        end
        call!(member, value, where:)
      end

      # A reference points at another object, at a union, or at one of the closed lists.
      def ref!(name, value, where)
        allowed = Enums::ALL[name]
        return one_of!(allowed, value, where) unless allowed.nil?

        call!(name, value, where:)
      end

      def list!(spec, value, where)
        expect(value, Array, where, "a list")
        value.each_with_index { |item, at| field!(spec[:items], item, "#{where}[#{at}]") }
      end

      # A map's keys are the app's own names; every value is the one shape the table gives.
      def map!(spec, value, where)
        expect(value, Hash, where, "an object")
        value.each { |key, item| field!(spec, item, "#{where}.#{key}") }
      end

      # The schema's ^ and $ bind the ends of the string and Ruby's the ends of a line, so a value
      # with a line break in it is refused before the pattern is asked.
      def string!(spec, value, where)
        expect(value, String, where, "a string")
        pattern = spec[:pattern]
        return value if pattern.nil? || (!value.include?("\n") && Regexp.new(pattern).match?(value))

        raise ProtocolError, "#{where}: #{value.inspect} does not match #{pattern}"
      end

      def one_of!(values, value, where)
        return value if values.include?(value)

        raise ProtocolError, "#{where}: #{value.inspect} is not one of #{values.join(", ")}"
      end

      def const!(const, value, where)
        return value if value == const

        raise ProtocolError, "#{where}: this field is always #{const.inspect}, never #{value.inspect}"
      end

      def expect(value, type, where, called)
        return value if value.is_a?(type)

        raise ProtocolError, "#{where}: expected #{called}, got #{named(value)}"
      end

      def expect_boolean(value, where)
        return value if value == true || value == false

        raise ProtocolError, "#{where}: expected true or false, got #{named(value)}"
      end

      # What to call the thing that arrived, in the words the message uses for what was wanted.
      def named(value)
        case value
        when nil then "nothing"
        when String then "a string"
        when Integer, Float then "a number"
        when true, false then "true or false"
        when Array then "a list"
        when Hash then "an object"
        else value.class.name
        end
      end
    end
  end
end
