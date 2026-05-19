import "dotenv/config";

import { appendFile, mkdir, readFile, realpath, rm, stat, writeFile } from "node:fs/promises";
import path from "node:path";
import { AttachmentBuilder, Client, Events, GatewayIntentBits, Partials, ChannelType } from "discord.js";
import OpenAI from "openai";
import { createCodexBridge } from "./codexBridge.js";

const DISCORD_LIMIT = 2000;
const SAFE_REPLY_LIMIT = 1850;
const STREAMING_PLACEHOLDER = "Thinking...";
const STREAMING_SUFFIX = "\n\n...";
const DEFAULT_FILE_SEND_EXTENSIONS = [
  ".png",
  ".jpg",
  ".jpeg",
  ".webp",
  ".gif",
  ".pdf",
  ".txt",
  ".md",
  ".csv",
  ".docx",
  ".xlsx",
  ".pptx",
  ".zip",
];
const DEFAULT_FILE_SEND_COMMANDS = ["傳檔", "送檔", "附件", "file", "attach"];
const DEFAULT_FILE_SEND_MAX_BYTES = 8 * 1024 * 1024;
const DEFAULT_FILE_RECEIVE_EXTENSIONS = [
  ...DEFAULT_FILE_SEND_EXTENSIONS,
  ".json",
  ".mp3",
  ".wav",
  ".m4a",
  ".mp4",
  ".mov",
];
const DEFAULT_FILE_RECEIVE_MAX_BYTES = 50 * 1024 * 1024;
const DEFAULT_FILE_RECEIVE_MAX_FILES = 5;
const DEFAULT_FILE_RECEIVE_TIMEOUT_MS = 30 * 1000;
const SENSITIVE_PATH_WORDS = [
  ".env",
  "secret",
  "secrets",
  "token",
  "tokens",
  "credential",
  "credentials",
  "cookie",
  "cookies",
  "password",
  "passwd",
];

function parseIdList(value) {
  return new Set(
    (value ?? "")
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean),
  );
}

function parseStringList(value, fallback = []) {
  const parsed = (value ?? "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);

  return parsed.length > 0 ? parsed : [...fallback];
}

function parsePathList(value, fallback = []) {
  const parsed = (value ?? "")
    .split(path.delimiter)
    .map((item) => item.trim())
    .filter(Boolean);

  return parsed.length > 0 ? parsed : [...fallback];
}

function parseExtensionSet(value, fallback = DEFAULT_FILE_SEND_EXTENSIONS) {
  return new Set(
    parseStringList(value, fallback).map((extension) => {
      const normalized = extension.trim().toLowerCase();
      return normalized.startsWith(".") ? normalized : `.${normalized}`;
    }),
  );
}

function parseBoolean(value, fallback) {
  if (value == null || value === "") return fallback;
  return ["1", "true", "yes", "y", "on"].includes(value.toLowerCase());
}

function parsePositiveInteger(value, fallback) {
  const parsed = Number.parseInt(value ?? "", 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

function parseNonNegativeInteger(value, fallback) {
  const parsed = Number.parseInt(value ?? "", 10);
  return Number.isFinite(parsed) && parsed >= 0 ? parsed : fallback;
}

function requireEnv(name) {
  const value = process.env[name]?.trim();
  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value;
}

const defaultCodexWorkdir = process.env.CODEX_WORKDIR?.trim() || path.resolve(process.cwd(), "..");

const config = {
  discordToken: requireEnv("DISCORD_BOT_TOKEN"),
  allowedUserIds: parseIdList(requireEnv("ALLOWED_USER_IDS")),
  allowedChannelIds: parseIdList(process.env.ALLOWED_CHANNEL_IDS),
  allowDms: parseBoolean(process.env.ALLOW_DMS, true),
  model: process.env.OPENAI_MODEL?.trim() || "gpt-5.5",
  openaiStreaming: parseBoolean(process.env.OPENAI_STREAMING, true),
  openaiStreamEditIntervalMs: parsePositiveInteger(process.env.OPENAI_STREAM_EDIT_INTERVAL_MS, 1200),
  openaiMaxOutputTokens: parsePositiveInteger(process.env.OPENAI_MAX_OUTPUT_TOKENS, 1200),
  openaiFallbackToCodex: parseBoolean(process.env.OPENAI_FALLBACK_TO_CODEX, true),
  maxHistoryMessages: parsePositiveInteger(process.env.MAX_HISTORY_MESSAGES, 8),
  cooldownMs: parseNonNegativeInteger(process.env.COOLDOWN_MS, 0),
  debugSafeLog: parseBoolean(process.env.DEBUG_SAFE_LOG, true),
  codex: {
    enabled: parseBoolean(process.env.CODEX_ENABLED, true),
    trigger: process.env.CODEX_TRIGGER?.trim() || "!codex",
    command: process.env.CODEX_COMMAND?.trim() || "codex.cmd",
    model: process.env.CODEX_MODEL?.trim() || "gpt-5.5",
    workdir: defaultCodexWorkdir,
    sandbox: process.env.CODEX_SANDBOX?.trim() || "workspace-write",
    timeoutMs: parsePositiveInteger(process.env.CODEX_TIMEOUT_MS, 10 * 60 * 1000),
    maxOutputChars: parsePositiveInteger(process.env.CODEX_MAX_OUTPUT_CHARS, 6000),
    handleAllMessages: parseBoolean(process.env.CODEX_HANDLE_ALL_MESSAGES, false),
    triggerOnly: parseBoolean(process.env.CODEX_TRIGGER_ONLY, false),
    sessionMode: process.env.CODEX_SESSION_MODE?.trim() || "per-channel",
    sessionStorePath:
      process.env.CODEX_SESSION_STORE?.trim() || path.resolve(process.cwd(), "state", "codex-sessions.json"),
    resetCommand: process.env.CODEX_RESET_COMMAND?.trim() || "\u91cd\u7f6e\u8108\u7d61",
  },
  fileSend: {
    enabled: parseBoolean(process.env.FILE_SEND_ENABLED, true),
    commands: parseStringList(process.env.FILE_SEND_COMMANDS, DEFAULT_FILE_SEND_COMMANDS),
    allowedRoots: parsePathList(process.env.FILE_SEND_ALLOWED_ROOTS, [defaultCodexWorkdir]),
    maxBytes: parsePositiveInteger(process.env.FILE_SEND_MAX_BYTES, DEFAULT_FILE_SEND_MAX_BYTES),
    allowedExtensions: parseExtensionSet(process.env.FILE_SEND_ALLOWED_EXTENSIONS),
  },
  fileReceive: {
    enabled: parseBoolean(process.env.FILE_RECEIVE_ENABLED, true),
    downloadDir:
      process.env.FILE_RECEIVE_DIR?.trim() ||
      path.resolve(defaultCodexWorkdir, "discord-downloads"),
    maxBytes: parsePositiveInteger(process.env.FILE_RECEIVE_MAX_BYTES, DEFAULT_FILE_RECEIVE_MAX_BYTES),
    maxFiles: parsePositiveInteger(process.env.FILE_RECEIVE_MAX_FILES, DEFAULT_FILE_RECEIVE_MAX_FILES),
    timeoutMs: parsePositiveInteger(process.env.FILE_RECEIVE_TIMEOUT_MS, DEFAULT_FILE_RECEIVE_TIMEOUT_MS),
    allowedExtensions: parseExtensionSet(
      process.env.FILE_RECEIVE_ALLOWED_EXTENSIONS,
      DEFAULT_FILE_RECEIVE_EXTENSIONS,
    ),
  },
  transcript: {
    enabled: parseBoolean(process.env.TRANSCRIPT_ENABLED, true),
    path:
      process.env.TRANSCRIPT_PATH?.trim() ||
      path.resolve(process.cwd(), "transcripts", "discord-codex.md"),
    maxChars: parsePositiveInteger(process.env.TRANSCRIPT_MAX_CHARS, 200000),
    deleteCommand: process.env.TRANSCRIPT_DELETE_COMMAND?.trim() || "\u522a\u9664\u8a18\u61b6\u6a94",
    includeUsage: parseBoolean(process.env.TRANSCRIPT_INCLUDE_USAGE, true),
  },
  instructions:
    process.env.BOT_INSTRUCTIONS?.trim() ||
    "You are a helpful private Discord assistant. Reply in the same language as the user unless asked otherwise. Keep answers concise and practical.",
};

const openaiApiKey = process.env.OPENAI_API_KEY?.trim();
const openai = openaiApiKey ? new OpenAI({ apiKey: openaiApiKey }) : null;
let openaiDisabledByQuotaAt = null;

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.DirectMessages,
    GatewayIntentBits.MessageContent,
  ],
  partials: [Partials.Channel],
});

const histories = new Map();
const lastReplyByUser = new Map();
const pendingTranscriptDeletes = new Map();
const codexBridge = createCodexBridge(config.codex);
const codexQueue = [];
let isProcessingCodexQueue = false;

const TRANSCRIPT_DELETE_CONFIRMATION = "確認刪除記憶檔";
const TRANSCRIPT_DELETE_CANCEL_WORDS = new Set(["取消", "不是", "否", "不用", "不要"]);
const TRANSCRIPT_DELETE_CONFIRMATION_TTL_MS = 5 * 60 * 1000;

function logRuntimeError(event, error) {
  console.error(
    JSON.stringify({
      event,
      message: String(error?.message || error),
      stack: error?.stack || null,
    }),
  );
}

process.on("uncaughtException", (error) => {
  logRuntimeError("uncaughtException", error);
});

process.on("unhandledRejection", (error) => {
  logRuntimeError("unhandledRejection", error);
});

process.on("exit", (code) => {
  console.log(JSON.stringify({ event: "process_exit", code }));
});

function utcTimestamp() {
  return new Date().toISOString();
}

function formatTranscriptBlock(title, body) {
  return [
    "",
    `## ${utcTimestamp()} - ${title}`,
    "",
    "```text",
    body || "",
    "```",
    "",
  ].join("\n");
}

async function appendTranscript(title, body) {
  if (!config.transcript.enabled) return;

  const transcriptPath = path.resolve(config.transcript.path);
  await mkdir(path.dirname(transcriptPath), { recursive: true });
  await appendFile(transcriptPath, formatTranscriptBlock(title, body), "utf8");
}

async function getTranscriptStats() {
  if (!config.transcript.enabled) {
    return { chars: 0, percent: 0, exists: false };
  }

  try {
    const text = await readFile(path.resolve(config.transcript.path), "utf8");
    const chars = text.length;
    const percent = Math.min(100, Math.round((chars / config.transcript.maxChars) * 100));
    return { chars, percent, exists: true };
  } catch (error) {
    if (error.code === "ENOENT") {
      return { chars: 0, percent: 0, exists: false };
    }
    throw error;
  }
}

async function memoryUsageLine() {
  if (!config.transcript.includeUsage) return "";

  const stats = await getTranscriptStats();
  return `Memory file: ${stats.percent}% (${stats.chars}/${config.transcript.maxChars} chars).`;
}

async function withMemoryUsage(text) {
  const line = await memoryUsageLine();
  return line ? `${text}\n\n${line}` : text;
}

function normalizePathForCompare(filePath) {
  return process.platform === "win32" ? filePath.toLowerCase() : filePath;
}

function isPathInsideRoot(filePath, rootPath) {
  const normalizedFile = normalizePathForCompare(path.resolve(filePath));
  const normalizedRoot = normalizePathForCompare(path.resolve(rootPath));
  return normalizedFile === normalizedRoot || normalizedFile.startsWith(`${normalizedRoot}${path.sep}`);
}

function stripPathWrapping(value) {
  let text = value.trim();
  if (text.startsWith("<") && text.endsWith(">")) {
    text = text.slice(1, -1).trim();
  }
  if (
    (text.startsWith('"') && text.endsWith('"')) ||
    (text.startsWith("'") && text.endsWith("'")) ||
    (text.startsWith("`") && text.endsWith("`"))
  ) {
    text = text.slice(1, -1).trim();
  }
  return text;
}

function looksSensitiveFilePath(filePath) {
  const normalized = normalizePathForCompare(filePath);
  return SENSITIVE_PATH_WORDS.some((word) => normalized.includes(word));
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
}

function safeAttachmentName(name) {
  const rawName = path.basename(String(name || "attachment"));
  const cleaned = rawName
    .replace(/[<>:"/\\|?*\u0000-\u001f]/g, "_")
    .replace(/\s+/g, " ")
    .trim();
  const parsed = path.parse(cleaned || "attachment");
  const base = parsed.name.slice(0, 90).trim() || "attachment";
  const extension = parsed.ext.slice(0, 20);
  return `${base}${extension}`;
}

function isTrustedDiscordAttachmentUrl(rawUrl) {
  try {
    const parsed = new URL(rawUrl);
    const host = parsed.hostname.toLowerCase();
    return (
      parsed.protocol === "https:" &&
      (host === "cdn.discordapp.com" ||
        host === "media.discordapp.net" ||
        host === "discord.com" ||
        host.endsWith(".discordapp.com") ||
        host.endsWith(".discordapp.net"))
    );
  } catch {
    return false;
  }
}

async function getAttachmentDownloadDir() {
  const workdir = await realpath(path.resolve(config.codex.workdir));
  const downloadDir = path.resolve(config.fileReceive.downloadDir);

  await mkdir(downloadDir, { recursive: true });
  const resolvedDownloadDir = await realpath(downloadDir);

  if (!isPathInsideRoot(resolvedDownloadDir, workdir)) {
    throw new Error("Discord 附件下載目錄必須在 CODEX_WORKDIR 內。");
  }

  return resolvedDownloadDir;
}

async function downloadUrlToFile(url, destinationPath) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), config.fileReceive.timeoutMs);

  try {
    const response = await fetch(url, { signal: controller.signal });
    if (!response.ok) {
      throw new Error(`Discord CDN 回應 ${response.status}`);
    }

    const contentLength = Number.parseInt(response.headers.get("content-length") || "", 10);
    if (Number.isFinite(contentLength) && contentLength > config.fileReceive.maxBytes) {
      throw new Error(`附件太大：${formatBytes(contentLength)}`);
    }

    const buffer = Buffer.from(await response.arrayBuffer());
    if (buffer.byteLength > config.fileReceive.maxBytes) {
      throw new Error(`附件太大：${formatBytes(buffer.byteLength)}`);
    }

    await writeFile(destinationPath, buffer, { flag: "wx" });
    return buffer.byteLength;
  } finally {
    clearTimeout(timeout);
  }
}

async function downloadDiscordAttachment(message, attachment, index, downloadDir) {
  const originalName = attachment.name || `attachment-${attachment.id}`;
  const fileName = safeAttachmentName(originalName);
  const extension = path.extname(fileName).toLowerCase();

  if (looksSensitiveFilePath(fileName)) {
    throw new Error("檔名看起來可能包含秘密、token、cookie 或憑證，已阻擋。");
  }

  if (!extension || !config.fileReceive.allowedExtensions.has(extension)) {
    throw new Error(
      `這個附件副檔名不在允許清單：${extension || "(無副檔名)"}`,
    );
  }

  if (attachment.size > config.fileReceive.maxBytes) {
    throw new Error(`附件太大：${formatBytes(attachment.size)}`);
  }

  if (!isTrustedDiscordAttachmentUrl(attachment.url)) {
    throw new Error("附件 URL 不是可信的 Discord CDN 位址。");
  }

  const destinationPath = path.resolve(
    downloadDir,
    `${message.id}-${String(index + 1).padStart(2, "0")}-${fileName}`,
  );

  if (!isPathInsideRoot(destinationPath, downloadDir)) {
    throw new Error("附件儲存路徑超出下載目錄。");
  }

  const size = await downloadUrlToFile(attachment.url, destinationPath);
  return {
    originalName,
    path: destinationPath,
    name: path.basename(destinationPath),
    size,
    contentType: attachment.contentType || "unknown",
  };
}

async function downloadMessageAttachments(message) {
  const attachments = [...message.attachments.values()];
  if (attachments.length === 0) {
    return { downloaded: [], failed: [] };
  }

  if (!config.fileReceive.enabled) {
    return {
      downloaded: [],
      failed: attachments.map((attachment) => ({
        name: attachment.name || attachment.id,
        reason: "Discord 附件下載功能未啟用。",
      })),
    };
  }

  const downloaded = [];
  const failed = [];
  const selected = attachments.slice(0, config.fileReceive.maxFiles);
  let downloadDir = "";

  try {
    downloadDir = await getAttachmentDownloadDir();
  } catch (error) {
    return {
      downloaded,
      failed: attachments.map((attachment) => ({
        name: attachment.name || attachment.id,
        reason: String(error.message || error),
      })),
    };
  }

  for (const [index, attachment] of selected.entries()) {
    try {
      downloaded.push(await downloadDiscordAttachment(message, attachment, index, downloadDir));
    } catch (error) {
      failed.push({
        name: attachment.name || attachment.id,
        reason: String(error.message || error),
      });
    }
  }

  for (const attachment of attachments.slice(config.fileReceive.maxFiles)) {
    failed.push({
      name: attachment.name || attachment.id,
      reason: `超過單次上限 ${config.fileReceive.maxFiles} 個附件。`,
    });
  }

  return { downloaded, failed };
}

function buildUserRequestWithAttachments(userText, attachmentResult) {
  const parts = [];
  const trimmed = userText.trim();
  if (trimmed) {
    parts.push(trimmed);
  } else if (attachmentResult.downloaded.length > 0) {
    parts.push("請處理我剛上傳到 Discord 的附件。");
  }

  if (attachmentResult.downloaded.length > 0) {
    parts.push(
      [
        "Discord 附件已下載到本機：",
        ...attachmentResult.downloaded.map(
          (file) =>
            `- ${file.originalName} -> ${file.path} (${formatBytes(file.size)}, ${file.contentType})`,
        ),
      ].join("\n"),
    );
  }

  if (attachmentResult.failed.length > 0) {
    parts.push(
      [
        "Discord 附件下載失敗或已阻擋：",
        ...attachmentResult.failed.map((file) => `- ${file.name}: ${file.reason}`),
      ].join("\n"),
    );
  }

  return parts.join("\n\n").trim();
}

function getFileSendRequest(userText) {
  if (!config.fileSend.enabled) return null;

  const candidates = [userText.trim(), commandBody(userText)];
  for (const candidate of candidates) {
    for (const command of config.fileSend.commands) {
      const trimmedCommand = command.trim();
      if (!trimmedCommand) continue;
      if (candidate === trimmedCommand) return "";
      if (candidate.startsWith(`${trimmedCommand} `)) {
        return candidate.slice(trimmedCommand.length).trim();
      }
    }
  }

  return null;
}

async function resolveSendableFile(rawPath) {
  const cleaned = stripPathWrapping(rawPath);
  if (!cleaned) {
    throw new Error(`請在指令後面加檔案路徑，例如：${config.fileSend.commands[0]} 雷-設定圖.png`);
  }

  const candidate = path.isAbsolute(cleaned)
    ? path.resolve(cleaned)
    : path.resolve(config.codex.workdir, cleaned);
  const resolvedFile = await realpath(candidate);
  const fileStat = await stat(resolvedFile);

  if (!fileStat.isFile()) {
    throw new Error("這不是檔案，不能當附件送出。");
  }

  if (looksSensitiveFilePath(resolvedFile)) {
    throw new Error("這個路徑看起來可能包含秘密、token、cookie 或憑證，已阻擋。");
  }

  const extension = path.extname(resolvedFile).toLowerCase();
  if (!config.fileSend.allowedExtensions.has(extension)) {
    throw new Error(
      `這個副檔名不在允許清單：${extension || "(無副檔名)"}。允許：${[
        ...config.fileSend.allowedExtensions,
      ].join(", ")}`,
    );
  }

  if (fileStat.size > config.fileSend.maxBytes) {
    throw new Error(
      `檔案太大：${formatBytes(fileStat.size)}，目前上限是 ${formatBytes(config.fileSend.maxBytes)}。`,
    );
  }

  const allowedRootResults = await Promise.allSettled(
    config.fileSend.allowedRoots.map((root) => realpath(path.resolve(root))),
  );
  const allowedRoots = allowedRootResults
    .filter((result) => result.status === "fulfilled")
    .map((result) => result.value);

  if (!allowedRoots.some((root) => isPathInsideRoot(resolvedFile, root))) {
    throw new Error(
      `這個檔案不在允許的附件根目錄內。允許根目錄：${config.fileSend.allowedRoots.join("; ")}`,
    );
  }

  return {
    path: resolvedFile,
    name: path.basename(resolvedFile),
    size: fileStat.size,
  };
}

function extractAttachmentDirectives(text) {
  const attachmentPaths = [];
  const lines = [];

  for (const line of String(text || "").split(/\r?\n/)) {
    const match = /^\s*ATTACH_FILE\s*:\s*(.+?)\s*$/.exec(line);
    if (match) {
      attachmentPaths.push(match[1].trim());
    } else {
      lines.push(line);
    }
  }

  return {
    text: lines.join("\n").trim(),
    attachmentPaths,
  };
}

async function sendFileToChannel(channel, rawPath) {
  const file = await resolveSendableFile(rawPath);
  await channel.send({
    content: await withMemoryUsage(`已附上：${file.name} (${formatBytes(file.size)})`),
    files: [new AttachmentBuilder(file.path, { name: file.name })],
  });
}

async function sendFileReply(message, rawPath) {
  try {
    const file = await resolveSendableFile(rawPath);
    await message.reply({
      content: await withMemoryUsage(`已附上：${file.name} (${formatBytes(file.size)})`),
      files: [new AttachmentBuilder(file.path, { name: file.name })],
    });
  } catch (error) {
    await sendLongReply(message, `無法送出附件：${String(error.message || error)}`);
  }
}

function commandBody(userText) {
  const text = userText.trim();
  const trigger = config.codex.trigger;

  if (!trigger) return text;
  if (text === trigger) return "";
  if (text.startsWith(`${trigger} `)) return text.slice(trigger.length).trim();
  return text;
}

function normalizeCommand(text) {
  return text.trim().replace(/\s+/g, " ").toLowerCase();
}

function compactCommand(text) {
  return normalizeCommand(text).replace(/\s+/g, "");
}

function isTranscriptDeleteConfirmation(userText) {
  const compact = compactCommand(commandBody(userText));
  return new Set([
    compactCommand(TRANSCRIPT_DELETE_CONFIRMATION),
    compactCommand("確認清空記憶檔"),
    compactCommand("確認刪除 memory file"),
    compactCommand("確認清空 memory file"),
  ]).has(compact);
}

function isTranscriptDeleteCancellation(userText) {
  const compact = compactCommand(commandBody(userText));
  return TRANSCRIPT_DELETE_CANCEL_WORDS.has(compact);
}

function isTranscriptDeleteCommand(userText) {
  const body = commandBody(userText);
  const normalized = normalizeCommand(body);
  const compact = compactCommand(body);
  const deleteCommand = config.transcript.deleteCommand;

  const normalizedAliases = new Set([
    normalizeCommand(deleteCommand),
    "delete memory file",
    "clear memory file",
  ]);

  const compactAliases = new Set([
    compactCommand(deleteCommand),
    compactCommand("清空記憶檔"),
    compactCommand("清除記憶檔"),
    compactCommand("刪除 memory file"),
    compactCommand("清空 memory file"),
    compactCommand("清除 memory file"),
  ]);

  return normalizedAliases.has(normalized) || compactAliases.has(compact);
}

function mentionsDeleteLikeAction(userText) {
  const body = commandBody(userText);
  const normalized = normalizeCommand(body);

  return [
    /刪|删|刪檔|删档|刪掉|删掉|清空|清除|清掉|移除|砍掉/u,
    /\b(delete|clear|remove|erase|wipe|truncate|rm|del)\b/i,
    /\b(remove-item|clear-content)\b/i,
  ].some((pattern) => pattern.test(normalized));
}

function transcriptDeleteConfirmationKey(message) {
  return `${message.author.id}:${message.channelId}`;
}

function getPendingTranscriptDelete(message) {
  const key = transcriptDeleteConfirmationKey(message);
  const pending = pendingTranscriptDeletes.get(key);
  if (!pending) return null;

  if (Date.now() - pending.createdAt > TRANSCRIPT_DELETE_CONFIRMATION_TTL_MS) {
    pendingTranscriptDeletes.delete(key);
    return null;
  }

  return pending;
}

async function askTranscriptDeleteConfirmation(message) {
  const key = transcriptDeleteConfirmationKey(message);
  pendingTranscriptDeletes.set(key, { createdAt: Date.now() });

  await sendLongReply(
    message,
    [
      "我看到你提到刪除/清空相關字眼，先停一下。",
      "",
      "你是不是要刪下面那個 `Memory file: x%`，也就是 Discord transcript？",
      "",
      `目標檔案：${config.transcript.path}`,
      "",
      `如果是，請回：${TRANSCRIPT_DELETE_CONFIRMATION}`,
      "如果不是，請回：取消",
      "",
      "目前不會刪任何檔案。",
    ].join("\n"),
  );
}

async function confirmTranscriptDelete(message) {
  const pending = getPendingTranscriptDelete(message);
  if (!pending) {
    await sendLongReply(
      message,
      [
        "目前沒有等待確認的刪除動作。",
        "",
        "如果你要刪 `Memory file: x%` 那個 transcript，請先傳 `刪除記憶檔`，我會再問一次確認。",
      ].join("\n"),
    );
    return;
  }

  pendingTranscriptDeletes.delete(transcriptDeleteConfirmationKey(message));
  const reset = await resetCurrentCodexSession(message);
  await deleteTranscriptFile();
  await sendLongReply(
    message,
    reset
      ? `Transcript memory file deleted: ${config.transcript.path}\n\nIn-memory fallback history and this channel's Codex context were also cleared. I did not touch C:\\Users\\User\\.codex\\memories.`
      : `Transcript memory file deleted: ${config.transcript.path}\n\nIn-memory fallback history was also cleared. I did not touch C:\\Users\\User\\.codex\\memories.`,
  );
}

async function cancelTranscriptDelete(message) {
  const key = transcriptDeleteConfirmationKey(message);
  const existed = pendingTranscriptDeletes.delete(key);
  if (existed) {
    await sendLongReply(message, "已取消。沒有刪任何檔案。");
  }
}

async function deleteTranscriptFile() {
  await rm(path.resolve(config.transcript.path), { force: true });
  histories.clear();
}

async function resetCurrentCodexSession(message) {
  const sessionKey = sessionKeyForMessage(message);
  if (!sessionKey) return false;
  return await codexBridge.resetSession(sessionKey);
}

function safeLog(message, reason, extra = {}) {
  if (!config.debugSafeLog) return;
  console.log(
    JSON.stringify({
      event: "message_check",
      reason,
      authorId: message.author?.id,
      channelId: message.channelId,
      parentId: message.channel?.parentId ?? null,
      guildId: message.guildId ?? null,
      channelType: message.channel?.type,
      contentLength: message.content?.length ?? 0,
      ...extra,
    }),
  );
}

function allowedChannelMatches(message) {
  if (message.channel.type === ChannelType.DM) {
    return config.allowDms;
  }

  return (
    config.allowedChannelIds.has(message.channelId) ||
    (message.channel.parentId && config.allowedChannelIds.has(message.channel.parentId))
  );
}

function canUseBot(message) {
  if (message.author.bot) {
    safeLog(message, "ignored_bot_author");
    return false;
  }

  if (!config.allowedUserIds.has(message.author.id)) {
    safeLog(message, "ignored_user_not_allowed");
    return false;
  }

  if (!allowedChannelMatches(message)) {
    safeLog(message, "ignored_channel_not_allowed");
    return false;
  }

  safeLog(message, "accepted");
  return true;
}

function isCoolingDown(userId) {
  if (config.cooldownMs <= 0) return false;

  const now = Date.now();
  const previous = lastReplyByUser.get(userId) ?? 0;
  if (now - previous < config.cooldownMs) {
    console.log(JSON.stringify({ event: "cooldown", userId }));
    return true;
  }
  lastReplyByUser.set(userId, now);
  return false;
}

function historyKey(message) {
  return `${message.author.id}:${message.channelId}`;
}

function sessionKeyForMessage(message) {
  const mode = config.codex.sessionMode.toLowerCase();
  if (["0", "false", "off", "none", "disabled"].includes(mode)) return null;

  if (message.guildId) {
    return `guild:${message.guildId}:channel:${message.channelId}`;
  }

  return `dm:${message.author.id}:channel:${message.channelId}`;
}

function getHistory(message) {
  return histories.get(historyKey(message)) ?? [];
}

function saveTurn(message, userText, assistantText) {
  const key = historyKey(message);
  const nextHistory = [
    ...getHistory(message),
    { role: "user", content: userText },
    { role: "assistant", content: assistantText },
  ].slice(-config.maxHistoryMessages);

  histories.set(key, nextHistory);
}

function splitDiscordMessage(text) {
  if (text.length <= DISCORD_LIMIT) return [text];

  const chunks = [];
  let remaining = text;

  while (remaining.length > SAFE_REPLY_LIMIT) {
    const window = remaining.slice(0, SAFE_REPLY_LIMIT);
    const breakAt = Math.max(window.lastIndexOf("\n"), window.lastIndexOf(" "));
    const index = breakAt > 500 ? breakAt : SAFE_REPLY_LIMIT;

    chunks.push(remaining.slice(0, index).trim());
    remaining = remaining.slice(index).trim();
  }

  if (remaining) chunks.push(remaining);
  return chunks;
}

function isOpenAIQuotaError(error) {
  const code = String(error?.code || error?.error?.code || "").toLowerCase();
  const type = String(error?.type || error?.error?.type || "").toLowerCase();
  const message = String(error?.message || error?.error?.message || error || "");
  const lowerMessage = message.toLowerCase();

  return code === "insufficient_quota" || type === "insufficient_quota" || lowerMessage.includes("quota");
}

function classifyOpenAIError(error) {
  const code = String(error?.code || error?.error?.code || "").toLowerCase();
  const message = String(error?.message || error?.error?.message || error || "");
  const lowerMessage = message.toLowerCase();

  if (isOpenAIQuotaError(error)) {
    return "OpenAI API quota is exhausted or billing is not available.";
  }

  if (code.includes("invalid") && code.includes("key")) {
    return "OpenAI API key is invalid.";
  }

  if (lowerMessage.includes("rate limit") || code.includes("rate_limit")) {
    return "OpenAI API is rate limiting this bot right now.";
  }

  return `OpenAI API failed: ${message.slice(0, 500)}`;
}

function activateCodexTriggerModeForQuota() {
  if (openaiDisabledByQuotaAt) return;

  openaiDisabledByQuotaAt = new Date();
  console.warn(
    JSON.stringify({
      event: "openai_quota_disabled",
      mode: "codex_trigger",
      trigger: config.codex.trigger,
      disabledAt: openaiDisabledByQuotaAt.toISOString(),
    }),
  );
}

async function replyOpenAIQuotaDisabled(message) {
  await sendLongReply(
    message,
    `OpenAI API quota is exhausted, so OpenAI fallback is paused. This bot is now in \`${config.codex.trigger}\` local mode; send \`${config.codex.trigger} ...\` to run local Codex.`,
  );
}

function buildStreamingPreview(text) {
  const body = text.trim() ? text : STREAMING_PLACEHOLDER;
  const budget = SAFE_REPLY_LIMIT - STREAMING_SUFFIX.length;
  return `${body.slice(0, budget).trimEnd()}${STREAMING_SUFFIX}`;
}

async function sendLongReply(message, text) {
  const extracted = extractAttachmentDirectives(text || "I could not generate a response.");
  const replyText = await withMemoryUsage(extracted.text || "I could not generate a response.");
  const chunks = splitDiscordMessage(replyText);
  await message.reply(chunks[0]);

  for (const chunk of chunks.slice(1)) {
    await message.channel.send(chunk);
  }

  for (const attachmentPath of extracted.attachmentPaths) {
    try {
      await sendFileToChannel(message.channel, attachmentPath);
    } catch (error) {
      await message.channel.send(`附件送出失敗：${String(error.message || error).slice(0, 1500)}`);
    }
  }
}

async function editOrSendLongReply(replyMessage, text) {
  const extracted = extractAttachmentDirectives(text || "Codex finished without a final message.");
  const replyText = await withMemoryUsage(extracted.text || "Codex finished without a final message.");
  const chunks = splitDiscordMessage(replyText);
  await replyMessage.edit(chunks[0]);

  for (const chunk of chunks.slice(1)) {
    await replyMessage.channel.send(chunk);
  }

  for (const attachmentPath of extracted.attachmentPaths) {
    try {
      await sendFileToChannel(replyMessage.channel, attachmentPath);
    } catch (error) {
      await replyMessage.channel.send(`附件送出失敗：${String(error.message || error).slice(0, 1500)}`);
    }
  }
}

async function withTyping(channel, fn) {
  await channel.sendTyping();
  const interval = setInterval(() => {
    channel.sendTyping().catch(() => {});
  }, 9000);

  try {
    return await fn();
  } finally {
    clearInterval(interval);
  }
}

async function askOpenAI(message, userText) {
  if (!openai) {
    throw new Error("OPENAI_API_KEY is not configured. Enable CODEX_HANDLE_ALL_MESSAGES or set an API key.");
  }

  const input = [
    ...getHistory(message),
    { role: "user", content: userText },
  ];

  const response = await openai.responses.create({
    model: config.model,
    instructions: config.instructions,
    input,
    max_output_tokens: config.openaiMaxOutputTokens,
    store: false,
  });

  return response.output_text?.trim() || "";
}

async function fallbackToCodexAfterOpenAIError(message, userText, error, existingAck = null) {
  const reason = classifyOpenAIError(error);
  const quotaExhausted = isOpenAIQuotaError(error);
  console.error(error);

  if (quotaExhausted) {
    activateCodexTriggerModeForQuota();
  }

  if (!config.openaiFallbackToCodex) {
    const text = quotaExhausted
      ? `${reason}\n\nSwitched to \`${config.codex.trigger}\` local mode. Send \`${config.codex.trigger} ...\` to run local Codex.`
      : `${reason}\n\nUse \`${config.codex.trigger} ${userText}\` for local Codex, or update the OpenAI API billing/key.`;
    if (existingAck) {
      await editOrSendLongReply(existingAck, text);
      return;
    }
    await sendLongReply(message, text);
    return;
  }

  await askLocalCodex(message, userText, {
    existingAck,
    prefix: quotaExhausted
      ? `${reason}\nSwitched to \`${config.codex.trigger}\` local mode. Routing this request to local Codex.`
      : `${reason}\nFalling back to local Codex for this request.`,
  });
}

async function askOpenAIStreamed(message, userText) {
  if (!openai) {
    throw new Error("OPENAI_API_KEY is not configured. Enable CODEX_HANDLE_ALL_MESSAGES or set an API key.");
  }

  const input = [
    ...getHistory(message),
    { role: "user", content: userText },
  ];

  const ack = await message.reply(STREAMING_PLACEHOLDER);
  let answer = "";
  let lastEditAt = 0;
  let lastPreview = "";

  async function editPreview(force = false) {
    const now = Date.now();
    if (!force && now - lastEditAt < config.openaiStreamEditIntervalMs) return;

    const preview = buildStreamingPreview(answer);
    if (preview === lastPreview) return;

    lastEditAt = now;
    lastPreview = preview;
    await ack.edit(preview);
  }

  try {
    await withTyping(message.channel, async () => {
      const stream = await openai.responses.create({
        model: config.model,
        instructions: config.instructions,
        input,
        max_output_tokens: config.openaiMaxOutputTokens,
        store: false,
        stream: true,
      });

      for await (const event of stream) {
        if (event.type === "response.output_text.delta") {
          answer += event.delta;
          await editPreview(false);
          continue;
        }

        if (event.type === "response.completed" && !answer.trim() && event.response?.output_text) {
          answer = event.response.output_text;
          continue;
        }

        if (event.type === "response.failed") {
          throw new Error(event.response?.error?.message || "OpenAI response failed.");
        }

        if (event.type === "error") {
          throw new Error(event.message || "OpenAI streaming error.");
        }
      }
    });
  } catch (error) {
    await fallbackToCodexAfterOpenAIError(message, userText, error, ack);
    return;
  }

  answer = answer.trim();
  saveTurn(message, userText, answer);
  await editOrSendLongReply(ack, answer);
}

function getCodexRequest(userText) {
  const trigger = config.codex.trigger;
  if (!trigger) return null;

  if (userText === trigger) return "";
  if (userText.startsWith(`${trigger} `)) return userText.slice(trigger.length).trim();
  return null;
}

async function askLocalCodex(message, userRequest, options = {}) {
  if (!userRequest) {
    await sendLongReply(message, `Add a request after \`${config.codex.trigger}\`.`);
    return;
  }

  const sessionKey = sessionKeyForMessage(message);
  const position = codexQueue.length + (isProcessingCodexQueue ? 1 : 0) + 1;
  const ackText =
    position > 1
      ? `Queued for local Codex. Position: ${position}.`
      : "Queued for local Codex in this channel context. I will edit this message when it finishes.";
  const queueText = options.prefix ? `${options.prefix}\n\n${ackText}` : ackText;

  await appendTranscript(
    "Queued Discord Request",
    [
      `authorId: ${message.author.id}`,
      `guildId: ${message.guildId ?? "DM"}`,
      `channelId: ${message.channelId}`,
      `sessionKey: ${sessionKey ?? "none"}`,
      `queuePosition: ${position}`,
      "",
      userRequest,
    ].join("\n"),
  );

  let ack = options.existingAck;
  if (ack) {
    await ack.edit(await withMemoryUsage(queueText));
  } else {
    ack = await message.reply(await withMemoryUsage(queueText));
  }

  codexQueue.push({
    ack,
    message,
    sessionKey,
    userRequest,
  });

  drainCodexQueue().catch((error) => {
    console.error(error);
  });
}

async function drainCodexQueue() {
  if (isProcessingCodexQueue) return;
  isProcessingCodexQueue = true;

  try {
    while (codexQueue.length > 0) {
      const task = codexQueue.shift();

      try {
        await task.ack.edit(await withMemoryUsage("Local Codex is running this task now."));
        await appendTranscript(
          "Running Discord Request",
          [
            `authorId: ${task.message.author.id}`,
            `guildId: ${task.message.guildId ?? "DM"}`,
            `channelId: ${task.message.channelId}`,
            `sessionKey: ${task.sessionKey ?? "none"}`,
            "",
            task.userRequest,
          ].join("\n"),
        );

        const result = await withTyping(task.message.channel, () =>
          codexBridge.run(task.userRequest, {
            authorId: task.message.author.id,
            guildId: task.message.guildId ?? null,
            channelId: task.message.channelId,
            sessionKey: task.sessionKey,
          }),
        );

        await appendTranscript(
          "Finished Codex Result",
          [
            `authorId: ${task.message.author.id}`,
            `guildId: ${task.message.guildId ?? "DM"}`,
            `channelId: ${task.message.channelId}`,
            `sessionKey: ${task.sessionKey ?? "none"}`,
            `codexThreadId: ${result.threadId ?? "none"}`,
            `resumed: ${result.resumed}`,
            "",
            result.finalText,
          ].join("\n"),
        );
        await editOrSendLongReply(task.ack, result.finalText);
      } catch (error) {
        console.error(error);
        await appendTranscript(
          "Failed Codex Result",
          [
            `authorId: ${task.message.author.id}`,
            `guildId: ${task.message.guildId ?? "DM"}`,
            `channelId: ${task.message.channelId}`,
            `sessionKey: ${task.sessionKey ?? "none"}`,
            "",
            String(error.message || error),
          ].join("\n"),
        );
        await editOrSendLongReply(
          task.ack,
          `Local Codex failed: ${String(error.message || error).slice(0, 1500)}`,
        );
      }
    }
  } finally {
    isProcessingCodexQueue = false;
  }
}

client.once(Events.ClientReady, (readyClient) => {
  const channelText =
    config.allowedChannelIds.size > 0
      ? [...config.allowedChannelIds].join(", ")
      : "DMs only";

  console.log(`Logged in as ${readyClient.user.tag}`);
  console.log(`Allowed users: ${[...config.allowedUserIds].join(", ")}`);
  console.log(`Allowed channels: ${channelText}`);
  console.log(`OpenAI fallback model: ${config.model}`);
  console.log(`OpenAI fallback configured: ${Boolean(openai)}`);
  console.log(`OpenAI streaming: ${config.openaiStreaming}`);
  console.log(`OpenAI fallback to Codex: ${config.openaiFallbackToCodex}`);
  console.log(`OpenAI max output tokens: ${config.openaiMaxOutputTokens}`);
  console.log(
    `Codex bridge: ${config.codex.enabled ? "enabled" : "disabled"} (${config.codex.trigger}, ${config.codex.model})`,
  );
  console.log(`Codex handles all messages: ${config.codex.handleAllMessages}`);
  console.log(`Codex trigger-only mode: ${config.codex.triggerOnly}`);
  console.log(`Codex workdir: ${config.codex.workdir}`);
  console.log(`Codex sandbox: ${config.codex.sandbox}`);
  console.log(`Codex session mode: ${config.codex.sessionMode}`);
  console.log(`Codex session store: ${config.codex.sessionStorePath}`);
  console.log(`Codex reset command: ${config.codex.resetCommand}`);
  console.log(`File send: ${config.fileSend.enabled ? "enabled" : "disabled"}`);
  console.log(`File send commands: ${config.fileSend.commands.join(", ")}`);
  console.log(`File send allowed roots: ${config.fileSend.allowedRoots.join("; ")}`);
  console.log(`File send max bytes: ${config.fileSend.maxBytes}`);
  console.log(`File receive: ${config.fileReceive.enabled ? "enabled" : "disabled"}`);
  console.log(`File receive dir: ${config.fileReceive.downloadDir}`);
  console.log(`File receive max bytes: ${config.fileReceive.maxBytes}`);
  console.log(`File receive max files: ${config.fileReceive.maxFiles}`);
  console.log(`Transcript: ${config.transcript.enabled ? config.transcript.path : "disabled"}`);
  console.log(`Transcript max chars: ${config.transcript.maxChars}`);
  console.log(`Transcript delete command: ${config.transcript.deleteCommand}`);
});

client.on(Events.Error, (error) => {
  logRuntimeError("discord_client_error", error);
});

client.on(Events.Warn, (warning) => {
  console.warn(JSON.stringify({ event: "discord_client_warn", message: warning }));
});

client.on(Events.ShardError, (error, shardId) => {
  logRuntimeError(`discord_shard_error_${shardId}`, error);
});

client.on(Events.ShardDisconnect, (event, shardId) => {
  console.warn(
    JSON.stringify({
      event: "discord_shard_disconnect",
      shardId,
      code: event?.code,
      reason: event?.reason,
    }),
  );
});

client.on(Events.MessageCreate, async (message) => {
  try {
    if (!canUseBot(message)) return;
    if (isCoolingDown(message.author.id)) return;

    const userText = message.content.trim();
    if (!userText && message.attachments.size === 0) {
      await message
        .reply(await withMemoryUsage(
          "I received the Discord event, but the message content is empty. Check Message Content Intent and channel permissions.",
        ))
        .catch(() => {});
      return;
    }

    if (isTranscriptDeleteConfirmation(userText)) {
      await confirmTranscriptDelete(message);
      return;
    }

    if (isTranscriptDeleteCancellation(userText)) {
      await cancelTranscriptDelete(message);
      return;
    }

    const fileSendRequest = getFileSendRequest(userText);
    if (fileSendRequest !== null && message.attachments.size === 0) {
      await sendFileReply(message, fileSendRequest);
      return;
    }

    if (isTranscriptDeleteCommand(userText) || mentionsDeleteLikeAction(userText)) {
      await askTranscriptDeleteConfirmation(message);
      return;
    }

    if (userText === config.codex.resetCommand) {
      const reset = await resetCurrentCodexSession(message);
      await appendTranscript(
        "Reset Codex Session",
        [
          `authorId: ${message.author.id}`,
          `guildId: ${message.guildId ?? "DM"}`,
          `channelId: ${message.channelId}`,
          `sessionKey: ${sessionKeyForMessage(message) ?? "none"}`,
          `hadSession: ${reset}`,
        ].join("\n"),
      );
      await sendLongReply(
        message,
        reset
          ? "Current channel Codex context reset. The next message will start a fresh local Codex thread."
          : "This channel had no stored Codex context yet.",
      );
      return;
    }

    const codexRequest = getCodexRequest(userText);
    if (codexRequest !== null) {
      const attachmentResult = await downloadMessageAttachments(message);
      const userRequest = buildUserRequestWithAttachments(codexRequest, attachmentResult);
      await askLocalCodex(message, userRequest);
      return;
    }

    if (config.codex.handleAllMessages) {
      const attachmentResult = await downloadMessageAttachments(message);
      const userRequest = buildUserRequestWithAttachments(userText, attachmentResult);
      if (!userText && attachmentResult.downloaded.length === 0 && attachmentResult.failed.length > 0) {
        await sendLongReply(message, userRequest);
        return;
      }
      await askLocalCodex(message, userRequest);
      return;
    }

    if (message.attachments.size > 0 && config.codex.enabled) {
      const attachmentResult = await downloadMessageAttachments(message);
      const userRequest = buildUserRequestWithAttachments(userText, attachmentResult);
      if (!userText && attachmentResult.downloaded.length === 0 && attachmentResult.failed.length > 0) {
        await sendLongReply(message, userRequest);
        return;
      }
      await askLocalCodex(message, userRequest);
      return;
    }

    if (config.codex.triggerOnly) {
      await sendLongReply(
        message,
        `目前是 \`${config.codex.trigger}\` 模式。請用 \`${config.codex.trigger} 你的需求\` 來呼叫本機 Codex。`,
      );
      return;
    }

    if (openaiDisabledByQuotaAt) {
      await replyOpenAIQuotaDisabled(message);
      return;
    }

    if (config.openaiStreaming) {
      await askOpenAIStreamed(message, userText);
      return;
    }

    try {
      const answer = await withTyping(message.channel, () => askOpenAI(message, userText));
      saveTurn(message, userText, answer);
      await sendLongReply(message, answer);
    } catch (error) {
      await fallbackToCodexAfterOpenAIError(message, userText, error);
    }
  } catch (error) {
    console.error(error);
    await message.reply("Bot error. Check the terminal logs.").catch(() => {});
  }
});

client.login(config.discordToken);
