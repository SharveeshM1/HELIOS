"use client";

import { ChangeEvent, CSSProperties, DragEvent, KeyboardEvent, useEffect, useMemo, useRef, useState } from "react";

type ModuleKey =
  | "dashboard"
  | "research"
  | "code"
  | "analytics"
  | "voice"
  | "collab"
  | "swarm"
  | "loop"
  | "planning"
  | "reasoning"
  | "workflow"
  | "knowledge";

type Role = "user" | "assistant";
type ConversationMode = "balanced" | "concise" | "deep" | "execute";

type ConversationModeConfig = {
  id: ConversationMode;
  label: string;
  description: string;
  directive: string;
  response_length: string;
  reasoning_depth: string;
  tool_posture: string;
};

type Attachment = {
  id: number;
  name: string;
  size: string;
  type: string;
  content?: string;
  status?: string;
};

type KnowledgeSource = {
  id: string | number;
  name: string;
  size: string;
  type: string;
  status?: string;
  scope?: string;
  content?: string;
};

type Message = {
  id: number;
  role: Role;
  text: string;
  attachments?: Attachment[];
};

type IconName = "brain" | "command" | "deploy" | "focus" | "theme" | "close" | "upload" | "search" | "user";

type RuntimeState = "checking" | "online" | "degraded" | "offline";

type RunLedgerStatus = "connecting" | "live" | "offline" | "error";

type RunLedgerEvent = {
  id: string;
  label: string;
  actor?: string;
  module?: string;
  tool?: string;
  status?: string;
  detail?: string;
  error?: string;
  input?: unknown;
  result?: unknown;
  parent_id?: string;
  metadata?: Record<string, unknown>;
  timestamp?: string;
  duration_ms?: number;
  attempt?: number;
};

type VoiceState = "idle" | "connecting" | "listening" | "speaking" | "error";

type VoiceTurn = {
  id: number;
  role: "you" | "helios" | "system";
  text: string;
};

type CognitiveTrace = {
  stage: string;
  actor: string;
  payload?: Record<string, unknown>;
  timestamp?: string;
};

type PlanStep = {
  agent?: string;
  objective?: string;
};

type HealthStatus = {
  backend?: string;
  ai?: {
    status?: string;
    provider?: string;
    model?: string;
    model_available?: boolean;
    available_models?: string[];
    providers?: Record<string, {
      status?: string;
      model?: string;
      model_available?: boolean;
      available_models?: string[];
      error?: string;
    }>;
    error?: string;
  };
  cognitive_engine?: {
    status?: string;
    plan?: PlanStep[];
    trace?: CognitiveTrace[];
    memory?: {
      total_conversations?: number;
      storage_usage_percent?: number;
      max_capacity?: number;
      total_characters?: number;
    };
  };
  sources?: {
    total_sources?: number;
    indexed_sources?: number;
    pending_sources?: number;
  };
  missions?: {
    total_events?: number;
    active_events?: number;
    agents?: AgentActivityMap;
  };
  execution?: {
    total_events?: number;
    tool_events?: number;
    successful_tools?: number;
    failed_tools?: number;
    blocked_tools?: number;
  };
  security?: {
    api_key_required?: boolean;
    token_auth_enabled?: boolean;
    rate_limit_per_minute?: number;
  };
};

type AuthUser = {
  id?: string;
  sub?: string;
  username: string;
  role: "viewer" | "operator" | "admin" | string;
  active?: boolean;
};

type AuthSession = {
  token: string;
  user: AuthUser;
};

type ChatResult = {
  response?: string;
  module?: string;
  agent?: string;
  mode?: ConversationMode;
  trace?: CognitiveTrace[];
  plan?: PlanStep[];
  grounded?: boolean;
  enforcement?: GroundingEnforcement;
};

type GroundingEnforcement = {
  policy?: string;
  grounded?: boolean;
  enforced?: boolean;
  coverage_ratio?: number;
  minimum_coverage_ratio?: number;
  unsupported_terms?: string[];
};

type SourcesResult = {
  sources?: KnowledgeSource[];
  stats?: {
    total_sources?: number;
    indexed_sources?: number;
    pending_sources?: number;
  };
};

type GraphNode = {
  id?: string;
  label?: string;
  kind?: string;
  weight?: number;
  detail?: string;
  confidence?: number;
};

type GraphLink = {
  from?: string;
  to?: string;
  label?: string;
  terms?: string[];
};

type SourceIntelligenceResult = {
  query?: string;
  sources?: KnowledgeSource[];
  citations?: Array<{
    id?: string;
    name?: string;
    scope?: string;
    snippet?: string;
    match_terms?: string[];
    confidence?: number;
  }>;
  claims?: Array<{
    claim?: string;
    citations?: string[];
    source?: string;
  }>;
  grounded_answer?: string;
  coverage?: {
    query_terms?: string[];
    matched_terms?: string[];
    unmatched_terms?: string[];
    citation_count?: number;
    grounded?: boolean;
    enforced?: boolean;
    coverage_ratio?: number;
    answer_policy?: string;
    minimum_coverage_ratio?: number;
  };
  enforcement?: GroundingEnforcement;
  graph?: {
    nodes?: GraphNode[];
    links?: GraphLink[];
  };
};

type ProjectBrainResult = {
  nodes?: GraphNode[];
  links?: GraphLink[];
  stats?: Record<string, unknown>;
  summary?: {
    total_nodes?: number;
    total_links?: number;
    health?: string;
  };
};

type ObservabilityResult = {
  stats?: Record<string, number>;
  window?: {
    events_analyzed?: number;
    completed_events?: number;
  };
  rates?: {
    failure_rate?: number;
    average_duration_ms?: number;
    max_duration_ms?: number;
  };
  latency_percentiles?: {
    p50_ms?: number;
    p95_ms?: number;
    p99_ms?: number;
  };
  traces?: Array<{
    trace_id?: string;
    events?: number;
    failed?: number;
    duration_ms?: number;
    tools?: string[];
  }>;
  tool_counts?: Record<string, number>;
  status_counts?: Record<string, number>;
  slow_tools?: Array<{
    tool?: string;
    average_duration_ms?: number;
    max_duration_ms?: number;
    samples?: number;
  }>;
  recent_failures?: RunLedgerEvent[];
  recommendations?: string[];
};

type VoiceStatusResult = {
  realtime_available?: boolean;
  openai_key_configured?: boolean;
  model?: string;
  voice?: string;
  status?: string;
};

type AutonomousRun = {
  id: string;
  objective: string;
  status: string;
  plan?: {
    primary_route?: string;
    tasks?: Array<{
      agent?: string;
      route?: string;
      objective?: string;
      priority?: number;
    }>;
  };
  steps?: Array<{
    agent?: string;
    route?: string;
    status?: string;
    output?: unknown;
  }>;
  synthesis?: {
    summary?: string;
    completed_routes?: string[];
  };
  execution_contract?: {
    mode?: string;
    independent_worker_steps?: boolean;
    long_running?: boolean;
    cancel_supported?: boolean;
    resume_supported?: boolean;
    max_rounds?: number;
    approval_gates?: string[];
  };
  worker_jobs?: Array<{
    id?: string;
    kind?: string;
    status?: string;
    attempts?: number;
  }>;
  events?: Array<{
    id?: string;
    stage?: string;
    status?: string;
    detail?: string;
    timestamp?: string;
  }>;
  updated_at?: string;
};

type PluginRecord = {
  name: string;
  filename: string;
  version?: string;
  description?: string;
  isolation?: string;
  signature_type?: string;
  verified?: boolean;
};

type IsolatedSwarmRun = {
  id: string;
  objective: string;
  status: string;
  round?: number;
  debate_protocol?: {
    mode?: string;
    independent_agents?: string[];
    rounds?: string[];
    consensus_required?: boolean;
  };
  debate_state?: {
    phase?: string;
    completed_rounds?: number;
  };
  consensus?: MissionArtifact["consensus"];
  assignments?: MissionArtifact["assignments"];
};

type GitDiffResult = {
  status?: string;
  staged?: boolean;
  path?: string | null;
  diff?: string;
};

type MissionEvent = {
  id: string;
  stage: "Created" | "Assigned" | "Executed" | "Reviewed" | "Archived" | string;
  title: string;
  agent?: string;
  module?: string;
  status?: string;
  detail?: string;
  artifact?: MissionArtifact;
  timestamp?: string;
};

type AgentActivity = {
  state?: string;
  module?: string;
  last_event?: string | null;
  updated_at?: string;
};

type AgentActivityMap = Record<string, AgentActivity>;

type MissionEventsResult = {
  events?: MissionEvent[];
  missions?: MissionSummary[];
  stats?: {
    total_events?: number;
    active_events?: number;
  };
  agents?: AgentActivityMap;
};

type ExecutionEventsResult = {
  events?: RunLedgerEvent[];
  stats?: {
    total_events?: number;
    tool_events?: number;
    successful_tools?: number;
    failed_tools?: number;
    blocked_tools?: number;
  };
};

type MissionSummary = {
  id: string;
  title: string;
  agent?: string;
  module?: ModuleKey | string;
  status?: string;
  stage?: string;
  event_count?: number;
  updated_at?: string;
};

type MissionArtifact = {
  kind?: string;
  summary?: string;
  evidence?: Array<{
    id?: string;
    name?: string;
    scope?: string;
    snippet?: string;
    match_terms?: string[];
  }>;
  citations?: Array<{
    id?: string;
    name?: string;
    scope?: string;
    snippet?: string;
    match_terms?: string[];
    confidence?: number;
  }>;
  claims?: Array<{
    claim?: string;
    citations?: string[];
    source?: string;
  }>;
  grounded_answer?: string;
  steps?: string[];
  checks?: string[];
  execution?: {
    mode?: string;
    edits?: Array<{
      tool?: string;
      path?: string;
      status?: string;
      result?: string;
      error?: string;
    }>;
    verification?: Array<{
      label?: string;
      command?: string;
      status?: string;
      return_code?: number | null;
      output?: string;
    }>;
    verification_health?: {
      total?: number;
      passed?: number;
      failed?: number;
      unknown?: number;
      failed_commands?: string[];
    };
    blockers?: string[];
    commit_ready?: boolean;
    action_required?: boolean;
    next_actions?: string[];
    summary?: string;
  };
  assignments?: Array<{
    agent?: string;
    objective?: string;
    priority?: number;
  }>;
  debate?: Array<{
    agent?: string;
    proposal?: string;
    critiques?: string[];
  }>;
  consensus?: {
    confidence?: number;
    active_focus?: string[];
    failed_agents?: string[];
    consensus_steps?: string[];
  };
  target_files?: string[];
  file_signals?: Array<{
    path?: string;
    extension?: string;
    matched_terms?: string[];
    line_count?: number;
    snippet?: string;
  }>;
  sources?: KnowledgeSource[];
  signals?: Record<string, number>;
  coverage?: Record<string, unknown>;
  enforcement?: GroundingEnforcement;
  graph?: {
    nodes?: GraphNode[];
    links?: GraphLink[];
  };
  target?: string;
};

type MissionCreateResult = {
  mission?: {
    id?: string;
    title?: string;
    agent?: string;
    module?: string;
    status?: string;
  };
  events?: MissionEvent[];
  stats?: {
    total_events?: number;
    active_events?: number;
  };
  agents?: AgentActivityMap;
};

type MissionAdvanceResult = {
  mission?: MissionSummary;
  event?: MissionEvent;
  missions?: MissionSummary[];
  stats?: {
    total_events?: number;
    active_events?: number;
  };
  agents?: AgentActivityMap;
};

type MissionRunResult = MissionAdvanceResult & {
  artifact?: MissionArtifact;
  task?: {
    id?: string;
    title?: string;
    agent?: string;
    status?: string;
    progress?: number;
    logs?: Array<{
      timestamp?: string;
      message?: string;
    }>;
  };
};

type ModuleConfig = {
  key: ModuleKey;
  title: string;
  icon: string;
  eyebrow: string;
  description: string;
  agent: string;
  tabs: string[];
  prompt: string;
  stats: { label: string; value: string; tone: string }[];
  primary: { title: string; body: string }[];
  timeline: string[];
};

const modules: ModuleConfig[] = [
  {
    key: "dashboard",
    title: "Command Center",
    icon: "⌘",
    eyebrow: "AI OS",
    description: "Live control surface for models, agents, memory, and active execution.",
    agent: "Orion",
    tabs: ["Overview", "Activity", "Plugins", "Launchpad"],
    prompt: "Ask HELIOS to route a task, inspect memory, or launch a module...",
    stats: [
      { label: "Neural sync", value: "98%", tone: "teal" },
      { label: "Active agents", value: "4", tone: "violet" },
      { label: "Open tasks", value: "12", tone: "blue" },
      { label: "Latency", value: "18ms", tone: "green" },
    ],
    primary: [
      { title: "Current Mission", body: "Upgrade HELIOS into a modular AI operating workspace." },
      { title: "Next Best Action", body: "Separate memory, knowledge, planning, and execution into scoped panels." },
      { title: "System Focus", body: "Keep the composer global while changing the workspace by module." },
    ],
    timeline: ["Workspace shell online", "Model route prepared", "Memory scope isolated"],
  },
  {
    key: "research",
    title: "Research Center",
    icon: "⌕",
    eyebrow: "Sources",
    description: "Search, compare, cite, and synthesize external knowledge.",
    agent: "Nova",
    tabs: ["Search", "Sources", "Notes", "Reports"],
    prompt: "Ask HELIOS to research a topic, compare sources, or draft a report...",
    stats: [
      { label: "Sources queued", value: "18", tone: "blue" },
      { label: "Verified", value: "11", tone: "green" },
      { label: "Contradictions", value: "2", tone: "amber" },
      { label: "Reports", value: "4", tone: "violet" },
    ],
    primary: [
      { title: "Source Map", body: "Cluster findings by evidence quality, date, and relevance." },
      { title: "Citation Queue", body: "Keep links, excerpts, and confidence notes attached to each answer." },
      { title: "Research Notes", body: "Convert loose findings into durable project knowledge." },
    ],
    timeline: ["Query builder ready", "Evidence board synced", "Report writer idle"],
  },
  {
    key: "code",
    title: "Code Intelligence",
    icon: "▣",
    eyebrow: "Engineering",
    description: "Inspect files, explain code paths, propose patches, and track test risk.",
    agent: "Vega",
    tabs: ["Files", "Analysis", "Patches", "Terminal"],
    prompt: "Ask HELIOS to inspect code, find bugs, or generate a patch...",
    stats: [
      { label: "Files indexed", value: "86", tone: "blue" },
      { label: "Risk flags", value: "3", tone: "amber" },
      { label: "Tests mapped", value: "14", tone: "green" },
      { label: "Patch queue", value: "2", tone: "violet" },
    ],
    primary: [
      { title: "Repository Map", body: "Group files by backend core, agents, components, memory, and tools." },
      { title: "Patch Studio", body: "Review proposed edits, changed paths, and verification status." },
      { title: "Terminal Feed", body: "Surface build, lint, and test output without leaving the workspace." },
    ],
    timeline: ["Code graph loaded", "Cognitive engine active", "Patch review standing by"],
  },
  {
    key: "analytics",
    title: "System Analytics",
    icon: "▥",
    eyebrow: "Telemetry",
    description: "Monitor model health, memory pressure, latency, and execution logs.",
    agent: "Orion",
    tabs: ["Health", "Logs", "Models", "Costs"],
    prompt: "Ask HELIOS to explain metrics, inspect logs, or diagnose performance...",
    stats: [
      { label: "Uptime", value: "99.9%", tone: "green" },
      { label: "Tokens/min", value: "4.2k", tone: "blue" },
      { label: "Errors", value: "0", tone: "green" },
      { label: "Memory load", value: "62%", tone: "amber" },
    ],
    primary: [
      { title: "Model Health", body: "Track active provider, response time, and fallback status." },
      { title: "Execution Logs", body: "Filter runs by agent, module, severity, and timestamp." },
      { title: "Resource View", body: "Show local model, vector memory, and tool usage at a glance." },
    ],
    timeline: ["Ollama route stable", "No critical errors", "Memory compaction available"],
  },
  {
    key: "voice",
    title: "Voice AI",
    icon: "◉",
    eyebrow: "Speech",
    description: "Control microphone input, transcripts, voice profile, and hands-free sessions.",
    agent: "Lyra",
    tabs: ["Console", "Transcript", "Voice", "Settings"],
    prompt: "Ask HELIOS to listen, summarize speech, or configure voice mode...",
    stats: [
      { label: "Mic status", value: "Ready", tone: "green" },
      { label: "Wake mode", value: "Off", tone: "amber" },
      { label: "Transcript", value: "Live", tone: "blue" },
      { label: "Voice", value: "Calm", tone: "violet" },
    ],
    primary: [
      { title: "Voice Console", body: "Start, pause, and review hands-free interactions." },
      { title: "Transcript Stack", body: "Turn speech into summaries, tasks, and memories." },
      { title: "Response Control", body: "Tune speed, tone, and spoken reply behavior." },
    ],
    timeline: ["Voice tools detected", "Transcript buffer clear", "Speak button ready"],
  },
  {
    key: "collab",
    title: "Collaborative AI",
    icon: "◇",
    eyebrow: "Multi-agent",
    description: "Coordinate specialist agents around shared goals and review handoffs.",
    agent: "Orion",
    tabs: ["Room", "Handoffs", "Decisions", "Artifacts"],
    prompt: "Ask HELIOS to assemble agents, debate options, or create a shared artifact...",
    stats: [
      { label: "Agents", value: "4", tone: "violet" },
      { label: "Handoffs", value: "7", tone: "blue" },
      { label: "Decisions", value: "5", tone: "green" },
      { label: "Open asks", value: "2", tone: "amber" },
    ],
    primary: [
      { title: "Agent Room", body: "Track who is working on strategy, code, research, and design." },
      { title: "Decision Log", body: "Capture what changed, why it changed, and who approved it." },
      { title: "Artifact Shelf", body: "Keep plans, reports, patches, and summaries in one place." },
    ],
    timeline: ["Orion coordinating", "Vega reviewing code", "Nova watching sources"],
  },
  {
    key: "swarm",
    title: "Swarm Intelligence",
    icon: "⌬",
    eyebrow: "Delegation",
    description: "Visualize agent load, routing, parallel work, and active task delegation.",
    agent: "Orion",
    tabs: ["Network", "Queue", "Load", "Messages"],
    prompt: "Ask HELIOS to delegate work, inspect agent load, or rebalance the swarm...",
    stats: [
      { label: "Routes", value: "12", tone: "blue" },
      { label: "Parallel jobs", value: "3", tone: "violet" },
      { label: "Queue", value: "6", tone: "amber" },
      { label: "Stable", value: "Yes", tone: "green" },
    ],
    primary: [
      { title: "Agent Network", body: "Show agent roles, load, and which task each one owns." },
      { title: "Delegation Queue", body: "Split large work into clear, reviewable slices." },
      { title: "Message Bus", body: "Trace agent-to-agent signals and important handoffs." },
    ],
    timeline: ["Routing table refreshed", "Load balanced", "No blocked agents"],
  },
  {
    key: "loop",
    title: "Autonomous Loop",
    icon: "∞",
    eyebrow: "Execution",
    description: "Run observe-plan-act-reflect cycles with guardrails and visible checkpoints.",
    agent: "Orion",
    tabs: ["Loop", "Guardrails", "Actions", "Review"],
    prompt: "Ask HELIOS to run an autonomous loop or explain the next action...",
    stats: [
      { label: "Cycle", value: "Observe", tone: "blue" },
      { label: "Actions", value: "9", tone: "violet" },
      { label: "Approvals", value: "2", tone: "amber" },
      { label: "Safety", value: "On", tone: "green" },
    ],
    primary: [
      { title: "Loop State", body: "Show current phase, next checkpoint, and waiting approvals." },
      { title: "Action Ledger", body: "Log tool calls, file edits, command runs, and outcomes." },
      { title: "Reflection Notes", body: "Turn each run into lessons for future execution." },
    ],
    timeline: ["Observe phase ready", "Action guardrails active", "Reflection queue empty"],
  },
  {
    key: "planning",
    title: "Planning Engine",
    icon: "▤",
    eyebrow: "Strategy",
    description: "Break goals into milestones, task graphs, dependencies, and next actions.",
    agent: "Orion",
    tabs: ["Overview", "Task Graph", "Reasoning", "History"],
    prompt: "Ask HELIOS to create, refine, or execute a plan...",
    stats: [
      { label: "Milestones", value: "5", tone: "blue" },
      { label: "Blocked", value: "1", tone: "amber" },
      { label: "Ready tasks", value: "8", tone: "green" },
      { label: "Depth", value: "4", tone: "violet" },
    ],
    primary: [
      { title: "Current Goal", body: "Convert HELIOS from repeated chat pages into module-specific workspaces." },
      { title: "Task Graph", body: "Route memory, knowledge, agents, and execution into separate UI regions." },
      { title: "Next Actions", body: "Wire real route state, scoped panels, and contextual composer prompts." },
    ],
    timeline: ["Goal decomposed", "Dependencies mapped", "Execution plan ready"],
  },
  {
    key: "reasoning",
    title: "Recursive Reasoning",
    icon: "✺",
    eyebrow: "Cognition",
    description: "Inspect reasoning traces, assumptions, alternatives, and refinement loops.",
    agent: "Orion",
    tabs: ["Trace", "Assumptions", "Branches", "Critique"],
    prompt: "Ask HELIOS to reason through a decision or compare alternatives...",
    stats: [
      { label: "Trace depth", value: "6", tone: "violet" },
      { label: "Branches", value: "4", tone: "blue" },
      { label: "Risks", value: "2", tone: "amber" },
      { label: "Confidence", value: "82%", tone: "green" },
    ],
    primary: [
      { title: "Reasoning Trace", body: "Show structured steps, assumptions, and unresolved questions." },
      { title: "Branch Compare", body: "Keep multiple solution paths visible before choosing one." },
      { title: "Critique Pass", body: "Review blind spots, tradeoffs, and failure modes." },
    ],
    timeline: ["Trace initialized", "Alternatives ranked", "Critique pass available"],
  },
  {
    key: "workflow",
    title: "Workflow Engine",
    icon: "↯",
    eyebrow: "Automation",
    description: "Build workflows with triggers, steps, runs, logs, and recovery paths.",
    agent: "Vega",
    tabs: ["Overview", "Builder", "Runs", "Triggers"],
    prompt: "Ask HELIOS to build, run, or debug a workflow...",
    stats: [
      { label: "Workflows", value: "9", tone: "blue" },
      { label: "Running", value: "1", tone: "green" },
      { label: "Paused", value: "2", tone: "amber" },
      { label: "Artifacts", value: "17", tone: "violet" },
    ],
    primary: [
      { title: "Workflow Builder", body: "Create step-by-step automations with clear inputs and outputs." },
      { title: "Run History", body: "Inspect every attempt, result, artifact, and failure." },
      { title: "Recovery Paths", body: "Retry, rollback, or ask for approval when a run becomes risky." },
    ],
    timeline: ["Builder ready", "Latest run succeeded", "Trigger monitor idle"],
  },
  {
    key: "knowledge",
    title: "Knowledge Sources",
    icon: "▧",
    eyebrow: "Memory",
    description: "Upload, index, scope, and manage files used by HELIOS.",
    agent: "Nova",
    tabs: ["Sources", "Indexing", "Scopes", "Cleanup"],
    prompt: "Ask HELIOS to index files, summarize sources, or forget stale context...",
    stats: [
      { label: "Uploaded", value: "3", tone: "blue" },
      { label: "Indexed", value: "2", tone: "green" },
      { label: "Pending", value: "1", tone: "amber" },
      { label: "Scopes", value: "5", tone: "violet" },
    ],
    primary: [
      { title: "Source Library", body: "Manage uploaded TXT, PY, MD, and project documents." },
      { title: "Indexing Status", body: "Show whether each file is searchable, active, or ignored." },
      { title: "Memory Scope", body: "Choose whether a source applies globally, to this project, or only this chat." },
    ],
    timeline: ["Knowledge panel isolated", "Upload route ready", "Scoped retrieval enabled"],
  },
];

const API_BASE_URL = process.env.NEXT_PUBLIC_HELIOS_API_URL ?? "http://localhost:8000";
const HELIOS_API_KEY = process.env.NEXT_PUBLIC_HELIOS_API_KEY ?? "";
const websocketBaseUrl = API_BASE_URL.startsWith("https://")
  ? `wss://${API_BASE_URL.slice("https://".length)}`
  : API_BASE_URL.startsWith("http://")
    ? `ws://${API_BASE_URL.slice("http://".length)}`
    : API_BASE_URL;
const RUN_LEDGER_WS_URL =
  (process.env.NEXT_PUBLIC_HELIOS_WS_URL ?? "").trim() ||
  `${websocketBaseUrl.replace(/\/$/, "")}/events`;
const CHAT_WS_URL = `${websocketBaseUrl.replace(/\/$/, "")}/ws`;
const REQUEST_TIMEOUT_MS = 12000;
const RUN_LEDGER_MAX_ENTRIES = 40;
const MAX_SOURCE_FILE_BYTES = 256 * 1024;
const MAX_SOURCE_CONTENT_CHARS = 12000;
const TEXT_SOURCE_EXTENSIONS = [".py", ".md", ".txt", ".json", ".csv", ".ts", ".tsx", ".js", ".css"];

const agents = [
  {
    name: "Orion",
    role: "Strategy Core",
    signal: "Priority routing",
    specialty: "Turns messy goals into ranked action plans.",
    load: "42%",
  },
  {
    name: "Vega",
    role: "Code Sentinel",
    signal: "Patch analysis",
    specialty: "Reviews code paths, risks, and release blockers.",
    load: "68%",
  },
  {
    name: "Nova",
    role: "Research Lens",
    signal: "Source mapping",
    specialty: "Finds evidence, contradictions, and missing context.",
    load: "35%",
  },
  {
    name: "Lyra",
    role: "Design Pilot",
    signal: "Interface shaping",
    specialty: "Refines product flows, visuals, and interaction rhythm.",
    load: "51%",
  },
];

type CommandDefinition = {
  id: string;
  label: string;
  category: string;
  detail: string;
  keywords: string[];
};

const launcherCommands: CommandDefinition[] = [
  { id: "mission:create", label: "Create Mission", category: "Mission", detail: "Open mission composer with the active module and agent.", keywords: ["new", "task", "objective"] },
  { id: "mission:run", label: "Run Active Mission", category: "Mission", detail: "Execute the currently selected mission workflow.", keywords: ["execute", "workflow", "run"] },
  { id: "mission:research", label: "Launch Research Mission", category: "Research", detail: "Create and open a source-grounded research mission.", keywords: ["sources", "citations", "nova"] },
  { id: "mission:code", label: "Launch Code Mission", category: "Code", detail: "Create and open a bounded code-agent workflow.", keywords: ["patch", "test", "vega"] },
  { id: "mission:recover", label: "Recover Active Mission", category: "Mission", detail: "Resume the selected mission from its latest checkpoint.", keywords: ["recover", "resume", "checkpoint"] },
  { id: "mission:export", label: "Export Active Mission", category: "Mission", detail: "Download the selected mission and its artifacts.", keywords: ["export", "download", "artifact"] },
  { id: "autonomy:queue", label: "Queue Autonomous Run", category: "Autonomy", detail: "Queue the command text as a durable autonomous objective.", keywords: ["autonomy", "queue", "worker", "run"] },
  { id: "swarm:queue", label: "Queue Isolated Swarm", category: "Swarm", detail: "Queue the command text for a durable multi-worker debate.", keywords: ["swarm", "debate", "workers", "critique"] },
  { id: "code:auto", label: "Run Automatic Code Repair", category: "Code", detail: "Use the Code workspace objective and target files to edit, verify, and retry.", keywords: ["repair", "edit", "test", "fix"] },
  { id: "source:intel", label: "Refresh Source Intelligence", category: "Knowledge", detail: "Query citations and unsupported terms for the current mission.", keywords: ["citations", "evidence", "sources"] },
  { id: "tool:status", label: "Run Git Status", category: "Tools", detail: "Execute safe git status through the backend tool ledger.", keywords: ["tool", "ledger", "git"] },
  { id: "tool:execute", label: "Execute Registered Tool", category: "Tools", detail: "Run a registered tool using: tool_name [JSON args array].", keywords: ["tool", "execute", "terminal", "file", "python"] },
  { id: "git:preview", label: "Preview Git Commit", category: "Git", detail: "Inspect staged files and proposed commit message.", keywords: ["commit", "staged", "preview"] },
  { id: "git:commit", label: "Commit Staged Changes", category: "Git", detail: "Commit already-staged files using the typed command text as message.", keywords: ["commit", "checkpoint", "staged"] },
  { id: "git:stage", label: "Stage Git Paths", category: "Git", detail: "Stage comma-separated project paths from the command text.", keywords: ["add", "stage", "paths"] },
  { id: "git:branch", label: "Create Git Branch", category: "Git", detail: "Create and switch to the branch named in the command text.", keywords: ["branch", "switch", "checkout"] },
  { id: "git:push", label: "Push Git Branch", category: "Git", detail: "Push the branch named in the command text to origin.", keywords: ["push", "remote", "origin"] },
  { id: "git:rollback", label: "Rollback Git Commit", category: "Git", detail: "Create a revert commit for the SHA in the command text.", keywords: ["rollback", "revert", "undo"] },
  { id: "deploy:project", label: "Deploy HELIOS", category: "System", detail: "Execute the real production deployment workflow (git pull + docker restart).", keywords: ["deploy", "production", "release", "restart"] },
  { id: "open:swarm", label: "Activate Swarm", category: "Workspace", detail: "Open the swarm coordination surface.", keywords: ["agents", "collab"] },
  { id: "open:memory", label: "Inspect Memory", category: "Workspace", detail: "Open scoped memory drawer.", keywords: ["brain", "memory"] },
  { id: "open:voice", label: "Open Voice Room", category: "Workspace", detail: "Switch to realtime voice workspace.", keywords: ["speak", "audio"] },
  { id: "source:upload", label: "Upload Source", category: "Knowledge", detail: "Open source upload flow.", keywords: ["file", "index"] },
  { id: "source:url", label: "Index Source URL", category: "Knowledge", detail: "Open the web and GitHub URL ingestion controls.", keywords: ["web", "github", "url", "index"] },
  { id: "voice:fallback", label: "Open Voice Fallback", category: "Voice", detail: "Open provider-independent text-to-speech voice mode.", keywords: ["voice", "fallback", "speech"] },
  { id: "mode:balanced", label: "Use Balanced Mode", category: "Conversation", detail: "Use adaptive depth and tools when useful.", keywords: ["mode", "balanced"] },
  { id: "mode:concise", label: "Use Concise Mode", category: "Conversation", detail: "Use short direct responses.", keywords: ["mode", "concise", "short"] },
  { id: "mode:deep", label: "Use Deep Analysis Mode", category: "Conversation", detail: "Use high-depth reasoning and evidence.", keywords: ["mode", "deep", "analysis"] },
  { id: "mode:execute", label: "Use Execution Mode", category: "Conversation", detail: "Prioritize action, tools, and verification.", keywords: ["mode", "execute", "action"] },
  { id: "thread:export", label: "Export Thread", category: "Session", detail: "Download the current chat transcript.", keywords: ["download", "save"] },
  { id: "export:memory", label: "Export Memory", category: "Export", detail: "Download conversation memory as JSON.", keywords: ["memory", "download", "json"] },
  { id: "export:sources", label: "Export Sources", category: "Export", detail: "Download the source library as JSON.", keywords: ["sources", "download", "json"] },
  { id: "export:brain", label: "Export Project Brain", category: "Export", detail: "Download the Project Brain graph as JSON.", keywords: ["brain", "graph", "download"] },
  { id: "export:report", label: "Export Operations Report", category: "Export", detail: "Download a combined health and observability report.", keywords: ["report", "analytics", "download"] },
];

const initialMessages: Message[] = [
  {
    id: 1,
    role: "assistant",
    text: "HELIOS is online. Define the mission.",
  },
];

const iconPaths: Record<IconName, string> = {
  brain: "M12 3a3 3 0 0 0-3 3v1H7a3 3 0 0 0-1 5.83A3 3 0 0 0 7 18h2v-4h6v4h2a3 3 0 0 0 1-5.17A3 3 0 0 0 17 7h-2V6a3 3 0 0 0-3-3Z M9 10h6",
  command: "M8 8H5.8A2.8 2.8 0 1 1 8 5.2V8Zm0 0h8m0 0h2.2A2.8 2.8 0 1 0 16 5.2V8Zm0 0v8m0 0v2.2A2.8 2.8 0 1 0 18.8 16H16Zm0 0H8m0 0H5.8A2.8 2.8 0 1 0 8 18.8V16Zm0 0V8",
  deploy: "M12 3v11m0-11 4 4m-4-4-4 4M5 13v5a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-5",
  focus: "M4 9V5a1 1 0 0 1 1-1h4M15 4h4a1 1 0 0 1 1 1v4M20 15v4a1 1 0 0 1-1 1h-4M9 20H5a1 1 0 0 1-1-1v-4",
  theme: "M12 3a7 7 0 1 0 7 7 5 5 0 0 1-7-7Z",
  close: "M6 6l12 12M18 6 6 18",
  upload: "M12 16V4m0 0 5 5m-5-5-5 5M5 17v2a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2",
  search: "M10.5 18a7.5 7.5 0 1 1 5.3-12.8 7.5 7.5 0 0 1-5.3 12.8Zm5.3-2.2L21 21",
  user: "M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm-7 8a7 7 0 0 1 14 0",
};

function Icon({ name }: { name: IconName }) {
  return (
    <svg className="ui-icon" viewBox="0 0 24 24" aria-hidden="true">
      <path d={iconPaths[name]} />
    </svg>
  );
}

const researchSources = [
  { title: "Model routing benchmark", confidence: "94%", status: "Verified", note: "Supports local inference routing and fallback checks." },
  { title: "Agent memory notes", confidence: "81%", status: "Needs review", note: "Contradicts older project memory scope assumptions." },
  { title: "Workflow telemetry log", confidence: "88%", status: "Fresh", note: "Useful for execution dashboard instrumentation." },
];

const codeFiles = [
  { path: "backend/core/cognitive_engine.py", signal: "Active file", risk: "Medium" },
  { path: "frontend/app/page.tsx", signal: "UI shell", risk: "Low" },
  { path: "frontend/app/globals.css", signal: "Visual system", risk: "Low" },
  { path: "backend/api/ai_provider.py", signal: "Ollama route", risk: "Medium" },
];

const planNodes = [
  { title: "Scope", meta: "Define module surfaces" },
  { title: "Design", meta: "Apply futuristic visual system" },
  { title: "Wire", meta: "Connect backend state" },
  { title: "Verify", meta: "Build, lint, test" },
];

const workflowRuns = [
  { step: "Trigger", detail: "User asks HELIOS to execute workflow", state: "Ready" },
  { step: "Plan", detail: "Generate ordered tasks and guardrails", state: "Running" },
  { step: "Act", detail: "Run tools, update files, capture logs", state: "Queued" },
  { step: "Review", detail: "Summarize outcome and next actions", state: "Waiting" },
];

function formatFileSize(size: number) {
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${Math.round(size / 1024)} KB`;
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

function renderText(value: unknown, fallback: string) {
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }

  return fallback;
}

async function fetchWithTimeout(input: RequestInfo | URL, init: RequestInit = {}, timeoutMs = REQUEST_TIMEOUT_MS) {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), timeoutMs);
  const headers = new Headers(init.headers);

  if (HELIOS_API_KEY) headers.set("x-helios-api-key", HELIOS_API_KEY);
  try {
    return await fetch(input, {
      ...init,
      headers,
      credentials: "include",
      signal: init.signal ?? controller.signal,
    });
  } finally {
    window.clearTimeout(timeout);
  }
}

function normalizeRunLedgerEvent(payload: Record<string, unknown>, fallbackDetail?: string): RunLedgerEvent {
  const labelValue = payload.label ?? payload.action ?? payload.stage ?? payload.type;
  const actorValue = payload.actor ?? payload.agent ?? payload.owner;
  const moduleValue = payload.module ?? payload.scope;
  const toolValue = payload.tool;
  const statusValue = payload.status ?? payload.state ?? payload.result;
  const detailValue = payload.detail ?? payload.summary ?? payload.message ?? fallbackDetail;
  const errorValue = payload.error;
  const inputValue = payload.input;
  const resultValue = payload.result;
  const parentValue = payload.parent_id;
  const metadataValue = payload.metadata;
  const timestampValue = payload.timestamp ?? payload.time ?? payload.at;
  const durationValue = payload.duration_ms;
  const attemptValue = payload.attempt;
  const idValue = payload.id ?? payload.event_id ?? payload.run_id;
  const id =
    typeof idValue === "string"
      ? idValue
      : typeof idValue === "number"
        ? String(idValue)
        : `${Date.now()}-${Math.random().toString(16).slice(2)}`;

  return {
    id,
    label: typeof labelValue === "string" && labelValue.trim().length > 0 ? labelValue : "Run event",
    actor: actorValue ? String(actorValue) : undefined,
    module: moduleValue ? String(moduleValue) : undefined,
    tool: toolValue ? String(toolValue) : undefined,
    status: statusValue ? String(statusValue) : undefined,
    detail: detailValue ? String(detailValue) : undefined,
    error: errorValue ? String(errorValue) : undefined,
    input: inputValue,
    result: resultValue,
    parent_id: parentValue ? String(parentValue) : undefined,
    metadata: metadataValue && typeof metadataValue === "object" ? metadataValue as Record<string, unknown> : undefined,
    timestamp: timestampValue ? String(timestampValue) : undefined,
    duration_ms: typeof durationValue === "number" ? durationValue : undefined,
    attempt: typeof attemptValue === "number" ? attemptValue : undefined,
  };
}

function parseRunLedgerMessage(message: string): RunLedgerEvent | null {
  const trimmed = message.trim();
  if (!trimmed) return null;

  try {
    const parsed = JSON.parse(trimmed) as unknown;
    if (parsed && typeof parsed === "object") {
      const payload = "event" in parsed ? (parsed as { event: unknown }).event : parsed;
      if (payload && typeof payload === "object") {
        return normalizeRunLedgerEvent(payload as Record<string, unknown>);
      }
    }
  } catch {
    return normalizeRunLedgerEvent({ message }, message);
  }

  return normalizeRunLedgerEvent({ message }, message);
}

function GraphMap({
  nodes,
  links,
  selectedId,
  onSelect,
  label,
}: {
  nodes: GraphNode[];
  links: GraphLink[];
  selectedId?: string | null;
  onSelect: (node: GraphNode) => void;
  label: string;
}) {
  const visibleNodes = nodes.slice(0, 24);
  const positions = new Map(
    visibleNodes.map((node, index) => {
      const angle = (Math.PI * 2 * index) / Math.max(visibleNodes.length, 1) - Math.PI / 2;
      const radius = index === 0 ? 0 : 34 + (index % 3) * 9;
      return [
        node.id,
        {
          x: 50 + Math.cos(angle) * radius,
          y: 50 + Math.sin(angle) * radius,
        },
      ] as const;
    }),
  );

  return (
    <svg className="interactive-graph" viewBox="0 0 100 100" role="img" aria-label={label}>
      {links.slice(0, 48).map((link, index) => {
        const from = positions.get(link.from);
        const to = positions.get(link.to);
        if (!from || !to) return null;
        return <line key={`${link.from}-${link.to}-${index}`} x1={from.x} y1={from.y} x2={to.x} y2={to.y} />;
      })}
      {visibleNodes.map((node, index) => {
        const position = positions.get(node.id);
        if (!position) return null;
        const radius = Math.min(5.5, 2.7 + Math.log2(Math.max(node.weight ?? 1, 1)));
        return (
          <g
            className={`graph-node-svg kind-${node.kind ?? "node"} ${selectedId === node.id ? "selected" : ""}`}
            key={node.id ?? index}
            role="button"
            tabIndex={0}
            aria-label={`${node.label ?? "Graph node"} ${node.kind ?? ""}`}
            onClick={() => onSelect(node)}
            onKeyDown={(event) => {
              if (event.key === "Enter" || event.key === " ") onSelect(node);
            }}
          >
            <circle cx={position.x} cy={position.y} r={radius} />
            <text x={position.x} y={position.y + radius + 4}>{String(node.label ?? node.id ?? "").slice(0, 18)}</text>
          </g>
        );
      })}
    </svg>
  );
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState("");
  const [activeModule, setActiveModule] = useState<ModuleKey>("dashboard");
  const [activeTab, setActiveTab] = useState("Overview");
  const [activeAgent, setActiveAgent] = useState(agents[0].name);
  const [conversationMode, setConversationMode] = useState<ConversationMode>(() => {
    if (typeof window === "undefined") return "balanced";
    const storedMode = window.localStorage.getItem("helios-conversation-mode") as ConversationMode | null;
    return storedMode && ["balanced", "concise", "deep", "execute"].includes(storedMode)
      ? storedMode
      : "balanced";
  });
  const [conversationModes, setConversationModes] = useState<ConversationModeConfig[]>([]);
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [commandOpen, setCommandOpen] = useState(false);
  const [missionOpen, setMissionOpen] = useState(false);
  const [missionTitle, setMissionTitle] = useState("");
  const [missionModule, setMissionModule] = useState<ModuleKey>("planning");
  const [missionAgent, setMissionAgent] = useState("Orion");
  const [missionScheduledAt, setMissionScheduledAt] = useState("");
  const [isCreatingMission, setIsCreatingMission] = useState(false);
  const [memoryOpen, setMemoryOpen] = useState(false);
  const [memoryItems, setMemoryItems] = useState<Array<Record<string, unknown>>>([]);
  const [memoryStatus, setMemoryStatus] = useState("Loading memory...");
  const [memoryBusy, setMemoryBusy] = useState(false);
  const [deployOpen, setDeployOpen] = useState(false);
  const [accountOpen, setAccountOpen] = useState(false);
  const [executionOpen, setExecutionOpen] = useState(false);
  const [selectedExecutionId, setSelectedExecutionId] = useState<string | null>(null);
  const [executionSearch, setExecutionSearch] = useState("");
  const [executionStatusFilter, setExecutionStatusFilter] = useState("all");
  const [focusMode, setFocusMode] = useState(false);
  const [commandQuery, setCommandQuery] = useState("");
  const [commandStatus, setCommandStatus] = useState("");
  const [runningCommandId, setRunningCommandId] = useState<string | null>(null);
  const [runtimeState, setRuntimeState] = useState<RuntimeState>("checking");
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [lastTrace, setLastTrace] = useState<CognitiveTrace[]>([]);
  const [lastPlan, setLastPlan] = useState<PlanStep[]>([]);
  const [lastRunAt, setLastRunAt] = useState<string>("No runs yet");
  const [runLedger, setRunLedger] = useState<RunLedgerEvent[]>([]);
  const [runLedgerStatus, setRunLedgerStatus] = useState<RunLedgerStatus>("connecting");
  const [missionEvents, setMissionEvents] = useState<MissionEvent[]>([]);
  const [missions, setMissions] = useState<MissionSummary[]>([]);
  const [activeMissionId, setActiveMissionId] = useState<string | null>(null);
  const [advancingMissionStage, setAdvancingMissionStage] = useState("");
  const [missionArtifact, setMissionArtifact] = useState<MissionArtifact | null>(null);
  const [missionTask, setMissionTask] = useState<MissionRunResult["task"] | null>(null);
  const [agentActivity, setAgentActivity] = useState<AgentActivityMap>({});
  const [indexedSources, setIndexedSources] = useState<KnowledgeSource[]>([]);
  const [sourceIntel, setSourceIntel] = useState<SourceIntelligenceResult | null>(null);
  const [selectedSourceGraphNode, setSelectedSourceGraphNode] = useState<GraphNode | null>(null);
  const [sourceUrl, setSourceUrl] = useState("");
  const [sourceUrlType, setSourceUrlType] = useState<"WEB" | "GITHUB">("WEB");
  const [sourceUrlBusy, setSourceUrlBusy] = useState(false);
  const [projectBrain, setProjectBrain] = useState<ProjectBrainResult | null>(null);
  const [selectedBrainNode, setSelectedBrainNode] = useState<GraphNode | null>(null);
  const [observability, setObservability] = useState<ObservabilityResult | null>(null);
  const [voiceStatusInfo, setVoiceStatusInfo] = useState<VoiceStatusResult | null>(null);
  const [autonomousRuns, setAutonomousRuns] = useState<AutonomousRun[]>([]);
  const [autonomyObjective, setAutonomyObjective] = useState("");
  const [autonomyBusy, setAutonomyBusy] = useState(false);
  const [isolatedSwarmRuns, setIsolatedSwarmRuns] = useState<IsolatedSwarmRun[]>([]);
  const [swarmObjective, setSwarmObjective] = useState("");
  const [swarmBusy, setSwarmBusy] = useState(false);
  const [codeRepairObjective, setCodeRepairObjective] = useState("");
  const [codeRepairTargets, setCodeRepairTargets] = useState("");
  const [codeRepairBusy, setCodeRepairBusy] = useState(false);
  const [gitDiffResult, setGitDiffResult] = useState<GitDiffResult | null>(null);
  const [gitStagePaths, setGitStagePaths] = useState("");
  const [gitBranchName, setGitBranchName] = useState("");
  const [gitCommitMessage, setGitCommitMessage] = useState("");
  const [gitPushBranch, setGitPushBranch] = useState("");
  const [gitRollbackCommit, setGitRollbackCommit] = useState("");
  const [gitOperationStatus, setGitOperationStatus] = useState("Ready for an approved git operation.");
  const [gitOperationBusy, setGitOperationBusy] = useState(false);
  const [plugins, setPlugins] = useState<PluginRecord[]>([]);
  const [pluginName, setPluginName] = useState("");
  const [pluginVersion, setPluginVersion] = useState("1.0.0");
  const [pluginDescription, setPluginDescription] = useState("");
  const [pluginCode, setPluginCode] = useState("");
  const [pluginStatus, setPluginStatus] = useState("");
  const [terminalCommand, setTerminalCommand] = useState("git status --short");
  const [terminalOutput, setTerminalOutput] = useState("");
  const [terminalBusy, setTerminalBusy] = useState(false);
  const idRef = useRef(10);
  const generationRef = useRef<number | null>(null);
  const requestRef = useRef<AbortController | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const peerConnectionRef = useRef<RTCPeerConnection | null>(null);
  const voiceDataChannelRef = useRef<RTCDataChannel | null>(null);
  const voiceAudioRef = useRef<HTMLAudioElement | null>(null);
  const voiceStreamRef = useRef<MediaStream | null>(null);
  const [voiceState, setVoiceState] = useState<VoiceState>("idle");
  const [voiceError, setVoiceError] = useState("");
  const [voiceTurns, setVoiceTurns] = useState<VoiceTurn[]>([
    { id: 1, role: "system", text: "Ready when you are." },
  ]);
  const [voiceTranscriptOpen, setVoiceTranscriptOpen] = useState(false);
  const [voiceFallbackText, setVoiceFallbackText] = useState("");
  const [voiceFallbackBusy, setVoiceFallbackBusy] = useState(false);
  const [runtimeTick, setRuntimeTick] = useState(0);
  const [authRequired, setAuthRequired] = useState(false);
  const [authChecking, setAuthChecking] = useState(true);
  const [authUser, setAuthUser] = useState<AuthUser | null>(null);
  const [aiSettingsProvider, setAiSettingsProvider] = useState("ollama");
  const [aiSettingsModel, setAiSettingsModel] = useState("");
  const [aiSettingsStatus, setAiSettingsStatus] = useState("Saved provider preference is applied on the next health refresh.");
  const [aiSettingsBusy, setAiSettingsBusy] = useState(false);
  const [loginUsername, setLoginUsername] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [loginError, setLoginError] = useState("");
  const [loginBusy, setLoginBusy] = useState(false);
  const [managedUsers, setManagedUsers] = useState<AuthUser[]>([]);
  const [newUsername, setNewUsername] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newRole, setNewRole] = useState<AuthUser["role"]>("viewer");
  const [userAdminStatus, setUserAdminStatus] = useState("");

  const activeModuleConfig = modules.find((item) => item.key === activeModule) ?? modules[0];
  const selectedAgent = agents.find((agent) => agent.name === activeAgent) ?? agents[0];
  const activeConversationMode = conversationModes.find((mode) => mode.id === conversationMode);
  const normalizedCommandQuery = commandQuery.trim().toLowerCase();
  const filteredModules = normalizedCommandQuery
    ? modules.filter((item) =>
        `${item.title} ${item.eyebrow} ${item.description}`.toLowerCase().includes(normalizedCommandQuery),
      )
    : modules;
  const filteredCommands = normalizedCommandQuery
    ? launcherCommands.filter((command) =>
        `${command.label} ${command.category} ${command.detail} ${command.keywords.join(" ")}`
          .toLowerCase()
          .includes(normalizedCommandQuery),
      )
    : launcherCommands;
  const aiStatus = health?.ai?.status ?? "unknown";
  const modelName = health?.ai?.model ?? "qwen2.5:3b";
  const availableProviderModels = health?.ai?.providers?.[aiSettingsProvider]?.available_models ?? health?.ai?.available_models ?? [];
  const memoryStats = health?.cognitive_engine?.memory;
  const sourceStats = health?.sources;
  const memoryUsage = memoryStats?.storage_usage_percent ?? 0;
  const memoryTotal = memoryStats?.total_conversations ?? messages.length;
  const runtimeLabel =
    runtimeState === "online"
      ? "Runtime Online"
      : runtimeState === "degraded"
        ? "Model Needs Attention"
        : runtimeState === "offline"
          ? "Backend Offline"
          : "Checking Runtime";
  const runtimeDetail =
    runtimeState === "offline"
      ? "Start FastAPI on port 8000"
      : aiStatus === "model_missing"
        ? `${modelName} is not installed`
        : aiStatus === "offline"
          ? "Ollama is not reachable"
          : `${modelName} • ${aiStatus}`;
  const liveMemoryScopes = [
    { label: "Conversations", value: String(memoryTotal), tone: "teal" },
    { label: "Memory Usage", value: `${memoryUsage}%`, tone: memoryUsage > 85 ? "amber" : "blue" },
    { label: "Trace Steps", value: String(lastTrace.length), tone: "violet" },
    { label: "Plan Steps", value: String(lastPlan.length), tone: "green" },
    { label: "Uploaded Sources", value: String((sourceStats?.total_sources ?? indexedSources.length) + attachments.length), tone: "amber" },
  ];
  const liveMetrics = [
    { label: "Backend", value: runtimeState === "online" ? "Online" : runtimeState === "checking" ? "Checking" : "Issue", tone: runtimeState === "online" ? "green" : "amber" },
    { label: "Model", value: health?.ai?.model_available ? "Ready" : "Check", tone: health?.ai?.model_available ? "green" : "amber" },
    { label: "Memory", value: String(memoryTotal), tone: "blue" },
    { label: "Tool Events", value: String(health?.execution?.tool_events ?? runLedger.filter((event) => event.tool).length), tone: "violet" },
  ];
  const displayedStats = activeModule === "dashboard" || activeModule === "analytics" ? liveMetrics : activeModuleConfig.stats;
  const traceEvents: CognitiveTrace[] =
    lastTrace.length > 0 ? lastTrace : activeModuleConfig.timeline.map((event) => ({ stage: event, actor: activeModuleConfig.agent }));
  const displayedPlanNodes =
    lastPlan.length > 0
      ? lastPlan.map((step) => ({
          title: step.agent ?? "agent",
          meta: step.objective ?? "Waiting for the next plan.",
        }))
      : planNodes;
  const agentRadar = agents.map((agent) => {
    const isSelected = agent.name === selectedAgent.name;
    const state = isGenerating && isSelected ? "working" : isSelected ? "focused" : runtimeState === "offline" ? "standby" : "ready";

    return {
      ...agent,
      state,
      orbit: isSelected ? "Primary" : state === "ready" ? "Linked" : "Idle",
    };
  });
  const runLedgerStatusLabel =
    runLedgerStatus === "live"
      ? "Live"
      : runLedgerStatus === "connecting"
        ? "Connecting"
        : runLedgerStatus === "error"
          ? "Error"
          : "Offline";
  const runLedgerEntries = runLedger.slice(0, 8);
  const selectedExecution =
    runLedger.find((event) => event.id === selectedExecutionId) ??
    runLedger[0] ??
    null;
  const filteredExecutionEvents = runLedger.filter((event) => {
    const query = executionSearch.trim().toLowerCase();
    const matchesStatus = executionStatusFilter === "all" || event.status === executionStatusFilter;
    const matchesQuery = !query || `${event.label} ${event.tool ?? ""} ${event.actor ?? ""} ${event.detail ?? ""}`
      .toLowerCase()
      .includes(query);
    return matchesStatus && matchesQuery;
  });
  const intelligenceStatus = isGenerating
    ? attachments.length > 0
      ? "Synthesizing"
      : activeModule === "research"
        ? "Searching"
        : activeModule === "workflow" || activeModule === "loop"
          ? "Executing"
          : "Thinking"
    : lastTrace.length > 0
      ? "Reviewing"
      : runtimeState === "online"
        ? "Idle"
        : "Checking";
  const missionStageFallback = ["Created", "Assigned", "Executed", "Reviewed", "Archived"];
  const missionTimelineItems =
    missionEvents.length > 0
      ? missionEvents.slice(-5).reverse()
      : missionStageFallback.map((stage, index) => ({
          id: `fallback-${stage}`,
          stage,
          title: index === 0 ? activeModuleConfig.title : activeModuleConfig.timeline[index - 1] ?? "Awaiting run",
          agent: index < 2 ? selectedAgent.name : "HELIOS",
          module: activeModule,
          status: index < 2 ? "active" : "queued",
        }));
  const sources = useMemo(
    () => [
      ...indexedSources,
      ...attachments.map((file) => ({ ...file, status: file.status ?? "Pending" })),
    ],
    [attachments, indexedSources],
  );
  const activeMission = missions.find((mission) => mission.id === activeMissionId) ?? missions[0];
  const latestMission = missionEvents.at(-1);
  const latestArtifact = missionArtifact ?? latestMission?.artifact ?? null;
  const researchArtifact =
    latestArtifact?.kind === "research"
      ? latestArtifact
      : missionEvents
          .slice()
          .reverse()
          .find((event) => event.artifact?.kind === "research")
          ?.artifact ?? null;
  const researchCitations = researchArtifact?.citations ?? sourceIntel?.citations ?? [];
  const researchClaims = researchArtifact?.claims ?? sourceIntel?.claims ?? [];
  const researchCoverage = researchArtifact?.coverage ?? sourceIntel?.coverage ?? null;
  const researchEnforcement = researchArtifact?.enforcement ?? sourceIntel?.enforcement ?? null;
  const researchIsGrounded = Boolean(researchEnforcement?.enforced ?? (researchCoverage as { enforced?: unknown } | null)?.enforced);
  const researchUnsupportedTerms = Array.isArray((researchCoverage as { unmatched_terms?: unknown } | null)?.unmatched_terms)
    ? ((researchCoverage as { unmatched_terms?: string[] }).unmatched_terms ?? [])
    : Array.isArray(researchEnforcement?.unsupported_terms)
      ? researchEnforcement.unsupported_terms
    : [];
  const researchGroundedAnswer = researchArtifact?.grounded_answer ?? sourceIntel?.grounded_answer;
  const researchGraph = researchArtifact?.graph ?? sourceIntel?.graph;
  const researchEvidence =
    researchArtifact?.evidence && researchArtifact.evidence.length > 0
      ? researchArtifact.evidence
      : sourceIntel?.sources && sourceIntel.sources.length > 0
        ? sourceIntel.sources.map((source) => ({
            id: String(source.id),
            name: source.name,
            scope: source.scope,
            snippet: source.content ?? source.status ?? "Indexed source signal.",
            match_terms: [],
          }))
      : sources.slice(0, 5).map((source) => ({
          name: source.name,
          scope: "scope" in source ? source.scope : "session",
          snippet: source.content ?? source.status ?? "Indexed source signal.",
          match_terms: [],
        }));
  const codeArtifact =
    latestArtifact?.kind === "code"
      ? latestArtifact
      : missionEvents
          .slice()
          .reverse()
          .find((event) => event.artifact?.kind === "code")
          ?.artifact ?? null;
  const codeTargetRows =
    codeArtifact?.file_signals && codeArtifact.file_signals.length > 0
      ? codeArtifact.file_signals.map((file) => ({
          path: file.path ?? "unknown",
          signal: file.matched_terms?.length ? `${file.matched_terms.length} matched terms` : file.extension ?? "signal",
          risk: file.line_count && file.line_count > 400 ? "High" : file.line_count && file.line_count > 160 ? "Medium" : "Low",
        }))
      : codeFiles;
  const codeVerificationRows =
    codeArtifact?.execution?.verification && codeArtifact.execution.verification.length > 0
      ? codeArtifact.execution.verification
      : [{ label: "Ledger", command: "Run a Code mission", status: "waiting", output: "Verification results will appear here." }];
  const codeEditRows = codeArtifact?.execution?.edits ?? [];
  const codeActionRows = codeArtifact?.execution?.next_actions ?? [];
  const diffLines = (gitDiffResult?.diff ?? "").split("\n");
  const diffRemoved = diffLines.filter((line) => line.startsWith("-") && !line.startsWith("---"));
  const diffAdded = diffLines.filter((line) => line.startsWith("+") && !line.startsWith("+++"));
  const codePatchRows =
    codeEditRows.length > 0
      ? codeEditRows.map((edit) => ({
          label: edit.path?.split("/").pop() ?? edit.tool ?? "edit",
          status: edit.status ?? "applied",
          key: `${edit.tool ?? "edit"}-${edit.path ?? edit.status ?? "row"}`,
        }))
      : codeTargetRows.map((file) => ({
          label: file.path.split("/").pop() ?? file.path,
          status: file.risk,
          key: file.path,
        }));
  const swarmArtifact =
    latestArtifact?.kind === "swarm"
      ? latestArtifact
      : missionEvents
          .slice()
          .reverse()
          .find((event) => event.artifact?.kind === "swarm")
          ?.artifact ?? null;
  const orchestrationFlow = [
    { agent: "Input", state: "Queued", detail: `${attachments.length} sources / ${messages.length} turns`, tone: "blue" },
    { agent: "Orion", state: isGenerating ? "Planning" : "Watching", detail: "Mission decomposition active", tone: "teal" },
    { agent: "Nova", state: sourceStats?.pending_sources ? "Retrying" : "Retrieving", detail: `${sourceStats?.total_sources ?? indexedSources.length} indexed sources`, tone: "amber" },
    { agent: "Vega", state: runtimeState === "online" ? "Critiquing" : "Blocked", detail: "Patch risk scan armed", tone: runtimeState === "online" ? "violet" : "danger" },
    { agent: "Lyra", state: activeModule === "voice" ? "Live" : "Synthesizing", detail: "Human-facing response layer", tone: "green" },
    { agent: "Memory", state: memoryUsage > 72 ? "Pressure" : "Indexing", detail: `${memoryTotal} recalled threads`, tone: memoryUsage > 72 ? "amber" : "teal" },
  ];

  const stopRealtimeVoice = () => {
    voiceDataChannelRef.current?.close();
    voiceDataChannelRef.current = null;

    peerConnectionRef.current?.getSenders().forEach((sender) => sender.track?.stop());
    peerConnectionRef.current?.close();
    peerConnectionRef.current = null;

    voiceStreamRef.current?.getTracks().forEach((track) => track.stop());
    voiceStreamRef.current = null;

    if (voiceAudioRef.current) {
      voiceAudioRef.current.srcObject = null;
      voiceAudioRef.current.remove();
      voiceAudioRef.current = null;
    }

    setVoiceState("idle");
  };

  const agentTimeline = [
    { actor: "Nova", status: "retrieval jitter", detail: "Source confidence dipped; retrying second-pass evidence.", risk: "warn" },
    { actor: "Vega", status: "conflict raised", detail: "Predicts backend instability if realtime bridge deploys without fallback.", risk: "danger" },
    { actor: "Orion", status: "approval gate", detail: "Execution risk moderate. Awaiting authorization before irreversible action.", risk: "warn" },
    { actor: "Lyra", status: "synthesis ready", detail: "Can convert this run into memory, plan, or spoken briefing.", risk: "ok" },
  ];

  useEffect(() => {
    let active = true;

    const restoreSession = async () => {
      try {
        const healthResult = await fetchWithTimeout(`${API_BASE_URL}/health`, {
          cache: "no-store",
        });
        const healthData = healthResult.ok ? (await healthResult.json()) as HealthStatus : null;
        const requiresToken = Boolean(healthData?.security?.token_auth_enabled) && !HELIOS_API_KEY;

        if (!active) return;
        setAuthRequired(requiresToken);

        if (!requiresToken) {
          setAuthChecking(false);
          return;
        }

        const meResult = await fetchWithTimeout(`${API_BASE_URL}/auth/me`, {
          cache: "no-store",
        });
        if (!meResult.ok) throw new Error("Session expired");

        const meData = (await meResult.json()) as { user?: AuthUser };
        if (!meData.user) throw new Error("Session user missing");

        if (!active) return;
        setAuthUser(meData.user);
      } catch {
        if (active) setAuthUser(null);
      } finally {
        if (active) setAuthChecking(false);
      }
    };

    void restoreSession();

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;

    const loadAiSettings = async () => {
      try {
        const result = await fetchWithTimeout(`${API_BASE_URL}/settings/ai`, {
          cache: "no-store",
        });

        if (!result.ok) return;

        const data = (await result.json()) as { provider?: string; model?: string };

        if (!active) return;

        setAiSettingsProvider(data.provider ?? "ollama");
        setAiSettingsModel(data.model ?? "");
      } catch {
        return;
      }
    };

    const loadHealth = async () => {
      try {
        const result = await fetchWithTimeout(`${API_BASE_URL}/health`, {
          cache: "no-store",
        });

        if (!result.ok) {
          throw new Error(`Health returned ${result.status}`);
        }

        const data = (await result.json()) as HealthStatus;

        if (!active) return;

        setHealth(data);
        setAiSettingsProvider((current) => current && current !== "ollama" ? current : (data.ai?.provider ?? "ollama"));
        setAiSettingsModel((current) => current || (data.ai?.model ?? ""));
        setAuthRequired(Boolean(data.security?.token_auth_enabled) && !HELIOS_API_KEY);
        setAgentActivity(data.missions?.agents ?? {});
        setLastTrace((current) => (current.length > 0 ? current : data.cognitive_engine?.trace ?? []));
        setLastPlan((current) => (current.length > 0 ? current : data.cognitive_engine?.plan ?? []));
        setRuntimeState(data.ai?.model_available ? "online" : "degraded");
      } catch {
        if (!active) return;
        setRuntimeState("offline");
      }
    };

    const loadSources = async () => {
      try {
        const result = await fetchWithTimeout(`${API_BASE_URL}/sources`, {
          cache: "no-store",
        });

        if (!result.ok) return;

        const data = (await result.json()) as SourcesResult;

        if (!active) return;

        setIndexedSources(data.sources ?? []);
      } catch {
        return;
      }
    };

    const loadMissionEvents = async () => {
      try {
        const result = await fetchWithTimeout(`${API_BASE_URL}/missions/events?limit=40`, {
          cache: "no-store",
        });

        if (!result.ok) return;

        const data = (await result.json()) as MissionEventsResult;

        if (!active) return;

        setMissionEvents(data.events ?? []);
        setMissions(data.missions ?? []);
        setActiveMissionId((current) => current ?? data.missions?.[0]?.id ?? null);
        setAgentActivity(data.agents ?? {});
      } catch {
        return;
      }
    };

    const loadExecutionEvents = async () => {
      try {
        const result = await fetchWithTimeout(`${API_BASE_URL}/execution/events?limit=40&event_type=tool_event`, {
          cache: "no-store",
        });

        if (!result.ok) return;

        const data = (await result.json()) as ExecutionEventsResult;

        if (!active) return;

        const events = (data.events ?? [])
          .map((event) => normalizeRunLedgerEvent(event as unknown as Record<string, unknown>))
          .reverse();

        setRunLedger((current) => {
          const merged = [...events, ...current];
          const seen = new Set<string>();

          return merged
            .filter((event) => {
              if (seen.has(event.id)) return false;
              seen.add(event.id);
              return true;
            })
            .slice(0, RUN_LEDGER_MAX_ENTRIES);
        });
      } catch {
        return;
      }
    };

    const loadProjectBrain = async () => {
      try {
        const result = await fetchWithTimeout(`${API_BASE_URL}/project/brain?limit=8`, {
          cache: "no-store",
        });

        if (!result.ok) return;

        const data = (await result.json()) as ProjectBrainResult;

        if (!active) return;

        setProjectBrain(data);
      } catch {
        return;
      }
    };

    const loadObservability = async () => {
      try {
        const result = await fetchWithTimeout(`${API_BASE_URL}/observability?limit=120`, {
          cache: "no-store",
        });

        if (!result.ok) return;

        const data = (await result.json()) as ObservabilityResult;

        if (!active) return;

        setObservability(data);
      } catch {
        return;
      }
    };

    const loadVoiceStatus = async () => {
      try {
        const result = await fetchWithTimeout(`${API_BASE_URL}/voice/status`, {
          cache: "no-store",
        });

        if (!result.ok) return;

        const data = (await result.json()) as VoiceStatusResult;

        if (!active) return;

        setVoiceStatusInfo(data);
      } catch {
        return;
      }
    };

    const loadConversationModes = async () => {
      try {
        const result = await fetchWithTimeout(`${API_BASE_URL}/conversation/modes`, {
          cache: "no-store",
        });
        if (!result.ok) return;
        const data = (await result.json()) as { modes?: ConversationModeConfig[] };
        if (active) setConversationModes(data.modes ?? []);
      } catch {
        return;
      }
    };

    const loadAutonomousRuns = async () => {
      try {
        const result = await fetchWithTimeout(`${API_BASE_URL}/autonomy/runs?limit=12`, {
          cache: "no-store",
        });

        if (!result.ok) return;

        const data = (await result.json()) as { runs?: AutonomousRun[] };

        if (!active) return;

        setAutonomousRuns((data.runs ?? []).reverse());
      } catch {
        return;
      }
    };

    const loadSwarmRuns = async () => {
      try {
        const result = await fetchWithTimeout(`${API_BASE_URL}/swarm/runs?limit=8`, {
          cache: "no-store",
        });
        if (!result.ok) return;
        const data = (await result.json()) as { runs?: IsolatedSwarmRun[] };
        if (active) setIsolatedSwarmRuns((data.runs ?? []).reverse());
      } catch {
        return;
      }
    };

    const loadPlugins = async () => {
      try {
        const result = await fetchWithTimeout(`${API_BASE_URL}/plugins`, {
          cache: "no-store",
        });
        if (!result.ok) return;
        const data = (await result.json()) as { plugins?: PluginRecord[] };
        if (active) setPlugins(data.plugins ?? []);
      } catch {
        return;
      }
    };

    void loadHealth();
    void loadAiSettings();
    void loadSources();
    void loadMissionEvents();
    void loadExecutionEvents();
    void loadProjectBrain();
    void loadObservability();
    void loadVoiceStatus();
    void loadConversationModes();
    void loadAutonomousRuns();
    void loadSwarmRuns();
    void loadPlugins();
    const timer = window.setInterval(loadHealth, 10000);
    const sourceTimer = window.setInterval(loadSources, 15000);
    const missionTimer = window.setInterval(loadMissionEvents, 12000);
    const executionTimer = window.setInterval(loadExecutionEvents, 8000);
    const brainTimer = window.setInterval(loadProjectBrain, 12000);
    const observabilityTimer = window.setInterval(loadObservability, 10000);
    const voiceTimer = window.setInterval(loadVoiceStatus, 20000);
    const autonomyTimer = window.setInterval(loadAutonomousRuns, 8000);
    const swarmTimer = window.setInterval(loadSwarmRuns, 8000);
    const pluginTimer = window.setInterval(loadPlugins, 30000);

    return () => {
      active = false;
      window.clearInterval(timer);
      window.clearInterval(sourceTimer);
      window.clearInterval(missionTimer);
      window.clearInterval(executionTimer);
      window.clearInterval(brainTimer);
      window.clearInterval(observabilityTimer);
      window.clearInterval(voiceTimer);
      window.clearInterval(autonomyTimer);
      window.clearInterval(swarmTimer);
      window.clearInterval(pluginTimer);
    };
  }, []);

  const saveAiSettings = async () => {
    setAiSettingsBusy(true);
    setAiSettingsStatus("Saving provider preference...");

    try {
      const result = await fetchWithTimeout(`${API_BASE_URL}/settings/ai`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          provider: aiSettingsProvider,
          model: aiSettingsModel,
        }),
      });

      if (!result.ok) throw new Error(`Save failed with ${result.status}`);

      const data = (await result.json()) as { provider?: string; model?: string };
      setAiSettingsProvider(data.provider ?? aiSettingsProvider);
      setAiSettingsModel(data.model ?? aiSettingsModel);
      setAiSettingsStatus(`Saved ${data.provider ?? aiSettingsProvider} preference${data.model ? ` for ${data.model}` : ""}.`);
      await fetchWithTimeout(`${API_BASE_URL}/health`, { cache: "no-store" });
    } catch (error) {
      setAiSettingsStatus(error instanceof Error ? error.message : "Unable to save provider preference.");
    } finally {
      setAiSettingsBusy(false);
    }
  };

  useEffect(() => {
    window.localStorage.setItem("helios-conversation-mode", conversationMode);
  }, [conversationMode]);

  useEffect(() => {
    const handleShortcut = (event: globalThis.KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setCommandOpen((open) => !open);
      }
    };

    window.addEventListener("keydown", handleShortcut);

    return () => window.removeEventListener("keydown", handleShortcut);
  }, []);

  useEffect(() => {
    let active = true;
    const query = activeMission?.title ?? activeModuleConfig.title;

    const loadSourceIntelligence = async () => {
      if (activeModule !== "research" && activeModule !== "knowledge") return;

      try {
        const params = new URLSearchParams({
          q: query,
          limit: "8",
        });
        const result = await fetchWithTimeout(`${API_BASE_URL}/sources/intelligence?${params.toString()}`, {
          cache: "no-store",
        });

        if (!result.ok) return;

        const data = (await result.json()) as SourceIntelligenceResult;

        if (!active) return;

        setSourceIntel(data);
      } catch {
        return;
      }
    };

    void loadSourceIntelligence();

    return () => {
      active = false;
    };
  }, [activeModule, activeModuleConfig.title, activeMission?.title, indexedSources.length]);

  useEffect(() => {
    if (!memoryOpen) return;

    void refreshMemoryItems();
  }, [memoryOpen]);

  useEffect(() => {
    return () => stopRealtimeVoice();
  }, []);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setRuntimeTick((current) => current + 1);
    }, 2400);

    return () => window.clearInterval(timer);
  }, []);

  useEffect(() => {
    let active = true;
    let socket: WebSocket | null = null;
    let retryTimer: number | null = null;
    let retryDelay = 1200;

    const scheduleReconnect = () => {
      if (!active) return;
      if (retryTimer) window.clearTimeout(retryTimer);
      retryTimer = window.setTimeout(() => {
        retryDelay = Math.min(retryDelay * 1.6, 12000);
        connect();
      }, retryDelay);
    };

    const connect = () => {
      if (!active) return;
      setRunLedgerStatus("connecting");

      try {
        socket = new WebSocket(RUN_LEDGER_WS_URL);
      } catch {
        setRunLedgerStatus("error");
        scheduleReconnect();
        return;
      }

      socket.onopen = () => {
        if (!active) return;
        retryDelay = 1200;
        setRunLedgerStatus("live");
      };

      socket.onmessage = (event) => {
        if (!active || typeof event.data !== "string") return;
        const entry = parseRunLedgerMessage(event.data);
        if (!entry) return;
        setRunLedger((current) => {
          if (current.some((item) => item.id === entry.id)) return current;
          return [entry, ...current].slice(0, RUN_LEDGER_MAX_ENTRIES);
        });
      };

      socket.onerror = () => {
        if (!active) return;
        setRunLedgerStatus("error");
      };

      socket.onclose = () => {
        if (!active) return;
        setRunLedgerStatus("offline");
        scheduleReconnect();
      };
    };

    connect();

    return () => {
      active = false;
      if (retryTimer) window.clearTimeout(retryTimer);
      if (socket && socket.readyState <= 1) socket.close();
    };
  }, []);

  const switchModule = (key: ModuleKey) => {
    const nextModule = modules.find((item) => item.key === key) ?? modules[0];
    const nextAgent = agents.find((agent) => agent.name === nextModule.agent) ?? agents[0];

    setActiveModule(key);
    setActiveTab(nextModule.tabs[0]);
    setActiveAgent(nextAgent.name);
  };

  const login = async () => {
    if (!loginUsername.trim() || !loginPassword || loginBusy) return;

    setLoginBusy(true);
    setLoginError("");

    try {
      const result = await fetchWithTimeout(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: loginUsername.trim(),
          password: loginPassword,
        }),
      });
      const data = (await result.json()) as AuthSession & { detail?: string };

      if (!result.ok || !data.token || !data.user) {
        throw new Error(data.detail ?? "Unable to sign in.");
      }

      setAuthUser(data.user);
      setLoginPassword("");
    } catch (error) {
      setLoginError(error instanceof Error ? error.message : "Unable to sign in.");
    } finally {
      setLoginBusy(false);
    }
  };

  const logout = () => {
    void fetchWithTimeout(`${API_BASE_URL}/auth/logout`, {
      method: "POST",
    }).catch(() => undefined);
    setAuthUser(null);
    setAccountOpen(false);
    setManagedUsers([]);
  };

  const loadManagedUsers = async () => {
    if (authUser?.role !== "admin") return;

    try {
      const result = await fetchWithTimeout(`${API_BASE_URL}/auth/users`, {
        cache: "no-store",
      });
      if (!result.ok) throw new Error(`Users returned ${result.status}`);
      const data = (await result.json()) as { users?: AuthUser[] };
      setManagedUsers(data.users ?? []);
    } catch {
      setUserAdminStatus("Unable to load users.");
    }
  };

  const openAccount = () => {
    setAccountOpen(true);
    setUserAdminStatus("");
    void loadManagedUsers();
  };

  const addManagedUser = async () => {
    if (!newUsername.trim() || !newPassword || authUser?.role !== "admin") return;

    setUserAdminStatus("Creating user...");
    try {
      const result = await fetchWithTimeout(`${API_BASE_URL}/auth/users`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: newUsername.trim(),
          password: newPassword,
          role: newRole,
        }),
      });
      const data = (await result.json()) as { user?: AuthUser; detail?: string };
      if (!result.ok || !data.user) throw new Error(data.detail ?? "Unable to create user.");

      setManagedUsers((current) => [...current, data.user as AuthUser]);
      setNewUsername("");
      setNewPassword("");
      setNewRole("viewer");
      setUserAdminStatus(`Created ${data.user.username}.`);
    } catch (error) {
      setUserAdminStatus(error instanceof Error ? error.message : "Unable to create user.");
    }
  };

  const attachFiles = async (files: FileList | File[]) => {
    const nextFiles = await Promise.all(
      Array.from(files).map(async (file) => {
        const type = file.type || file.name.split(".").pop()?.toUpperCase() || "FILE";
        const isTextSource =
          file.type.startsWith("text/") ||
          TEXT_SOURCE_EXTENSIONS.some((extension) =>
            file.name.toLowerCase().endsWith(extension),
          );
        const isPdf = file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf");
        const isDocx =
          file.type === "application/vnd.openxmlformats-officedocument.wordprocessingml.document" ||
          file.name.toLowerCase().endsWith(".docx");
        const canIndex = (isTextSource || isPdf || isDocx) && file.size <= MAX_SOURCE_FILE_BYTES * 4;

        let content = "";

        if (canIndex) {
          if (isPdf || isDocx) {
            // Convert binary documents to base64 for backend ingestion.
            const reader = new FileReader();
            content = await new Promise((resolve) => {
              reader.onload = () => {
                const base64 = (reader.result as string).split(",")[1];
                resolve(base64);
              };
              reader.readAsDataURL(file);
            });
          } else {
            content = (await file.text()).slice(0, MAX_SOURCE_CONTENT_CHARS);
          }
        }

        return {
          id: idRef.current++,
          name: file.name,
          size: formatFileSize(file.size),
          type: isPdf ? "PDF" : isDocx ? "DOCX" : type,
          content,
          status: content ? "Ready" : isTextSource || isPdf || isDocx ? "Too large" : "Attached",
        };
      }),
    );

    setAttachments((current) => [...current, ...nextFiles]);

    const persisted = await Promise.all(
      nextFiles
        .filter((file) => file.content)
        .map(async (file) => {
          try {
            const result = await fetchWithTimeout(`${API_BASE_URL}/sources`, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({
                name: file.name,
                type: file.type,
                size: file.size,
                content: file.content,
                scope: "project",
              }),
            });

            if (!result.ok) return null;

            const data = (await result.json()) as { source?: KnowledgeSource };

            return data.source ?? null;
          } catch {
            return null;
          }
        }),
    );

    const savedSources = persisted.filter((source): source is KnowledgeSource => Boolean(source));

    if (savedSources.length > 0) {
      setIndexedSources((current) => {
        const next = [...current];

        for (const source of savedSources) {
          const index = next.findIndex((item) => item.id === source.id);

          if (index >= 0) next[index] = source;
          else next.push(source);
        }

        return next;
      });
    }
  };

  const ingestSourceUrl = async () => {
    const cleanUrl = sourceUrl.trim();
    if (!cleanUrl || sourceUrlBusy) return;
    setSourceUrlBusy(true);
    try {
      const result = await fetchWithTimeout(`${API_BASE_URL}/sources`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: cleanUrl,
          type: sourceUrlType,
          size: "remote",
          content: cleanUrl,
          scope: "project",
        }),
      }, REQUEST_TIMEOUT_MS * 3);
      if (!result.ok) throw new Error(`Source ingestion returned ${result.status}`);
      const data = (await result.json()) as { source?: KnowledgeSource };
      if (data.source) {
        setIndexedSources((current) => [
          data.source as KnowledgeSource,
          ...current.filter((item) => item.id !== data.source?.id),
        ]);
      }
      setSourceUrl("");
    } catch {
      setRuntimeState("degraded");
    } finally {
      setSourceUrlBusy(false);
    }
  };

  const removeSource = async (source: KnowledgeSource) => {
    if (!window.confirm(`Remove source "${source.name}" from the indexed library?`)) return;

    try {
      const result = await fetchWithTimeout(`${API_BASE_URL}/sources/${encodeURIComponent(String(source.id))}`, {
        method: "DELETE",
      });

      const data = (await result.json()) as { detail?: string };

      if (!result.ok) throw new Error(data.detail ?? `Source removal returned ${result.status}`);

      setIndexedSources((current) => current.filter((item) => item.id !== source.id));
      setSourceIntel(null);
    } catch (error) {
      setRuntimeState("degraded");
      window.alert(error instanceof Error ? error.message : "Unable to remove source.");
    }
  };

  const reindexSource = async (source: KnowledgeSource) => {
    try {
      const result = await fetchWithTimeout(`${API_BASE_URL}/sources/${encodeURIComponent(String(source.id))}/reindex`, {
        method: "POST",
      });
      const data = (await result.json()) as { source?: KnowledgeSource; detail?: string };

      if (!result.ok) throw new Error(data.detail ?? `Source reindex returned ${result.status}`);

      if (data.source) {
        setIndexedSources((current) => [
          data.source as KnowledgeSource,
          ...current.filter((item) => item.id !== data.source?.id),
        ]);
      }
    } catch (error) {
      setRuntimeState("degraded");
      window.alert(error instanceof Error ? error.message : "Unable to reindex source.");
    }
  };

  const refreshPlugins = async () => {
    const result = await fetchWithTimeout(`${API_BASE_URL}/plugins`, {
      cache: "no-store",
    });
    if (!result.ok) throw new Error(`Plugins returned ${result.status}`);
    const data = (await result.json()) as { plugins?: PluginRecord[] };
    setPlugins(data.plugins ?? []);
  };

  const uploadPlugin = async () => {
    if (!pluginName.trim() || !pluginCode.trim()) return;
    setPluginStatus("Uploading and verifying plugin...");
    try {
      const result = await fetchWithTimeout(`${API_BASE_URL}/plugins/upload`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: pluginName.trim(),
          version: pluginVersion.trim() || "1.0.0",
          description: pluginDescription.trim(),
          code: pluginCode,
          dependencies: [],
        }),
      });
      const data = (await result.json()) as { message?: string; detail?: string };
      if (!result.ok) throw new Error(data.detail ?? `Plugin upload returned ${result.status}`);
      setPluginStatus(data.message ?? "Plugin uploaded.");
      setPluginName("");
      setPluginDescription("");
      setPluginCode("");
      await refreshPlugins();
    } catch (error) {
      setPluginStatus(error instanceof Error ? error.message : "Plugin upload failed.");
    }
  };

  const removePlugin = async (plugin: PluginRecord) => {
    if (!window.confirm(`Uninstall plugin "${plugin.name}"?`)) return;
    const result = await fetchWithTimeout(`${API_BASE_URL}/plugins/${encodeURIComponent(plugin.filename)}`, {
      method: "DELETE",
    });
    const data = (await result.json()) as { message?: string; detail?: string };
    if (!result.ok) throw new Error(data.detail ?? `Plugin uninstall returned ${result.status}`);
    setPluginStatus(data.message ?? "Plugin uninstalled.");
    await refreshPlugins();
  };

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) void attachFiles(event.target.files);
    event.target.value = "";
  };

  const stopGeneration = () => {
    if (generationRef.current) window.clearInterval(generationRef.current);
    requestRef.current?.abort();
    requestRef.current = null;
    generationRef.current = null;
    setIsGenerating(false);
  };

  const exportThread = () => {
    const body = messages
      .map((message) => `${message.role.toUpperCase()}: ${message.text}`)
      .join("\n\n");
    const blob = new Blob([body], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = "helios-thread.txt";
    link.click();
    URL.revokeObjectURL(url);
  };

  const exportJson = (filename: string, value: unknown) => {
    const blob = new Blob([JSON.stringify(value, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  };

  const exportProjectData = async (kind: "memory" | "sources" | "project-brain" | "report") => {
    const result = await fetchWithTimeout(`${API_BASE_URL}/exports/${kind}`, {
      cache: "no-store",
    });
    if (!result.ok) throw new Error(`Export ${kind} returned ${result.status}`);
    exportJson(`helios-${kind}.json`, await result.json());
  };

  async function refreshMemoryItems() {
    setMemoryBusy(true);
    setMemoryStatus("Loading memory...");

    try {
      const result = await fetchWithTimeout(`${API_BASE_URL}/memory`, {
        cache: "no-store",
      });

      if (!result.ok) throw new Error(`Memory returned ${result.status}`);

      const data = (await result.json()) as { items?: Array<Record<string, unknown>>; total?: number };
      setMemoryItems(data.items ?? []);
      setMemoryStatus(`${data.total ?? 0} conversation turns available for inspection.`);
    } catch (error) {
      setMemoryStatus(error instanceof Error ? error.message : "Unable to load memory.");
    } finally {
      setMemoryBusy(false);
    }
  }

  const deleteMemoryItem = async (index: number) => {
    try {
      const result = await fetchWithTimeout(`${API_BASE_URL}/memory/${index}`, {
        method: "DELETE",
      });

      if (!result.ok) throw new Error(`Delete returned ${result.status}`);
      await refreshMemoryItems();
    } catch (error) {
      setMemoryStatus(error instanceof Error ? error.message : "Unable to delete memory item.");
    }
  };

  const openMissionComposer = (module = activeModule, agent = selectedAgent.name, title = "") => {
    stopGeneration();
    setMessages(initialMessages);
    setInput("");
    setAttachments([]);
    setMissionTitle(title);
    setMissionModule(module);
    setMissionAgent(agent);
    setMissionScheduledAt("");
    setMissionOpen(true);
  };

  const createMission = async (
    title = missionTitle,
    module = missionModule,
    agent = missionAgent,
    scheduledAt = missionScheduledAt,
  ) => {
    const cleanTitle = title.trim();
    if (!cleanTitle || isCreatingMission) return;

    setIsCreatingMission(true);

    try {
      const scheduledTimestamp = scheduledAt ? Date.parse(scheduledAt) / 1000 : null;
      const isScheduled = scheduledTimestamp !== null && Number.isFinite(scheduledTimestamp);
      const result = await fetchWithTimeout(`${API_BASE_URL}${isScheduled ? "/missions/schedule" : "/missions"}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(HELIOS_API_KEY ? { "x-helios-api-key": HELIOS_API_KEY } : {}),
        },
        body: JSON.stringify({
          title: cleanTitle,
          module,
          agent,
          detail: isScheduled
            ? "Scheduled from the HELIOS mission composer."
            : "Created from the premium HELIOS mission composer.",
          ...(isScheduled ? { scheduled_at: scheduledTimestamp } : {}),
        }),
      });

      if (!result.ok) throw new Error(`Mission returned ${result.status}`);

      const data = (await result.json()) as MissionCreateResult;

      if (!isScheduled) {
        setMissionEvents((current) => [...current, ...(data.events ?? [])].slice(-80));
        setAgentActivity(data.agents ?? {});
      }
      if (!isScheduled && data.mission?.id) {
        const summary = {
          id: data.mission.id,
          title: data.mission.title ?? cleanTitle,
          agent: data.mission.agent,
          module: data.mission.module,
          status: data.mission.status,
          stage: "Assigned",
          event_count: 2,
        };

        setMissions((current) => [summary, ...current.filter((mission) => mission.id !== summary.id)].slice(0, 12));
        setActiveMissionId(data.mission.id);
      }
      setMissionOpen(false);
      setMissionTitle("");
      setMissionScheduledAt("");
      switchModule(module);
      setActiveAgent(agent);
      setInput(cleanTitle);
      if (isScheduled) {
        setCommandStatus(`Mission scheduled for ${new Date((scheduledTimestamp as number) * 1000).toLocaleString()}.`);
      }
    } catch {
      setRuntimeState("degraded");
    } finally {
      setIsCreatingMission(false);
    }
  };

  const launchMissionPreset = (label: string, module: ModuleKey, agent: string) => {
    setMissionTitle(label);
    setMissionModule(module);
    setMissionAgent(agent);
    setMissionOpen(true);
  };

  const advanceMission = async (stage: string) => {
    if (!activeMission || advancingMissionStage) return;

    setAdvancingMissionStage(stage);

    try {
      const result = await fetchWithTimeout(`${API_BASE_URL}/missions/${activeMission.id}/advance`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(HELIOS_API_KEY ? { "x-helios-api-key": HELIOS_API_KEY } : {}),
        },
        body: JSON.stringify({
          stage,
          detail: `Mission advanced to ${stage} from HELIOS command field.`,
        }),
      });

      if (!result.ok) throw new Error(`Mission advance returned ${result.status}`);

      const data = (await result.json()) as MissionAdvanceResult;

      if (data.event) {
        setMissionEvents((current) => [...current, data.event as MissionEvent].slice(-80));
      }

      setMissions(data.missions ?? []);
      setAgentActivity(data.agents ?? {});
      setActiveMissionId(data.mission?.id ?? activeMission.id);
    } catch {
      setRuntimeState("degraded");
    } finally {
      setAdvancingMissionStage("");
    }
  };

  const runMissionWorkflow = async () => {
    if (!activeMission || advancingMissionStage) return;

    setAdvancingMissionStage("Run");

    try {
      const result = await fetchWithTimeout(`${API_BASE_URL}/missions/${activeMission.id}/run`, {
        method: "POST",
      }, REQUEST_TIMEOUT_MS * 2);

      if (!result.ok) throw new Error(`Mission run returned ${result.status}`);

      const data = (await result.json()) as MissionRunResult;

      if (data.event) {
        setMissionEvents((current) => [...current, data.event as MissionEvent].slice(-80));
      }

      setMissionArtifact(data.artifact ?? null);
      setMissionTask(data.task ?? null);
      setMissions(data.missions ?? []);
      setAgentActivity(data.agents ?? {});
      setActiveMissionId(data.mission?.id ?? activeMission.id);
    } catch {
      setRuntimeState("degraded");
    } finally {
      setAdvancingMissionStage("");
    }
  };

  const createAutonomousRun = async (objective = autonomyObjective) => {
    if (!objective.trim() || autonomyBusy) return;

    setAutonomyBusy(true);
    try {
      const result = await fetchWithTimeout(`${API_BASE_URL}/autonomy/runs`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          objective: objective.trim(),
        }),
      });
      if (!result.ok) throw new Error(`Autonomous run returned ${result.status}`);
      const data = (await result.json()) as { run?: AutonomousRun };
      if (data.run) setAutonomousRuns((current) => [data.run as AutonomousRun, ...current]);
      setAutonomyObjective("");
    } catch {
      setRuntimeState("degraded");
    } finally {
      setAutonomyBusy(false);
    }
  };

  const updateAutonomousRun = async (runId: string, action: "cancel" | "resume") => {
    try {
      const result = await fetchWithTimeout(`${API_BASE_URL}/autonomy/runs/${runId}/${action}`, {
        method: "POST",
      });
      if (!result.ok) throw new Error(`Autonomous ${action} returned ${result.status}`);
      const data = (await result.json()) as { run?: AutonomousRun };
      if (data.run) {
        setAutonomousRuns((current) => current.map((run) => (run.id === runId ? data.run as AutonomousRun : run)));
      }
    } catch {
      setRuntimeState("degraded");
    }
  };

  const createIsolatedSwarmRun = async (objective = swarmObjective) => {
    if (!objective.trim() || swarmBusy) return;
    setSwarmBusy(true);
    try {
      const result = await fetchWithTimeout(`${API_BASE_URL}/swarm/runs`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          objective: objective.trim(),
          conversation_context: "Started from the Next.js Swarm Intelligence workspace.",
        }),
      });
      if (!result.ok) throw new Error(`Swarm run returned ${result.status}`);
      const data = (await result.json()) as { run?: IsolatedSwarmRun };
      if (data.run) setIsolatedSwarmRuns((current) => [data.run as IsolatedSwarmRun, ...current]);
      setSwarmObjective("");
    } catch {
      setRuntimeState("degraded");
    } finally {
      setSwarmBusy(false);
    }
  };

  const runAutomaticCodeRepair = async () => {
    const targets = codeRepairTargets
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);
    if (!codeRepairObjective.trim() || targets.length === 0 || codeRepairBusy) return;

    setCodeRepairBusy(true);
    try {
      const result = await fetchWithTimeout(`${API_BASE_URL}/code/repair/auto`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          objective: codeRepairObjective.trim(),
          target_files: targets,
          repair_attempts: 3,
        }),
      }, REQUEST_TIMEOUT_MS * 4);
      if (!result.ok) throw new Error(`Code repair returned ${result.status}`);
      const data = (await result.json()) as Record<string, unknown>;
      const attempts = Array.isArray(data.attempts) ? data.attempts : [];
      const latest = attempts.length > 0 ? attempts[attempts.length - 1] as { repair?: MissionArtifact["execution"] } : null;
      setMissionArtifact({
        kind: "code",
        summary: data.status === "completed" ? "Automatic code repair completed and verified." : "Automatic code repair stopped with unresolved verification failures.",
        target_files: targets,
        execution: latest?.repair ?? {
          mode: "general_code_repair",
          blockers: Array.isArray(data.blockers) ? data.blockers as string[] : [],
          commit_ready: Boolean(data.commit_ready),
          action_required: Boolean(data.action_required),
          next_actions: Array.isArray(data.next_actions) ? data.next_actions as string[] : [],
        },
      });
      switchModule("code");
    } catch {
      setRuntimeState("degraded");
    } finally {
      setCodeRepairBusy(false);
    }
  };

  const loadGitDiff = async (staged = false) => {
    try {
      const result = await fetchWithTimeout(`${API_BASE_URL}/git/diff?staged=${staged ? "true" : "false"}`, {
        cache: "no-store",
      });
      if (!result.ok) throw new Error(`Git diff returned ${result.status}`);
      setGitDiffResult((await result.json()) as GitDiffResult);
    } catch {
      setRuntimeState("degraded");
    }
  };

  const runGitOperation = async (
    endpoint: "stage" | "branch" | "commit" | "push" | "rollback",
    payload: Record<string, unknown>,
    prompt: string,
  ) => {
    if (gitOperationBusy || !window.confirm(prompt)) return;
    setGitOperationBusy(true);
    setGitOperationStatus(`Running git ${endpoint}...`);
    try {
      const result = await fetchWithTimeout(`${API_BASE_URL}/git/${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ...payload,
          confirm: true,
        }),
      });
      const data = (await result.json()) as {
        status?: string;
        reason?: string;
        stdout?: string;
        stderr?: string;
      };
      if (!result.ok) throw new Error(data.reason ?? `Git ${endpoint} returned ${result.status}`);
      setGitOperationStatus(
        [data.status, data.reason, data.stdout, data.stderr].filter(Boolean).join(" | ") || `Git ${endpoint} completed.`,
      );
      await loadGitDiff(endpoint === "stage");
    } catch (error) {
      setGitOperationStatus(error instanceof Error ? error.message : `Git ${endpoint} failed.`);
      setRuntimeState("degraded");
    } finally {
      setGitOperationBusy(false);
    }
  };

  const executeApprovedTool = async (payload: Record<string, unknown>) => {
    const requestTool = async (approvalId?: string) => {
      const result = await fetchWithTimeout(`${API_BASE_URL}/tools/execute`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ...payload,
          ...(approvalId ? { approval_id: approvalId } : {}),
        }),
      }, REQUEST_TIMEOUT_MS * 20);
      const data = (await result.json()) as {
        status?: string;
        result?: unknown;
        error?: string;
        detail?: string;
        approval?: {
          approval_id?: string;
          status?: string;
        };
      };
      if (!result.ok) throw new Error(data.detail ?? `Tool execution returned ${result.status}`);
      return data;
    };

    const first = await requestTool();
    if (first.status !== "approval_required") return first;

    const approvalId = first.approval?.approval_id;
    if (!approvalId) throw new Error("Approval was required but no approval id was returned.");

    const approval = await fetchWithTimeout(`${API_BASE_URL}/approvals/${encodeURIComponent(approvalId)}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        status: "approved",
      }),
    });
    if (!approval.ok) throw new Error(`Approval returned ${approval.status}`);

    return requestTool(approvalId);
  };

  const runTerminalCommand = async () => {
    if (!terminalCommand.trim() || terminalBusy) return;
    setTerminalBusy(true);
    try {
      const data = await executeApprovedTool({
        tool: "run_command",
        args: [terminalCommand.trim()],
        module: "code",
      });
      setTerminalOutput(typeof data.result === "string" ? data.result : JSON.stringify(data.result ?? data.error ?? "", null, 2));
    } catch {
      setTerminalOutput("Terminal command failed.");
    } finally {
      setTerminalBusy(false);
    }
  };

  const deployProject = async () => {
    if (!window.confirm("Deploy HELIOS from origin/main and rebuild the production containers?")) return;
    try {
      const data = await executeApprovedTool({
        tool: "deploy_project",
        args: [],
        module: "dashboard",
      }) as { status?: string; result?: { stdout?: string; error?: string }; detail?: string };
      setCommandStatus(`Deployment ${data.status ?? "triggered"}: ${data.result?.stdout || data.result?.error || ""}`);
      setDeployOpen(false);
    } catch (error) {
      setCommandStatus(error instanceof Error ? error.message : "Deployment failed.");
    }
  };

  const recoverActiveMission = async () => {
    if (!activeMission) return;
    try {
      const result = await fetchWithTimeout(`${API_BASE_URL}/missions/${activeMission.id}/recover`, {
        method: "POST",
      });
      if (!result.ok) throw new Error(`Mission recovery returned ${result.status}`);
      const data = (await result.json()) as MissionAdvanceResult & { checkpoint?: MissionArtifact };
      setMissions(data.missions ?? []);
      setAgentActivity(data.agents ?? {});
      setMissionArtifact(data.checkpoint ?? missionArtifact);
    } catch {
      setRuntimeState("degraded");
    }
  };

  const exportActiveMission = async () => {
    if (!activeMission) return;
    try {
      const result = await fetchWithTimeout(`${API_BASE_URL}/missions/${activeMission.id}/export`, {
        cache: "no-store",
      });
      if (!result.ok) throw new Error(`Mission export returned ${result.status}`);
      const payload = await result.text();
      const blob = new Blob([payload], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${activeMission.title.replace(/[^a-z0-9]+/gi, "-").toLowerCase() || "mission"}.json`;
      link.click();
      URL.revokeObjectURL(url);
    } catch {
      setRuntimeState("degraded");
    }
  };

  const refreshExecutionEvents = async () => {
    const result = await fetchWithTimeout(`${API_BASE_URL}/execution/events?limit=40&event_type=tool_event`, {
      cache: "no-store",
    });
    if (!result.ok) throw new Error(`Execution log returned ${result.status}`);
    const data = (await result.json()) as ExecutionEventsResult;
    setRunLedger((data.events ?? []).map((event) => normalizeRunLedgerEvent(event as unknown as Record<string, unknown>)).reverse());
  };

  const retrySelectedExecution = async () => {
    if (!selectedExecution?.tool) return;
    const input = selectedExecution.input as { args?: unknown[]; kwargs?: Record<string, unknown> } | undefined;
    const result = await fetchWithTimeout(`${API_BASE_URL}/tools/execute`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        tool: selectedExecution.tool,
        args: input?.args ?? [],
        kwargs: input?.kwargs ?? {},
        module: selectedExecution.module ?? "dashboard",
        confirm: true,
      }),
    });
    if (!result.ok) throw new Error(`Tool retry returned ${result.status}`);
    await refreshExecutionEvents();
  };

  const runLauncherCommand = async (command: CommandDefinition) => {
    if (runningCommandId) return;

    setRunningCommandId(command.id);
    setCommandStatus(`Running ${command.label}...`);

    try {
      if (command.id === "mission:create") {
        openMissionComposer();
        setCommandStatus("Mission composer opened.");
        setCommandOpen(false);
        return;
      }

      if (command.id === "mission:run") {
        await runMissionWorkflow();
        setCommandStatus("Mission workflow triggered.");
        setCommandOpen(false);
        return;
      }

      if (command.id === "mission:research") {
        const title = commandQuery.trim() || "Source-grounded research mission";
        await createMission(title, "research", "Nova");
        setCommandStatus("Research mission created.");
        setCommandOpen(false);
        return;
      }

      if (command.id === "mission:code") {
        const title = commandQuery.trim() || "Run bounded code verification";
        await createMission(title, "code", "Vega");
        setCommandStatus("Code mission created.");
        setCommandOpen(false);
        return;
      }

      if (command.id === "mission:recover") {
        await recoverActiveMission();
        setCommandStatus("Active mission recovered from its latest checkpoint.");
        setCommandOpen(false);
        return;
      }

      if (command.id === "mission:export") {
        await exportActiveMission();
        setCommandStatus("Active mission exported.");
        setCommandOpen(false);
        return;
      }

      if (command.id === "autonomy:queue") {
        await createAutonomousRun(commandQuery.trim());
        setCommandStatus("Autonomous run queued.");
        setCommandOpen(false);
        return;
      }

      if (command.id === "swarm:queue") {
        await createIsolatedSwarmRun(commandQuery.trim());
        setCommandStatus("Isolated swarm queued.");
        setCommandOpen(false);
        return;
      }

      if (command.id === "code:auto") {
        switchModule("code");
        setCommandStatus("Use the repair objective and target files in the Code workspace.");
        setCommandOpen(false);
        return;
      }

      if (command.id === "source:intel") {
        const query = activeMission?.title || commandQuery.trim() || activeModuleConfig.title;
        const params = new URLSearchParams({
          q: query,
          limit: "8",
        });
        const result = await fetchWithTimeout(`${API_BASE_URL}/sources/intelligence?${params.toString()}`, {
          cache: "no-store",
        });

        if (!result.ok) throw new Error(`Source intelligence returned ${result.status}`);

        const data = (await result.json()) as SourceIntelligenceResult;

        setSourceIntel(data);
        switchModule("research");
        setCommandStatus(`Source intelligence loaded: ${data.citations?.length ?? 0} citation(s).`);
        setCommandOpen(false);
        return;
      }

      if (command.id === "tool:status") {
        const result = await fetchWithTimeout(`${API_BASE_URL}/tools/execute`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            tool: "run_command",
            args: ["git status --short"],
            module: "dashboard",
          }),
        });

        if (!result.ok) throw new Error(`Tool execution returned ${result.status}`);

        const data = (await result.json()) as { events?: RunLedgerEvent[]; status?: string };
        const events = (data.events ?? []).map((event) => normalizeRunLedgerEvent(event as unknown as Record<string, unknown>));

        setRunLedger((current) => [...events.reverse(), ...current].slice(0, RUN_LEDGER_MAX_ENTRIES));
        setCommandStatus(`Git status ${data.status ?? "completed"}.`);
        setCommandOpen(false);
        return;
      }

      if (command.id === "tool:execute") {
        const [toolName, ...rawArgs] = commandQuery.trim().split(/\s+/);
        if (!toolName) throw new Error("Enter a tool name and optional JSON args array.");
        const argsText = rawArgs.join(" ").trim();
        const args = argsText ? JSON.parse(argsText) : [];
        if (!Array.isArray(args)) throw new Error("Tool arguments must be a JSON array.");
        const data = await executeApprovedTool({
          tool: toolName,
          args,
          module: activeModule,
        }) as { events?: RunLedgerEvent[]; status?: string; result?: { reason?: string } };
        const events = (data.events ?? []).map((event) => normalizeRunLedgerEvent(event as unknown as Record<string, unknown>));
        setRunLedger((current) => [...events.reverse(), ...current].slice(0, RUN_LEDGER_MAX_ENTRIES));
        setCommandStatus(`${toolName} ${data.status ?? "completed"}.`);
        setCommandOpen(false);
        return;
      }

      if (command.id === "git:preview" || command.id === "git:commit") {
        const message = commandQuery.trim() || "HELIOS checkpoint";
        const result = await fetchWithTimeout(`${API_BASE_URL}/git/commit`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message,
            confirm: command.id === "git:commit",
          }),
        });

        if (!result.ok) throw new Error(`Git commit flow returned ${result.status}`);

        const data = (await result.json()) as {
          status?: string;
          reason?: string;
          stdout?: string;
          stderr?: string;
          git?: {
            staged?: string[];
            changed?: string[];
          };
        };

        const stagedCount = data.git?.staged?.length ?? 0;
        setCommandStatus(
          data.status === "success"
            ? data.stdout || "Commit completed."
            : `${data.status ?? "preview"}: ${data.reason ?? `${stagedCount} staged file(s).`}`,
        );
        setRunLedger((current) => [
          {
            id: `${Date.now()}-git-${command.id}`,
            label: command.label,
            actor: "HELIOS Git",
            module: "code",
            tool: "git",
            status: data.status,
            detail: data.reason ?? data.stdout ?? data.stderr ?? `${stagedCount} staged file(s).`,
            timestamp: new Date().toISOString(),
          },
          ...current,
        ].slice(0, RUN_LEDGER_MAX_ENTRIES));

        if (command.id === "git:commit" && data.status === "success") setCommandOpen(false);
        return;
      }

      if (command.id === "git:stage") {
        const paths = commandQuery.split(",").map((path) => path.trim()).filter(Boolean);
        await runGitOperation("stage", { paths }, `Stage ${paths.length} selected path(s)?`);
        setCommandOpen(false);
        return;
      }

      if (command.id === "git:branch") {
        await runGitOperation("branch", { name: commandQuery.trim() }, `Create and switch to branch "${commandQuery.trim()}"?`);
        setCommandOpen(false);
        return;
      }

      if (command.id === "git:push") {
        await runGitOperation("push", { branch: commandQuery.trim(), remote: "origin" }, `Push "${commandQuery.trim()}" to origin?`);
        setCommandOpen(false);
        return;
      }

      if (command.id === "git:rollback") {
        await runGitOperation("rollback", { commit: commandQuery.trim() }, `Create a revert commit for ${commandQuery.trim()}?`);
        setCommandOpen(false);
        return;
      }

      if (command.id === "open:swarm") switchModule("swarm");
      if (command.id === "open:memory") setMemoryOpen(true);
      if (command.id === "open:voice") switchModule("voice");
      if (command.id === "source:upload") {
        switchModule("knowledge");
        fileInputRef.current?.click();
      }
      if (command.id === "source:url") switchModule("knowledge");
      if (command.id === "voice:fallback") {
        switchModule("voice");
        setVoiceTranscriptOpen(true);
      }
      if (command.id.startsWith("mode:")) {
        const mode = command.id.slice(5) as ConversationMode;
        setConversationMode(mode);
      }
      if (command.id === "thread:export") exportThread();
      if (command.id === "export:memory") await exportProjectData("memory");
      if (command.id === "export:sources") await exportProjectData("sources");
      if (command.id === "export:brain") await exportProjectData("project-brain");
      if (command.id === "export:report") await exportProjectData("report");

      if (command.id === "deploy:project") {
        setDeployOpen(true);
        setCommandOpen(false);
        return;
      }

      setCommandStatus(`${command.label} completed.`);
      setCommandOpen(false);
    } catch (error) {
      setCommandStatus(error instanceof Error ? error.message : "Command failed.");
      setRuntimeState("degraded");
    } finally {
      setRunningCommandId(null);
    }
  };

  const generateAssistantReply = async (text: string, uploadedFiles: Attachment[]) => {
    const replyId = idRef.current++;
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS * 2);

    setMessages((current) => [...current, { id: replyId, role: "assistant", text: "" }]);
    setIsGenerating(true);
    requestRef.current = controller;

    try {
      const streamed = await new Promise<boolean>((resolve, reject) => {
        let socket: WebSocket | null = null;
        let receivedDelta = false;
        let completed = false;
        const closeSocket = () => {
          if (socket && socket.readyState <= WebSocket.OPEN) socket.close();
          socket = null;
        };
        const abortStreaming = () => {
          closeSocket();
          reject(new Error("Streaming chat was stopped."));
        };

        controller.signal.addEventListener("abort", abortStreaming, { once: true });

        try {
          socket = new WebSocket(CHAT_WS_URL);
        } catch (error) {
          controller.signal.removeEventListener("abort", abortStreaming);
          reject(error);
          return;
        }

        socket.addEventListener("open", () => {
          socket?.send(JSON.stringify({
            message: text || "Attached files",
            module: activeModuleConfig.key,
            agent: selectedAgent.name,
            mode: conversationMode,
            attachments: uploadedFiles,
            stream: true,
          }));
        });

        socket.addEventListener("message", (event) => {
          try {
            const payload = JSON.parse(event.data) as { type?: string; delta?: string; response?: string; trace?: CognitiveTrace[]; plan?: PlanStep[] };

            if (payload.type === "chat.delta" && typeof payload.delta === "string") {
              receivedDelta = true;
              setMessages((current) =>
                current.map((message) => (message.id === replyId ? { ...message, text: `${message.text}${payload.delta}` } : message)),
              );
            }

            if (payload.type === "chat.done") {
              completed = true;
              setLastTrace(payload.trace ?? []);
              setLastPlan(payload.plan ?? []);
              setLastRunAt(new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }));
              setRuntimeState("online");
              controller.signal.removeEventListener("abort", abortStreaming);
              closeSocket();
              resolve(true);
            }
          } catch {
            if (typeof event.data === "string") {
              receivedDelta = true;
              setMessages((current) =>
                current.map((message) => (message.id === replyId ? { ...message, text: `${message.text}${event.data}` } : message)),
              );
            }
          }
        });

        socket.addEventListener("error", () => {
          controller.signal.removeEventListener("abort", abortStreaming);
          reject(new Error("Streaming chat socket failed."));
        });

        socket.addEventListener("close", () => {
          controller.signal.removeEventListener("abort", abortStreaming);
          if (!completed && !receivedDelta) reject(new Error("Streaming chat socket closed before response."));
          else if (!completed) resolve(receivedDelta);
        });
      });

      if (streamed) {
        window.clearTimeout(timeout);
        requestRef.current = null;
        setIsGenerating(false);
        return;
      }
    } catch {
      setMessages((current) =>
        current.map((message) => (message.id === replyId ? { ...message, text: "" } : message)),
      );
    }

    try {
      const result = await fetchWithTimeout(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: text || "Attached files",
          module: activeModuleConfig.key,
          agent: selectedAgent.name,
          mode: conversationMode,
          attachments: uploadedFiles,
        }),
        signal: controller.signal,
      });

      if (!result.ok) {
        throw new Error(`Backend returned ${result.status}`);
      }

      const data = (await result.json()) as ChatResult;
      const reply = data.response || "HELIOS returned an empty response.";

      setLastTrace(data.trace ?? []);
      setLastPlan(data.plan ?? []);
      setLastRunAt(new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }));
      setRuntimeState("online");

      setMessages((current) =>
        current.map((message) => (message.id === replyId ? { ...message, text: reply } : message)),
      );
    } catch {
      if (controller.signal.aborted) {
        setMessages((current) =>
          current.map((message) =>
            message.id === replyId
              ? {
                  ...message,
                  text: "Request stopped or timed out. Nothing was changed; send it again when the backend is ready.",
                }
              : message,
          ),
        );
        setRuntimeState("degraded");
        return;
      }

      setMessages((current) =>
        current.map((message) =>
          message.id === replyId
            ? {
                ...message,
                text: `Backend is not reachable yet. Start the FastAPI server on port 8000, then resend: "${text || "attached files"}".`,
              }
            : message,
        ),
      );
      setRuntimeState("offline");
    } finally {
      window.clearTimeout(timeout);
      requestRef.current = null;
      setIsGenerating(false);
    }
  };

  const sendMessage = () => {
    const trimmed = input.trim();
    if ((!trimmed && attachments.length === 0) || isGenerating) return;
    const outgoingAttachments = attachments;

    setMessages((current) => [
      ...current,
      {
        id: idRef.current++,
        role: "user",
        text: trimmed || "Attached files",
        attachments,
      },
    ]);
    setInput("");
    setAttachments([]);
    generateAssistantReply(trimmed, outgoingAttachments);
  };

  const handleDrop = (event: DragEvent<HTMLElement>) => {
    event.preventDefault();
    setIsDragging(false);
    void attachFiles(event.dataTransfer.files);
    switchModule("knowledge");
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  const addVoiceTurn = (role: VoiceTurn["role"], text: string) => {
    const cleanText = text.trim();
    if (!cleanText) return;
    setVoiceTurns((current) => [...current.slice(-7), { id: idRef.current++, role, text: cleanText }]);
    void fetchWithTimeout(`${API_BASE_URL}/voice/transcripts`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        role,
        text: cleanText,
        session_id: "frontend-realtime",
      }),
    }).catch(() => undefined);
  };

  const runVoiceFallback = async () => {
    const text = voiceFallbackText.trim();
    if (!text || voiceFallbackBusy) return;
    setVoiceFallbackBusy(true);
    setVoiceError("");
    addVoiceTurn("you", text);
    setVoiceFallbackText("");
    try {
      const result = await fetchWithTimeout(`${API_BASE_URL}/voice/fallback`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text,
          mode: conversationMode,
          session_id: "frontend-fallback",
        }),
      });
      const data = (await result.json()) as { response?: string; detail?: string };
      if (!result.ok || !data.response) throw new Error(data.detail ?? `Voice fallback returned ${result.status}`);
      addVoiceTurn("helios", data.response);
      if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(data.response);
        utterance.rate = conversationMode === "concise" ? 1.05 : 0.98;
        window.speechSynthesis.speak(utterance);
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : "Voice fallback failed.";
      setVoiceError(message);
      addVoiceTurn("system", message);
    } finally {
      setVoiceFallbackBusy(false);
    }
  };

  const startRealtimeVoice = async () => {
    if (voiceState === "connecting" || voiceState === "listening" || voiceState === "speaking") return;

    setVoiceError("");
    setVoiceState("connecting");
    addVoiceTurn("system", "Opening live voice channel...");

    try {
      const peerConnection = new RTCPeerConnection();
      peerConnectionRef.current = peerConnection;

      const audioElement = document.createElement("audio");
      audioElement.autoplay = true;
      voiceAudioRef.current = audioElement;

      peerConnection.ontrack = (event) => {
        audioElement.srcObject = event.streams[0];
        setVoiceState("speaking");
      };

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      voiceStreamRef.current = stream;
      stream.getAudioTracks().forEach((track) => peerConnection.addTrack(track, stream));

      const dataChannel = peerConnection.createDataChannel("oai-events");
      voiceDataChannelRef.current = dataChannel;

      dataChannel.addEventListener("open", () => {
        setVoiceState("listening");
        addVoiceTurn("system", "Live. Just talk.");
        dataChannel.send(
          JSON.stringify({
            type: "conversation.item.create",
            item: {
              type: "message",
              role: "user",
              content: [
                {
                  type: "input_text",
                  text: "You are now in HELIOS live voice mode. Keep replies natural, emotionally aware, and concise.",
                },
              ],
            },
          }),
        );
      });

      dataChannel.addEventListener("message", (event) => {
        try {
          const payload = JSON.parse(event.data) as Record<string, unknown>;
          const type = String(payload.type ?? "");
          const transcript = payload.transcript ?? payload.delta;

          if (type.includes("input_audio_transcription") && typeof transcript === "string") {
            addVoiceTurn("you", transcript);
            setVoiceState("listening");
          }

          if (type.includes("response.audio_transcript") && typeof transcript === "string") {
            addVoiceTurn("helios", transcript);
            setVoiceState("speaking");
          }

          if (type.includes("response.done")) {
            setVoiceState("listening");
          }
        } catch {
          // Realtime events are best-effort UI signals; audio remains the source of truth.
        }
      });

      const offer = await peerConnection.createOffer();
      await peerConnection.setLocalDescription(offer);

      const sessionResponse = await fetchWithTimeout(`${API_BASE_URL}/realtime/session`, {
        method: "POST",
        body: offer.sdp,
        headers: {
          "Content-Type": "application/sdp",
        },
      });

      if (!sessionResponse.ok) {
        throw new Error(await sessionResponse.text());
      }

      await peerConnection.setRemoteDescription({
        type: "answer",
        sdp: await sessionResponse.text(),
      });
    } catch (error) {
      stopRealtimeVoice();
      const message = error instanceof Error ? error.message : "Realtime voice could not start.";
      setVoiceError(message);
      setVoiceState("error");
      addVoiceTurn("system", message);
    }
  };

  const renderModuleBody = () => {
    if (activeModule === "voice") {
      return (
        <section className={`voice-room voice-${voiceState}`}>
          <div className="voice-stage">
            <div className="voice-orb" aria-hidden="true">
              <span />
              <i />
            </div>
            <p className="section-label">HELIOS LIVE VOICE</p>
            <h3>
              {voiceState === "idle"
                ? "Ready"
                : voiceState === "connecting"
                  ? "Connecting"
                  : voiceState === "speaking"
                    ? "Speaking"
                    : voiceState === "error"
                      ? "Needs setup"
                      : "Listening"}
            </h3>
            <p className="voice-subtitle">
              {voiceState === "idle"
                ? voiceStatusInfo?.realtime_available
                  ? "Start a realtime speech session and talk naturally."
                  : "Realtime voice is unavailable, but the provider-independent fallback is ready."
                : voiceState === "error"
                  ? "Use the fallback below or retry the realtime bridge."
                  : "Talk normally. Interrupt whenever you need to."}
            </p>
            <div className="voice-readiness">
              <span>{voiceStatusInfo?.status ?? "checking"}</span>
              <b>{voiceStatusInfo?.model ?? "realtime model"}</b>
              <i>{voiceStatusInfo?.voice ?? "voice"}</i>
            </div>
            {voiceError && <p className="voice-error">{voiceError}</p>}
          </div>

          <div className="voice-controls" aria-label="Voice call controls">
            <button className="voice-control secondary" type="button" onClick={() => setVoiceTranscriptOpen((open) => !open)}>
              Transcript
            </button>
            <button
              className="voice-control primary"
              type="button"
              disabled={(voiceState === "idle" || voiceState === "error") && voiceStatusInfo?.realtime_available === false}
              onClick={voiceState === "idle" || voiceState === "error" ? startRealtimeVoice : stopRealtimeVoice}
            >
              {voiceState === "idle" || voiceState === "error" ? "Start voice" : "End"}
            </button>
            <button
              className="voice-control secondary"
              type="button"
              disabled={voiceState === "idle" || voiceState === "error"}
              onClick={() => {
                voiceDataChannelRef.current?.send(JSON.stringify({ type: "response.cancel" }));
                setVoiceState("listening");
                addVoiceTurn("system", "Interrupted.");
              }}
            >
              Interrupt
            </button>
          </div>

          <form
            className="voice-fallback"
            onSubmit={(event) => {
              event.preventDefault();
              void runVoiceFallback();
            }}
          >
            <div>
              <p className="section-label">Provider-Independent Fallback</p>
              <span>Type a voice turn and HELIOS will respond through the configured model route with browser speech playback.</span>
            </div>
            <input
              value={voiceFallbackText}
              placeholder="Ask HELIOS to speak..."
              onChange={(event) => setVoiceFallbackText(event.target.value)}
            />
            <button type="submit" disabled={!voiceFallbackText.trim() || voiceFallbackBusy}>
              {voiceFallbackBusy ? "Speaking..." : "Speak reply"}
            </button>
          </form>

          <aside className={`voice-transcript ${voiceTranscriptOpen ? "open" : ""}`}>
            <div>
              <p className="section-label">Transcript</p>
              <button type="button" onClick={() => setVoiceTranscriptOpen(false)}>
                Close
              </button>
            </div>
            {voiceTurns.slice(-8).map((turn) => (
              <article className={`voice-turn ${turn.role}`} key={turn.id}>
                <b>{turn.role === "helios" ? "HELIOS" : turn.role === "you" ? "You" : "System"}</b>
                <span>{turn.text}</span>
              </article>
            ))}
          </aside>
        </section>
      );
    }

    if (activeModule === "dashboard") {
      return (
        <div className="command-runtime">
          {activeTab === "Overview" && (
            <section className="spatial-command-field" aria-label="HELIOS 3D command field">
              <div className="spatial-copy">
                <p className="section-label">Mission Field</p>
                <h3>Good evening, Sharveesh.</h3>
                <span>{intelligenceStatus} • {selectedAgent.name} • {activeModuleConfig.title}</span>
                <div className="mission-launch-row" aria-label="Mission presets">
                  {[
                    { label: "Research", module: "research" as ModuleKey, agent: "Nova" },
                    { label: "Build", module: "code" as ModuleKey, agent: "Vega" },
                    { label: "Plan", module: "planning" as ModuleKey, agent: "Orion" },
                    { label: "Analyze", module: "analytics" as ModuleKey, agent: "Orion" },
                    { label: "Monitor", module: "swarm" as ModuleKey, agent: "Orion" },
                  ].map((preset) => (
                    <button
                      key={preset.label}
                      type="button"
                      onClick={() => launchMissionPreset(`${preset.label} mission`, preset.module, preset.agent)}
                    >
                      {preset.label}
                    </button>
                  ))}
                </div>
                {latestMission && (
                  <div className="mission-now">
                    <b>{latestMission.stage}</b>
                    <span>{latestMission.title}</span>
                  </div>
                )}
                {activeMission && (
                  <div className="mission-control-strip">
                    <div>
                      <p className="section-label">Active Mission</p>
                      <strong>{activeMission.title}</strong>
                      <span>{[activeMission.stage, activeMission.agent, activeMission.module].filter(Boolean).join(" • ")}</span>
                    </div>
                    <div className="mission-stage-actions">
                      <button
                        type="button"
                        disabled={advancingMissionStage.length > 0}
                        onClick={() => void runMissionWorkflow()}
                      >
                        {advancingMissionStage === "Run" ? "..." : "Run"}
                      </button>
                      {["Executed", "Reviewed", "Archived"].map((stage) => (
                        <button
                          key={stage}
                          type="button"
                          disabled={advancingMissionStage.length > 0 || activeMission.stage === stage}
                          onClick={() => void advanceMission(stage)}
                        >
                          {advancingMissionStage === stage ? "..." : stage}
                        </button>
                      ))}
                      <button type="button" onClick={() => void recoverActiveMission()}>
                        Recover
                      </button>
                      <button type="button" onClick={() => void exportActiveMission()}>
                        Export
                      </button>
                    </div>
                  </div>
                )}
                <section className="mission-artifact-panel" aria-label="AI provider settings">
                  <div>
                    <p className="section-label">AI provider preferences</p>
                    <strong>Choose the preferred provider and model route</strong>
                    <span>These values are saved in the backend settings file and used on the next health refresh.</span>
                  </div>
                  <div className="settings-grid">
                    <label>
                      <span>Provider</span>
                      <select value={aiSettingsProvider} onChange={(event) => setAiSettingsProvider(event.target.value)}>
                        {(Object.keys(health?.ai?.providers ?? {}).length > 0
                          ? Object.keys(health?.ai?.providers ?? {})
                          : ["ollama", "gemini"])
                          .map((provider) => (
                            <option key={provider} value={provider}>{provider}</option>
                          ))}
                      </select>
                    </label>
                    <label>
                      <span>Model override</span>
                      <input
                        value={aiSettingsModel}
                        placeholder="qwen2.5:3b or gemini-1.5-flash"
                        onChange={(event) => setAiSettingsModel(event.target.value)}
                        list="ai-model-options"
                      />
                      {availableProviderModels.length > 0 && (
                        <small>Detected models: {availableProviderModels.join(", ")}</small>
                      )}
                    </label>
                  </div>
                  <datalist id="ai-model-options">
                    {(availableProviderModels.length > 0 ? availableProviderModels : ["qwen2.5:3b", "gemini-1.5-flash"]).map((option) => (
                      <option key={option} value={option} />
                    ))}
                  </datalist>
                  <div className="settings-actions">
                    <button type="button" onClick={() => void saveAiSettings()} disabled={aiSettingsBusy}>
                      {aiSettingsBusy ? "Saving..." : "Save preference"}
                    </button>
                    <span>{aiSettingsStatus}</span>
                  </div>
                </section>

                {latestArtifact && (
                  <div className="mission-artifact-panel">
                    <div>
                      <p className="section-label">{latestArtifact.kind ?? "Artifact"}</p>
                      <strong>{latestArtifact.summary ?? "Mission artifact ready."}</strong>
                      {missionTask && <span>{missionTask.status} • {missionTask.progress ?? 0}%</span>}
                    </div>
                    {latestArtifact.evidence && latestArtifact.evidence.length > 0 && (
                      <div className="artifact-evidence-list">
                        {latestArtifact.evidence.slice(0, 3).map((item, index) => (
                          <article key={`${item.name}-${index}`}>
                            <b>{item.name ?? "Source"}</b>
                            <span>{item.snippet ?? "No snippet available."}</span>
                          </article>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
              <div className="holo-city" aria-hidden="true">
                {Array.from({ length: 24 }, (_, index) => (
                  <i
                    key={index}
                    style={{
                      "--x": `${(index % 8) * 12 - 42}px`,
                      "--z": `${Math.floor(index / 8) * 34 - 36}px`,
                      "--h": `${34 + ((index * 23 + runtimeTick * 3) % 92)}px`,
                      "--delay": `${index * 80}ms`,
                    } as CSSProperties}
                  />
                ))}
                <b>HELIOS</b>
              </div>
            </section>
          )}

          {activeTab === "Activity" && (
            <div className="activity-view">
              <section className="mission-timeline-board">
                <div className="feature-heading">
                  <p className="section-label">Mission Timeline</p>
                  <strong>{health?.missions?.total_events ?? missionEvents.length} events</strong>
                </div>
                <div className="mission-stage-rail">
                  {missionTimelineItems.map((event, index) => (
                    <article className={`mission-stage stage-${event.stage.toLowerCase()}`} key={event.id}>
                      <span>{index + 1}</span>
                      <b>{event.stage}</b>
                      <strong>{event.title}</strong>
                      <small>{[event.agent, event.module, event.status].filter(Boolean).join(" • ")}</small>
                    </article>
                  ))}
                </div>
              </section>
              <section className="agent-conflict-log">
                <div className="feature-heading">
                  <p className="section-label">Autonomous Execution Log</p>
                  <strong>Retries, conflict, approval gates</strong>
                </div>
                {agentTimeline.map((event) => (
                  <article className={`conflict-row ${event.risk}`} key={`${event.actor}-${event.status}`}>
                    <b>{event.actor}</b>
                    <span>{event.status}</span>
                    <p>{event.detail}</p>
                  </article>
                ))}
              </section>
            </div>
          )}

          {activeTab === "Plugins" && (
            <div className="plugins-view">
              <section className="plugins-grid">
                <div className="feature-heading">
                  <p className="section-label">HELIOS Plugin Marketplace</p>
                  <strong>{plugins.length} active extensions</strong>
                </div>
                <form
                  className="plugin-upload-form"
                  onSubmit={(event) => {
                    event.preventDefault();
                    void uploadPlugin();
                  }}
                >
                  <input placeholder="Plugin name" value={pluginName} onChange={(event) => setPluginName(event.target.value)} />
                  <input placeholder="Version" value={pluginVersion} onChange={(event) => setPluginVersion(event.target.value)} />
                  <input placeholder="Description" value={pluginDescription} onChange={(event) => setPluginDescription(event.target.value)} />
                  <textarea
                    placeholder={"def register_plugin(registry):\n    registry['my_tool'] = lambda: 'ready'"}
                    value={pluginCode}
                    onChange={(event) => setPluginCode(event.target.value)}
                  />
                  <button type="submit" disabled={!pluginName.trim() || !pluginCode.trim()}>Upload signed plugin</button>
                </form>
                {pluginStatus && <span className="plugin-status">{pluginStatus}</span>}
                <div className="plugin-list">
                  {plugins.length > 0 ? (
                    plugins.map((plugin) => (
                      <article className="plugin-card" key={plugin.filename}>
                        <span className="plugin-mark">P</span>
                        <div>
                          <b>{plugin.name}</b>
                          <span>{plugin.version ?? "unversioned"} / {plugin.filename}</span>
                          <small>{plugin.description || `${plugin.isolation ?? "legacy"} / ${plugin.verified ? "verified" : "unverified"}`}</small>
                        </div>
                        <button type="button" onClick={() => void removePlugin(plugin)}>Uninstall</button>
                      </article>
                    ))
                  ) : (
                    <div className="plugin-empty">
                      <b>No custom plugins loaded.</b>
                      <span>Add .py files to backend/plugins to extend HELIOS.</span>
                    </div>
                  )}
                </div>
              </section>
            </div>
          )}

          {activeTab === "Launchpad" && (
            <div className="launchpad-view">
              <section className="orchestration-theater">
                <div className="feature-heading">
                  <p className="section-label">Cognitive Operations</p>
                  <strong>{intelligenceStatus}</strong>
                </div>
                <div className="flow-line">
                  {orchestrationFlow.map((node, index) => (
                    <article className={`flow-node ${node.tone}`} key={node.agent}>
                      <span>{index + 1}</span>
                      <b>{node.agent}</b>
                      <strong>{node.state}</strong>
                      <small>{node.detail}</small>
                    </article>
                  ))}
                </div>
              </section>
              <div className="runtime-lower-grid">
                <section className="agent-radar">
                  <div className="radar-field">
                    <div className="radar-core">
                      <b>HELIOS</b>
                    </div>
                    {agentRadar.map((agent, index) => (
                      <button className={`radar-agent radar-agent-${index + 1} ${agent.state}`} key={agent.name} type="button">
                        <b>{agent.name}</b>
                        <span>{agent.orbit}</span>
                      </button>
                    ))}
                  </div>
                </section>
              </div>
            </div>
          )}
        </div>
      );
    }

    if (activeModule === "analytics") {
      return (
        <div className="module-special observability-grid">
          <section className="observability-hero">
            <p className="section-label">Execution Observability</p>
            <h3>{Math.round((observability?.rates?.failure_rate ?? 0) * 100)}% failure pressure</h3>
            <span>{observability?.recommendations?.[0] ?? "Execution health is collecting from the live ledger."}</span>
          </section>
          <div className="observability-metrics">
            {[
              { label: "Events", value: observability?.window?.events_analyzed ?? 0 },
              { label: "Completed", value: observability?.window?.completed_events ?? 0 },
              { label: "Avg ms", value: observability?.rates?.average_duration_ms ?? 0 },
              { label: "P95 ms", value: observability?.latency_percentiles?.p95_ms ?? 0 },
            ].map((item) => (
              <article key={item.label}>
                <span>{item.label}</span>
                <b>{item.value}</b>
              </article>
            ))}
          </div>
          <section className="observability-panel slow">
            <p className="section-label">Slow Tools</p>
            {(observability?.slow_tools ?? []).slice(0, 5).map((tool) => (
              <div key={tool.tool}>
                <b>{tool.tool}</b>
                <span>{tool.average_duration_ms} ms avg / {tool.samples} samples</span>
              </div>
            ))}
          </section>
          <section className="observability-panel failures">
            <p className="section-label">Recent Failures</p>
            {(observability?.recent_failures ?? []).slice(0, 5).map((event) => (
              <div key={event.id}>
                <b>{event.tool ?? event.label}</b>
                <span>{event.status} / {event.detail ?? event.error}</span>
              </div>
            ))}
            {(!observability?.recent_failures || observability.recent_failures.length === 0) && (
              <div>
                <b>No recent failures</b>
                <span>Ledger looks stable in the current window.</span>
              </div>
            )}
          </section>
          <section className="observability-panel traces">
            <p className="section-label">Distributed Trace Groups</p>
            {(observability?.traces ?? []).slice(-6).reverse().map((trace) => (
              <div key={trace.trace_id}>
                <b>{trace.trace_id}</b>
                <span>{trace.events} events / {trace.duration_ms} ms / {trace.failed} failed / {(trace.tools ?? []).join(", ")}</span>
              </div>
            ))}
            {(!observability?.traces || observability.traces.length === 0) && (
              <div>
                <b>No trace groups yet</b>
                <span>Tool events will be grouped by parent or trace identifier.</span>
              </div>
            )}
          </section>
        </div>
      );
    }

    if (activeModule === "research") {
      return (
        <div className="module-special research-intelligence-space">
          <section className="evidence-orbit">
            <div className="evidence-core">
              <p className="section-label">Evidence Core</p>
              <h4>{activeMission?.module === "research" ? activeMission.title : "Research Mission"}</h4>
              <span>{researchArtifact?.summary ?? "Run a research mission to generate evidence artifacts."}</span>
              <button
                type="button"
                disabled={!activeMission || advancingMissionStage.length > 0}
                onClick={() => void runMissionWorkflow()}
              >
                {advancingMissionStage === "Run" ? "Running" : "Run Research"}
              </button>
            </div>
            {researchEvidence.slice(0, 5).map((item, index) => (
              <article className={`evidence-node evidence-node-${index + 1}`} key={`${item.name}-${index}`}>
                <b>{item.name ?? `Signal ${index + 1}`}</b>
                <span>{item.scope ?? "project"}</span>
              </article>
            ))}
          </section>

          <section className="evidence-workbench">
            <div className="feature-heading">
              <p className="section-label">Evidence</p>
              <strong>{researchCitations.length || researchEvidence.length} cited signals</strong>
            </div>
            <div className="evidence-list">
              {researchEvidence.length > 0 ? (
                researchEvidence.map((item, index) => (
                  <article className="evidence-card" key={`${item.name}-${index}`}>
                    <div>
                      <p className="section-label">{researchCitations[index]?.id ?? item.scope ?? "source"}</p>
                      <h4>{item.name ?? `Evidence ${index + 1}`}</h4>
                      <span>{item.snippet ?? "No snippet available."}</span>
                    </div>
                    <strong>{researchCitations[index]?.confidence ? `${Math.round((researchCitations[index]?.confidence ?? 0) * 100)}%` : item.match_terms?.length ? `${item.match_terms.length}x` : "Live"}</strong>
                  </article>
                ))
              ) : (
                researchSources.map((source) => (
                  <article className="evidence-card" key={source.title}>
                    <div>
                      <p className="section-label">{source.status}</p>
                      <h4>{source.title}</h4>
                      <span>{source.note}</span>
                    </div>
                    <strong>{source.confidence}</strong>
                  </article>
                ))
              )}
            </div>
          </section>

          <section className="source-graph-panel">
            <div className="feature-heading">
              <p className="section-label">Source Intelligence Graph</p>
              <strong>{researchGraph?.nodes?.length ?? 0} nodes / {researchGraph?.links?.length ?? 0} links</strong>
            </div>
            <GraphMap
              nodes={researchGraph?.nodes ?? []}
              links={researchGraph?.links ?? []}
              selectedId={selectedSourceGraphNode?.id}
              onSelect={setSelectedSourceGraphNode}
              label="Source Intelligence citation and claim graph"
            />
            <div className="graph-selection">
              <b>{selectedSourceGraphNode?.label ?? "Select a source, claim, or query node"}</b>
              <span>{selectedSourceGraphNode?.detail ?? selectedSourceGraphNode?.kind ?? "Explore how evidence grounds claims."}</span>
            </div>
          </section>

          <section className="research-briefing-panel">
            <p className="section-label">Briefing</p>
            <h4>{researchIsGrounded ? "Source-grounded answer" : researchArtifact?.kind ? "Artifact ready" : "Awaiting citations"}</h4>
            <span>{researchGroundedAnswer ?? researchArtifact?.summary ?? "Create or select a Research mission, then run it from this workspace."}</span>
            <div className={`grounding-contract ${researchIsGrounded ? "enforced" : "waiting"}`}>
              <b>{researchEnforcement?.policy ?? "cite_or_refuse"}</b>
              <span>
                {Math.round(((researchEnforcement?.coverage_ratio ?? (researchCoverage as { coverage_ratio?: number } | null)?.coverage_ratio ?? 0) as number) * 100)}%
                {" "}coverage / minimum {Math.round(((researchEnforcement?.minimum_coverage_ratio ?? (researchCoverage as { minimum_coverage_ratio?: number } | null)?.minimum_coverage_ratio ?? 0.5) as number) * 100)}%
              </span>
            </div>
            {researchClaims.length > 0 && (
              <div className="citation-claims">
                {researchClaims.slice(0, 3).map((claim, index) => (
                  <div key={`${claim.source}-${index}`}>
                    <b>{claim.citations?.join(", ") ?? `S${index + 1}`}</b>
                    <span>{claim.claim}</span>
                  </div>
                ))}
              </div>
            )}
            {researchUnsupportedTerms.length > 0 && (
              <div className="citation-gap">
                <b>Unsupported terms</b>
                <span>{researchUnsupportedTerms.slice(0, 8).join(", ")}</span>
              </div>
            )}
            <div className="research-briefing-steps">
              {["Scope", "Cite", "Check", "Synthesize"].map((step, index) => (
                <div key={step}>
                  <b>{index + 1}</b>
                  <span>{step}</span>
                </div>
              ))}
            </div>
          </section>
        </div>
      );
    }

    if (activeModule === "code") {
      return (
        <div className="module-special code-split depth-lab">
          <div className="code-depth-grid" aria-hidden="true" />
          <div className="file-rail">
            {codeTargetRows.map((file) => (
              <button className="file-row" key={file.path} type="button">
                <b>{file.path}</b>
                <span>{file.signal}</span>
              </button>
            ))}
          </div>
          <div className="analysis-stage">
            <p className="section-label">Patch Intelligence</p>
            <h4>{codeArtifact?.execution?.commit_ready ? "Patch ready for review" : codeArtifact ? "Code workflow captured" : "Awaiting code mission"}</h4>
            <span>{codeArtifact?.summary ?? "Run a Code mission to identify files, apply bounded edits, and capture verification logs."}</span>
            <form
              className="code-repair-form"
              onSubmit={(event) => {
                event.preventDefault();
                void runAutomaticCodeRepair();
              }}
            >
              <input
                placeholder="Repair objective"
                value={codeRepairObjective}
                onChange={(event) => setCodeRepairObjective(event.target.value)}
              />
              <input
                placeholder="Target files, comma separated"
                value={codeRepairTargets}
                onChange={(event) => setCodeRepairTargets(event.target.value)}
              />
              <button type="submit" disabled={!codeRepairObjective.trim() || !codeRepairTargets.trim() || codeRepairBusy}>
                {codeRepairBusy ? "Repairing..." : "Edit, test, retry"}
              </button>
            </form>
            <div className="code-terminal">
              <code>{codeVerificationRows[0]?.command ?? "git status --short"}</code>
              <b>{codeVerificationRows[0]?.status ?? "waiting"}</b>
              <span>{codeVerificationRows[0]?.output ?? "Execution output will stream through the run ledger."}</span>
            </div>
            {codeArtifact?.execution?.verification_health && (
              <div className="code-terminal compact-terminal">
                <code>verification health</code>
                <b>{`${codeArtifact.execution.verification_health.passed ?? 0}/${codeArtifact.execution.verification_health.total ?? 0} passed`}</b>
                <span>{codeArtifact.execution.verification_health.failed_commands?.join(", ") || "No failed commands reported."}</span>
              </div>
            )}
          </div>
          <div className="patch-panel">
            <p className="section-label">{codeEditRows.length > 0 ? "Applied Edits" : "Risk Queue"}</p>
            {codePatchRows.map((file) => (
              <div className="risk-row" key={file.key}>
                <span>{file.status}</span>
                <b>{file.label}</b>
              </div>
            ))}
            {codeActionRows.map((action) => (
              <div className="risk-row action-row" key={action}>
                <span>{codeArtifact?.execution?.action_required ? "next" : "ready"}</span>
                <b>{action}</b>
              </div>
            ))}
            <button className="patch-review-button" type="button" onClick={() => void loadGitDiff(false)}>
              Review diff
            </button>
          </div>
          <section className="diff-review">
            <div className="feature-heading">
              <p className="section-label">Side-by-Side Diff</p>
              <strong>{gitDiffResult?.diff ? `${diffAdded.length} added / ${diffRemoved.length} removed` : "Load repository diff"}</strong>
            </div>
            <div className="diff-columns">
              <pre className="diff-removed">{diffRemoved.join("\n") || "No removed lines."}</pre>
              <pre className="diff-added">{diffAdded.join("\n") || "No added lines."}</pre>
            </div>
          </section>
          <section className="git-workflow">
            <div className="feature-heading">
              <p className="section-label">Git Workflow</p>
              <strong>Branch, stage, commit, push, rollback</strong>
            </div>
            <div className="git-workflow-grid">
              <form
                onSubmit={(event) => {
                  event.preventDefault();
                  const paths = gitStagePaths.split(",").map((path) => path.trim()).filter(Boolean);
                  void runGitOperation("stage", { paths }, `Stage ${paths.length} selected path(s)?`);
                }}
              >
                <input
                  placeholder="Paths to stage, comma separated"
                  value={gitStagePaths}
                  onChange={(event) => setGitStagePaths(event.target.value)}
                />
                <button type="submit" disabled={!gitStagePaths.trim() || gitOperationBusy}>Stage</button>
              </form>
              <form
                onSubmit={(event) => {
                  event.preventDefault();
                  void runGitOperation("branch", { name: gitBranchName.trim() }, `Create and switch to branch "${gitBranchName.trim()}"?`);
                }}
              >
                <input placeholder="New branch name" value={gitBranchName} onChange={(event) => setGitBranchName(event.target.value)} />
                <button type="submit" disabled={!gitBranchName.trim() || gitOperationBusy}>Create branch</button>
              </form>
              <form
                onSubmit={(event) => {
                  event.preventDefault();
                  void runGitOperation("commit", { message: gitCommitMessage.trim() }, "Commit the currently staged files?");
                }}
              >
                <input placeholder="Commit message" value={gitCommitMessage} onChange={(event) => setGitCommitMessage(event.target.value)} />
                <button type="submit" disabled={!gitCommitMessage.trim() || gitOperationBusy}>Commit</button>
              </form>
              <form
                onSubmit={(event) => {
                  event.preventDefault();
                  void runGitOperation("push", { branch: gitPushBranch.trim(), remote: "origin" }, `Push "${gitPushBranch.trim()}" to origin?`);
                }}
              >
                <input placeholder="Branch to push" value={gitPushBranch} onChange={(event) => setGitPushBranch(event.target.value)} />
                <button type="submit" disabled={!gitPushBranch.trim() || gitOperationBusy}>Push</button>
              </form>
              <form
                onSubmit={(event) => {
                  event.preventDefault();
                  void runGitOperation("rollback", { commit: gitRollbackCommit.trim() }, `Create a revert commit for ${gitRollbackCommit.trim()}?`);
                }}
              >
                <input placeholder="Commit SHA to revert" value={gitRollbackCommit} onChange={(event) => setGitRollbackCommit(event.target.value)} />
                <button type="submit" disabled={!gitRollbackCommit.trim() || gitOperationBusy}>Rollback</button>
              </form>
            </div>
            <pre>{gitOperationStatus}</pre>
          </section>
          <section className="terminal-runner">
            <p className="section-label">Approved Terminal Runner</p>
            <form
              onSubmit={(event) => {
                event.preventDefault();
                void runTerminalCommand();
              }}
            >
              <input value={terminalCommand} onChange={(event) => setTerminalCommand(event.target.value)} />
              <button type="submit" disabled={!terminalCommand.trim() || terminalBusy}>
                {terminalBusy ? "Running..." : "Run"}
              </button>
            </form>
            <pre>{terminalOutput || "Command output will appear here."}</pre>
          </section>
        </div>
      );
    }

    if (activeModule === "swarm") {
      return (
        <div className="module-special swarm-map">
          <div className="signal-ring" />
          <div className="swarm-depth-grid" aria-hidden="true" />
          {agents.map((agent, index) => (
            <button className={`swarm-node node-${index + 1}`} key={agent.name} type="button" onClick={() => setActiveAgent(agent.name)}>
              <b>{agent.name}</b>
              <span>{agent.load}</span>
            </button>
          ))}
          <div className="swarm-core">
            <b>HELIOS</b>
            <span>{swarmArtifact?.consensus?.confidence ? `${Math.round((swarmArtifact.consensus.confidence ?? 0) * 100)}% consensus` : "Router Core"}</span>
          </div>
          <div className="swarm-consensus-panel">
            <p className="section-label">Debate Loop</p>
            {(swarmArtifact?.debate ?? []).slice(0, 3).map((item, index) => (
              <article key={`${item.agent}-${index}`}>
                <b>{item.agent}</b>
                <span>{item.proposal}</span>
                <small>{item.critiques?.[0] ?? "Awaiting critique."}</small>
              </article>
            ))}
            {(!swarmArtifact?.debate || swarmArtifact.debate.length === 0) && (
              <article>
                <b>Awaiting swarm mission</b>
                <span>Create or run a Swarm mission to generate debate and consensus.</span>
                <small>Agents will propose, critique, and converge.</small>
              </article>
            )}
          </div>
          <div className="swarm-assignment-panel">
            <p className="section-label">Assignments</p>
            {(swarmArtifact?.assignments ?? []).slice(0, 4).map((item, index) => (
              <span key={`${item.agent}-${index}`}>{item.agent} / P{item.priority}: {item.objective}</span>
            ))}
          </div>
          <section className="isolated-swarm-panel">
            <p className="section-label">Isolated Worker Swarm</p>
            <form
              onSubmit={(event) => {
                event.preventDefault();
                void createIsolatedSwarmRun();
              }}
            >
              <input
                placeholder="Objective for durable multi-worker debate"
                value={swarmObjective}
                onChange={(event) => setSwarmObjective(event.target.value)}
              />
              <button type="submit" disabled={!swarmObjective.trim() || swarmBusy}>
                {swarmBusy ? "Queueing..." : "Queue isolated swarm"}
              </button>
            </form>
            <div>
              {isolatedSwarmRuns.slice(0, 4).map((run) => (
                <article key={run.id}>
                  <b>{run.objective}</b>
                  <span>{run.status} / round {run.round ?? 1} / {Math.round((run.consensus?.confidence ?? 0) * 100)}% consensus</span>
                  <small>{run.debate_state?.phase ?? run.debate_protocol?.mode ?? "two-round worker debate"} / {(run.debate_protocol?.independent_agents ?? []).length || 3} agents</small>
                </article>
              ))}
            </div>
          </section>
        </div>
      );
    }

    if (activeModule === "planning") {
      return (
        <div className="module-special planning-graph">
          {displayedPlanNodes.map((node, index) => (
            <article className="plan-node" key={`${node.title}-${index}`}>
              <span>{index + 1}</span>
              <h4>{node.title}</h4>
              <p>{node.meta}</p>
            </article>
          ))}
        </div>
      );
    }

    if (activeModule === "reasoning") {
      return (
        <div className="module-special reasoning-space">
          <div className="reasoning-root">
            <b>Intent</b>
            <span>{intelligenceStatus}</span>
          </div>
          {traceEvents.slice(0, 6).map((event, index) => (
            <article className={`reasoning-node reasoning-node-${index + 1}`} key={`${event.stage}-${index}`}>
              <b>{event.stage}</b>
              <span>{event.actor}</span>
            </article>
          ))}
        </div>
      );
    }

    if (activeModule === "loop") {
      return (
        <div className="module-special autonomy-console">
          <section className="autonomy-launcher">
            <p className="section-label">Durable Autonomy</p>
            <h4>Queue independent agent work</h4>
            <form
              onSubmit={(event) => {
                event.preventDefault();
                void createAutonomousRun();
              }}
            >
              <input
                placeholder="Objective for a long-running autonomous run"
                value={autonomyObjective}
                onChange={(event) => setAutonomyObjective(event.target.value)}
              />
              <button type="submit" disabled={!autonomyObjective.trim() || autonomyBusy}>
                {autonomyBusy ? "Queueing..." : "Queue run"}
              </button>
            </form>
          </section>
          <section className="autonomy-run-list">
            {(autonomousRuns.length > 0 ? autonomousRuns : []).map((run) => (
              <article className={`autonomy-run status-${run.status}`} key={run.id}>
                <div>
                  <p className="section-label">{run.plan?.primary_route ?? "routing"} / {run.status}</p>
                  <h4>{run.objective}</h4>
                  <span>{run.synthesis?.summary ?? `${run.plan?.tasks?.length ?? 0} routed step(s), ${run.steps?.length ?? 0} complete.`}</span>
                  <small>
                    {run.execution_contract?.mode ?? "durable_worker_queue"} / {run.worker_jobs?.length ?? 0} worker job(s) / max {run.execution_contract?.max_rounds ?? 3} round(s)
                  </small>
                </div>
                <div className="autonomy-route-row">
                  {(run.plan?.tasks ?? []).slice(0, 5).map((task, index) => (
                    <span key={`${task.route}-${index}`}>{task.agent} / {task.route}</span>
                  ))}
                </div>
                <div className="autonomy-actions">
                  {["queued", "running"].includes(run.status) && (
                    <button type="button" onClick={() => void updateAutonomousRun(run.id, "cancel")}>Cancel</button>
                  )}
                  {["cancelled", "failed"].includes(run.status) && (
                    <button type="button" onClick={() => void updateAutonomousRun(run.id, "resume")}>Resume</button>
                  )}
                </div>
              </article>
            ))}
            {autonomousRuns.length === 0 && (
              <article className="autonomy-run">
                <h4>No autonomous runs yet</h4>
                <span>Queue an objective to route work through durable worker jobs.</span>
              </article>
            )}
          </section>
        </div>
      );
    }

    if (activeModule === "workflow") {
      return (
        <div className="module-special workflow-rail">
          {workflowRuns.map((run, index) => (
            <article className="workflow-step" key={run.step}>
              <span>{index + 1}</span>
              <div>
                <p className="section-label">{run.state}</p>
                <h4>{run.step}</h4>
                <small>{run.detail}</small>
              </div>
            </article>
          ))}
        </div>
      );
    }

    if (activeModule === "knowledge") {
      return (
        <div className="knowledge-board">
          <div className="upload-zone">
            <button className="upload-button" type="button" onClick={() => fileInputRef.current?.click()}>
              Upload source
            </button>
              <span>{sourceStats?.indexed_sources ?? indexedSources.length} indexed • scoped retrieval ready</span>
          </div>
          <form
            className="source-url-form"
            onSubmit={(event) => {
              event.preventDefault();
              void ingestSourceUrl();
            }}
          >
            <select value={sourceUrlType} onChange={(event) => setSourceUrlType(event.target.value as "WEB" | "GITHUB")}>
              <option value="WEB">Web page</option>
              <option value="GITHUB">GitHub repository</option>
            </select>
            <input
              value={sourceUrl}
              placeholder={sourceUrlType === "GITHUB" ? "https://github.com/owner/repository" : "https://example.com/article"}
              onChange={(event) => setSourceUrl(event.target.value)}
            />
            <button type="submit" disabled={!sourceUrl.trim() || sourceUrlBusy}>
              {sourceUrlBusy ? "Indexing..." : "Index URL"}
            </button>
          </form>
          {sources.map((source) => (
            <div className="source-row" key={source.id}>
              <div>
                <b>{source.name}</b>
                <span>{source.type} • {source.size}</span>
                <em>{source.status}</em>
              </div>
              <div className="source-actions">
                <button type="button" onClick={() => void reindexSource(source)}>Reindex</button>
                <button type="button" onClick={() => void removeSource(source)}>Remove</button>
              </div>
            </div>
          ))}
        </div>
      );
    }

    return (
      <div className="timeline-panel">
        <p className="section-label">Run Ledger • {runLedgerStatusLabel}</p>
        {runLedgerEntries.length > 0 ? (
          runLedgerEntries.map((entry, index) => {
            const timing = typeof entry.duration_ms === "number" ? `${entry.duration_ms} ms` : undefined;
            const attempt = entry.attempt && entry.attempt > 1 ? `attempt ${entry.attempt}` : undefined;
            const meta = [entry.actor, entry.module, entry.tool, entry.status, attempt, timing, entry.timestamp].filter(Boolean).join(" • ");
            const detail = entry.detail ? (meta ? `${meta} • ${entry.detail}` : entry.detail) : meta;

            return (
              <div className={`timeline-item trace-item ledger-event ${entry.status ?? "unknown"}`} key={entry.id}>
                <span>{index + 1}</span>
                <div>
                  <b>{entry.label}</b>
                  {detail && <small>{detail}</small>}
                </div>
              </div>
            );
          })
        ) : (
          <div className="timeline-item trace-item">
            <span>•</span>
            <div>
              <b>Awaiting live events</b>
              <small>Connect HELIOS to the WebSocket event feed.</small>
            </div>
          </div>
        )}

        <p className="section-label">{lastTrace.length > 0 ? "Live Cognitive Trace" : "Execution Timeline"}</p>
        {traceEvents.map((event, index) => (
          <div className="timeline-item trace-item" key={`${event.stage}-${index}`}>
            <span>{index + 1}</span>
            <div>
              <b>{event.stage}</b>
              <small>{event.actor}{event.timestamp ? ` • ${event.timestamp}` : ""}</small>
            </div>
          </div>
        ))}
      </div>
    );
  };

  if (authChecking) {
    return (
      <main className="auth-shell">
        <section className="auth-panel auth-loading" aria-live="polite">
          <span className="brand-mark">H</span>
          <p className="eyebrow">HELIOS</p>
          <h1>Checking session</h1>
          <span className="auth-status">Connecting to the control plane...</span>
        </section>
      </main>
    );
  }

  if (authRequired && !authUser) {
    return (
      <main className="auth-shell">
        <section className="auth-panel">
          <div className="auth-brand">
            <span className="brand-mark">H</span>
            <div>
              <p className="eyebrow">HELIOS</p>
              <h1>Sign in</h1>
            </div>
          </div>
          <form
            className="auth-form"
            onSubmit={(event) => {
              event.preventDefault();
              void login();
            }}
          >
            <label>
              <span>Username</span>
              <input
                autoFocus
                autoComplete="username"
                value={loginUsername}
                onChange={(event) => setLoginUsername(event.target.value)}
              />
            </label>
            <label>
              <span>Password</span>
              <input
                autoComplete="current-password"
                type="password"
                value={loginPassword}
                onChange={(event) => setLoginPassword(event.target.value)}
              />
            </label>
            {loginError && <div className="auth-error" role="alert">{loginError}</div>}
            <button type="submit" disabled={!loginUsername.trim() || !loginPassword || loginBusy}>
              {loginBusy ? "Signing in..." : "Sign in"}
            </button>
          </form>
        </section>
      </main>
    );
  }

  return (
    <main
      className={`dashboard ${theme} ${focusMode ? "focus-mode" : ""}`}
      onDragOver={(event) => {
        event.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
    >
      {isDragging && <div className="drop-zone">Drop sources into HELIOS</div>}

      <aside className="sidebar">
        <div className="brand-block">
          <span className="brand-mark">H</span>
          <div>
            <p className="eyebrow">HELIOS</p>
            <h1>AI Operating System</h1>
          </div>
        </div>

        <button className="primary-action" type="button" onClick={() => setCommandOpen(true)}>
          <span>+</span>
          New session
        </button>

        <div className="sidebar-section modules-section">
          <p className="section-label">Modules</p>
          {modules.map((item) => (
            <button
              className={`module-link ${item.key === activeModule ? "active" : ""}`}
              key={item.key}
              type="button"
              onClick={() => switchModule(item.key)}
            >
              <span className="module-icon">{item.icon}</span>
              <span>{item.title}</span>
            </button>
          ))}
        </div>

        <div className="system-card">
          <p className="section-label">System Status</p>
          <strong>{runtimeLabel}</strong>
          <span>{runtimeDetail}</span>
        </div>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div className="topbar-title">
            <span className={`status-dot runtime-${runtimeState}`} aria-hidden="true" />
            <div>
              <p className="eyebrow">HELIOS AI</p>
              <h2>{runtimeLabel}</h2>
              <span className="topbar-subtitle">{runtimeDetail}</span>
            </div>
          </div>
          <div className="topbar-actions">
            <button
              className="account-button"
              type="button"
              aria-label={`Account: ${authUser?.username ?? "Local"}`}
              onClick={openAccount}
            >
              <Icon name="user" />
              <span>{authUser?.username ?? "Local"}</span>
              <small>{authUser?.role ?? (HELIOS_API_KEY ? "api key" : "local")}</small>
            </button>
            <span className={`model-pill runtime-${runtimeState}`}>{modelName}</span>
            <button className="icon-button" type="button" aria-label="Open memory" onClick={() => setMemoryOpen(true)}>
              <Icon name="brain" />
            </button>
            <button className="icon-button" type="button" aria-label="Open execution log" onClick={() => setExecutionOpen(true)}>
              <Icon name="search" />
            </button>
            <button
              className="icon-button"
              type="button"
              aria-label="Open command palette"
              onClick={() => setCommandOpen(true)}
            >
              <Icon name="command" />
            </button>
            <button
              className="icon-button"
              type="button"
              aria-label="Open deploy panel"
              onClick={() => setDeployOpen(true)}
            >
              <Icon name="deploy" />
            </button>
            <button
              className={`icon-button ${focusMode ? "active" : ""}`}
              type="button"
              aria-label="Toggle focus mode"
              onClick={() => setFocusMode((current) => !current)}
            >
              <Icon name="focus" />
            </button>
            <button
              className="icon-button"
              type="button"
              aria-label="Toggle theme"
              onClick={() => setTheme((current) => (current === "dark" ? "light" : "dark"))}
            >
              <Icon name="theme" />
            </button>
          </div>
        </header>

        <div className={`content-grid ${activeModule === "voice" ? "voice-layout" : ""}`}>
          <section className={`module-panel ${activeModule === "voice" ? "voice-panel" : ""}`} key={activeModule}>
            {activeModule !== "voice" && (
              <div className="module-hero">
              <span className="module-mark">{activeModuleConfig.icon}</span>
              <div>
                <p className="eyebrow">{activeModuleConfig.eyebrow} • {selectedAgent.name}</p>
                <h3>{activeModuleConfig.title}</h3>
                <span>{activeModuleConfig.description}</span>
              </div>
              </div>
            )}

            {activeModule !== "voice" && (
              <div className="module-tabs" aria-label={`${activeModuleConfig.title} views`}>
                {activeModuleConfig.tabs.map((tab) => (
                  <button
                    className={tab === activeTab ? "active" : ""}
                    key={tab}
                    type="button"
                    onClick={() => setActiveTab(tab)}
                  >
                    {tab}
                  </button>
                ))}
              </div>
            )}

            {activeModule !== "voice" && (
              <div className="metric-strip">
                {displayedStats.map((stat) => (
                  <div className={`metric ${stat.tone}`} key={stat.label}>
                    <span>{stat.label}</span>
                    <strong>{stat.value}</strong>
                  </div>
                ))}
                </div>
            )}

            <div className="module-body">
              {activeModule !== "voice" && activeModule !== "dashboard" && (
                <div className="primary-stack">
                  <div className="work-grid">
                    {activeModuleConfig.primary.map((card) => (
                      <article className="work-card" key={card.title}>
                        <p className="section-label">{activeTab}</p>
                        <h4>{card.title}</h4>
                        <span>{card.body}</span>
                      </article>
                    ))}
                  </div>
                </div>
              )}

              {renderModuleBody()}
            </div>

            {activeModule !== "voice" && (
              <div className="conversation-dock">
              <div className="mini-chat">
                {messages.slice(-3).map((message) => (
                  <article className={`mini-message ${message.role}`} key={message.id}>
                    <b>{message.role === "assistant" ? "HELIOS" : "You"}</b>
                    <span>{message.text || "Thinking..."}</span>
                  </article>
                ))}
                {isGenerating && (
                  <div className="thinking compact">
                    <span />
                    <span />
                    <span />
                  </div>
                )}
              </div>

              <div className="composer">
                <div className="conversation-modes" aria-label="Conversation mode">
                  {(["balanced", "concise", "deep", "execute"] as ConversationMode[]).map((mode) => (
                    <button
                      className={conversationMode === mode ? "active" : ""}
                      key={mode}
                      type="button"
                      onClick={() => setConversationMode(mode)}
                    >
                      {mode}
                    </button>
                  ))}
                </div>
                <div className="conversation-mode-detail">
                  <b>{activeConversationMode?.label ?? conversationMode}</b>
                  <span>{activeConversationMode?.description ?? "Conversation behavior adapts to the selected mode."}</span>
                  <small>
                    {[
                      activeConversationMode?.response_length ? `length: ${activeConversationMode.response_length}` : null,
                      activeConversationMode?.reasoning_depth ? `depth: ${activeConversationMode.reasoning_depth}` : null,
                      activeConversationMode?.tool_posture ? `tools: ${activeConversationMode.tool_posture}` : null,
                    ].filter(Boolean).join(" / ")}
                  </small>
                </div>
                {attachments.length > 0 && (
                  <div className="attachment-tray">
                    {attachments.map((file) => (
                      <span className="file-chip" key={file.id}>
                        <b>{file.name}</b>
                        <small>{file.size}</small>
                        <button
                          type="button"
                          aria-label={`Remove ${file.name}`}
                          onClick={() => setAttachments((current) => current.filter((item) => item.id !== file.id))}
                        >
                          x
                        </button>
                      </span>
                    ))}
                  </div>
                )}

                <div className={`composer-shell ${isGenerating ? "generating" : ""}`}>
                  <input
                    ref={fileInputRef}
                    className="hidden-input"
                    type="file"
                    multiple
                    onChange={handleFileChange}
                  />
                  <textarea
                    aria-label="Chat message"
                    placeholder={activeModuleConfig.prompt}
                    rows={1}
                    value={input}
                    onChange={(event) => setInput(event.target.value)}
                    onKeyDown={handleKeyDown}
                  />
                  <div className="composer-controls">
                    <div className="composer-tools">
                      <button className="tool-button" type="button" aria-label="Attach files" onClick={() => fileInputRef.current?.click()}>
                        <Icon name="upload" />
                      </button>
                      <button className="tool-button" type="button" aria-label="Search">
                        <Icon name="search" />
                      </button>
                      <button className="tool-button wide" type="button" aria-label="Selected module">
                        {activeModuleConfig.title}
                      </button>
                    </div>
                    {isGenerating ? (
                      <button className="submit-button stop-button" type="button" aria-label="Stop generating" onClick={stopGeneration}>
                        <span />
                      </button>
                    ) : (
                      <button
                        className="submit-button send-button"
                        type="button"
                        aria-label="Send message"
                        disabled={!input.trim() && attachments.length === 0}
                        onClick={sendMessage}
                      >
                        ↑
                      </button>
                    )}
                  </div>
                </div>
              </div>
              </div>
            )}
          </section>

          {activeModule !== "voice" && (
            <aside className="insights-panel">
            <div className="status-card">
              <p className="section-label">Active Agent</p>
              <strong>{selectedAgent.name}</strong>
              <span>{selectedAgent.specialty}</span>
              <em className={`runtime-badge runtime-${runtimeState}`}>{runtimeLabel}</em>
              <div className="load-meter" aria-label={`${selectedAgent.name} load ${selectedAgent.load}`}>
                <i style={{ width: selectedAgent.load }} />
              </div>
            </div>

            <div className="side-section">
              <p className="section-label">Live Runtime</p>
              {liveMemoryScopes.map((scope) => (
                <div className={`scope-row ${scope.tone}`} key={scope.label}>
                  <span>{scope.label}</span>
                  <b>{scope.value}</b>
                </div>
              ))}
            </div>

            <div className="side-section">
              <p className="section-label">Latest Plan</p>
              {(lastPlan.length > 0 ? lastPlan : [{ agent: "waiting", objective: "Send a message to generate a live plan." }]).map((step, index) => (
                <div className="trace-row" key={`${step.agent}-${index}`}>
                  <b>{step.agent ?? "agent"}</b>
                  <span>{step.objective ?? "No objective yet."}</span>
                </div>
              ))}
            </div>

            <div className="side-section">
              <p className="section-label">Agents</p>
              {agents.map((agent) => (
                <button
                  className={`agent-row ${agent.name === activeAgent ? "active" : ""}`}
                  key={agent.name}
                  type="button"
                  onClick={() => setActiveAgent(agent.name)}
                >
                  <b>{agent.name}</b>
                  <span>{agent.role}</span>
                </button>
              ))}
            </div>
            </aside>
          )}
        </div>
      </section>

      <aside className="agent-dock" aria-label="Agent dock">
        {agents.map((agent) => {
          const backendState = agentActivity[agent.name];
          const state =
            backendState?.state ??
            (agent.name === activeAgent
              ? intelligenceStatus
              : agent.name === "Nova" && activeModule === "research"
                ? "Researching"
                : agent.name === "Vega" && activeModule === "code"
                  ? "Building"
                  : "Idle");

          return (
            <button
              className={`dock-agent ${agent.name === activeAgent ? "active" : ""} state-${state.toLowerCase()}`}
              key={agent.name}
              type="button"
              onClick={() => setActiveAgent(agent.name)}
            >
              <b>{agent.name}</b>
              <span>{state}</span>
              {backendState?.last_event && <small>{backendState.last_event}</small>}
            </button>
          );
        })}
      </aside>

      {missionOpen && (
        <div className="mission-composer-backdrop" role="presentation" onClick={() => setMissionOpen(false)}>
          <section className="mission-composer-panel" role="dialog" aria-modal="true" onClick={(event) => event.stopPropagation()}>
            <button className="drawer-close" type="button" aria-label="Close mission composer" onClick={() => setMissionOpen(false)}>
              <Icon name="close" />
            </button>
            <div className="mission-composer-visual" aria-hidden="true">
              <span />
              <i />
              <b>MISSION</b>
            </div>
            <div className="mission-composer-copy">
              <p className="eyebrow">HELIOS Mission Composer</p>
              <h3>Define the objective.</h3>
              <span>{missionAgent} will route this through {modules.find((item) => item.key === missionModule)?.title ?? "HELIOS"}.</span>
            </div>
            <input
              autoFocus
              value={missionTitle}
              placeholder="What should HELIOS accomplish?"
              onChange={(event) => setMissionTitle(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") void createMission();
              }}
            />
            <label className="mission-schedule-field">
              <span className="section-label">Schedule (optional)</span>
              <input
                type="datetime-local"
                value={missionScheduledAt}
                min={new Date().toISOString().slice(0, 16)}
                onChange={(event) => setMissionScheduledAt(event.target.value)}
              />
            </label>
            <div className="mission-picker-grid">
              <div>
                <p className="section-label">Workspace</p>
                <div className="mission-picker-options">
                  {modules.slice(0, 12).map((item) => (
                    <button
                      className={item.key === missionModule ? "active" : ""}
                      key={item.key}
                      type="button"
                      onClick={() => {
                        setMissionModule(item.key);
                        setMissionAgent(item.agent);
                      }}
                    >
                      <span>{item.icon}</span>
                      <b>{item.title}</b>
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <p className="section-label">Agent</p>
                <div className="mission-picker-options compact">
                  {agents.map((agent) => (
                    <button
                      className={agent.name === missionAgent ? "active" : ""}
                      key={agent.name}
                      type="button"
                      onClick={() => setMissionAgent(agent.name)}
                    >
                      <b>{agent.name}</b>
                      <small>{agentActivity[agent.name]?.state ?? "Idle"}</small>
                    </button>
                  ))}
                </div>
              </div>
            </div>
            <button
              className="mission-create-button"
              type="button"
              disabled={!missionTitle.trim() || isCreatingMission}
              onClick={() => void createMission()}
            >
              {isCreatingMission ? "Saving" : missionScheduledAt ? "Schedule Mission" : "Create Mission"}
            </button>
          </section>
        </div>
      )}

      {memoryOpen && (
        <div className="memory-drawer" role="dialog" aria-modal="true">
          <div className="drawer-panel">
            <button className="drawer-close" type="button" aria-label="Close memory" onClick={() => setMemoryOpen(false)}>
              <Icon name="close" />
            </button>
            <p className="eyebrow">Scoped Memory</p>
            <h3>{memoryTotal} saved conversations</h3>
            <span className="drawer-copy">
              Live backend memory and indexed project sources are available to the cognitive engine.
            </span>
            <div className="memory-controls">
              <button type="button" onClick={() => void refreshMemoryItems()} disabled={memoryBusy}>Refresh</button>
              <button type="button" onClick={() => exportJson("helios-memory.json", memoryItems)}>Export JSON</button>
              <span>{memoryStatus}</span>
            </div>
            <div className="memory-list">
              {memoryItems.length > 0 ? memoryItems.map((item, index) => (
                <article className="memory-entry" key={`${item.timestamp ?? "memory"}-${index}`}>
                  <div>
                    <b>{renderText(item.user, "User")}</b>
                    <span>{renderText(item.assistant, "Assistant")}</span>
                  </div>
                  <small>{renderText(item.timestamp, "Stored memory entry")}</small>
                  <button type="button" onClick={() => void deleteMemoryItem(index)}>Delete</button>
                </article>
              )) : <p className="memory-empty">No memory items are stored yet.</p>}
            </div>
            <div className="brain-map">
              <div className="brain-core">
                <b>{projectBrain?.summary?.total_nodes ?? 0}</b>
                <span>nodes</span>
                <i>{projectBrain?.summary?.health ?? "loading"}</i>
              </div>
              <div className="deep-brain-graph">
                <GraphMap
                  nodes={projectBrain?.nodes ?? []}
                  links={projectBrain?.links ?? []}
                  selectedId={selectedBrainNode?.id}
                  onSelect={setSelectedBrainNode}
                  label="Interactive Project Brain knowledge graph"
                />
                <div className="graph-selection">
                  <b>{selectedBrainNode?.label ?? "Select a Project Brain node"}</b>
                  <span>{selectedBrainNode?.detail ?? selectedBrainNode?.kind ?? "Inspect memory, sources, missions, semantic records, and executions."}</span>
                </div>
              </div>
            </div>
            {liveMemoryScopes.map((scope) => (
              <div className={`memory-card ${scope.tone}`} key={scope.label}>
                <b>{scope.label}</b>
                <span>{scope.value}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {executionOpen && (
        <div className="memory-drawer" role="dialog" aria-modal="true">
          <div className="drawer-panel execution-drawer">
            <button className="drawer-close" type="button" aria-label="Close execution log" onClick={() => setExecutionOpen(false)}>
              <Icon name="close" />
            </button>
            <p className="eyebrow">Execution Log</p>
            <h3>{runLedger.length} captured events</h3>
            <span className="drawer-copy">Inspect tool calls, attempts, failures, inputs, and outputs from the live execution ledger.</span>
            <div className="execution-controls">
              <input
                placeholder="Filter events"
                value={executionSearch}
                onChange={(event) => setExecutionSearch(event.target.value)}
              />
              <select value={executionStatusFilter} onChange={(event) => setExecutionStatusFilter(event.target.value)}>
                <option value="all">All statuses</option>
                <option value="success">Success</option>
                <option value="failed">Failed</option>
                <option value="blocked">Blocked</option>
                <option value="running">Running</option>
              </select>
              <button type="button" onClick={() => exportJson("helios-execution-log.json", filteredExecutionEvents)}>Export</button>
              <button type="button" onClick={() => void refreshExecutionEvents()}>Refresh</button>
              <button type="button" disabled={!selectedExecution?.tool} onClick={() => void retrySelectedExecution()}>Retry tool</button>
              <button type="button" onClick={() => setRunLedger([])}>Clear view</button>
            </div>
            <div className="execution-drawer-grid">
              <div className="execution-event-list">
                {filteredExecutionEvents.map((event) => (
                  <button
                    className={`${selectedExecution?.id === event.id ? "active" : ""} ${event.status ?? "unknown"}`}
                    key={event.id}
                    type="button"
                    onClick={() => setSelectedExecutionId(event.id)}
                  >
                    <b>{event.label}</b>
                    <span>{[event.tool, event.status, event.duration_ms ? `${event.duration_ms} ms` : null].filter(Boolean).join(" / ")}</span>
                  </button>
                ))}
              </div>
              <div className="execution-event-detail">
                {selectedExecution ? (
                  <>
                    <b>{selectedExecution.label}</b>
                    <span>{[selectedExecution.actor, selectedExecution.module, selectedExecution.status, selectedExecution.timestamp].filter(Boolean).join(" / ")}</span>
                    <div>
                      <strong>Attempt</strong>
                      <pre>{selectedExecution.attempt ?? 1}</pre>
                    </div>
                    <div>
                      <strong>Input</strong>
                      <pre>{JSON.stringify(selectedExecution.input ?? null, null, 2)}</pre>
                    </div>
                    <div>
                      <strong>Result</strong>
                      <pre>{JSON.stringify(selectedExecution.result ?? selectedExecution.error ?? null, null, 2)}</pre>
                    </div>
                  </>
                ) : (
                  <span>No execution events captured yet.</span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {deployOpen && (
        <div className="memory-drawer" role="dialog" aria-modal="true">
          <div className="drawer-panel deploy-panel">
            <button className="drawer-close" type="button" aria-label="Close deploy" onClick={() => setDeployOpen(false)}>
              <Icon name="close" />
            </button>
            <p className="eyebrow">Deploy Console</p>
            <h3>{runtimeLabel}</h3>
            <span className="drawer-copy">Runtime checks are pulled from the local FastAPI health endpoint.</span>
            {[
              { label: "FastAPI backend", ok: runtimeState !== "offline" },
              { label: `${modelName} available`, ok: Boolean(health?.ai?.model_available) },
              { label: "Live events feed", ok: runLedgerStatus === "live" },
              { label: "Cognitive engine", ok: health?.cognitive_engine?.status === "online" },
              { label: `Last run ${lastRunAt}`, ok: lastTrace.length > 0 },
            ].map((item) => (
              <div className={`deploy-check ${item.ok ? "ok" : "warn"}`} key={item.label}>
                <span>{item.ok ? "✓" : "!"}</span>
                <b>{item.label}</b>
              </div>
            ))}
            <button
              className="mission-create-button"
              type="button"
              disabled={Boolean(authUser && authUser.role !== "admin")}
              onClick={() => void deployProject()}
            >
              Deploy HELIOS
            </button>
          </div>
        </div>
      )}

      {accountOpen && (
        <div className="memory-drawer" role="dialog" aria-modal="true">
          <div className="drawer-panel account-drawer">
            <button className="drawer-close" type="button" aria-label="Close account" onClick={() => setAccountOpen(false)}>
              <Icon name="close" />
            </button>
            <p className="eyebrow">Account</p>
            <h3>{authUser?.username ?? "Local access"}</h3>
            <span className="drawer-copy">
              {authUser ? `${authUser.role} permissions are active for this session.` : "Authentication is managed by local API key or open development mode."}
            </span>
            <div className="account-profile">
              <Icon name="user" />
              <div>
                <b>{authUser?.username ?? "Local operator"}</b>
                <span>{authUser?.role ?? (HELIOS_API_KEY ? "API key access" : "Development access")}</span>
              </div>
              <i>{authUser?.active === false ? "disabled" : "active"}</i>
            </div>

            {authUser?.role === "admin" && (
              <section className="user-admin">
                <p className="section-label">User Management</p>
                <form
                  className="user-admin-form"
                  onSubmit={(event) => {
                    event.preventDefault();
                    void addManagedUser();
                  }}
                >
                  <input
                    placeholder="Username"
                    autoComplete="off"
                    value={newUsername}
                    onChange={(event) => setNewUsername(event.target.value)}
                  />
                  <input
                    placeholder="Temporary password"
                    autoComplete="new-password"
                    type="password"
                    value={newPassword}
                    onChange={(event) => setNewPassword(event.target.value)}
                  />
                  <select value={newRole} onChange={(event) => setNewRole(event.target.value)}>
                    <option value="viewer">Viewer</option>
                    <option value="operator">Operator</option>
                    <option value="admin">Admin</option>
                  </select>
                  <button type="submit" disabled={!newUsername.trim() || !newPassword}>Create user</button>
                </form>
                {userAdminStatus && <span className="user-admin-status">{userAdminStatus}</span>}
                <div className="user-list">
                  {managedUsers.map((user) => (
                    <div className="user-row" key={user.id ?? user.username}>
                      <div>
                        <b>{user.username}</b>
                        <span>{user.role}</span>
                      </div>
                      <i>{user.active === false ? "disabled" : "active"}</i>
                    </div>
                  ))}
                  {managedUsers.length === 0 && <span className="user-admin-status">No users loaded yet.</span>}
                </div>
              </section>
            )}

            {authUser && (
              <button className="logout-button" type="button" onClick={logout}>
                Sign out
              </button>
            )}
          </div>
        </div>
      )}

      {commandOpen && (
        <div className="command-backdrop" role="presentation" onClick={() => setCommandOpen(false)}>
          <div className="command-palette" role="dialog" aria-modal="true" onClick={(event) => event.stopPropagation()}>
            <input
              autoFocus
              placeholder="Cmd K • command HELIOS"
              value={commandQuery}
              onChange={(event) => setCommandQuery(event.target.value)}
            />
            {commandStatus && <div className="command-status">{commandStatus}</div>}
            {filteredCommands.map((command) => (
              <button
                className="launcher-command"
                key={command.id}
                type="button"
                disabled={Boolean(runningCommandId)}
                onClick={() => void runLauncherCommand(command)}
              >
                <span>{command.category}</span>
                <b>{runningCommandId === command.id ? "Running..." : command.label}</b>
                <small>{command.detail}</small>
              </button>
            ))}
            {filteredModules.map((item) => (
              <button className="launcher-command" key={item.key} type="button" onClick={() => { switchModule(item.key); setCommandOpen(false); }}>
                <span>Workspace</span>
                <b>Open {item.title}</b>
                <small>{item.description}</small>
              </button>
            ))}
            {filteredCommands.length === 0 && filteredModules.length === 0 && (
              <div className="empty-command">No matching command</div>
            )}
          </div>
        </div>
      )}
    </main>
  );
}
