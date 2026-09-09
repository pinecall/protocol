# frozen_string_literal: true

# Generated from schema/: every named shape, as the table Validate walks.
# Written by protocol/generate; never edited by hand.

module Pinecall
  module Protocol
    module Shapes
      # Every object the wire carries: its fields, and what each field may be. A shape is
      # closed — the schema says additionalProperties: false — so a key nobody declared is
      # a message from a newer protocol and the reader is told so by name.
      SHAPES = {
        "Contact" => {
          id: { kind: :str },
          phone: { kind: :str },
          name: { kind: :str },
          email: { kind: :str },
          external_id: { kind: :str }
        }.freeze,
        "Route" => {
          channel: { kind: :ref, ref: "Channel", required: true },
          number: { kind: :str, null: true, required: true },
          label: { kind: :str }
        }.freeze,
        "Supervisor" => {
          id: { kind: :str, required: true },
          name: { kind: :str }
        }.freeze,
        "ToolSpec" => {
          name: { kind: :str, required: true },
          description: { kind: :str, required: true },
          parameters: { kind: :json, required: true },
          side_effect: { kind: :enum, values: %w[read write irreversible], default: "read" },
          confirm: { kind: :str },
          pii: { kind: :list, items: { kind: :str } },
          timeout_s: { kind: :float }
        }.freeze,
        "ToolResult" => {
          call_id: { kind: :str, required: true },
          name: { kind: :str, required: true },
          output: { kind: :any },
          error: { kind: :str },
          summary: { kind: :str },
          duration_s: { kind: :float }
        }.freeze,
        "MemoryFact" => {
          id: { kind: :str },
          text: { kind: :str, required: true },
          score: { kind: :float },
          source: { kind: :str }
        }.freeze,
        "MemoryOp" => {
          op: { kind: :enum, values: %w[recall remember forget], required: true },
          contact: { kind: :str },
          query: { kind: :str },
          facts: { kind: :list, items: { kind: :ref, ref: "MemoryFact" }, required: true },
          took_ms: { kind: :float, required: true }
        }.freeze,
        "DocSource" => {
          id: { kind: :str, required: true },
          path: { kind: :str, required: true },
          heading: { kind: :str },
          score: { kind: :float, required: true },
          excerpt: { kind: :str }
        }.freeze,
        "CostRate" => {
          currency: { kind: :const, const: "EUR", required: true },
          usd_to_eur: { kind: :float, required: true },
          as_of: { kind: :str, required: true }
        }.freeze,
        "CostRow" => {
          provider: { kind: :str, required: true },
          model: { kind: :str, required: true },
          unit: { kind: :enum, values: %w[input_tokens cached_input_tokens cache_creation_tokens output_tokens characters audio_seconds requests session_seconds], required: true },
          quantity: { kind: :float, required: true },
          unit_price_usd: { kind: :float, required: true },
          eur: { kind: :float, required: true }
        }.freeze,
        "UnpricedRow" => {
          provider: { kind: :str, required: true },
          model: { kind: :str, required: true }
        }.freeze,
        "Cost" => {
          eur: { kind: :float, required: true },
          rate: { kind: :ref, ref: "CostRate", required: true },
          rows: { kind: :list, items: { kind: :ref, ref: "CostRow" }, required: true },
          unpriced: { kind: :list, items: { kind: :ref, ref: "UnpricedRow" }, required: true }
        }.freeze,
        "VoiceConfig" => {
          name: { kind: :str },
          provider: { kind: :str },
          model: { kind: :str },
          voice_id: { kind: :str }
        }.freeze,
        "ModelConfig" => {
          provider: { kind: :str, required: true },
          model: { kind: :str, required: true },
          temperature: { kind: :float }
        }.freeze,
        "TurnConfig" => {
          min_interruption_words: { kind: :int },
          endpointing_ms: { kind: :int }
        }.freeze,
        "Pronunciation" => {
          word: { kind: :str, required: true },
          spoken: { kind: :str, required: true }
        }.freeze,
        "StateFieldSpec" => {
          name: { kind: :str, required: true },
          visibility: { kind: :ref, ref: "Visibility", required: true }
        }.freeze,
        "EventSpec" => {
          name: { kind: :str, required: true },
          from: { kind: :list, items: { kind: :ref, ref: "EventSource" }, required: true }
        }.freeze,
        "AgentConfig" => {
          instructions: { kind: :str },
          language: { kind: :str },
          greeting: { kind: :str },
          voice: { kind: :ref, ref: "VoiceConfig" },
          llm: { kind: :ref, ref: "ModelConfig" },
          stt: { kind: :ref, ref: "ModelConfig" },
          turn: { kind: :ref, ref: "TurnConfig" },
          says: { kind: :list, items: { kind: :ref, ref: "Pronunciation" } },
          hears: { kind: :list, items: { kind: :str } },
          tools: { kind: :list, items: { kind: :ref, ref: "ToolSpec" } },
          state_fields: { kind: :list, items: { kind: :ref, ref: "StateFieldSpec" } },
          events: { kind: :list, items: { kind: :ref, ref: "EventSpec" } }
        }.freeze,
        "Entry" => {
          seq: { kind: :int, required: true },
          ts: { kind: :float, required: true },
          call: { kind: :str, null: true, required: true },
          agent: { kind: :str, required: true },
          type: { kind: :str, required: true },
          ephemeral: { kind: :bool, required: true },
          data: { kind: :json, required: true }
        }.freeze,
        "Command" => {
          type: { kind: :str, required: true },
          agent: { kind: :str, required: true },
          call: { kind: :str, null: true, required: true },
          id: { kind: :str },
          data: { kind: :json, required: true }
        }.freeze,
        "Metadata" => {
          model_name: { kind: :str, null: true },
          model_provider: { kind: :str, null: true }
        }.freeze,
        "LLMMetrics" => {
          type: { kind: :const, const: "llm_metrics", required: true },
          label: { kind: :str, required: true },
          request_id: { kind: :str, required: true },
          timestamp: { kind: :float, required: true },
          duration: { kind: :float, required: true },
          ttft: { kind: :float, required: true },
          cancelled: { kind: :bool, required: true },
          completion_tokens: { kind: :int, required: true },
          prompt_tokens: { kind: :int, required: true },
          prompt_cached_tokens: { kind: :int, required: true },
          cache_creation_tokens: { kind: :int },
          reasoning_tokens: { kind: :int },
          total_tokens: { kind: :int, required: true },
          tokens_per_second: { kind: :float, required: true },
          speech_id: { kind: :str, null: true },
          metadata: { kind: :ref, null: true, ref: "Metadata" }
        }.freeze,
        "STTMetrics" => {
          type: { kind: :const, const: "stt_metrics", required: true },
          label: { kind: :str, required: true },
          request_id: { kind: :str, required: true },
          timestamp: { kind: :float, required: true },
          duration: { kind: :float, required: true },
          audio_duration: { kind: :float, required: true },
          input_tokens: { kind: :int },
          output_tokens: { kind: :int },
          streamed: { kind: :bool, required: true },
          acquire_time: { kind: :float },
          connection_reused: { kind: :bool },
          metadata: { kind: :ref, null: true, ref: "Metadata" }
        }.freeze,
        "TTSMetrics" => {
          type: { kind: :const, const: "tts_metrics", required: true },
          label: { kind: :str, required: true },
          request_id: { kind: :str, required: true },
          timestamp: { kind: :float, required: true },
          ttfb: { kind: :float, required: true },
          duration: { kind: :float, required: true },
          audio_duration: { kind: :float, required: true },
          cancelled: { kind: :bool, required: true },
          characters_count: { kind: :int, required: true },
          input_tokens: { kind: :int },
          output_tokens: { kind: :int },
          streamed: { kind: :bool, required: true },
          acquire_time: { kind: :float },
          connection_reused: { kind: :bool },
          segment_id: { kind: :str, null: true },
          speech_id: { kind: :str, null: true },
          metadata: { kind: :ref, null: true, ref: "Metadata" }
        }.freeze,
        "VADMetrics" => {
          type: { kind: :const, const: "vad_metrics", required: true },
          label: { kind: :str, required: true },
          timestamp: { kind: :float, required: true },
          idle_time: { kind: :float, required: true },
          inference_duration_total: { kind: :float, required: true },
          inference_count: { kind: :int, required: true },
          metadata: { kind: :ref, null: true, ref: "Metadata" }
        }.freeze,
        "EOUMetrics" => {
          type: { kind: :const, const: "eou_metrics", required: true },
          timestamp: { kind: :float, required: true },
          end_of_utterance_delay: { kind: :float, required: true },
          transcription_delay: { kind: :float, required: true },
          on_user_turn_completed_delay: { kind: :float, required: true },
          speech_id: { kind: :str, null: true },
          metadata: { kind: :ref, null: true, ref: "Metadata" }
        }.freeze,
        "EOTInferenceMetrics" => {
          type: { kind: :const, const: "eot_inference_metrics", required: true },
          timestamp: { kind: :float, required: true },
          total_duration: { kind: :float, required: true },
          detection_delay: { kind: :float, required: true },
          prediction_duration: { kind: :float, required: true },
          num_requests: { kind: :int },
          metadata: { kind: :ref, null: true, ref: "Metadata" }
        }.freeze,
        "InterruptionMetrics" => {
          type: { kind: :const, const: "interruption_metrics", required: true },
          timestamp: { kind: :float, required: true },
          total_duration: { kind: :float, required: true },
          prediction_duration: { kind: :float, required: true },
          detection_delay: { kind: :float, required: true },
          num_interruptions: { kind: :int, required: true },
          num_backchannels: { kind: :int, required: true },
          num_requests: { kind: :int, required: true },
          metadata: { kind: :ref, null: true, ref: "Metadata" }
        }.freeze,
        "RealtimeCachedTokenDetails" => {
          audio_tokens: { kind: :int },
          text_tokens: { kind: :int },
          image_tokens: { kind: :int }
        }.freeze,
        "RealtimeInputTokenDetails" => {
          audio_tokens: { kind: :int },
          text_tokens: { kind: :int },
          image_tokens: { kind: :int },
          cached_tokens: { kind: :int },
          cached_tokens_details: { kind: :ref, null: true, ref: "RealtimeCachedTokenDetails" }
        }.freeze,
        "RealtimeOutputTokenDetails" => {
          text_tokens: { kind: :int },
          audio_tokens: { kind: :int },
          image_tokens: { kind: :int }
        }.freeze,
        "RealtimeModelMetrics" => {
          type: { kind: :const, const: "realtime_model_metrics", required: true },
          label: { kind: :str },
          request_id: { kind: :str, required: true },
          timestamp: { kind: :float, required: true },
          duration: { kind: :float },
          session_duration: { kind: :float },
          ttft: { kind: :float },
          cancelled: { kind: :bool },
          input_tokens: { kind: :int },
          output_tokens: { kind: :int },
          total_tokens: { kind: :int },
          tokens_per_second: { kind: :float },
          input_token_details: { kind: :ref, ref: "RealtimeInputTokenDetails", required: true },
          output_token_details: { kind: :ref, ref: "RealtimeOutputTokenDetails", required: true },
          acquire_time: { kind: :float },
          connection_reused: { kind: :bool },
          metadata: { kind: :ref, null: true, ref: "Metadata" }
        }.freeze,
        "AvatarMetrics" => {
          type: { kind: :const, const: "avatar_metrics", required: true },
          timestamp: { kind: :float, required: true },
          playback_latency: { kind: :float },
          session_started_time: { kind: :float, null: true },
          avatar_joined_time: { kind: :float, null: true },
          metadata: { kind: :ref, null: true, ref: "Metadata" }
        }.freeze,
        "TurnMetadata" => {
          model_name: { kind: :str },
          model_provider: { kind: :str }
        }.freeze,
        "UserTurnMetrics" => {
          started_speaking_at: { kind: :float },
          stopped_speaking_at: { kind: :float },
          transcription_delay: { kind: :float },
          end_of_turn_delay: { kind: :float },
          on_user_turn_completed_delay: { kind: :float },
          stt_metadata: { kind: :ref, ref: "TurnMetadata" }
        }.freeze,
        "AgentTurnMetrics" => {
          started_speaking_at: { kind: :float },
          stopped_speaking_at: { kind: :float },
          llm_node_ttft: { kind: :float },
          llm_node_tps: { kind: :float },
          llm_node_ttfs: { kind: :float },
          tts_node_ttfb: { kind: :float },
          playback_latency: { kind: :float },
          e2e_latency: { kind: :float },
          provider_request_ids: { kind: :list, items: { kind: :str } },
          llm_metadata: { kind: :ref, ref: "TurnMetadata" },
          tts_metadata: { kind: :ref, ref: "TurnMetadata" }
        }.freeze,
        "LLMModelUsage" => {
          type: { kind: :const, const: "llm_usage", required: true },
          provider: { kind: :str, required: true },
          model: { kind: :str, required: true },
          input_tokens: { kind: :int },
          input_cached_tokens: { kind: :int },
          input_cache_creation_tokens: { kind: :int },
          input_audio_tokens: { kind: :int },
          input_cached_audio_tokens: { kind: :int },
          input_text_tokens: { kind: :int },
          input_cached_text_tokens: { kind: :int },
          input_image_tokens: { kind: :int },
          input_cached_image_tokens: { kind: :int },
          output_tokens: { kind: :int },
          output_audio_tokens: { kind: :int },
          output_text_tokens: { kind: :int },
          output_reasoning_tokens: { kind: :int },
          session_duration: { kind: :float }
        }.freeze,
        "TTSModelUsage" => {
          type: { kind: :const, const: "tts_usage", required: true },
          provider: { kind: :str, required: true },
          model: { kind: :str, required: true },
          input_tokens: { kind: :int },
          output_tokens: { kind: :int },
          characters_count: { kind: :int },
          audio_duration: { kind: :float }
        }.freeze,
        "STTModelUsage" => {
          type: { kind: :const, const: "stt_usage", required: true },
          provider: { kind: :str, required: true },
          model: { kind: :str, required: true },
          input_tokens: { kind: :int },
          output_tokens: { kind: :int },
          audio_duration: { kind: :float }
        }.freeze,
        "InterruptionModelUsage" => {
          type: { kind: :const, const: "interruption_usage", required: true },
          provider: { kind: :str, required: true },
          model: { kind: :str, required: true },
          total_requests: { kind: :int }
        }.freeze,
        "EOTModelUsage" => {
          type: { kind: :const, const: "eot_usage", required: true },
          provider: { kind: :str, required: true },
          model: { kind: :str, required: true },
          total_requests: { kind: :int }
        }.freeze,
        "CallState" => {
          state: { kind: :ref, ref: "State", required: true },
          last_seq: { kind: :int, required: true },
          live: { kind: :bool, required: true }
        }.freeze,
        "LogPage" => {
          entries: { kind: :list, items: { kind: :ref, ref: "Entry" }, required: true },
          live: { kind: :bool, required: true },
          next: { kind: :int, null: true, required: true }
        }.freeze,
        "SessionLine" => {
          call: { kind: :str, required: true },
          live: { kind: :bool, required: true },
          last_seq: { kind: :int, required: true },
          status: { kind: :ref, ref: "CallStatus", required: true },
          channel: { kind: :ref, null: true, ref: "Channel", required: true },
          direction: { kind: :ref, null: true, ref: "Direction", required: true },
          from: { kind: :str, null: true, required: true },
          to: { kind: :str, null: true, required: true },
          caller: { kind: :ref, null: true, ref: "Contact", required: true },
          started_at: { kind: :float, null: true, required: true },
          ended_at: { kind: :float, null: true, required: true },
          end_reason: { kind: :ref, null: true, ref: "EndReason", required: true },
          outcome: { kind: :str, null: true, required: true },
          cost: { kind: :ref, null: true, ref: "Cost", required: true }
        }.freeze,
        "SessionList" => {
          calls: { kind: :list, items: { kind: :ref, ref: "SessionLine" }, required: true }
        }.freeze,
        "HeldAgent" => {
          slug: { kind: :str, required: true },
          channels: { kind: :list, items: { kind: :ref, ref: "Channel" }, required: true }
        }.freeze,
        "AgentList" => {
          agents: { kind: :list, items: { kind: :ref, ref: "HeldAgent" }, required: true }
        }.freeze,
        "RoomOpened" => {
          name: { kind: :str, required: true },
          sid: { kind: :str, required: true },
          channel: { kind: :ref, ref: "Channel", required: true }
        }.freeze,
        "ParticipantJoined" => {
          identity: { kind: :str, required: true },
          kind: { kind: :ref, ref: "ParticipantKind", required: true },
          name: { kind: :str },
          attributes: { kind: :json, required: true }
        }.freeze,
        "ParticipantLeft" => {
          identity: { kind: :str, required: true },
          reason: { kind: :str, required: true }
        }.freeze,
        "ParticipantSpeaking" => {
          identity: { kind: :str, required: true },
          speaking: { kind: :bool, required: true }
        }.freeze,
        "TrackPublished" => {
          identity: { kind: :str, required: true },
          kind: { kind: :ref, ref: "TrackKind", required: true },
          source: { kind: :ref, ref: "TrackSource", required: true }
        }.freeze,
        "TrackUnpublished" => {
          identity: { kind: :str, required: true },
          kind: { kind: :ref, ref: "TrackKind", required: true },
          source: { kind: :ref, ref: "TrackSource", required: true }
        }.freeze,
        "EventReceived" => {
          name: { kind: :str, required: true },
          data: { kind: :json, required: true },
          source: { kind: :ref, ref: "EventSource", required: true },
          identity: { kind: :str }
        }.freeze,
        "RoomSent" => {
          topic: { kind: :str, required: true },
          to: { kind: :str },
          bytes: { kind: :int, required: true }
        }.freeze,
        "UserTurn" => {
          role: { kind: :const, const: "user", required: true },
          speech_id: { kind: :str, required: true },
          item_id: { kind: :str },
          text: { kind: :str, required: true },
          language: { kind: :str },
          transcript_confidence: { kind: :float },
          metrics: { kind: :ref, ref: "UserTurnMetrics", required: true }
        }.freeze,
        "AgentTurn" => {
          role: { kind: :const, const: "agent", required: true },
          speech_id: { kind: :str, required: true },
          item_id: { kind: :str },
          text: { kind: :str, required: true },
          interrupted: { kind: :bool, required: true },
          metrics: { kind: :ref, ref: "AgentTurnMetrics", required: true }
        }.freeze,
        "CollectedMetrics" => {
          llm: { kind: :list, items: { kind: :ref, ref: "LLMMetrics" }, required: true },
          stt: { kind: :list, items: { kind: :ref, ref: "STTMetrics" }, required: true },
          tts: { kind: :list, items: { kind: :ref, ref: "TTSMetrics" }, required: true },
          vad: { kind: :list, items: { kind: :ref, ref: "VADMetrics" }, required: true },
          eou: { kind: :list, items: { kind: :ref, ref: "EOUMetrics" }, required: true },
          eot: { kind: :list, items: { kind: :ref, ref: "EOTInferenceMetrics" }, required: true },
          interruption: { kind: :list, items: { kind: :ref, ref: "InterruptionMetrics" }, required: true },
          realtime: { kind: :list, items: { kind: :ref, ref: "RealtimeModelMetrics" }, required: true },
          avatar: { kind: :list, items: { kind: :ref, ref: "AvatarMetrics" }, required: true }
        }.freeze,
        "ToolRun" => {
          call_id: { kind: :str, required: true },
          name: { kind: :str, required: true },
          arguments: { kind: :json, required: true },
          speech_id: { kind: :str },
          status: { kind: :enum, values: %w[running done failed], required: true },
          output: { kind: :any },
          error: { kind: :str },
          summary: { kind: :str },
          duration_s: { kind: :float },
          seq: { kind: :int, required: true }
        }.freeze,
        "PromptRegionState" => {
          hash: { kind: :str, required: true },
          chars: { kind: :int, required: true },
          seq: { kind: :int, required: true }
        }.freeze,
        "PromptState" => {
          static: { kind: :ref, null: true, ref: "PromptRegionState", required: true },
          view: { kind: :ref, null: true, ref: "PromptRegionState", required: true }
        }.freeze,
        "Confirm" => {
          tool: { kind: :str, required: true },
          call_id: { kind: :str, required: true },
          audience: { kind: :str, required: true },
          phrase: { kind: :str, required: true },
          status: { kind: :enum, values: %w[pending granted declined], required: true },
          said: { kind: :str },
          reason: { kind: :str }
        }.freeze,
        "Handoff" => {
          active: { kind: :bool, required: true },
          by: { kind: :ref, null: true, ref: "Supervisor", required: true }
        }.freeze,
        "TransferState" => {
          to: { kind: :str, required: true },
          mode: { kind: :ref, ref: "TransferMode", required: true },
          status: { kind: :enum, values: %w[requested done failed], required: true },
          by: { kind: :enum, values: %w[agent supervisor], required: true }
        }.freeze,
        "LiveTranscript" => {
          user: { kind: :str, null: true, required: true },
          agent: { kind: :str, null: true, required: true }
        }.freeze,
        "Gap" => {
          from_seq: { kind: :int, required: true },
          to_seq: { kind: :int, required: true }
        }.freeze,
        "LoggedError" => {
          seq: { kind: :int, required: true },
          code: { kind: :str, required: true },
          message: { kind: :str, required: true }
        }.freeze,
        "Participant" => {
          identity: { kind: :str, required: true },
          kind: { kind: :ref, ref: "ParticipantKind", required: true },
          name: { kind: :str },
          joined_at: { kind: :float, required: true },
          speaking: { kind: :bool, required: true },
          attributes: { kind: :json, required: true }
        }.freeze,
        "Room" => {
          name: { kind: :str, required: true },
          sid: { kind: :str, required: true },
          participants: { kind: :list, items: { kind: :ref, ref: "Participant" }, required: true },
          caller: { kind: :str, null: true, required: true }
        }.freeze,
        "ReceivedEvent" => {
          seq: { kind: :int, required: true },
          name: { kind: :str, required: true },
          source: { kind: :ref, ref: "EventSource", required: true },
          identity: { kind: :str }
        }.freeze,
        "CustomNote" => {
          seq: { kind: :int, required: true },
          name: { kind: :str, required: true },
          data: { kind: :json, required: true }
        }.freeze,
        "State" => {
          seq: { kind: :int, required: true },
          agent: { kind: :str, required: true },
          call: { kind: :str, null: true, required: true },
          status: { kind: :ref, ref: "CallStatus", required: true },
          channel: { kind: :ref, null: true, ref: "Channel", required: true },
          direction: { kind: :ref, null: true, ref: "Direction", required: true },
          from: { kind: :str, null: true, required: true },
          to: { kind: :str, null: true, required: true },
          caller: { kind: :ref, null: true, ref: "Contact", required: true },
          room: { kind: :ref, null: true, ref: "Room", required: true },
          started_at: { kind: :float, null: true, required: true },
          ended_at: { kind: :float, null: true, required: true },
          end_reason: { kind: :ref, null: true, ref: "EndReason", required: true },
          outcome: { kind: :str, null: true, required: true },
          user_state: { kind: :ref, null: true, ref: "UserState", required: true },
          agent_state: { kind: :ref, null: true, ref: "AgentState", required: true },
          live: { kind: :ref, ref: "LiveTranscript", required: true },
          turns: { kind: :list, items: { kind: :ref, ref: "Turn" }, required: true },
          metrics: { kind: :ref, ref: "CollectedMetrics", required: true },
          tools: { kind: :list, items: { kind: :ref, ref: "ToolRun" }, required: true },
          app_state: { kind: :json, required: true },
          events: { kind: :list, items: { kind: :ref, ref: "ReceivedEvent" }, required: true },
          prompt: { kind: :ref, ref: "PromptState", required: true },
          tools_visible: { kind: :list, items: { kind: :str }, required: true },
          confirms: { kind: :list, items: { kind: :ref, ref: "Confirm" }, required: true },
          memory: { kind: :list, items: { kind: :ref, ref: "MemoryOp" }, required: true },
          sources: { kind: :list, items: { kind: :ref, ref: "DocSource" }, required: true },
          handoff: { kind: :ref, ref: "Handoff", required: true },
          held: { kind: :bool, required: true },
          muted: { kind: :bool, required: true },
          transfer: { kind: :ref, null: true, ref: "TransferState", required: true },
          usage: { kind: :list, items: { kind: :ref, ref: "ModelUsage" }, required: true },
          cost: { kind: :ref, null: true, ref: "Cost", required: true },
          routes: { kind: :list, items: { kind: :ref, ref: "Route" }, required: true },
          gaps: { kind: :list, items: { kind: :ref, ref: "Gap" }, required: true },
          errors: { kind: :list, items: { kind: :ref, ref: "LoggedError" }, required: true },
          custom: { kind: :list, items: { kind: :ref, ref: "CustomNote" }, required: true }
        }.freeze,
        "SayVerb" => {
          verb: { kind: :const, const: "say", required: true },
          text: { kind: :str, required: true }
        }.freeze,
        "WhisperVerb" => {
          verb: { kind: :const, const: "whisper", required: true },
          text: { kind: :str, required: true }
        }.freeze,
        "TakeoverVerb" => {
          verb: { kind: :const, const: "takeover", required: true }
        }.freeze,
        "ReleaseVerb" => {
          verb: { kind: :const, const: "release", required: true }
        }.freeze,
        "TransferVerb" => {
          verb: { kind: :const, const: "transfer", required: true },
          to: { kind: :str, required: true },
          mode: { kind: :ref, ref: "TransferMode", required: true }
        }.freeze,
        "EndVerb" => {
          verb: { kind: :const, const: "end", required: true },
          reason: { kind: :str }
        }.freeze,
        "AgentConfigure" => {
          config: { kind: :ref, ref: "AgentConfig", required: true }
        }.freeze,
        "AgentRegister" => {
          routes: { kind: :list, items: { kind: :ref, ref: "Route" }, required: true },
          sdk: { kind: :str },
          takes_unclaimed: { kind: :bool, default: true }
        }.freeze,
        "AgentReply" => {
          instructions: { kind: :str, required: true },
          allow_interruptions: { kind: :bool }
        }.freeze,
        "AgentSay" => {
          text: { kind: :str, required: true },
          allow_interruptions: { kind: :bool }
        }.freeze,
        "CallDial" => {
          to: { kind: :str, required: true },
          from: { kind: :str },
          caller: { kind: :ref, ref: "Contact" },
          metadata: { kind: :json }
        }.freeze,
        "CallDtmf" => {
          digits: { kind: :str, required: true }
        }.freeze,
        "CallEvent" => {
          name: { kind: :str, required: true },
          data: { kind: :json, required: true }
        }.freeze,
        "CallHangup" => {
          reason: { kind: :str }
        }.freeze,
        "CallHold" => {}.freeze,
        "CallLog" => {
          name: { kind: :str, required: true },
          data: { kind: :json, required: true }
        }.freeze,
        "CallMute" => {}.freeze,
        "CallTransfer" => {
          to: { kind: :str, required: true },
          mode: { kind: :ref, ref: "TransferMode", required: true }
        }.freeze,
        "CallUnhold" => {}.freeze,
        "CallUnmute" => {}.freeze,
        "ParticipantMute" => {
          identity: { kind: :str, required: true }
        }.freeze,
        "ParticipantRemove" => {
          identity: { kind: :str, required: true }
        }.freeze,
        "Ping" => {}.freeze,
        "PromptSet" => {
          region: { kind: :ref, ref: "PromptRegion", required: true },
          text: { kind: :str, required: true }
        }.freeze,
        "RoomInvite" => {
          to: { kind: :str, required: true },
          kind: { kind: :enum, values: %w[sip participant], required: true }
        }.freeze,
        "RoomSend" => {
          topic: { kind: :str, required: true },
          data: { kind: :json, required: true },
          to: { kind: :str }
        }.freeze,
        "SessionConfigure" => {
          state: { kind: :json },
          config: { kind: :ref, ref: "AgentConfig" }
        }.freeze,
        "StateSet" => {
          state: { kind: :json, required: true },
          changed: { kind: :list, items: { kind: :str } }
        }.freeze,
        "SupervisorVerb" => {
          by: { kind: :ref, ref: "Supervisor", required: true },
          verb: { kind: :ref, ref: "Verb", required: true }
        }.freeze,
        "ToolsSet" => {
          tools: { kind: :list, items: { kind: :ref, ref: "ToolSpec" }, required: true }
        }.freeze,
        "AgentConfigured" => {
          changed: { kind: :list, items: { kind: :str }, required: true }
        }.freeze,
        "AgentRegistered" => {
          routes: { kind: :list, items: { kind: :ref, ref: "Route" }, required: true },
          app: { kind: :str, required: true },
          sdk: { kind: :str }
        }.freeze,
        "AgentStateChanged" => {
          state: { kind: :ref, ref: "AgentState", required: true }
        }.freeze,
        "AgentTranscript" => {
          speech_id: { kind: :str, required: true },
          text: { kind: :str, required: true },
          final: { kind: :bool, required: true },
          start: { kind: :float },
          end: { kind: :float }
        }.freeze,
        "CallDialing" => {
          channel: { kind: :ref, ref: "Channel", required: true },
          from: { kind: :str, required: true },
          to: { kind: :str, required: true },
          caller: { kind: :ref, null: true, ref: "Contact", required: true },
          external_id: { kind: :str }
        }.freeze,
        "CallEnded" => {
          reason: { kind: :ref, ref: "EndReason", required: true },
          ended_by: { kind: :ref, ref: "EndedBy", required: true },
          ended_at: { kind: :float, required: true },
          duration_s: { kind: :float, required: true }
        }.freeze,
        "CallLine" => {
          held: { kind: :bool, required: true },
          muted: { kind: :bool, required: true }
        }.freeze,
        "CallRinging" => {
          channel: { kind: :ref, ref: "Channel", required: true },
          from: { kind: :str, required: true },
          to: { kind: :str, required: true },
          route: { kind: :ref, ref: "Route", required: true },
          caller: { kind: :ref, null: true, ref: "Contact", required: true },
          external_id: { kind: :str }
        }.freeze,
        "CallScore" => {
          passed: { kind: :bool },
          not_judged: { kind: :str },
          judges: { kind: :list, items: { kind: :ref, ref: "Judgment" }, required: true },
          panel: { kind: :list, items: { kind: :str } },
          judge_calls: { kind: :int, required: true },
          judge_cost_eur: { kind: :float }
        }.freeze,
        "Judgment" => {
          name: { kind: :str, required: true },
          verdict: { kind: :ref, ref: "ScoreVerdict", required: true },
          criteria: { kind: :str, required: true },
          reason: { kind: :str, required: true },
          evidence: { kind: :ref, ref: "JudgmentEvidence", required: true }
        }.freeze,
        "JudgmentEvidence" => {
          seqs: { kind: :list, items: { kind: :int }, required: true },
          said: { kind: :str }
        }.freeze,
        "CallStarted" => {
          channel: { kind: :ref, ref: "Channel", required: true },
          direction: { kind: :ref, ref: "Direction", required: true },
          from: { kind: :str, required: true },
          to: { kind: :str, required: true },
          caller: { kind: :ref, null: true, ref: "Contact", required: true },
          started_at: { kind: :float, required: true }
        }.freeze,
        "CallSummary" => {
          reason: { kind: :ref, ref: "EndReason", required: true },
          outcome: { kind: :str, required: true },
          duration_s: { kind: :float, required: true },
          turns: { kind: :int, required: true },
          usage: { kind: :list, items: { kind: :ref, ref: "ModelUsage" }, required: true },
          cost: { kind: :ref, ref: "Cost", required: true },
          recording: { kind: :str }
        }.freeze,
        "CallTransferred" => {
          to: { kind: :str, required: true },
          mode: { kind: :ref, ref: "TransferMode", required: true },
          ok: { kind: :bool, required: true },
          error: { kind: :str }
        }.freeze,
        "ConfirmDeclined" => {
          tool: { kind: :str, required: true },
          call_id: { kind: :str, required: true },
          audience: { kind: :str, required: true },
          said: { kind: :str },
          reason: { kind: :enum, values: %w[no timeout changed cancelled], required: true }
        }.freeze,
        "ConfirmGranted" => {
          tool: { kind: :str, required: true },
          call_id: { kind: :str, required: true },
          audience: { kind: :str, required: true },
          said: { kind: :str, required: true },
          ttl_s: { kind: :int, required: true }
        }.freeze,
        "ConfirmRequest" => {
          tool: { kind: :str, required: true },
          call_id: { kind: :str, required: true },
          arguments: { kind: :json, required: true },
          audience: { kind: :str, required: true },
          phrase: { kind: :str, required: true },
          ttl_s: { kind: :int, required: true }
        }.freeze,
        "CreditsExhausted" => {
          org: { kind: :str, required: true },
          quota: { kind: :enum, values: %w[minutes messages agents concurrent_calls], required: true },
          used: { kind: :float, required: true },
          limit: { kind: :int, required: true }
        }.freeze,
        "Custom" => {
          name: { kind: :str, required: true },
          data: { kind: :json, required: true }
        }.freeze,
        "DocsSources" => {
          query: { kind: :str, required: true },
          sources: { kind: :list, items: { kind: :ref, ref: "DocSource" }, required: true },
          took_ms: { kind: :float, required: true },
          speech_id: { kind: :str }
        }.freeze,
        "ErrorEvent" => {
          code: { kind: :str, required: true },
          message: { kind: :str, required: true },
          command: { kind: :str },
          id: { kind: :str },
          recoverable: { kind: :bool, required: true }
        }.freeze,
        "LogCaughtUp" => {
          seq: { kind: :int, required: true }
        }.freeze,
        "LogGap" => {
          from_seq: { kind: :int, required: true },
          to_seq: { kind: :int, required: true },
          snapshot: { kind: :ref, null: true, ref: "State", required: true }
        }.freeze,
        "MemoryOps" => {
          ops: { kind: :list, items: { kind: :ref, ref: "MemoryOp" }, required: true },
          speech_id: { kind: :str }
        }.freeze,
        "Pong" => {
          ts: { kind: :float, required: true }
        }.freeze,
        "PromptChanged" => {
          region: { kind: :ref, ref: "PromptRegion", required: true },
          hash: { kind: :str, required: true },
          chars: { kind: :int, required: true }
        }.freeze,
        "StateChanged" => {
          state: { kind: :json, required: true },
          changed: { kind: :list, items: { kind: :str }, required: true },
          cause: { kind: :ref, ref: "StateCause" }
        }.freeze,
        "StateCauseTool" => {
          kind: { kind: :const, const: "tool", required: true },
          tool: { kind: :str, required: true },
          call_id: { kind: :str, required: true }
        }.freeze,
        "StateCauseEvent" => {
          kind: { kind: :const, const: "event", required: true },
          name: { kind: :str, required: true },
          seq: { kind: :int, required: true }
        }.freeze,
        "SupervisorEnded" => {
          by: { kind: :ref, ref: "Supervisor", required: true },
          reason: { kind: :str }
        }.freeze,
        "SupervisorReleased" => {
          by: { kind: :ref, ref: "Supervisor", required: true }
        }.freeze,
        "SupervisorSaid" => {
          by: { kind: :ref, ref: "Supervisor", required: true },
          text: { kind: :str, required: true }
        }.freeze,
        "SupervisorTookOver" => {
          by: { kind: :ref, ref: "Supervisor", required: true }
        }.freeze,
        "SupervisorTransferred" => {
          by: { kind: :ref, ref: "Supervisor", required: true },
          to: { kind: :str, required: true },
          mode: { kind: :ref, ref: "TransferMode", required: true }
        }.freeze,
        "SupervisorWhispered" => {
          by: { kind: :ref, ref: "Supervisor", required: true },
          text: { kind: :str, required: true }
        }.freeze,
        "ToolCall" => {
          call_id: { kind: :str, required: true },
          name: { kind: :str, required: true },
          arguments: { kind: :json, required: true },
          speech_id: { kind: :str }
        }.freeze,
        "ToolsChanged" => {
          visible: { kind: :list, items: { kind: :str }, required: true }
        }.freeze,
        "AgentTurnEnded" => {
          speech_id: { kind: :str, required: true },
          item_id: { kind: :str },
          text: { kind: :str, required: true },
          interrupted: { kind: :bool, required: true },
          metrics: { kind: :ref, ref: "AgentTurnMetrics", required: true }
        }.freeze,
        "UserTurnEnded" => {
          speech_id: { kind: :str, required: true },
          item_id: { kind: :str },
          text: { kind: :str, required: true },
          language: { kind: :str },
          transcript_confidence: { kind: :float },
          metrics: { kind: :ref, ref: "UserTurnMetrics", required: true }
        }.freeze,
        "UserStateChanged" => {
          state: { kind: :ref, ref: "UserState", required: true }
        }.freeze,
        "UserTranscript" => {
          text: { kind: :str, required: true },
          final: { kind: :bool, required: true },
          language: { kind: :str },
          confidence: { kind: :float }
        }.freeze
      }.freeze

      # A union is told apart by one field, the way the schema's discriminator says.
      UNIONS = {
        "ModelUsage" => { on: :type, members: %w[LLMModelUsage TTSModelUsage STTModelUsage InterruptionModelUsage EOTModelUsage] }.freeze,
        "Turn" => { on: :role, members: %w[UserTurn AgentTurn] }.freeze,
        "Verb" => { on: :verb, members: %w[SayVerb WhisperVerb TakeoverVerb ReleaseVerb TransferVerb EndVerb] }.freeze,
        "StateCause" => { on: :kind, members: %w[StateCauseTool StateCauseEvent] }.freeze
      }.freeze
    end
  end
end
