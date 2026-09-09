# frozen_string_literal: true

# Generated from schema/: every closed list on the wire, as a frozen array.
# Written by protocol/generate; never edited by hand.

module Pinecall
  module Protocol
    module Enums
      # The door the public came through: a phone call over SIP, the browser widget over WebRTC,
      # or WhatsApp text.
      CHANNEL = %w[phone web whatsapp].freeze
      # Inbound: the public reached the agent. Outbound: the agent reached out (a dial).
      DIRECTION = %w[inbound outbound].freeze
      # Why the call is over. Who hung up, what failed before anybody could, drained: the platform
      # took the worker down (a deploy, a stop) with the call still on it, or app_detached: the
      # app holding the agent closed its socket mid-call, so nothing was rendering the prompt or
      # answering a tool — both are nobody's fault and neither is an error.
      END_REASON = %w[caller_hung_up agent_hung_up supervisor_ended transferred no_answer busy dial_failed timeout drained app_detached error].freeze
      # Whose action ended the call. platform covers timeouts, errors and a drained worker.
      ENDED_BY = %w[caller agent supervisor platform].freeze
      # What one judge answered about a finished call. Held: the rule held. Broken: it did not,
      # and the reason names the evidence. Deferred: the judge was asked and could not settle it.
      # Skipped: nobody asked it — no model was reachable inside the call's judging budget.
      SCORE_VERDICT = %w[held broken deferred skipped].freeze
      # Cold: the caller is sent on and the agent leaves. Warm: the agent stays on the line until
      # the other side answers, then leaves.
      TRANSFER_MODE = %w[cold warm].freeze
      # Which region of the prompt a block lives in: static, before the history, cached by the
      # provider; or dynamic, after the history, replaced every turn. The append-only history in
      # between is never written by the app.
      PROMPT_REGION = %w[static dynamic].freeze
      # How the knowledge base reaches the model: retrieved, the runtime searches it every turn
      # and fills the retrieved marker before the model is asked; or tool, the model searches it
      # itself through a tool the runtime declares.
      DOCS_MODE = %w[retrieved tool].freeze
      # The three markers a view may write in a block and never resolves: memory (the contact's
      # facts, per turn), retrieved (chunks of the knowledge base, per turn), knowledge (the one
      # file, once per call). The runtime reads the line, does the work, and replaces it.
      MARKER_NAME = %w[memory retrieved knowledge].freeze
      # What the platform believes the person on the line is doing right now. The states are the
      # session's own.
      USER_STATE = %w[listening speaking away].freeze
      # What the agent is doing right now, in the session's own words: warming up, waiting,
      # hearing the caller, generating, or playing audio.
      AGENT_STATE = %w[initializing idle listening thinking speaking].freeze
      # Who a participant is to the call: the person the agent serves (over SIP or the widget),
      # the agent itself, a supervisor who took a seat in the room, a listener who only hears, or
      # a second SIP leg that room.invite brought in.
      PARTICIPANT_KIND = %w[caller agent supervisor listener sip].freeze
      # What a track carries: a microphone's audio, a camera's video, or a screen share.
      TRACK_KIND = %w[audio video screen].freeze
      # Where a track comes from, as livekit's TrackSource names it, in lower case.
      TRACK_SOURCE = %w[microphone camera screen_share screen_share_audio unknown].freeze
      # Where an outside fact came from: the tenant's backend over the app socket (app), or a
      # participant's browser over the DataChannel (participant).
      EVENT_SOURCE = %w[app participant].freeze
      # Who may see a field of the app's state: everyone in the call (public), the tenant's own
      # readers (tenant, the default for a field never declared), or nobody without masking (pii).
      VISIBILITY = %w[public tenant pii].freeze
      # Which projection a sink applies before a state or an entry leaves the platform: public for
      # a participant reading its own call, tenant for the tenant's readers. The contract is
      # docs/protocol/projections.md; a client never applies one.
      PROJECTION = %w[public tenant].freeze
      # Where the call is in its life. idle before any call.* entry, which is what an agent's own
      # log looks like.
      CALL_STATUS = %w[idle ringing dialing active ended].freeze
      # Every closed list by the name the schema gave it, for a validator to look up.
      ALL = {
        "Channel" => CHANNEL,
        "Direction" => DIRECTION,
        "EndReason" => END_REASON,
        "EndedBy" => ENDED_BY,
        "ScoreVerdict" => SCORE_VERDICT,
        "TransferMode" => TRANSFER_MODE,
        "PromptRegion" => PROMPT_REGION,
        "DocsMode" => DOCS_MODE,
        "MarkerName" => MARKER_NAME,
        "UserState" => USER_STATE,
        "AgentState" => AGENT_STATE,
        "ParticipantKind" => PARTICIPANT_KIND,
        "TrackKind" => TRACK_KIND,
        "TrackSource" => TRACK_SOURCE,
        "EventSource" => EVENT_SOURCE,
        "Visibility" => VISIBILITY,
        "Projection" => PROJECTION,
        "CallStatus" => CALL_STATUS
      }.freeze
    end
  end
end
