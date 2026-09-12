import {
  SearchRequest,
  SearchResponse,
  DecisionItem,
  Participant,
  EvaluationReport,
  ContextMessage,
} from './types';

const API_BASE = (import.meta.env.VITE_API_BASE || '/api').replace(/\/+$/, '');

export async function searchMessages(request: SearchRequest): Promise<SearchResponse> {
  const res = await fetch(`${API_BASE}/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!res.ok) {
    throw new Error(`Search request failed with status: ${res.status}`);
  }
  return res.json();
}

export async function getDecisions(): Promise<DecisionItem[]> {
  const res = await fetch(`${API_BASE}/decisions`);
  if (!res.ok) {
    throw new Error(`Failed to load decisions: ${res.status}`);
  }
  return res.json();
}

export async function getParticipants(): Promise<Participant[]> {
  const res = await fetch(`${API_BASE}/participants`);
  if (!res.ok) {
    throw new Error(`Failed to load participants: ${res.status}`);
  }
  return res.json();
}

export async function getMessageContext(
  messageId: string,
  window: number = 3
): Promise<ContextMessage[]> {
  const res = await fetch(`${API_BASE}/context/${messageId}?window=${window}`);
  if (!res.ok) {
    throw new Error(`Failed to load context for message ${messageId}: ${res.status}`);
  }
  return res.json();
}

export async function getThread(threadId: string): Promise<ContextMessage[]> {
  const res = await fetch(`${API_BASE}/thread/${threadId}`);
  if (!res.ok) {
    throw new Error(`Failed to load thread ${threadId}: ${res.status}`);
  }
  return res.json();
}

export async function getEvaluationReport(suite: string = 'official'): Promise<EvaluationReport> {
  const res = await fetch(`${API_BASE}/evaluation?suite=${suite}`);
  if (!res.ok) {
    throw new Error(`Failed to load evaluation report: ${res.status}`);
  }
  return res.json();
}

export async function getHealthCheck(): Promise<{
  status: string;
  service: string;
  index_ready: boolean;
  indexed_messages: number;
  version: string;
}> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) {
    throw new Error(`Failed to fetch health check: ${res.status}`);
  }
  return res.json();
}

export function getExportPdfUrl(params: {
  threadId?: string;
  messageId?: string;
  query?: string;
  directAnswer?: string;
}): string {
  const sp = new URLSearchParams();
  if (params.threadId) sp.set('thread_id', params.threadId);
  if (params.messageId) sp.set('message_id', params.messageId);
  if (params.query) sp.set('query', params.query);
  if (params.directAnswer) sp.set('direct_answer', params.directAnswer);
  return `${API_BASE}/export/pdf?${sp.toString()}`;
}

export function getExportImageUrl(params: {
  threadId?: string;
  messageId?: string;
  query?: string;
  directAnswer?: string;
}): string {
  const sp = new URLSearchParams();
  if (params.threadId) sp.set('thread_id', params.threadId);
  if (params.messageId) sp.set('message_id', params.messageId);
  if (params.query) sp.set('query', params.query);
  if (params.directAnswer) sp.set('direct_answer', params.directAnswer);
  return `${API_BASE}/export/image?${sp.toString()}`;
}

