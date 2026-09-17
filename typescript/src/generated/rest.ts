// Generated from schema/rest.json: the envelopes the read doors answer in. Never edited by hand.

import { z } from "zod";
import {
  ChannelSchema,
  ContactSchema,
  CostSchema,
  DirectionSchema,
  EndReasonSchema,
  EnvSchema,
  KnowledgeFileSchema,
  PlatformToolSchema,
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

/**
 * One call's call.score as a list draws it: how many judges held of how many answered, and why the
 * first one that broke did.
 */
export const SessionScoreSchema = z.strictObject({
  held: z.int(),
  judged: z.int(),
  passed: z.boolean(),
  reason: z.string().nullable(),
});
export type SessionScore = z.infer<typeof SessionScoreSchema>;

/**
 * escalated: a person took part — a transfer, a supervisor taking the line, saying something, or
 * ending the call. low_score: a judge answered broken. promise: the promises judge found the agent
 * committing the business to something no tool call records.
 */
export const SessionFlagSchema = z.enum(["escalated", "low_score", "promise"]);
export type SessionFlag = z.infer<typeof SessionFlagSchema>;

/** One call as a list draws it: which call, how far the log got, and the state's own fields. */
export const SessionLineSchema = z.strictObject({
  call: z.string(),
  agent: z.string(),
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
  score: SessionScoreSchema.nullable().nullish(),
  flags: z.array(SessionFlagSchema).nullish(),
});
export type SessionLine = z.infer<typeof SessionLineSchema>;

/**
 * GET /v1/agents/{slug}/sessions and GET /v1/sessions: the calls that match, newest first, a page
 * at a time.
 */
export const SessionListSchema = z.strictObject({
  calls: z.array(SessionLineSchema),
  total: z.int().nullable().nullish(),
  next: z.string().nullable().nullish(),
});
export type SessionList = z.infer<typeof SessionListSchema>;

/** How many calls started on the day, and on the day before it. */
export const InsightsConversationsSchema = z.strictObject({
  today: z.int(),
  yesterday: z.int(),
});
export type InsightsConversations = z.infer<typeof InsightsConversationsSchema>;

/** The day's calls by the door they came in by. */
export const InsightsChannelsSchema = z.strictObject({
  phone: z.int(),
  web: z.int(),
  whatsapp: z.int(),
});
export type InsightsChannels = z.infer<typeof InsightsChannelsSchema>;

/** One agent's day. */
export const InsightsAgentSchema = z.strictObject({
  slug: z.string(),
  today: z.int(),
  score: z.number().nullable(),
});
export type InsightsAgent = z.infer<typeof InsightsAgentSchema>;

/** What the org may spend in a month and what it has spent so far, both worlds together. */
export const InsightsBudgetSchema = z.strictObject({
  limit_eur: z.number().nullable(),
  spent_eur_month: z.number(),
});
export type InsightsBudget = z.infer<typeof InsightsBudgetSchema>;

/**
 * GET /v1/insights: one day of the key's world and corner at a glance, counted off the call index
 * and never off a log.
 */
export const InsightsSchema = z.strictObject({
  day: z.string(),
  timezone: z.string(),
  conversations: InsightsConversationsSchema,
  resolved_rate: z.number().nullable(),
  median_e2e_s: z.number().nullable(),
  spend_eur: z.number(),
  channels: InsightsChannelsSchema,
  sessions_total: z.int(),
  live: z.int(),
  agents: z.array(InsightsAgentSchema),
  budget: InsightsBudgetSchema,
});
export type Insights = z.infer<typeof InsightsSchema>;

/**
 * GET and PUT /v1/org/judging: whether the org's calls are judged at hang-up, and what judging one
 * may spend on a model.
 */
export const JudgingSchema = z.strictObject({
  on: z.boolean(),
  ceiling_eur: z.number().nullable(),
});
export type Judging = z.infer<typeof JudgingSchema>;

/** PUT /v1/org/judging, the body. */
export const JudgingWantedSchema = z.strictObject({
  on: z.boolean(),
});
export type JudgingWanted = z.infer<typeof JudgingWantedSchema>;

/**
 * in: the contact wrote it. out: the agent, or a person as the agent, did. call: a spoken call,
 * drawn as one pill.
 */
export const ThreadKindSchema = z.enum(["in", "out", "call"]);
export type ThreadKind = z.infer<typeof ThreadKindSchema>;

/** The newest thing on a contact's thread. */
export const ThreadLastSchema = z.strictObject({
  text: z.string().nullable(),
  at: z.number(),
  kind: ThreadKindSchema,
});
export type ThreadLast = z.infer<typeof ThreadLastSchema>;

/** One contact of an agent's inbox: every call of theirs, folded into one line. */
export const ThreadLineSchema = z.strictObject({
  contact: z.string(),
  name: z.string().nullable(),
  channel_last: ChannelSchema,
  last: ThreadLastSchema,
  unread: z.int(),
  calls: z.int(),
});
export type ThreadLine = z.infer<typeof ThreadLineSchema>;

/** GET /v1/agents/{slug}/threads: the agent's contacts, the newest thread first. */
export const ThreadListSchema = z.strictObject({
  threads: z.array(ThreadLineSchema),
  next: z.string().nullable(),
});
export type ThreadList = z.infer<typeof ThreadListSchema>;

/** One message of a thread, or one spoken call drawn as a pill. */
export const ThreadMessageSchema = z.strictObject({
  kind: ThreadKindSchema,
  text: z.string().nullable(),
  at: z.number(),
  call: z.string(),
  channel: ChannelSchema,
  duration_s: z.number().nullable().nullish(),
  answered: z.boolean().nullish(),
});
export type ThreadMessage = z.infer<typeof ThreadMessageSchema>;

/** GET /v1/agents/{slug}/threads/{contact}: every call of one contact, merged, oldest first. */
export const ThreadSchema = z.strictObject({
  contact: z.string(),
  name: z.string().nullable(),
  messages: z.array(ThreadMessageSchema),
});
export type Thread = z.infer<typeof ThreadSchema>;

/** POST /v1/agents/{slug}/threads/{contact}/messages, the body. */
export const ThreadSaySchema = z.strictObject({
  text: z.string(),
});
export type ThreadSay = z.infer<typeof ThreadSaySchema>;

/**
 * POST /v1/agents/{slug}/threads/{contact}/messages, the answer: the call it was said on. The
 * turn.agent it lands as is on that call's log.
 */
export const ThreadSaidSchema = z.strictObject({
  contact: z.string(),
  call: z.string(),
});
export type ThreadSaid = z.infer<typeof ThreadSaidSchema>;

/** One current fact memory holds, across the contacts an agent's calls taught. */
export const AgentFactSchema = z.strictObject({
  id: z.string(),
  contact: z.string(),
  text: z.string(),
  category: z.string().nullable(),
  written_at: z.number(),
});
export type AgentFact = z.infer<typeof AgentFactSchema>;

/** GET /v1/agents/{slug}/memory: the current facts the agent's calls taught, newest first. */
export const AgentMemorySchema = z.strictObject({
  facts: z.array(AgentFactSchema),
  next: z.string().nullable(),
});
export type AgentMemory = z.infer<typeof AgentMemorySchema>;

/**
 * GET and PUT /v1/agents/{slug}/widget: how the widget presents this agent, kept per org, world
 * and agent. PUT takes the whole set.
 */
export const WidgetSettingsSchema = z.strictObject({
  title: z.string().nullable(),
  tagline: z.string().nullable(),
  greeting: z.string().nullable(),
  accent: z.string().nullable(),
  autostart: z.boolean(),
});
export type WidgetSettings = z.infer<typeof WidgetSettingsSchema>;

/**
 * GET and PUT /v1/org/sso: the OpenID Connect provider this org's people sign in at, and never the
 * client secret it was wired with.
 */
export const OrgSsoSchema = z.strictObject({
  configured: z.boolean(),
  issuer: z.string().nullable(),
  client_id: z.string().nullable(),
  domains: z.array(z.string()),
  role: z.string().nullable(),
  required: z.boolean(),
  redirect_uri: z.string(),
});
export type OrgSso = z.infer<typeof OrgSsoSchema>;

/**
 * PUT /v1/org/sso, the body. The configuration is replaced whole, the client secret included: it
 * is write-only, so a change of anything else carries it again.
 */
export const OrgSsoWantedSchema = z.strictObject({
  issuer: z.string(),
  client_id: z.string(),
  client_secret: z.string(),
  domains: z.array(z.string()),
  role: z.string().nullable().nullish(),
  required: z.boolean().nullish(),
});
export type OrgSsoWanted = z.infer<typeof OrgSsoWantedSchema>;

/**
 * One org a sign-in page may send somebody to, named — and nothing about whether anybody answers
 * to the address that asked.
 */
export const SsoOrgSchema = z.strictObject({
  org: z.string(),
  slug: z.string(),
  name: z.string(),
});
export type SsoOrg = z.infer<typeof SsoOrgSchema>;

/**
 * POST /v1/login/sso/discover: the orgs whose domains match an address's and that wired a
 * provider. Empty is the answer for a domain nobody wired, and for a box that keeps no provider at
 * all.
 */
export const SsoDiscoverySchema = z.strictObject({
  orgs: z.array(SsoOrgSchema),
});
export type SsoDiscovery = z.infer<typeof SsoDiscoverySchema>;

/** One corner of a world holding an agent: the member whose it is, named so a person can read it. */
export const LineHolderSchema = z.strictObject({
  holder: z.string().nullable(),
  name: z.string().nullable(),
});
export type LineHolder = z.infer<typeof LineHolderSchema>;

/** One agent, as somebody choosing which to open needs to see it: its name and its channels. */
export const HeldAgentSchema = z.strictObject({
  slug: z.string(),
  channels: z.array(ChannelSchema),
  holder: LineHolderSchema.nullish(),
});
export type HeldAgent = z.infer<typeof HeldAgentSchema>;

/** GET /v1/agents: every agent this fleet is holding right now, as the front page lists them. */
export const AgentListSchema = z.strictObject({
  agents: z.array(HeldAgentSchema),
});
export type AgentList = z.infer<typeof AgentListSchema>;

/**
 * GET /v1/agents/{slug}/line: whose terminal a call that RINGS at this agent's doors lands in. An
 * org shares one sandbox number, so it rings in one place and which one is claimed.
 */
export const TheLineSchema = z.strictObject({
  agent: z.string(),
  env: EnvSchema,
  held: z.boolean(),
  holding: LineHolderSchema.nullish(),
  yours: z.boolean(),
  waiting: z.array(LineHolderSchema),
  calling: z.array(z.string()),
});
export type TheLine = z.infer<typeof TheLineSchema>;

/**
 * PUT /v1/knowledge/{base}, the body: the tenant's folder as of now, sent whole. The base is
 * replaced, never merged.
 */
export const KnowledgePushSchema = z.strictObject({
  files: z.array(KnowledgeFileSchema),
});
export type KnowledgePush = z.infer<typeof KnowledgePushSchema>;

/**
 * One question of a base's golden: what somebody asks, and the chunk that should answer it. A
 * chunk answers when its file and heading path start with `expects`, so naming a file alone
 * accepts any chunk of it and naming a heading accepts that section.
 */
export const GoldenQuestionSchema = z.strictObject({
  asks: z.string(),
  expects: z.string(),
});
export type GoldenQuestion = z.infer<typeof GoldenQuestionSchema>;

/**
 * POST /v1/knowledge/{base}/eval, the body: the questions a base is held to. A golden is fixed and
 * the index is the variable; a question is never softened so a change can pass.
 */
export const KnowledgeGoldenSchema = z.strictObject({
  questions: z.array(GoldenQuestionSchema),
  k: z.int().nullish(),
});
export type KnowledgeGolden = z.infer<typeof KnowledgeGoldenSchema>;

/** One question whose expected chunk was not among the k returned, and what came back instead. */
export const GoldenMissSchema = z.strictObject({
  asks: z.string(),
  expects: z.string(),
  found: z.array(z.string()),
});
export type GoldenMiss = z.infer<typeof GoldenMissSchema>;

/**
 * POST /v1/knowledge/{base}/eval, the answer: how the index did on its own golden. Both figures
 * are computed by code, with no model, so two runs of the same golden over the same base answer
 * the same numbers.
 */
export const KnowledgeScoreSchema = z.strictObject({
  base: z.string(),
  model: z.string(),
  questions: z.int(),
  k: z.int(),
  recall_at_k: z.number(),
  ndcg_at_10: z.number(),
  took_ms: z.number(),
  misses: z.array(GoldenMissSchema),
});
export type KnowledgeScore = z.infer<typeof KnowledgeScoreSchema>;

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
  model: z.string(),
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
 * One question of a memory golden: what memory holds about the contact who asks it, the words they
 * just said, and the fact or facts that should come back. The facts are the question's own, so a
 * golden needs no contact in any table.
 */
export const MemoryQuestionSchema = z.strictObject({
  holds: z.array(z.string()),
  asks: z.string(),
  expects: z.array(z.string()),
});
export type MemoryQuestion = z.infer<typeof MemoryQuestionSchema>;

/**
 * POST /v1/contacts/memory/eval, the body: the questions memory is held to. Each question brings
 * its own facts, which are written to a scratch contact of this org, asked, and deleted. A golden
 * is fixed and the ranking is the variable; a question is never softened so a change can pass.
 */
export const MemoryGoldenSchema = z.strictObject({
  questions: z.array(MemoryQuestionSchema),
  k: z.int().nullish(),
});
export type MemoryGolden = z.infer<typeof MemoryGoldenSchema>;

/**
 * One question memory did not answer whole: what it wanted and did not get, and what came back
 * instead. GoldenMiss is the knowledge base's and names the one chunk that should have won; a
 * memory question may expect several facts and miss some of them.
 */
export const MemoryMissSchema = z.strictObject({
  asks: z.string(),
  missing: z.array(z.string()),
  found: z.array(z.string()),
});
export type MemoryMiss = z.infer<typeof MemoryMissSchema>;

/**
 * POST /v1/contacts/memory/eval, the answer: how memory ranked the facts its own golden asked for.
 * Both figures are computed by code, with no model in the loop, so two runs of one golden answer
 * the same numbers.
 */
export const MemoryScoreSchema = z.strictObject({
  model: z.string(),
  questions: z.int(),
  k: z.int(),
  recall_at_k: z.number(),
  ndcg_at_10: z.number(),
  took_ms: z.number(),
  misses: z.array(MemoryMissSchema),
});
export type MemoryScore = z.infer<typeof MemoryScoreSchema>;

/**
 * What must come of one call's hang-up: each field is one of the four ways a hang-up costs a
 * business. Nothing here compares one sentence to another — a category is the class's own word, a
 * value is a literal the caller said out loud, and a supersession is an id — because two ways of
 * writing one fact are one fact.
 */
export const ExtractionExpectedSchema = z.strictObject({
  writes: z.array(z.string()).nullish(),
  never: z.array(z.string()).nullish(),
  never_says: z.array(z.string()).nullish(),
  invalidates: z.array(z.string()).nullish(),
});
export type ExtractionExpected = z.infer<typeof ExtractionExpectedSchema>;

/**
 * One call written down and what memory must make of it: the write side of the table, judged by
 * code. The read side is MemoryGolden and neither answers for the other — a call may extract the
 * perfect fact and never see it again, because six is what a turn is handed and the seventh is
 * cut.
 */
export const ExtractionGoldenSchema = z.strictObject({
  name: z.string(),
  said: z.array(z.tuple([z.string(), z.string()])),
  holds: z.array(z.string()).nullish(),
  plants: z.array(z.string()).nullish(),
  channel: ChannelSchema.nullish(),
  expect: ExtractionExpectedSchema.nullish(),
});
export type ExtractionGolden = z.infer<typeof ExtractionGoldenSchema>;

/**
 * POST /v1/agents/{slug}/memory/extraction, the body: the goldens whole, as the tenant wrote them
 * down. Each costs ONE model call — the very one a hang-up makes — run on the org's own model and
 * keys against the class the caller is holding.
 */
export const ExtractionCasesSchema = z.strictObject({
  cases: z.array(ExtractionGoldenSchema),
});
export type ExtractionCases = z.infer<typeof ExtractionCasesSchema>;

/**
 * One thing that did not hold about a case: which of the questions, and the evidence in a sentence
 * a person can act on.
 */
export const ExtractionBrokeSchema = z.strictObject({
  check: z.string(),
  detail: z.string(),
});
export type ExtractionBroke = z.infer<typeof ExtractionBrokeSchema>;

/** One case, run: what memory would have kept, what admission refused, and what did not hold. */
export const ExtractionJudgedSchema = z.strictObject({
  name: z.string(),
  held: z.boolean(),
  wrote: z.array(z.string()).nullish(),
  refused: z.array(z.string()).nullish(),
  broke: z.array(ExtractionBrokeSchema).nullish(),
});
export type ExtractionJudged = z.infer<typeof ExtractionJudgedSchema>;

/**
 * POST /v1/agents/{slug}/memory/extraction, the answer: which model answered, how many cases held,
 * and every one of them. A verb prints this and a pipeline exits on it.
 */
export const ExtractionRunSchema = z.strictObject({
  agent: z.string(),
  model: z.string(),
  cases: z.int(),
  held: z.int(),
  took_ms: z.number(),
  results: z.array(ExtractionJudgedSchema),
});
export type ExtractionRun = z.infer<typeof ExtractionRunSchema>;

/**
 * POST /v1/calls/{call}/lookup, the body: which platform tool to run for this turn, and what to
 * run it with. Worker-only; the gateway runs it against its own stores and writes memory.ops or
 * docs.sources on the call's log itself.
 */
export const LookupRequestSchema = z.strictObject({
  tool: PlatformToolSchema,
  input: z.record(z.string(), z.unknown()),
  speech_id: z.string().nullish(),
});
export type LookupRequest = z.infer<typeof LookupRequestSchema>;

/**
 * POST /v1/calls/{call}/lookup, the answer: what the tool found, and how long finding it took. The
 * output is JSON-encoded into a tool_result block, which is where everything from outside the
 * conversation goes and the only place it goes.
 */
export const LookupResultSchema = z.strictObject({
  output: z.record(z.string(), z.unknown()),
  took_ms: z.number(),
});
export type LookupResult = z.infer<typeof LookupResultSchema>;

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
