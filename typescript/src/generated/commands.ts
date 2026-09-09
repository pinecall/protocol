// Generated from schema/commands/: one schema per command. Never edited by hand.

import { z } from "zod";
import {
  AgentConfigSchema,
  ContactSchema,
  PromptRegionSchema,
  RouteSchema,
  SupervisorSchema,
  ToolSpecSchema,
  TransferModeSchema,
} from "./defs.js";
import { VerbSchema } from "./verbs.js";

/**
 * Declare or change what the agent is: voice, models, language, greeting, the full tool list. Only
 * the fields sent change.
 */
export const AgentConfigureSchema = z.strictObject({
  config: AgentConfigSchema,
});
export type AgentConfigure = z.infer<typeof AgentConfigureSchema>;

/**
 * The app's first message: this socket speaks for this agent and answers these doors. The gateway
 * answers agent.registered, or error.
 */
export const AgentRegisterSchema = z.strictObject({
  routes: z.array(RouteSchema),
  sdk: z.string().nullish(),
  takes_unclaimed: z.boolean().nullish(),
});
export type AgentRegister = z.infer<typeof AgentRegisterSchema>;

/**
 * Make the model speak now, guided by an instruction it reads and the caller never hears: 'tell
 * them a slot at 10:15 just opened'. On livekit's session.generate_reply; the sibling of
 * agent.say, which speaks verbatim. The reply lands as turn.agent.
 */
export const AgentReplySchema = z.strictObject({
  instructions: z.string(),
  allow_interruptions: z.boolean().nullish(),
});
export type AgentReply = z.infer<typeof AgentReplySchema>;

/**
 * Make the agent say this text now, verbatim, outside the model's turn: a greeting, a read-back, a
 * system notice. The reply lands as turn.agent.
 */
export const AgentSaySchema = z.strictObject({
  text: z.string(),
  allow_interruptions: z.boolean().nullish(),
});
export type AgentSay = z.infer<typeof AgentSaySchema>;

/**
 * Place an outbound call as this agent. The new call's log opens with call.dialing; call.started
 * follows when the far end answers.
 */
export const CallDialSchema = z.strictObject({
  to: z.string(),
  from: z.string().nullish(),
  caller: ContactSchema.nullish(),
  metadata: z.record(z.string(), z.unknown()).nullish(),
});
export type CallDial = z.infer<typeof CallDialSchema>;

/** Send touch tones down the line, for an IVR on the far end. */
export const CallDtmfSchema = z.strictObject({
  digits: z.string(),
});
export type CallDtmf = z.infer<typeof CallDtmfSchema>;

/**
 * Hand the agent a fact from the tenant's backend: a slot freed, an order shipped, a payment
 * confirmed. Lands as event.received with source app. The agent must have declared the name in its
 * events with app among the senders, or the gateway answers error and nothing touches the log.
 */
export const CallEventSchema = z.strictObject({
  name: z.string(),
  data: z.record(z.string(), z.unknown()),
});
export type CallEvent = z.infer<typeof CallEventSchema>;

/** End the call from the app's side. call.ended follows with reason agent_hung_up. */
export const CallHangupSchema = z.strictObject({
  reason: z.string().nullish(),
});
export type CallHangup = z.infer<typeof CallHangupSchema>;

/** Put the caller on hold: they hear hold audio, the agent hears nothing. */
export const CallHoldSchema = z.strictObject({});
export type CallHold = z.infer<typeof CallHoldSchema>;

/**
 * Write a line of the app's own into the call's log. It gets a seq like everything else and lands
 * as custom.
 */
export const CallLogSchema = z.strictObject({
  name: z.string(),
  data: z.record(z.string(), z.unknown()),
});
export type CallLog = z.infer<typeof CallLogSchema>;

/** Mute the agent: it keeps listening and thinking, produces no audio. */
export const CallMuteSchema = z.strictObject({});
export type CallMute = z.infer<typeof CallMuteSchema>;

/** Send the caller to another number. call.transferred says whether it worked. */
export const CallTransferSchema = z.strictObject({
  to: z.string(),
  mode: TransferModeSchema,
});
export type CallTransfer = z.infer<typeof CallTransferSchema>;

/** Take the caller off hold. */
export const CallUnholdSchema = z.strictObject({});
export type CallUnhold = z.infer<typeof CallUnholdSchema>;

/** Unmute the agent. */
export const CallUnmuteSchema = z.strictObject({});
export type CallUnmute = z.infer<typeof CallUnmuteSchema>;

/**
 * Silence a participant for the rest of the call: their audio leaves the room, for everyone in it.
 * Lands as track.unpublished for their microphone. There is no unmute; a leg that must speak again
 * is invited again.
 */
export const ParticipantMuteSchema = z.strictObject({
  identity: z.string(),
});
export type ParticipantMute = z.infer<typeof ParticipantMuteSchema>;

/**
 * Put a participant out of the room. Lands as participant.left with reason participant_removed.
 * Removing the caller ends the call.
 */
export const ParticipantRemoveSchema = z.strictObject({
  identity: z.string(),
});
export type ParticipantRemove = z.infer<typeof ParticipantRemoveSchema>;

/** Is the socket alive? The gateway answers pong. */
export const PingSchema = z.strictObject({});
export type Ping = z.infer<typeof PingSchema>;

/**
 * Rewrite one region of the prompt. The static prefix is cached by the provider and rarely
 * changes; the view is render(state) and changes with the state.
 */
export const PromptSetSchema = z.strictObject({
  region: PromptRegionSchema,
  text: z.string(),
});
export type PromptSet = z.infer<typeof PromptSetSchema>;

/**
 * Bring somebody else into the call's room. A second SIP leg dialed to a number is the warm path:
 * the agent stays on with the caller while the other side answers. Lands as participant.joined
 * when they arrive, or error when they do not.
 */
export const RoomInviteSchema = z.strictObject({
  to: z.string(),
  kind: z.enum(["sip", "participant"]),
});
export type RoomInvite = z.infer<typeof RoomInviteSchema>;

/**
 * Push a payload to a browser in the room over the DataChannel: a card to render, a form to open.
 * Lands as room.sent with the size, never the payload. The widget listens on pinecall.ui; a topic
 * of the tenant's own reaches the tenant's own page code.
 */
export const RoomSendSchema = z.strictObject({
  topic: z.string(),
  data: z.record(z.string(), z.unknown()),
  to: z.string().nullish(),
});
export type RoomSend = z.infer<typeof RoomSendSchema>;

/**
 * Set up this one call before the first turn: the app's initial state, and any config that differs
 * from the agent's defaults for this caller.
 */
export const SessionConfigureSchema = z.strictObject({
  state: z.record(z.string(), z.unknown()).nullish(),
  config: AgentConfigSchema.nullish(),
});
export type SessionConfigure = z.infer<typeof SessionConfigureSchema>;

/** The app's state changed and this is all of it. The platform logs state.changed and re-renders. */
export const StateSetSchema = z.strictObject({
  state: z.record(z.string(), z.unknown()),
  changed: z.array(z.string()).nullish(),
});
export type StateSet = z.infer<typeof StateSetSchema>;

/** One supervise verb, from the human the door named. */
export const SupervisorVerbSchema = z.strictObject({
  by: SupervisorSchema,
  verb: VerbSchema,
});
export type SupervisorVerb = z.infer<typeof SupervisorVerbSchema>;

/**
 * The tools the model may see now. The full list was declared in agent.configure; this is the
 * subset whose when allows them in this state.
 */
export const ToolsSetSchema = z.strictObject({
  tools: z.array(ToolSpecSchema),
});
export type ToolsSet = z.infer<typeof ToolsSetSchema>;
