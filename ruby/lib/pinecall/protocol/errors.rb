# frozen_string_literal: true

module Pinecall
  module Protocol
    # A message did not match the protocol: an unknown type, a bad shape, a key nobody declared.
    #
    # It is raised where the mistake was made — on the way out of an app, on the way in from a
    # gateway — so the backtrace still points at the code that built the frame.
    class ProtocolError < StandardError
    end
  end
end
