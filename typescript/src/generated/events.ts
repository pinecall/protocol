// Generated from schema/events/: one schema per event. Never edited by hand.

import { z } from "zod";
import {
  AgentStateSchema,
  ChannelSchema,
  ContactSchema,
  CostSchema,
  DevVerbSchema,
  DirectionSchema,
  DocSourceSchema,
  EndedBySchema,
  EndReasonSchema,
  EnvSchema,
  MemoryOpSchema,
  RouteSchema,
  ScoreVerdictSchema,
  SupervisorSchema,
  TransferModeSchema,
  UserStateSchema,
} from "./defs.js";
import { AgentTurnMetricsSchema, ModelUsageSchema, UserTurnMetricsSchema } from "./metrics.js";
import { StateSchema } from "./state.js";

/**
 * The gateway applied an agent.configure. Live calls keep their session; the next call starts with
 * the new config.
 */
export const AgentConfiguredSchema = z.strictObject({
  changed: z.array(z.string()),
});
export type AgentConfigured = z.infer<typeof AgentConfiguredSchema>;

/** One socket stopped holding the agent. */
export const AgentDetachedSchema = z.strictObject({
  app: z.string(),
  env: EnvSchema,
  left: z.boolean(),
});
export type AgentDetached = z.infer<typeof AgentDetachedSchema>;

/**
 * The gateway accepted an agent.register: this socket now speaks for the agent and answers its
 * routes. Many sockets may hold one agent at once — a new call takes the newest of them, unless
 * the caller names one by its `app` id.
 */
export const AgentRegisteredSchema = z.strictObject({
  routes: z.array(RouteSchema),
  app: z.string(),
  sdk: z.string().nullish(),
  env: EnvSchema.nullish(),
});
export type AgentRegistered = z.infer<typeof AgentRegisteredSchema>;

/** The agent's state changed, in the session's own words. */
export const AgentStateChangedSchema = z.strictObject({
  state: AgentStateSchema,
});
export type AgentStateChanged = z.infer<typeof AgentStateChangedSchema>;

/**
 * One delta of the reply the agent is giving, never the reply so far: in a voice call one word, as
 * the voice plays it, with the seconds it was aligned to; in a written call one model token. The
 * reply so far is every delta of the same speech_id since the last turn.agent, joined; turn.agent
 * carries the whole reply and closes it. Interim entries are ephemeral.
 */
export const AgentTranscriptSchema = z.strictObject({
  speech_id: z.string(),
  text: z.string(),
  final: z.boolean(),
  start: z.number().nullish(),
  end: z.number().nullish(),
});
export type AgentTranscript = z.infer<typeof AgentTranscriptSchema>;

/**
 * The platform is placing an outbound call and the far end has not answered yet. The first entry
 * of an outbound call's log.
 */
export const CallDialingSchema = z.strictObject({
  channel: ChannelSchema,
  from: z.string(),
  to: z.string(),
  run: z.string().nullable().nullish(),
  caller: ContactSchema.nullable(),
  external_id: z.string().nullish(),
  asked_by: z.string().nullish(),
});
export type CallDialing = z.infer<typeof CallDialingSchema>;

/** The call is over. Nothing about the conversation follows; call.summary still does. */
export const CallEndedSchema = z.strictObject({
  reason: EndReasonSchema,
  ended_by: EndedBySchema,
  ended_at: z.number(),
  duration_s: z.number(),
});
export type CallEnded = z.infer<typeof CallEndedSchema>;

/**
 * The line's hold and mute flags after one of them changed. Both are stated so a reader never has
 * to remember the other.
 */
export const CallLineSchema = z.strictObject({
  held: z.boolean(),
  muted: z.boolean(),
});
export type CallLine = z.infer<typeof CallLineSchema>;

/**
 * An inbound call is offered to this agent and has not been answered yet. The first entry of an
 * inbound call's log.
 */
export const CallRingingSchema = z.strictObject({
  channel: ChannelSchema,
  from: z.string(),
  to: z.string(),
  route: RouteSchema,
  run: z.string().nullable().nullish(),
  caller: ContactSchema.nullable(),
  external_id: z.string().nullish(),
});
export type CallRinging = z.infer<typeof CallRingingSchema>;

/**
 * Where in the call's own log a judgment is about. A reader who disagrees with a verdict opens the
 * log at those lines.
 */
export const JudgmentEvidenceSchema = z.strictObject({
  seqs: z.array(z.int()),
  said: z.string().nullish(),
});
export type JudgmentEvidence = z.infer<typeof JudgmentEvidenceSchema>;

/**
 * One judge's answer about one call: the question it was asked, the word it answered and the
 * sentence that says why.
 */
export const JudgmentSchema = z.strictObject({
  name: z.string(),
  verdict: ScoreVerdictSchema,
  criteria: z.string(),
  reason: z.string(),
  evidence: JudgmentEvidenceSchema,
});
export type Judgment = z.infer<typeof JudgmentSchema>;

/**
 * The last entry of a call: what the judges said about it at hang-up, one row per judge. Written
 * after call.summary, and the entry the log seals on.
 */
export const CallScoreSchema = z.strictObject({
  passed: z.boolean().nullish(),
  not_judged: z.string().nullish(),
  judges: z.array(JudgmentSchema),
  panel: z.array(z.string()).nullish(),
  judge_calls: z.int(),
  judge_cost_eur: z.number().nullish(),
});
export type CallScore = z.infer<typeof CallScoreSchema>;

/**
 * Media is up: the caller and the agent can hear each other, or the text session is open.
 * Everything the agent says and hears comes after this.
 */
export const CallStartedSchema = z.strictObject({
  channel: ChannelSchema,
  direction: DirectionSchema,
  from: z.string(),
  to: z.string(),
  run: z.string().nullable().nullish(),
  caller: ContactSchema.nullable(),
  started_at: z.number(),
  env: EnvSchema.nullish(),
});
export type CallStarted = z.infer<typeof CallStartedSchema>;

/**
 * What the call was about, how it went, what it consumed and what that cost. Written after
 * call.ended, once memory and pricing are done; call.score follows it and seals the log.
 */
export const CallSummarySchema = z.strictObject({
  reason: EndReasonSchema,
  outcome: z.string(),
  duration_s: z.number(),
  turns: z.int(),
  usage: z.array(ModelUsageSchema),
  cost: CostSchema,
  recording: z.string().nullish(),
});
export type CallSummary = z.infer<typeof CallSummarySchema>;

/** A transfer asked for by the agent or a supervisor finished, one way or the other. */
export const CallTransferredSchema = z.strictObject({
  to: z.string(),
  mode: TransferModeSchema,
  ok: z.boolean(),
  error: z.string().nullish(),
});
export type CallTransferred = z.infer<typeof CallTransferredSchema>;

/**
 * Somebody asked to be called back because no seat was free: a phone caller the overflow agent
 * answered, or a web visitor who left a number at the widget. Written into the agent's own log;
 * the tenant's app reads it and places the call.
 */
export const CallbackRequestedSchema = z.strictObject({
  channel: ChannelSchema,
  number: z.string(),
  via: z.enum(["overflow", "widget"]),
  call: z.string().nullable(),
  contact: ContactSchema.nullable(),
});
export type CallbackRequested = z.infer<typeof CallbackRequestedSchema>;

/** The caller did not say yes, or the request lapsed. The tool does not run; the model is told. */
export const ConfirmDeclinedSchema = z.strictObject({
  tool: z.string(),
  call_id: z.string(),
  audience: z.string(),
  said: z.string().nullish(),
  reason: z.enum(["no", "timeout", "changed", "cancelled"]),
});
export type ConfirmDeclined = z.infer<typeof ConfirmDeclinedSchema>;

/**
 * The caller said yes. The platform minted a one-shot token bound to the audience and the tool now
 * runs. The token itself never enters the log.
 */
export const ConfirmGrantedSchema = z.strictObject({
  tool: z.string(),
  call_id: z.string(),
  audience: z.string(),
  said: z.string(),
  ttl_s: z.int(),
});
export type ConfirmGranted = z.infer<typeof ConfirmGrantedSchema>;

/**
 * A tool with confirm set is about to run and the platform is asking the caller. The agent reads
 * the phrase; nothing runs until confirm.granted.
 */
export const ConfirmRequestSchema = z.strictObject({
  tool: z.string(),
  call_id: z.string(),
  arguments: z.record(z.string(), z.unknown()),
  audience: z.string(),
  phrase: z.string(),
  ttl_s: z.int(),
});
export type ConfirmRequest = z.infer<typeof ConfirmRequestSchema>;

/**
 * The gateway refused a call or a register because one of the org's quotas ran out. Written into
 * the agent's own log, which is the org's, before the door says no.
 */
export const CreditsExhaustedSchema = z.strictObject({
  org: z.string(),
  quota: z.enum(["minutes", "messages", "agents", "concurrent_calls", "memory_facts", "knowledge_chunks", "numbers", "seats"]),
  used: z.number(),
  limit: z.int(),
});
export type CreditsExhausted = z.infer<typeof CreditsExhaustedSchema>;

/**
 * A line the app wrote into the log with call.log. The platform never reads it; the console shows
 * it and evals may.
 */
export const CustomSchema = z.strictObject({
  name: z.string(),
  data: z.record(z.string(), z.unknown()),
});
export type Custom = z.infer<typeof CustomSchema>;

/** One ask of the process in the agent's directory, on a console's behalf. */
export const DevRequestSchema = z.strictObject({
  id: z.string(),
  verb: DevVerbSchema,
  data: z.record(z.string(), z.unknown()),
});
export type DevRequest = z.infer<typeof DevRequestSchema>;

/**
 * What retrieval put in front of the model for this turn. An answer can be traced back to its
 * chunks.
 */
export const DocsSourcesSchema = z.strictObject({
  query: z.string(),
  sources: z.array(DocSourceSchema),
  took_ms: z.number(),
  speech_id: z.string().nullish(),
});
export type DocsSources = z.infer<typeof DocsSourcesSchema>;

/**
 * Something went wrong. Inside a call it says what failed; outside a call it says which command
 * the gateway refused.
 */
export const ErrorEventSchema = z.strictObject({
  code: z.string(),
  message: z.string(),
  command: z.string().nullish(),
  id: z.string().nullish(),
  recoverable: z.boolean(),
});
export type ErrorEvent = z.infer<typeof ErrorEventSchema>;

/**
 * The gateway refused to open a call because every worker of the fleet was full. Written into the
 * agent's own log, which is the org's, before the door says no — the caller was offered a call
 * back instead of a room.
 */
export const FleetFullSchema = z.strictObject({
  channel: ChannelSchema,
  workers: z.int(),
  active: z.int(),
});
export type FleetFull = z.infer<typeof FleetFullSchema>;

/**
 * The replay is done: everything up to seq has been sent and what follows is live. Never stored;
 * sent to the reader.
 */
export const LogCaughtUpSchema = z.strictObject({
  seq: z.int(),
});
export type LogCaughtUp = z.infer<typeof LogCaughtUpSchema>;

/**
 * This reader missed a stretch: it reconnected too late for the store, or fell behind and the
 * fanout dropped ephemeral entries. When the platform has a snapshot, it is here so the reader can
 * catch up in one step. Never stored; sent to the reader.
 */
export const LogGapSchema = z.strictObject({
  from_seq: z.int(),
  to_seq: z.int(),
  snapshot: StateSchema.nullable(),
});
export type LogGap = z.infer<typeof LogGapSchema>;

/**
 * What memory did for this turn or at hangup: a recall before the reply, a remember after the
 * call, a forget on request.
 */
export const MemoryOpsSchema = z.strictObject({
  ops: z.array(MemoryOpSchema),
  speech_id: z.string().nullish(),
});
export type MemoryOps = z.infer<typeof MemoryOpsSchema>;

/** The answer to ping. Ephemeral: it proves the socket is alive and says nothing else. */
export const PongSchema = z.strictObject({
  ts: z.number(),
});
export type Pong = z.infer<typeof PongSchema>;

/**
 * A block of the prompt was rewritten. The text stays out of the log; its hash and length let two
 * states be compared.
 */
export const PromptChangedSchema = z.strictObject({
  name: z.string(),
  hash: z.string(),
  chars: z.int(),
});
export type PromptChanged = z.infer<typeof PromptChangedSchema>;

/** A tool call's result changed the state. */
export const StateCauseToolSchema = z.strictObject({
  kind: z.literal("tool"),
  tool: z.string(),
  call_id: z.string(),
});
export type StateCauseTool = z.infer<typeof StateCauseToolSchema>;

/** A fact from outside changed the state: the app's handler for an event.received moved a field. */
export const StateCauseEventSchema = z.strictObject({
  kind: z.literal("event"),
  name: z.string(),
  seq: z.int(),
});
export type StateCauseEvent = z.infer<typeof StateCauseEventSchema>;

/** What changed the state: a tool's result, or a fact from outside. Told apart by kind. */
export const StateCauseSchema = z.discriminatedUnion("kind", [StateCauseToolSchema, StateCauseEventSchema]);
export type StateCause = z.infer<typeof StateCauseSchema>;

/**
 * The app's declared state changed. A tool's result or an outside fact caused it, and the cause
 * says which; the whole state travels so a reader never needs the previous entry.
 */
export const StateChangedSchema = z.strictObject({
  state: z.record(z.string(), z.unknown()),
  changed: z.array(z.string()),
  cause: StateCauseSchema.nullish(),
});
export type StateChanged = z.infer<typeof StateChangedSchema>;

/** A supervisor hung up the call. call.ended follows with reason supervisor_ended. */
export const SupervisorEndedSchema = z.strictObject({
  by: SupervisorSchema,
  reason: z.string().nullish(),
});
export type SupervisorEnded = z.infer<typeof SupervisorEndedSchema>;

/** The supervisor gave the line back; the agent resumes with the history intact. */
export const SupervisorReleasedSchema = z.strictObject({
  by: SupervisorSchema,
});
export type SupervisorReleased = z.infer<typeof SupervisorReleasedSchema>;

/** A supervisor made the agent say this to the caller. */
export const SupervisorSaidSchema = z.strictObject({
  by: SupervisorSchema,
  text: z.string(),
});
export type SupervisorSaid = z.infer<typeof SupervisorSaidSchema>;

/** A supervisor took the line; the agent is quiet until supervisor.released. */
export const SupervisorTookOverSchema = z.strictObject({
  by: SupervisorSchema,
});
export type SupervisorTookOver = z.infer<typeof SupervisorTookOverSchema>;

/** A supervisor asked for a transfer. call.transferred says how it went. */
export const SupervisorTransferredSchema = z.strictObject({
  by: SupervisorSchema,
  to: z.string(),
  mode: TransferModeSchema,
});
export type SupervisorTransferred = z.infer<typeof SupervisorTransferredSchema>;

/** A supervisor told the agent something the caller never heard. */
export const SupervisorWhisperedSchema = z.strictObject({
  by: SupervisorSchema,
  text: z.string(),
});
export type SupervisorWhispered = z.infer<typeof SupervisorWhisperedSchema>;

/**
 * The model called a tool. The platform sends this to the app and the app's method runs in the
 * app's own process; tool.result closes it.
 */
export const ToolCallSchema = z.strictObject({
  call_id: z.string(),
  name: z.string(),
  arguments: z.record(z.string(), z.unknown()),
  speech_id: z.string().nullish(),
});
export type ToolCall = z.infer<typeof ToolCallSchema>;

/** The tools the model can see changed. The app's state moved and each tool's when was recomputed. */
export const ToolsChangedSchema = z.strictObject({
  visible: z.array(z.string()),
});
export type ToolsChanged = z.infer<typeof ToolsChangedSchema>;

/**
 * The agent's reply is over and this is what was said. With it, everything the session measured
 * about the reply.
 */
export const AgentTurnEndedSchema = z.strictObject({
  speech_id: z.string(),
  item_id: z.string().nullish(),
  text: z.string(),
  interrupted: z.boolean(),
  metrics: AgentTurnMetricsSchema,
});
export type AgentTurnEnded = z.infer<typeof AgentTurnEndedSchema>;

/**
 * The caller's turn is over and this is what they said. With it, everything the session measured
 * about the turn.
 */
export const UserTurnEndedSchema = z.strictObject({
  speech_id: z.string(),
  item_id: z.string().nullish(),
  text: z.string(),
  language: z.string().nullish(),
  transcript_confidence: z.number().nullish(),
  metrics: UserTurnMetricsSchema,
});
export type UserTurnEnded = z.infer<typeof UserTurnEndedSchema>;

/** The caller's state changed, in the session's own words. */
export const UserStateChangedSchema = z.strictObject({
  state: UserStateSchema,
});
export type UserStateChanged = z.infer<typeof UserStateChangedSchema>;

/**
 * Words from the caller as the recognizer hears them. Interim while final is false; the final one
 * becomes turn.user. Interim entries are ephemeral.
 */
export const UserTranscriptSchema = z.strictObject({
  text: z.string(),
  final: z.boolean(),
  language: z.string().nullish(),
  confidence: z.number().nullish(),
});
export type UserTranscript = z.infer<typeof UserTranscriptSchema>;
