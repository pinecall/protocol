# frozen_string_literal: true

# Generated from schema/: every event and command by its wire type.
# Written by protocol/generate; never edited by hand.

require "set"

module Pinecall
  module Protocol
    module Registry
      # The shape each event's data is, by the event's wire type.
      EVENTS = {
        "agent.configured" => "AgentConfigured",
        "agent.registered" => "AgentRegistered",
        "agent.state" => "AgentStateChanged",
        "agent.transcript" => "AgentTranscript",
        "call.dialing" => "CallDialing",
        "call.ended" => "CallEnded",
        "call.line" => "CallLine",
        "call.ringing" => "CallRinging",
        "call.score" => "CallScore",
        "call.started" => "CallStarted",
        "call.summary" => "CallSummary",
        "call.transferred" => "CallTransferred",
        "callback.requested" => "CallbackRequested",
        "confirm.declined" => "ConfirmDeclined",
        "confirm.granted" => "ConfirmGranted",
        "confirm.request" => "ConfirmRequest",
        "credits.exhausted" => "CreditsExhausted",
        "custom" => "Custom",
        "docs.sources" => "DocsSources",
        "error" => "ErrorEvent",
        "event.received" => "EventReceived",
        "fleet.full" => "FleetFull",
        "log.caught_up" => "LogCaughtUp",
        "log.gap" => "LogGap",
        "memory.ops" => "MemoryOps",
        "metrics.avatar" => "AvatarMetrics",
        "metrics.eot" => "EOTInferenceMetrics",
        "metrics.eou" => "EOUMetrics",
        "metrics.interruption" => "InterruptionMetrics",
        "metrics.llm" => "LLMMetrics",
        "metrics.realtime" => "RealtimeModelMetrics",
        "metrics.stt" => "STTMetrics",
        "metrics.tts" => "TTSMetrics",
        "metrics.vad" => "VADMetrics",
        "participant.joined" => "ParticipantJoined",
        "participant.left" => "ParticipantLeft",
        "participant.speaking" => "ParticipantSpeaking",
        "pong" => "Pong",
        "prompt.changed" => "PromptChanged",
        "room.opened" => "RoomOpened",
        "room.sent" => "RoomSent",
        "state.changed" => "StateChanged",
        "supervisor.ended" => "SupervisorEnded",
        "supervisor.released" => "SupervisorReleased",
        "supervisor.said" => "SupervisorSaid",
        "supervisor.took_over" => "SupervisorTookOver",
        "supervisor.transferred" => "SupervisorTransferred",
        "supervisor.whispered" => "SupervisorWhispered",
        "tool.call" => "ToolCall",
        "tool.result" => "ToolResult",
        "tools.changed" => "ToolsChanged",
        "track.published" => "TrackPublished",
        "track.unpublished" => "TrackUnpublished",
        "turn.agent" => "AgentTurnEnded",
        "turn.user" => "UserTurnEnded",
        "user.state" => "UserStateChanged",
        "user.transcript" => "UserTranscript"
      }.freeze

      # The shape each command's data is, by the command's wire type.
      COMMANDS = {
        "agent.configure" => "AgentConfigure",
        "agent.register" => "AgentRegister",
        "agent.reply" => "AgentReply",
        "agent.say" => "AgentSay",
        "call.dial" => "CallDial",
        "call.dtmf" => "CallDtmf",
        "call.event" => "CallEvent",
        "call.hangup" => "CallHangup",
        "call.hold" => "CallHold",
        "call.log" => "CallLog",
        "call.mute" => "CallMute",
        "call.transfer" => "CallTransfer",
        "call.unhold" => "CallUnhold",
        "call.unmute" => "CallUnmute",
        "participant.mute" => "ParticipantMute",
        "participant.remove" => "ParticipantRemove",
        "ping" => "Ping",
        "prompt.set" => "PromptSet",
        "room.invite" => "RoomInvite",
        "room.send" => "RoomSend",
        "session.configure" => "SessionConfigure",
        "state.set" => "StateSet",
        "supervisor.verb" => "SupervisorVerb",
        "tool.result" => "ToolResult",
        "tools.set" => "ToolsSet"
      }.freeze

      # Every event this protocol declares, in the schema's own order.
      EVENT_TYPES = %w[agent.configured agent.registered agent.state agent.transcript call.dialing call.ended call.line call.ringing call.score call.started call.summary call.transferred callback.requested confirm.declined confirm.granted confirm.request credits.exhausted custom docs.sources error event.received fleet.full log.caught_up log.gap memory.ops metrics.avatar metrics.eot metrics.eou metrics.interruption metrics.llm metrics.realtime metrics.stt metrics.tts metrics.vad participant.joined participant.left participant.speaking pong prompt.changed room.opened room.sent state.changed supervisor.ended supervisor.released supervisor.said supervisor.took_over supervisor.transferred supervisor.whispered tool.call tool.result tools.changed track.published track.unpublished turn.agent turn.user user.state user.transcript].freeze

      # Every command an app may send.
      COMMAND_TYPES = %w[agent.configure agent.register agent.reply agent.say call.dial call.dtmf call.event call.hangup call.hold call.log call.mute call.transfer call.unhold call.unmute participant.mute participant.remove ping prompt.set room.invite room.send session.configure state.set supervisor.verb tool.result tools.set].freeze

      # Entries a store may drop and a slow reader may miss without harm: the entry's
      # own ephemeral flag defaults to this.
      EPHEMERAL_EVENTS = %w[agent.transcript log.caught_up log.gap metrics.vad participant.speaking pong room.sent user.transcript].to_set.freeze

      # The one event that ends a call: after it nothing more is true and the log seals.
      TERMINAL_EVENT = "call.score"

      # Which events a command lands in the log as, so a caller knows what to wait for.
      PRODUCES = {
        "agent.configure" => %w[agent.configured],
        "agent.register" => %w[agent.registered],
        "agent.reply" => %w[turn.agent],
        "agent.say" => %w[turn.agent],
        "call.dial" => %w[call.dialing],
        "call.dtmf" => [],
        "call.event" => %w[event.received],
        "call.hangup" => %w[call.ended],
        "call.hold" => %w[call.line],
        "call.log" => %w[custom],
        "call.mute" => %w[call.line],
        "call.transfer" => %w[call.transferred],
        "call.unhold" => %w[call.line],
        "call.unmute" => %w[call.line],
        "participant.mute" => %w[track.unpublished],
        "participant.remove" => %w[participant.left],
        "ping" => %w[pong],
        "prompt.set" => %w[prompt.changed],
        "room.invite" => %w[participant.joined],
        "room.send" => %w[room.sent],
        "session.configure" => %w[state.changed agent.configured],
        "state.set" => %w[state.changed],
        "supervisor.verb" => %w[supervisor.said supervisor.whispered supervisor.took_over supervisor.released supervisor.transferred supervisor.ended],
        "tool.result" => %w[tool.result],
        "tools.set" => %w[tools.changed]
      }.freeze
    end
  end
end
