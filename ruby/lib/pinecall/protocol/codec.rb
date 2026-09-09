# frozen_string_literal: true

module Pinecall
  module Protocol
    # One line of a log. The envelope IS the event: what a gateway streams and what it stores are
    # the same bytes, and `seq` is written before control returns, so two readers never disagree.
    Entry = Data.define(:seq, :ts, :call, :agent, :type, :ephemeral, :data)

    # One instruction from an app to the gateway. The gateway answers with the events the command
    # produces, or with an `error` naming the id the app sent.
    Command = Data.define(:type, :agent, :call, :id, :data)

    # An entry read as what it means: the wire type, and the payload that type names.
    Event = Data.define(:type, :data)

    # JSON in, frames out, and back. The only file that knows the wire is JSON at all.
    #
    # Keys arrive as symbols and leave as strings, which is the one conversion Ruby needs: the
    # wire is snake_case and so is Ruby, so unlike the TypeScript client there is no camelCase
    # layer here — a field is called on both sides what the schema calls it.
    module Codec
      module_function

      # One log line from parsed JSON. A shape the protocol does not declare is a ProtocolError.
      def decode_entry(raw)
        fields = symbolize(raw)
        Validate.call!("Entry", fields, where: "entry")
        Entry.new(**fields)
      end

      # A whole log from the text of a JSON array, in the order it came.
      def decode_entries(text)
        parsed = JSON.parse(text, symbolize_names: true)
        raise ProtocolError, "a log is a list of entries" unless parsed.is_a?(Array)

        parsed.map { |raw| decode_entry(raw) }
      end

      # The entry's data as the shape its type names. An unknown type is a ProtocolError, because
      # a reader that shrugs at one is a reader that will shrug at a call it should have served.
      def event_of(entry)
        shape = Registry::EVENTS[entry.type]
        raise ProtocolError, "unknown event type: #{entry.type}" if shape.nil?

        Validate.call!(shape, entry.data, where: entry.type)
        Event.new(type: entry.type, data: entry.data)
      end

      # One command frame, checked here — where the backtrace still belongs to the app — against
      # the shape its type names, and then as a whole envelope.
      def command(type:, agent:, data:, call: nil, id: nil)
        shape = Registry::COMMANDS[type]
        raise ProtocolError, "unknown command type: #{type}" if shape.nil?

        Validate.call!(shape, data, where: type)
        frame = { type:, agent:, call:, data: }
        frame[:id] = id unless id.nil?
        Validate.call!("Command", frame, where: type)
        Command.new(type:, agent:, call:, id:, data:)
      end

      # A frame as it goes on the wire, as JSON text. A command with no id of its own leaves
      # without the key rather than with a null the schema would refuse; `call` is null on purpose,
      # because a command about the agent itself belongs to no call.
      def encode(frame)
        fields = frame.to_h
        fields.delete(:id) if frame.is_a?(Command) && fields[:id].nil?
        JSON.generate(fields)
      end

      # Whether an entry of this type is one a store may drop and a slow reader may miss.
      def ephemeral?(type)
        Registry::EPHEMERAL_EVENTS.include?(type)
      end

      # JSON.parse gives us symbols when we ask for them; a Hash built by hand may not have.
      def symbolize(value)
        case value
        when Hash then value.to_h { |key, inner| [key.to_sym, symbolize(inner)] }
        when Array then value.map { |inner| symbolize(inner) }
        else value
        end
      end
    end
  end
end
