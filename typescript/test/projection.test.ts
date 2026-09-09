// The projection contract of docs/protocol/projections.md, asserted over the golden state.

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { decodeEntries, reduce, type State } from "../src/index.js";

const fixtures = fileURLToPath(new URL("../../python/pinecall_protocol/fixtures/", import.meta.url));
const golden = reduce(decodeEntries(readFileSync(`${fixtures}call-log-golden.json`, "utf8")));
const MASK = "***";

// What the golden agent declares about its state: the patient is personal, two fields are public
// and stage, undeclared, is the tenant's.
const visibility: Record<string, "public" | "tenant" | "pii"> = { patient: "pii", slots: "public", booking: "public" };

const publicFields = ["seq", "status", "user_state", "agent_state", "live", "turns", "app_state", "room", "confirms", "transfer", "held", "events"];
const publicTurnFields = new Set(["role", "speech_id", "text", "interrupted", "metrics"]);

type Json = Record<string, unknown>;

// The contract in code, small enough to read next to the page. Owned by the tests until the
// console's projection module takes it over and these assertions move onto that.
function project(state: State, projection: "public" | "tenant", viewer?: string): Json {
  if (projection === "tenant") {
    const masked = Object.fromEntries(
      Object.entries(state.app_state).map(([name, value]) => [name, visibility[name] === "pii" ? MASK : value]),
    );
    return { ...state, app_state: masked };
  }
  return {
    seq: state.seq,
    status: state.status,
    user_state: state.user_state,
    agent_state: state.agent_state,
    live: state.live,
    turns: state.turns.map(publicTurn),
    app_state: Object.fromEntries(Object.entries(state.app_state).filter(([name]) => visibility[name] === "public")),
    room: publicRoom(state.room),
    confirms: state.confirms.map((one) => ({ phrase: one.phrase, status: one.status })),
    transfer: state.transfer,
    held: state.held,
    events: state.events.filter((one) => one.source === "participant" && one.identity === viewer),
  };
}

function publicTurn(turn: State["turns"][number]): Json {
  if (turn.role === "user") {
    return { role: turn.role, speech_id: turn.speech_id, text: turn.text };
  }
  const metrics = turn.metrics.e2e_latency === undefined ? {} : { e2e_latency: turn.metrics.e2e_latency };
  return { role: turn.role, speech_id: turn.speech_id, text: turn.text, interrupted: turn.interrupted, metrics };
}

function publicRoom(room: State["room"]): Json | null {
  if (room === null) {
    return null;
  }
  return { ...room, participants: room.participants.map(({ attributes: _attributes, ...seat }) => seat) };
}

describe("the public projection", () => {
  const pub = project(golden, "public", "sip_+34600123456");

  it("keeps only the fields the contract names", () => {
    expect(Object.keys(pub).sort()).toEqual([...publicFields].sort());
  });

  it("drops every participant attribute", () => {
    const seats = (pub.room as { participants: Json[] }).participants;
    expect(seats.length).toBeGreaterThan(0);
    expect(seats.every((seat) => !("attributes" in seat))).toBe(true);
    expect(JSON.stringify(pub)).not.toContain("sip.");
  });

  it("carries only the app state fields declared public", () => {
    expect(Object.keys(pub.app_state as Json).sort()).toEqual(["booking", "slots"]);
  });

  it("gives the turns their words and, of the metrics, only e2e_latency", () => {
    const turns = pub.turns as Json[];
    for (const turn of turns) {
      expect(Object.keys(turn).every((name) => publicTurnFields.has(name))).toBe(true);
      expect(Object.keys((turn.metrics as Json | undefined) ?? {}).every((name) => name === "e2e_latency")).toBe(true);
    }
    expect(turns.some((turn) => turn.role === "agent" && Object.keys(turn.metrics as Json).length === 0)).toBe(true);
    expect(turns.some((turn) => turn.role === "agent" && "e2e_latency" in (turn.metrics as Json))).toBe(true);
    expect(turns.every((turn) => turn.role !== "user" || !("metrics" in turn))).toBe(true);
  });

  it("shows of a confirm the phrase and the verdict, nothing of the tool", () => {
    expect(pub.confirms).toEqual([{ phrase: golden.confirms[0]?.phrase, status: "granted" }]);
  });

  it("carries only the viewer's own events", () => {
    expect(golden.events.length).toBeGreaterThan(0);
    expect(pub.events).toEqual([]);
  });
});

describe("the tenant projection", () => {
  const tenant = project(golden, "tenant");

  it("keeps everything and masks the pii field", () => {
    expect(Object.keys(tenant).sort()).toEqual(Object.keys(golden).sort());
    const appState = tenant.app_state as Json;
    expect(appState.patient).toBe(MASK);
    expect(JSON.stringify(appState)).not.toContain("Marta");
    expect(appState.stage).toBe(golden.app_state.stage);
    const { app_state: _golden, ...restOfGolden } = golden;
    const { app_state: _tenant, ...restOfTenant } = tenant;
    expect(restOfTenant).toEqual(restOfGolden);
  });
});
