// The wire, decoded and typed. The only file that touches a key name: snake_case on the wire,
// camelCase for whoever wants it. Never edited by hand.

import { z } from "zod";
import { CommandSchema, EntrySchema, type Command, type Entry } from "./envelope.js";
import { COMMAND_SCHEMAS, EVENT_SCHEMAS, type CommandType, type EventType } from "./registry.js";

export class ProtocolError extends Error {
  override readonly name = "ProtocolError";
}

/** The data shape of one event type. */
export type EventData<K extends EventType> = z.infer<(typeof EVENT_SCHEMAS)[K]>;

/** One event, typed by its type: switch on `type` and `data` narrows with it. */
export type Event = { [K in EventType]: { type: K; data: EventData<K> } }[EventType];

/** The data shape of one command type. */
export type CommandData<K extends CommandType> = z.infer<(typeof COMMAND_SCHEMAS)[K]>;

/** One command, typed by its type. */
export type AnyCommand = { [K in CommandType]: { type: K; data: CommandData<K> } }[CommandType];

/** One log line from decoded JSON. A bad shape throws. */
export function decodeEntry(raw: unknown): Entry {
  return EntrySchema.parse(raw);
}

/** A whole log from a JSON array text, in the order it came. */
export function decodeEntries(text: string): Entry[] {
  return z.array(EntrySchema).parse(JSON.parse(text));
}

/** The entry's data as the shape its type names. An unknown type or a bad shape throws. */
export function eventOf(entry: Entry): Event {
  if (!isEventType(entry.type)) {
    throw new ProtocolError(`unknown event type: ${entry.type}`);
  }
  const data: unknown = EVENT_SCHEMAS[entry.type].parse(entry.data);
  return { type: entry.type, data } as Event;
}

/** The command's data as the shape its type names. An unknown type or a bad shape throws. */
export function commandOf(command: Command): AnyCommand {
  if (!isCommandType(command.type)) {
    throw new ProtocolError(`unknown command type: ${command.type}`);
  }
  const data: unknown = COMMAND_SCHEMAS[command.type].parse(command.data);
  return { type: command.type, data } as AnyCommand;
}

export function isEventType(type: string): type is EventType {
  return Object.hasOwn(EVENT_SCHEMAS, type);
}

export function isCommandType(type: string): type is CommandType {
  return Object.hasOwn(COMMAND_SCHEMAS, type);
}

// ── key names ──────────────────────────────────────────────────────────────────

/** "llm_node_ttft" as a type becomes "llmNodeTtft". */
export type CamelCase<S extends string> = S extends `${infer Head}_${infer Tail}`
  ? `${Head}${Capitalize<CamelCase<Tail>>}`
  : S;

/** "llmNodeTtft" as a type becomes "llm_node_ttft". */
export type SnakeCase<S extends string> = S extends `${infer Head}${infer Tail}`
  ? Head extends Lowercase<Head>
    ? `${Head}${SnakeCase<Tail>}`
    : `_${Lowercase<Head>}${SnakeCase<Tail>}`
  : S;

/** A wire shape with every key camelCased, deep, except under the opaque keys. */
export type Camel<T> = T extends readonly (infer Item)[]
  ? Camel<Item>[]
  : T extends object
    ? { [K in keyof T as K extends string ? CamelCase<K> : K]: K extends OpaqueKey ? T[K] : Camel<T[K]> }
    : T;

/** A camelCased shape back to the wire's keys, deep, except under the opaque keys. */
export type Snake<T> = T extends readonly (infer Item)[]
  ? Snake<Item>[]
  : T extends object
    ? { [K in keyof T as K extends string ? SnakeCase<K> : K]: K extends OpaqueKey ? T[K] : Snake<T[K]> }
    : T;

/** The keys whose values belong to the app (its state, a tool's arguments, a map it named): never renamed below them. */
export const OPAQUE_KEYS = new Set<string>(["app_state", "arguments", "attributes", "data", "input", "metadata", "output", "parameters", "prompt", "state"]);
export type OpaqueKey = "app_state" | "arguments" | "attributes" | "data" | "input" | "metadata" | "output" | "parameters" | "prompt" | "state";

/** Rename every key from snake_case to camelCase, deep. Values are never touched. */
export function toCamel<T>(value: T): Camel<T> {
  return renameKeys(value, camelCase) as Camel<T>;
}

/** Rename every key from camelCase to snake_case, deep. Values are never touched. */
export function toSnake<T>(value: T): Snake<T> {
  return renameKeys(value, snakeCase) as Snake<T>;
}

function renameKeys(value: unknown, rename: (key: string) => string): unknown {
  if (Array.isArray(value)) {
    return value.map((item) => renameKeys(item, rename));
  }
  if (value === null || typeof value !== "object") {
    return value;
  }
  const renamed: Record<string, unknown> = {};
  for (const [key, inner] of Object.entries(value)) {
    renamed[rename(key)] = OPAQUE_KEYS.has(key) ? inner : renameKeys(inner, rename);
  }
  return renamed;
}

function camelCase(key: string): string {
  return key.replace(/_([a-z0-9])/g, (_, letter: string) => letter.toUpperCase());
}

function snakeCase(key: string): string {
  return key.replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`);
}
