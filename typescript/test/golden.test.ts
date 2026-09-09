// The golden fixture is the contract: every entry decodes, and it reduces to the same state as Python.

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { decodeEntries, EPHEMERAL_EVENTS, EVENT_SCHEMAS, eventOf, reduce } from "../src/index.js";

// The goldens live in the Python package's own directory — hatchling cannot pack a file
// from outside the project it builds — and `pnpm build` copies them into this one's dist,
// so both languages ship the same bytes. A test reads the source, not the copy.
const fixtures = fileURLToPath(new URL("../../python/pinecall_protocol/fixtures/", import.meta.url));
const golden = decodeEntries(readFileSync(`${fixtures}call-log-golden.json`, "utf8"));

describe("the golden log", () => {
  it("decodes every entry to the shape its type names", () => {
    for (const entry of golden) {
      const event = eventOf(entry);
      expect(event.type).toBe(entry.type);
      expect(Object.hasOwn(EVENT_SCHEMAS, event.type)).toBe(true);
    }
  });

  it("reduces to the state Python must reach", () => {
    const expected: unknown = JSON.parse(readFileSync(`${fixtures}call-log-golden.state.json`, "utf8"));
    expect(reduce(golden)).toEqual(expected);
  });

  it("marks as ephemeral only what the schema says may be dropped", () => {
    for (const entry of golden) {
      if (entry.ephemeral) {
        expect(EPHEMERAL_EVENTS.has(entry.type as never) || entry.type === "user.transcript").toBe(true);
      }
    }
  });
});
