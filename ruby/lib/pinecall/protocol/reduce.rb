# frozen_string_literal: true

module Pinecall
  module Protocol
    # Folds a log into its State, one entry at a time. The third implementation of one rule: the
    # TypeScript reducer and the runtime's Python one keep the same, and the golden fixture is
    # what says so — the same log has to leave all three in the same place, field for field.
    module Reduce
      # What a reader says about an entry it cannot read, in the log's own errors list.
      UNREADABLE = "unreadable"

      module_function

      # Fold every entry, in the order given, into the state an empty log starts from.
      def reduce(entries)
        entries.reduce(State.initial) { |state, entry| apply(state, entry) }
      end

      # One entry folded in. A gap that carries a snapshot replaces the state outright — that is
      # what the snapshot is for; every other entry changes it in place. Either way the seq moves.
      def apply(state, entry)
        event = begin
          Codec.event_of(entry)
        rescue ProtocolError => why
          return moved(unreadable(state, entry, why), entry)
        end
        following = event.type == "log.gap" ? on_log_gap(state, event.data) : apply_event(state, entry, event)
        moved(following, entry)
      end

      # A log outlives the shape of the entries in it: a call recorded before a field was renamed
      # is still in the table, and a reader that refuses it refuses the whole call with it. So an
      # entry this reader cannot validate is one line of the errors list and nothing more — the
      # fold goes on, and the state says out loud which seq it could not read. The Python and
      # TypeScript reducers do the same: the three of them fold one golden log into one state.
      def unreadable(state, entry, why)
        said = why.message.to_s.lines.first.to_s.strip
        state[:errors] << {
          seq: entry.seq,
          code: UNREADABLE,
          message: "#{entry.type} at seq #{entry.seq} is not the shape this reader knows: #{said}"
        }
        state
      end

      # Whatever the entry was, the fold has now reached its seq.
      def moved(state, entry)
        state[:seq] = entry.seq
        state[:agent] = entry.agent
        state[:call] = entry.call unless entry.call.nil?
        state
      end

      # rubocop:disable Metrics/MethodLength, Metrics/CyclomaticComplexity
      def apply_event(state, entry, event)
        data = event.data
        case event.type
        # ── the call ──
        when "call.ringing" then the_line(state, data, status: "ringing", direction: "inbound")
        when "call.dialing" then the_line(state, data, status: "dialing", direction: "outbound")
        when "call.started" then started(state, data)
        when "call.ended" then ended(state, data)
        when "call.transferred" then transferred(state, data)
        when "call.line" then state.merge!(held: data[:held], muted: data[:muted])
        when "call.summary" then summarised(state, data)
        # ── the conversation ──
        when "user.state" then state[:user_state] = data[:state]
        when "agent.state" then state[:agent_state] = data[:state]
        when "user.transcript" then state[:live][:user] = data[:final] ? nil : data[:text]
        when "agent.transcript" then state[:live][:agent] = data[:final] ? nil : said_so_far(state[:live][:agent], data)
        when "turn.user" then turn(state, data, "user")
        when "turn.agent" then turn(state, data, "agent")
        when "memory.ops" then state[:memory].concat(data[:ops])
        when "docs.sources" then state[:sources] = data[:sources].dup
        # ── metrics: every block is kept, in order, by kind ──
        when "metrics.llm", "metrics.stt", "metrics.tts", "metrics.vad", "metrics.eou",
             "metrics.eot", "metrics.interruption", "metrics.realtime", "metrics.avatar"
          state[:metrics][event.type.delete_prefix("metrics.").to_sym] << data
        # ── tools, state, confirmation ──
        when "tool.call" then state[:tools] << data.merge(status: "running", seq: entry.seq)
        when "tool.result" then on_tool_result(state, data)
        when "state.changed" then state[:app_state] = data[:state].dup
        when "prompt.changed" then on_prompt_changed(state, data, entry)
        when "tools.changed" then state[:tools_visible] = data[:visible].dup
        when "confirm.request" then requested(state, data)
        when "confirm.granted" then settle(state, data[:call_id], { status: "granted", said: data[:said] })
        when "confirm.declined" then declined(state, data)
        # ── supervision, the agent, markers ──
        when "supervisor.took_over" then state[:handoff] = { active: true, by: data[:by] }
        when "supervisor.released" then state[:handoff] = { active: false, by: nil }
        when "supervisor.transferred" then took_the_line(state, data)
        when "attention.requested" then asked_for_a_person(state, data, entry.ts)
        when "attention.answered" then answered(state, data)
        when "agent.registered" then state[:routes] = data[:routes].dup
        when "error" then state[:errors] << { seq: entry.seq, code: data[:code], message: data[:message] }
        when "custom" then state[:custom] << { seq: entry.seq, name: data[:name], data: data[:data].dup }
        # ── the room and the outside world ──
        when "room.opened" then state[:room] = { name: data[:name], sid: data[:sid], participants: [], caller: nil }
        when "participant.joined" then joined(state, data, entry.ts)
        when "participant.left" then left(state, data[:identity])
        when "participant.speaking" then speaking(state, data)
        when "event.received" then state[:events] << data.except(:data).merge(seq: entry.seq)
        end
        state
      end
      # rubocop:enable Metrics/MethodLength, Metrics/CyclomaticComplexity

      # Nothing a reader keeps: supervisor.said and .whispered land as turns and prompt changes,
      # supervisor.ended as call.ended; agent.configured, pong and log.caught_up say nothing about
      # the call; track.published, track.unpublished and room.sent are facts the log keeps and the
      # state does not. They reach the case above and leave it unchanged, on purpose.

      def the_line(state, line, status:, direction:)
        state.merge!(
          status:,
          direction:,
          channel: line[:channel],
          from: line[:from],
          to: line[:to],
          caller: line[:caller]
        )
      end

      def started(state, data)
        the_line(state, data, status: "active", direction: data[:direction])
        state[:started_at] = data[:started_at]
      end

      def ended(state, data)
        state[:status] = "ended"
        state[:ended_at] = data[:ended_at]
        state[:end_reason] = data[:reason]
        state[:live] = { user: nil, agent: nil }
        # A caller who hung up while waiting for a person was never answered.
        state[:attention] = state[:attention].merge(status: "lapsed") if state[:attention]&.fetch(:status) == "open"
      end

      def transferred(state, data)
        state[:transfer] = {
          to: data[:to],
          mode: data[:mode],
          status: data[:ok] ? "done" : "failed",
          by: state[:transfer]&.fetch(:by, nil) || "agent"
        }
      end

      def took_the_line(state, data)
        state[:transfer] = { to: data[:to], mode: data[:mode], status: "requested", by: "supervisor" }
      end

      def asked_for_a_person(state, data, asked_at)
        state[:attention] = { reason: data[:reason], wait_s: data[:wait_s], status: "open", asked_at: asked_at, by: nil }
      end

      def answered(state, data)
        return if state[:attention].nil?

        state[:attention] = state[:attention].merge(status: data[:ok] ? "answered" : "lapsed", by: data[:by])
      end

      def summarised(state, data)
        state[:usage] = data[:usage].dup
        state[:cost] = data[:cost]
        state[:outcome] = data[:outcome]
        state[:end_reason] ||= data[:reason]
      end

      # A delta, not the reply so far: one word of a spoken reply, one token of a written one. A word
      # the voice aligned arrives bare and is set a space apart; a token carries its own spacing.
      def said_so_far(so_far, data)
        return data[:text] if so_far.nil? || so_far.empty?

        apart = so_far.match?(/\s\z/) || data[:text].match?(/\A\s/)
        !data[:start].nil? && !apart ? "#{so_far} #{data[:text]}" : "#{so_far}#{data[:text]}"
      end

      def turn(state, data, who)
        state[:turns] << { role: who }.merge(data)
        state[:live][who.to_sym] = nil
      end

      def requested(state, data)
        state[:confirms] << {
          tool: data[:tool],
          call_id: data[:call_id],
          audience: data[:audience],
          phrase: data[:phrase],
          status: "pending"
        }
      end

      def declined(state, data)
        verdict = { status: "declined", reason: data[:reason] }
        verdict[:said] = data[:said] if data.key?(:said)
        settle(state, data[:call_id], verdict)
      end

      def on_tool_result(state, result)
        at = state[:tools].rindex { |run| run[:call_id] == result[:call_id] }
        return if at.nil?

        outcome = result.except(:call_id, :name)
        state[:tools][at] = state[:tools][at].merge(outcome, status: outcome.key?(:error) ? "failed" : "done")
      end

      def settle(state, call_id, verdict)
        at = state[:confirms].rindex { |confirm| confirm[:call_id] == call_id }
        return if at.nil?

        state[:confirms][at] = state[:confirms][at].merge(verdict)
      end

      def on_prompt_changed(state, data, entry)
        state[:prompt][data[:name].to_sym] = { hash: data[:hash], chars: data[:chars], seq: entry.seq }
      end

      # joined_at is the entry's ts: the room said when, so the event did not have to repeat it.
      def joined(state, joined, at)
        return if state[:room].nil?

        state[:room][:participants] << joined.merge(joined_at: at, speaking: false)
        state[:room][:caller] = joined[:identity] if joined[:kind] == "caller"
      end

      # An identity is unique within a room: LiveKit disconnects the first of two that share one.
      def left(state, identity)
        return if state[:room].nil?

        state[:room][:participants].reject! { |one| one[:identity] == identity }
        state[:room][:caller] = nil if state[:room][:caller] == identity
      end

      def speaking(state, data)
        who = state[:room]&.fetch(:participants)&.find { |one| one[:identity] == data[:identity] }
        who[:speaking] = data[:speaking] unless who.nil?
      end

      # A gap the reader fell into. With a snapshot it replaces what the reader thought it knew;
      # without one, everything before the gap still stands and only the hole is recorded.
      def on_log_gap(state, data)
        following = data[:snapshot].nil? ? state : deep_copy(data[:snapshot])
        following[:gaps] << { from_seq: data[:from_seq], to_seq: data[:to_seq] }
        following
      end

      # The snapshot belongs to the entry that carried it, and the state we hand back is written
      # into from here on. Marshal is Ruby's deep copy and the payload is plain JSON data.
      def deep_copy(value)
        Marshal.load(Marshal.dump(value))
      end
    end
  end
end
