# frozen_string_literal: true

module Pinecall
  module Protocol
    # What a log reduces to: one object holding everything a reader of the whole log would know.
    module State
      module_function

      # What an empty log is: nothing known, every list empty, the call idle. The three languages
      # start from the same object, so the same log leaves them in the same place.
      def initial
        {
          seq: 0,
          agent: "",
          call: nil,
          status: "idle",
          channel: nil,
          direction: nil,
          from: nil,
          to: nil,
          caller: nil,
          room: nil,
          started_at: nil,
          ended_at: nil,
          end_reason: nil,
          outcome: nil,
          user_state: nil,
          agent_state: nil,
          live: { user: nil, agent: nil },
          turns: [],
          metrics: { llm: [], stt: [], tts: [], vad: [], eou: [], eot: [], interruption: [], realtime: [], avatar: [] },
          tools: [],
          app_state: {},
          events: [],
          prompt: {},
          tools_visible: [],
          confirms: [],
          memory: [],
          sources: [],
          handoff: { active: false, by: nil },
          held: false,
          muted: false,
          transfer: nil,
          usage: [],
          cost: nil,
          routes: [],
          gaps: [],
          errors: [],
          custom: []
        }
      end
    end
  end
end
