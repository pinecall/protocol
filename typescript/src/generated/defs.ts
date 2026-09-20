// Generated from schema/defs.json: the shapes shared across the wire. Never edited by hand.

import { z } from "zod";

/**
 * The door the public came through: a phone call over SIP, the browser widget over WebRTC, or
 * WhatsApp text.
 */
export const ChannelSchema = z.enum(["phone", "web", "whatsapp"]);
export type Channel = z.infer<typeof ChannelSchema>;

/** Inbound: the public reached the agent. Outbound: the agent reached out (a dial). */
export const DirectionSchema = z.enum(["inbound", "outbound"]);
export type Direction = z.infer<typeof DirectionSchema>;

/**
 * Which of the two worlds a key opens, and so which world an agent is held in and a call ran in. A
 * key is issued into one; an agent registered on it and every call it takes carry that one; a door
 * claimed in one is refused to a key of the other. `sandbox` is where things are written and
 * `production` is what the public reaches — and whether a sandbox agent is one PERSON's copy or
 * the team's shared one is not this field: it is whether the key that registered it names a
 * person. Every key issued before the field existed is production.
 */
export const EnvSchema = z.enum(["production", "sandbox"]);
export type Env = z.infer<typeof EnvSchema>;

/**
 * What a console may ask of the process standing in the agent's directory, relayed by the gateway:
 * a written call to the class mounted there (chat), a simulated caller put on the class it holds,
 * its goldens and a suite of them, its knowledge folder pushed or its golden asked, its memory
 * goldens, a call promoted to a candidate file, the drift of the last two windows, and the
 * reproductions a broken run left on that disk. Everything else a console needs is a door of the
 * gateway.
 */
export const DevVerbSchema = z.enum(["chat.roster", "chat.start", "chat.say", "chat.end", "simulate.start", "goldens.roster", "goldens.run", "knowledge.roster", "knowledge.push", "knowledge.eval", "memory.roster", "memory.eval", "memory.extraction", "promote.roster", "promote.write", "drift.read", "reproductions.roster", "reproductions.read"]);
export type DevVerb = z.infer<typeof DevVerbSchema>;

/**
 * Why the call is over. Who hung up, what failed before anybody could, drained: the platform took
 * the worker down (a deploy, a stop) with the call still on it, or app_detached: the app holding
 * the agent closed its socket mid-call, so nothing was rendering the prompt or answering a tool —
 * both are nobody's fault and neither is an error.
 */
export const EndReasonSchema = z.enum(["caller_hung_up", "agent_hung_up", "supervisor_ended", "transferred", "no_answer", "busy", "dial_failed", "timeout", "drained", "app_detached", "error"]);
export type EndReason = z.infer<typeof EndReasonSchema>;

/** Whose action ended the call. platform covers timeouts, errors and a drained worker. */
export const EndedBySchema = z.enum(["caller", "agent", "supervisor", "platform"]);
export type EndedBy = z.infer<typeof EndedBySchema>;

/**
 * What one judge answered about a finished call. Held: the rule held. Broken: it did not, and the
 * reason names the evidence. Deferred: the judge was asked and could not settle it. Skipped:
 * nobody asked it — no model was reachable inside the call's judging budget.
 */
export const ScoreVerdictSchema = z.enum(["held", "broken", "deferred", "skipped"]);
export type ScoreVerdict = z.infer<typeof ScoreVerdictSchema>;

/**
 * Cold: the caller is sent on and the agent leaves. Warm: the agent stays on the line until the
 * other side answers, then leaves.
 */
export const TransferModeSchema = z.enum(["cold", "warm"]);
export type TransferMode = z.infer<typeof TransferModeSchema>;

/**
 * Which region of the prompt a block lives in: static, before the history, cached by the provider;
 * or dynamic, after the history, replaced every turn. The append-only history in between is never
 * written by the app.
 */
export const PromptRegionSchema = z.enum(["static", "dynamic"]);
export type PromptRegion = z.infer<typeof PromptRegionSchema>;

/**
 * How the knowledge base reaches the model: retrieved, the platform runs search itself when the
 * caller's turn ends; or tool, the model calls search when it decides to. Either way the chunks
 * arrive as a tool result.
 */
export const DocsModeSchema = z.enum(["retrieved", "tool"]);
export type DocsMode = z.infer<typeof DocsModeSchema>;

/**
 * The two tools the platform runs on the app's behalf: recall reads the contact's facts out of
 * memory, search reads chunks out of the knowledge base. The app declares memory and docs and
 * writes neither method; the platform runs the lookup, and the answer reaches the model as a tool
 * result rather than as part of the prompt.
 */
export const PlatformToolSchema = z.enum(["recall", "search"]);
export type PlatformTool = z.infer<typeof PlatformToolSchema>;

/**
 * One named block of the prompt and the region it lives in. The default layout, when an agent
 * declares none, is identity, knowledge and tools (static), then the history, then view (dynamic).
 * A block's text is written per call with prompt.set.
 */
export const PromptBlockSpecSchema = z.strictObject({
  name: z.string().regex(/^[a-z][a-z0-9_]*$/),
  region: PromptRegionSchema,
});
export type PromptBlockSpec = z.infer<typeof PromptBlockSpecSchema>;

/**
 * What the platform believes the person on the line is doing right now. The states are the
 * session's own.
 */
export const UserStateSchema = z.enum(["listening", "speaking", "away"]);
export type UserState = z.infer<typeof UserStateSchema>;

/**
 * What the agent is doing right now, in the session's own words: warming up, waiting, hearing the
 * caller, generating, or playing audio.
 */
export const AgentStateSchema = z.enum(["initializing", "idle", "listening", "thinking", "speaking"]);
export type AgentState = z.infer<typeof AgentStateSchema>;

/**
 * Who a participant is to the call: the person the agent serves (over SIP or the widget), the
 * agent itself, a supervisor who took a seat in the room, a listener who only hears, or a second
 * SIP leg that room.invite brought in.
 */
export const ParticipantKindSchema = z.enum(["caller", "agent", "supervisor", "listener", "sip"]);
export type ParticipantKind = z.infer<typeof ParticipantKindSchema>;

/** What a track carries: a microphone's audio, a camera's video, or a screen share. */
export const TrackKindSchema = z.enum(["audio", "video", "screen"]);
export type TrackKind = z.infer<typeof TrackKindSchema>;

/** Where a track comes from, as livekit's TrackSource names it, in lower case. */
export const TrackSourceSchema = z.enum(["microphone", "camera", "screen_share", "screen_share_audio", "unknown"]);
export type TrackSource = z.infer<typeof TrackSourceSchema>;

/**
 * Where an outside fact came from: the tenant's backend over the app socket (app), or a
 * participant's browser over the DataChannel (participant).
 */
export const EventSourceSchema = z.enum(["app", "participant"]);
export type EventSource = z.infer<typeof EventSourceSchema>;

/**
 * Who may see a field of the app's state: everyone in the call (public), the tenant's own readers
 * (tenant, the default for a field never declared), or nobody without masking (pii).
 */
export const VisibilitySchema = z.enum(["public", "tenant", "pii"]);
export type Visibility = z.infer<typeof VisibilitySchema>;

/**
 * Which projection a sink applies before a state or an entry leaves the platform: public for a
 * participant reading its own call, tenant for the tenant's readers. The contract is
 * docs/protocol/projections.md; a client never applies one.
 */
export const ProjectionSchema = z.enum(["public", "tenant"]);
export type Projection = z.infer<typeof ProjectionSchema>;

/**
 * Who is on the line, as far as the platform knows. Everything is optional: a web visitor may be
 * nobody yet.
 */
export const ContactSchema = z.strictObject({
  id: z.string().nullish(),
  phone: z.string().nullish(),
  name: z.string().nullish(),
  email: z.string().nullish(),
  external_id: z.string().nullish(),
});
export type Contact = z.infer<typeof ContactSchema>;

/**
 * One door to an agent: a channel and, for phone and WhatsApp, the number that answers. A number
 * is a route, never an agent.
 */
export const RouteSchema = z.strictObject({
  channel: ChannelSchema,
  number: z.string().nullable(),
  label: z.string().nullish(),
});
export type Route = z.infer<typeof RouteSchema>;

/** The human who sent a supervise verb, as the token that let them in names them. */
export const SupervisorSchema = z.strictObject({
  id: z.string(),
  name: z.string().nullish(),
});
export type Supervisor = z.infer<typeof SupervisorSchema>;

/**
 * What the app declares about one tool: the contract the model sees and the rules the platform
 * enforces before running it.
 */
export const ToolSpecSchema = z.strictObject({
  name: z.string(),
  description: z.string(),
  parameters: z.record(z.string(), z.unknown()),
  side_effect: z.enum(["read", "write", "irreversible"]).nullish(),
  confirm: z.string().nullish(),
  pii: z.array(z.string()).nullish(),
  timeout_s: z.number().nullish(),
});
export type ToolSpec = z.infer<typeof ToolSpecSchema>;

/**
 * What came back from running a tool in the app's process. Either an output or an error, never
 * both.
 */
export const ToolResultSchema = z.strictObject({
  call_id: z.string(),
  name: z.string(),
  output: z.unknown().nullish(),
  error: z.string().nullish(),
  summary: z.string().nullish(),
  duration_s: z.number().nullish(),
});
export type ToolResult = z.infer<typeof ToolResultSchema>;

/**
 * One thing remembered about a contact: a sentence, where it came from, and how well it matched
 * when recalled.
 */
export const MemoryFactSchema = z.strictObject({
  id: z.string().nullish(),
  text: z.string(),
  category: z.string().nullish(),
  score: z.number().nullish(),
  source: z.string().nullish(),
});
export type MemoryFact = z.infer<typeof MemoryFactSchema>;

/**
 * One operation against the contact's memory: a recall during the turn, a remember at hangup, or a
 * forget on request.
 */
export const MemoryOpSchema = z.strictObject({
  op: z.enum(["recall", "remember", "forget"]),
  contact: z.string().nullish(),
  query: z.string().nullish(),
  facts: z.array(MemoryFactSchema),
  took_ms: z.number(),
});
export type MemoryOp = z.infer<typeof MemoryOpSchema>;

/** One chunk of the knowledge base that retrieval put in front of the model for this turn. */
export const DocSourceSchema = z.strictObject({
  id: z.string(),
  base: z.string().nullish(),
  path: z.string(),
  heading: z.string().nullish(),
  score: z.number(),
  excerpt: z.string().nullish(),
});
export type DocSource = z.infer<typeof DocSourceSchema>;

/** The exchange rate the cost was computed with, stated so the number can be reproduced. */
export const CostRateSchema = z.strictObject({
  currency: z.literal("EUR"),
  usd_to_eur: z.number(),
  as_of: z.string(),
});
export type CostRate = z.infer<typeof CostRateSchema>;

/** One priced line: a model, what was counted, how much, and what it came to. */
export const CostRowSchema = z.strictObject({
  provider: z.string(),
  model: z.string(),
  unit: z.enum(["input_tokens", "cached_input_tokens", "cache_creation_tokens", "output_tokens", "characters", "audio_seconds", "requests", "session_seconds"]),
  quantity: z.number(),
  unit_price_usd: z.number(),
  eur: z.number(),
});
export type CostRow = z.infer<typeof CostRowSchema>;

/** A usage row the price table does not know. It is listed, never priced at zero. */
export const UnpricedRowSchema = z.strictObject({
  provider: z.string(),
  model: z.string(),
});
export type UnpricedRow = z.infer<typeof UnpricedRowSchema>;

/**
 * What the call cost in provider fees, informational, in euros. The runtime never prices
 * commercially; this is the provider's bill as best we know it.
 */
export const CostSchema = z.strictObject({
  eur: z.number(),
  rate: CostRateSchema,
  rows: z.array(CostRowSchema),
  unpriced: z.array(UnpricedRowSchema),
});
export type Cost = z.infer<typeof CostSchema>;

/** Which voice speaks for the agent: the name it was asked for, or the id the provider knows it by. */
export const VoiceConfigSchema = z.strictObject({
  name: z.string().nullish(),
  provider: z.string().nullish(),
  model: z.string().nullish(),
  voice_id: z.string().nullish(),
});
export type VoiceConfig = z.infer<typeof VoiceConfigSchema>;

/** Which model does a job (the LLM, or the STT), and the one or two knobs worth turning. */
export const ModelConfigSchema = z.strictObject({
  provider: z.string(),
  model: z.string(),
  temperature: z.number().nullish(),
});
export type ModelConfig = z.infer<typeof ModelConfigSchema>;

/** How the session decides that the caller has finished, and when the caller may interrupt. */
export const TurnConfigSchema = z.strictObject({
  min_interruption_words: z.int().nullish(),
  endpointing_ms: z.int().nullish(),
});
export type TurnConfig = z.infer<typeof TurnConfigSchema>;

/** How the voice says one word it would otherwise get wrong: a proper name, a brand, a street. */
export const PronunciationSchema = z.strictObject({
  word: z.string(),
  spoken: z.string(),
});
export type Pronunciation = z.infer<typeof PronunciationSchema>;

/**
 * What the app declares about one field of its state: who may see it. A field never declared is
 * tenant.
 */
export const StateFieldSpecSchema = z.strictObject({
  name: z.string(),
  visibility: VisibilitySchema,
});
export type StateFieldSpec = z.infer<typeof StateFieldSpecSchema>;

/**
 * One outside event the agent accepts, and from whom. An event nobody declared is refused before
 * it touches the log.
 */
export const EventSpecSchema = z.strictObject({
  name: z.string(),
  from: z.array(EventSourceSchema),
});
export type EventSpec = z.infer<typeof EventSpecSchema>;

/** One file of a base, as a push sends it: its path as the tenant keeps it, and its text. */
export const KnowledgeFileSchema = z.strictObject({
  path: z.string(),
  text: z.string(),
});
export type KnowledgeFile = z.infer<typeof KnowledgeFileSchema>;

/**
 * The knowledge base the agent answers from, and how its chunks reach the model. It is named by
 * the base it was pushed under, with PUT /v1/knowledge/{base}.
 */
export const DocsConfigSchema = z.strictObject({
  base: z.string(),
  mode: DocsModeSchema.nullish(),
  k: z.int().nullish(),
  min_score: z.number().nullish(),
});
export type DocsConfig = z.infer<typeof DocsConfigSchema>;

/**
 * How the agent opens a call, before the caller has said anything. Exactly one of the two, because
 * there are only two ways to open one: `say` are the words themselves and `reply` is what the
 * model is told before it finds its own. They are agent.say and agent.reply declared instead of
 * called, so a class that opens every call the same way needs no onCall hook to do it, and an
 * operator can turn the opening at the pipeline door without a deploy. Absent: nobody speaks until
 * the caller does.
 */
export const GreetingConfigSchema = z.strictObject({
  say: z.string().nullish(),
  reply: z.string().nullish(),
  allow_interruptions: z.boolean().nullish(),
});
export type GreetingConfig = z.infer<typeof GreetingConfigSchema>;

/**
 * Whether the model may end the call itself. Declaring this is what puts livekit's own end_call
 * tool in front of the model; a class that says nothing here cannot hang up, and the call ends
 * when the caller does or when a supervisor says so. The tool is hidden while the agent is
 * greeting, because a model that can hang up on its first turn eventually does.
 */
export const HangupConfigSchema = z.strictObject({
  when: z.string().nullish(),
});
export type HangupConfig = z.infer<typeof HangupConfigSchema>;

/**
 * What memory keeps about a contact across calls, and what it must never keep. Both lists are in
 * the tenant's own words.
 */
export const MemoryConfigSchema = z.strictObject({
  remember: z.array(z.string()).nullish(),
  forget: z.array(z.string()).nullish(),
});
export type MemoryConfig = z.infer<typeof MemoryConfigSchema>;

/**
 * What an app declares about its agent: the prompt's layout, the language, the tools, whether it
 * searches its bases itself, and who may see and send what. Every field is optional so a configure
 * can change one thing. The environment — voice, models, greeting, hangup, turn, says, hears,
 * knowledge, docs, memory — is the world's, set in the agent's settings, and no longer read off
 * this declaration.
 */
export const AgentConfigSchema = z.strictObject({
  prompt: z.array(PromptBlockSpecSchema).nullish(),
  language: z.string().nullish(),
  greeting: GreetingConfigSchema.nullish(),
  voice: VoiceConfigSchema.nullish(),
  llm: ModelConfigSchema.nullish(),
  stt: ModelConfigSchema.nullish(),
  turn: TurnConfigSchema.nullish(),
  says: z.array(PronunciationSchema).nullish(),
  hears: z.array(z.string()).nullish(),
  knowledge: KnowledgeFileSchema.nullish(),
  docs: DocsConfigSchema.nullish(),
  memory: MemoryConfigSchema.nullish(),
  hangup: HangupConfigSchema.nullish(),
  tools: z.array(ToolSpecSchema).nullish(),
  uses_knowledge: z.boolean().nullish(),
  state_fields: z.array(StateFieldSpecSchema).nullish(),
  events: z.array(EventSpecSchema).nullish(),
});
export type AgentConfig = z.infer<typeof AgentConfigSchema>;
