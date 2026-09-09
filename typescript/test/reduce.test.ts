// The reducer's rules, one sentence each, on logs small enough to read.

import { describe, expect, it } from "vitest";
import { apply, decodeEntry, initialState, reduce, type Entry } from "../src/index.js";

const caller = { id: "ct_1", phone: "+34600000001", name: "Ana" };
const line = { channel: "phone", from: "+34600000001", to: "+34910000001" };
const room = { name: "call-CA_1", sid: "RM_1", channel: "phone" };
const seat = { identity: "sip_+34600000001", kind: "caller", attributes: { "sip.phoneNumber": "+34600000001" } };

function entry(seq: number, type: string, data: Record<string, unknown>, ephemeral = false): Entry {
  return decodeEntry({ seq, ts: 1786537500 + seq, call: "CA_1", agent: "clinica-norte", type, ephemeral, data });
}

describe("reduce", () => {
  it("an empty log is idle with nothing known", () => {
    const state = reduce([]);
    expect(state.seq).toBe(0);
    expect(state.status).toBe("idle");
    expect(state.turns).toEqual([]);
  });

  it("a ringing call knows who is calling before media is up", () => {
    const route = { channel: "phone", number: "+34910000001" };
    const state = reduce([entry(1, "call.ringing", { ...line, route, caller })]);
    expect(state.status).toBe("ringing");
    expect(state.caller?.name).toBe("Ana");
    expect(state.started_at).toBeNull();
  });

  it("a tool result closes its call as done or failed", () => {
    const call = { call_id: "t1", name: "find_slots", arguments: { day: "jueves" } };
    const done = reduce([entry(1, "tool.call", call), entry(2, "tool.result", { call_id: "t1", name: "find_slots", output: [1] })]);
    const failed = reduce([entry(1, "tool.call", call), entry(2, "tool.result", { call_id: "t1", name: "find_slots", error: "down" })]);
    expect(done.tools[0]).toMatchObject({ status: "done", output: [1], seq: 1 });
    expect(failed.tools[0]).toMatchObject({ status: "failed", error: "down" });
  });

  it("a granted confirm settles the pending request with what was said", () => {
    const asked = { tool: "book", call_id: "t2", arguments: {}, audience: "sha256:x", phrase: "¿Confirmo?", ttl_s: 120 };
    const granted = { tool: "book", call_id: "t2", audience: "sha256:x", said: "sí", ttl_s: 120 };
    const state = reduce([entry(1, "confirm.request", asked), entry(2, "confirm.granted", granted)]);
    expect(state.confirms[0]).toMatchObject({ status: "granted", said: "sí" });
  });

  it("a gap with a snapshot replaces everything and is remembered", () => {
    const snapshot = reduce([entry(1, "call.started", { ...line, direction: "inbound", caller, started_at: 1 })]);
    const state = reduce([entry(3, "log.gap", { from_seq: 1, to_seq: 3, snapshot }, true)]);
    expect(state.status).toBe("active");
    expect(state.seq).toBe(3);
    expect(state.gaps).toEqual([{ from_seq: 1, to_seq: 3 }]);
  });

  it("a gap without a snapshot only moves the cursor", () => {
    const state = apply(initialState(), entry(5, "log.gap", { from_seq: 4, to_seq: 5, snapshot: null }, true));
    expect(state.status).toBe("idle");
    expect(state.seq).toBe(5);
    expect(state.gaps).toHaveLength(1);
  });

  it("a room fills as participants join and the caller takes the caller seat", () => {
    const state = reduce([entry(1, "room.opened", room), entry(2, "participant.joined", seat)]);
    expect(state.room?.caller).toBe("sip_+34600000001");
    expect(state.room?.participants[0]).toEqual({ ...seat, joined_at: 1786537500 + 2, speaking: false });
  });

  it("the room lights a participant while it hears them", () => {
    const lit = { identity: "sip_+34600000001", speaking: true };
    let state = reduce([entry(1, "room.opened", room), entry(2, "participant.joined", seat), entry(3, "participant.speaking", lit, true)]);
    expect(state.room?.participants[0]?.speaking).toBe(true);
    state = apply(state, entry(4, "participant.speaking", { ...lit, speaking: false }, true));
    expect(state.room?.participants[0]?.speaking).toBe(false);
  });

  it("a participant leaving is forgotten and the caller seat empties", () => {
    const gone = { identity: "sip_+34600000001", reason: "client_initiated" };
    const state = reduce([entry(1, "room.opened", room), entry(2, "participant.joined", seat), entry(3, "participant.left", gone)]);
    expect(state.room).toEqual({ name: "call-CA_1", sid: "RM_1", participants: [], caller: null });
  });

  it("a participant fact before the room opened changes nothing", () => {
    expect(reduce([entry(1, "participant.joined", seat)]).room).toBeNull();
  });

  it("a prompt block is kept by name with its hash, its length and the seq that set it", () => {
    const identity = { name: "identity", hash: "a".repeat(64), chars: 1840 };
    const availability = { name: "availability", hash: "b".repeat(64), chars: 120 };
    const state = reduce([entry(1, "prompt.changed", identity), entry(2, "prompt.changed", availability)]);
    expect(state.prompt).toEqual({
      identity: { hash: "a".repeat(64), chars: 1840, seq: 1 },
      availability: { hash: "b".repeat(64), chars: 120, seq: 2 },
    });
  });

  it("an outside fact is kept by name and origin and its cause names it", () => {
    const fact = { name: "slot.released", data: { at: "10:15" }, source: "app" };
    const cause = { kind: "event", name: "slot.released", seq: 1 };
    const state = reduce([entry(1, "event.received", fact), entry(2, "state.changed", { state: { slots: ["10:15"] }, changed: ["slots"], cause })]);
    expect(state.events).toEqual([{ seq: 1, name: "slot.released", source: "app" }]);
    expect(state.app_state).toEqual({ slots: ["10:15"] });
  });
});
