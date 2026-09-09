// Generated from schema/rest.json: the envelopes the read doors answer in. Never edited by hand.

import { z } from "zod";
import {
  ChannelSchema,
  ContactSchema,
  CostSchema,
  DirectionSchema,
  EndReasonSchema,
  KnowledgeFileSchema,
  MarkerNameSchema,
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

/**
 * PUT /v1/knowledge/{base}, the body: the tenant's folder as of now, sent whole. The base is
 * replaced, never merged.
 */
export const KnowledgePushSchema = z.strictObject({
  files: z.array(KnowledgeFileSchema),
});
export type KnowledgePush = z.infer<typeof KnowledgePushSchema>;

/**
 * PUT /v1/knowledge/{base}, the answer: which base, how many chunks it became, and how long that
 * took.
 */
export const KnowledgePushedSchema = z.strictObject({
  base: z.string(),
  chunks: z.int(),
  took_ms: z.number(),
});
export type KnowledgePushed = z.infer<typeof KnowledgePushedSchema>;

/** One knowledge base as the list draws it: its name, its size, and when it was last pushed. */
export const KnowledgeBaseSchema = z.strictObject({
  base: z.string(),
  chunks: z.int(),
  pushed_at: z.number(),
});
export type KnowledgeBase = z.infer<typeof KnowledgeBaseSchema>;

/** GET /v1/knowledge: every base this org has pushed. */
export const KnowledgeListSchema = z.strictObject({
  bases: z.array(KnowledgeBaseSchema),
});
export type KnowledgeList = z.infer<typeof KnowledgeListSchema>;

/**
 * One fact of a contact's history: a MemoryFact with the two dates that bound it. A fact is never
 * deleted, only superseded, so the history keeps every version.
 */
export const ContactFactSchema = z.strictObject({
  id: z.string().nullish(),
  text: z.string(),
  category: z.string().nullish(),
  source: z.string().nullish(),
  valid_from: z.number(),
  invalidated_at: z.number().nullable(),
});
export type ContactFact = z.infer<typeof ContactFactSchema>;

/**
 * GET /v1/contacts/{contact}/memory: everything memory ever kept about one contact, current facts
 * first.
 */
export const ContactMemorySchema = z.strictObject({
  facts: z.array(ContactFactSchema),
});
export type ContactMemory = z.infer<typeof ContactMemorySchema>;

/**
 * DELETE /v1/contacts/{contact}/memory, the answer: how many facts the right to be forgotten
 * erased.
 */
export const ForgottenSchema = z.strictObject({
  forgotten: z.int(),
});
export type Forgotten = z.infer<typeof ForgottenSchema>;

/**
 * One marker the worker found in a dynamic block, as the gateway is asked to fill it. The view
 * wrote it and never resolves it.
 */
export const FillMarkerSchema = z.strictObject({
  name: MarkerNameSchema,
  payload: z.string(),
});
export type FillMarker = z.infer<typeof FillMarkerSchema>;

/**
 * POST /v1/calls/{call}/fill, the body: what the caller just said and the markers to fill before
 * the model is asked. Worker-only; the gateway writes memory.ops and docs.sources on the call's
 * log itself.
 */
export const FillRequestSchema = z.strictObject({
  query: z.string(),
  markers: z.array(FillMarkerSchema),
  speech_id: z.string().nullish(),
});
export type FillRequest = z.infer<typeof FillRequestSchema>;

/** One marker filled: the marker as it was asked, and the text that takes its line. */
export const FillSchema = z.strictObject({
  name: MarkerNameSchema,
  payload: z.string(),
  text: z.string(),
});
export type Fill = z.infer<typeof FillSchema>;

/** POST /v1/calls/{call}/fill, the answer: every marker filled, and how long the whole fill took. */
export const FillsSchema = z.strictObject({
  fills: z.array(FillSchema),
  took_ms: z.number(),
});
export type Fills = z.infer<typeof FillsSchema>;

/**
 * POST /v1/calls/{call}/remember, the answer: what the call taught about the contact, counted.
 * Worker-only; the body is empty, the gateway reads the turns off its own log and writes
 * memory.ops itself.
 */
export const RememberedSchema = z.strictObject({
  ops: z.int(),
  took_ms: z.number(),
});
export type Remembered = z.infer<typeof RememberedSchema>;
