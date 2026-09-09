// The codec is the only place a key name changes hands, and it never touches the app's own JSON.

import { describe, expect, it } from "vitest";
import { OPAQUE_KEYS, ProtocolError, decodeEntry, eventOf, toCamel, toSnake } from "../src/index.js";

describe("the codec", () => {
  it("camelCases wire keys deep and snake_cases them back, untouched under opaque keys", () => {
    const wire = { speech_id: "s1", metrics: { llm_node_ttft: 0.4 }, state: { keep_me: 1 }, arguments: { as_is: true } };
    const camel = toCamel(wire);
    expect(camel).toEqual({ speechId: "s1", metrics: { llmNodeTtft: 0.4 }, state: { keep_me: 1 }, arguments: { as_is: true } });
    expect(toSnake(camel)).toEqual(wire);
    expect(OPAQUE_KEYS.has("state")).toBe(true);
  });

  it("never renames the keys of a map the app named", () => {
    const wire = { prompt: { my_block: { hash: "h", chars: 1, seq: 1 } } };
    expect(toCamel(wire)).toEqual(wire);
  });

  it("refuses an entry whose type nobody defined", () => {
    const entry = decodeEntry({ seq: 1, ts: 1, call: null, agent: "a", type: "bot.reply", ephemeral: false, data: {} });
    expect(() => eventOf(entry)).toThrow(ProtocolError);
  });

  it("refuses data that does not match the type's shape", () => {
    const entry = decodeEntry({ seq: 1, ts: 1, call: "c", agent: "a", type: "user.state", ephemeral: false, data: { state: "dancing" } });
    expect(() => eventOf(entry)).toThrow();
  });
});
