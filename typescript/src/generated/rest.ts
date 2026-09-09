// Generated from schema/rest.json: the envelopes the read doors answer in. Never edited by hand.

import { z } from "zod";
import {
  ChannelSchema,
  ContactSchema,
  CostSchema,
  DirectionSchema,
  EndReasonSchema,
} from "./defs.js";
import { EntrySchema } from "./envelope.js";
import { CallStatusSchema, StateSchema } from "./state.js";

/** GET /v1/calls/{call}/state: the whole log folded, and the seq a stream resumes from. */
export const CallStateSchema = z.strictObject({
  state: StateSchema,
  last_seq: z.int(),
  live: z.boolean(),
});
export type CallState = z.infer<typeof CallStateSchema>;

/** One page of a log: what this reader may see, whether the log is open, and where to resume. */
export const LogPageSchema = z.strictObject({
  entries: z.array(EntrySchema),
  live: z.boolean(),
  next: z.int().nullable(),
});
export type LogPage = z.infer<typeof LogPageSchema>;

/** One call as a list draws it: which call, how far the log got, and the state's own fields. */
export const SessionLineSchema = z.strictObject({
  call: z.string(),
  live: z.boolean(),
  last_seq: z.int(),
  status: CallStatusSchema,
  channel: ChannelSchema.nullable(),
  direction: DirectionSchema.nullable(),
  from: z.string().nullable(),
  to: z.string().nullable(),
  caller: ContactSchema.nullable(),
  started_at: z.number().nullable(),
  ended_at: z.number().nullable(),
  end_reason: EndReasonSchema.nullable(),
  outcome: z.string().nullable(),
  cost: CostSchema.nullable(),
});
export type SessionLine = z.infer<typeof SessionLineSchema>;

/** GET /v1/agents/{slug}/sessions: which calls that agent handled, newest first. */
export const SessionListSchema = z.strictObject({
  calls: z.array(SessionLineSchema),
});
export type SessionList = z.infer<typeof SessionListSchema>;

/** One agent, as somebody choosing which to open needs to see it: its name and its channels. */
export const HeldAgentSchema = z.strictObject({
  slug: z.string(),
  channels: z.array(ChannelSchema),
});
export type HeldAgent = z.infer<typeof HeldAgentSchema>;

/** GET /v1/agents: every agent this fleet is holding right now, as the front page lists them. */
export const AgentListSchema = z.strictObject({
  agents: z.array(HeldAgentSchema),
});
export type AgentList = z.infer<typeof AgentListSchema>;
