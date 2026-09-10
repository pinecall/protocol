import { describe, expect, it } from "vitest";

import type { Entry } from "../src/index.js";
import { apply, initialState, UNREADABLE } from "../src/reduce.js";

// A log outlives the shape of its entries: `prompt.changed` carried `region` before it carried
// `name`, and those rows are still in the table. A reader that threw on one refused the call.
const FROM_ANOTHER_VERSION: Entry = {
  seq: 7,
  ts: 1,
  call: "CA_8f4a2c",
  agent: "clinica-norte",
  type: "prompt.changed",
  ephemeral: false,
  data: { region: "static", hash: "abc", chars: 10 },
};

describe("an entry this reader cannot read", () => {
  it("is one line of the errors list and never the end of the fold", () => {
    const state = apply(initialState(), FROM_ANOTHER_VERSION);
    expect(state.errors).toHaveLength(1);
    expect(state.errors[0]?.code).toBe(UNREADABLE);
    expect(state.errors[0]?.message).toContain("prompt.changed at seq 7");
    expect(state.prompt).toEqual({});
  });

  it("still moves the fold to its seq, so the next entry is not read twice", () => {
    const state = apply(initialState(), FROM_ANOTHER_VERSION);
    expect(state.seq).toBe(7);
    expect(state.agent).toBe("clinica-norte");
    expect(state.call).toBe("CA_8f4a2c");
  });

  it("is refused by type as well as by shape", () => {
    const state = apply(initialState(), { ...FROM_ANOTHER_VERSION, type: "nobody.knows" });
    expect(state.errors[0]?.message).toContain("nobody.knows at seq 7");
  });
});
