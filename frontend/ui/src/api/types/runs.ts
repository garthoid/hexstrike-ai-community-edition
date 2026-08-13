export interface ToolExecResponse {
  stdout: string;
  stderr: string;
  return_code: number;
  success: boolean;
  timed_out: boolean;
  partial_results: boolean;
  execution_time: number;
  timestamp: string;
}

export interface RunHistoryEntry {
  id: number;
  tool: string;
  endpoint: string;
  params: Record<string, unknown>;
  session_id?: string;
  stdout: string;
  stderr: string;
  return_code: number;
  success: boolean;
  timed_out: boolean;
  partial_results: boolean;
  execution_time: number;
  timestamp: string;
  hash?: string;
  prev_hash?: string;
}

export interface RunHistoryResponse {
  success: boolean;
  total: number;
  runs: RunHistoryEntry[];
}

/** Lightweight run record returned by /api/runs/history/summary — no stdout/stderr/params. */
export interface RunHistorySummaryEntry {
  id: number;
  tool: string;
  timestamp: string;
  success: boolean;
  execution_time: number;
}

export interface RunHistorySummaryResponse {
  success: boolean;
  total: number;
  runs: RunHistorySummaryEntry[];
}

/** Response from GET /api/runs/lookup?hash=<hex> — find the run that produced a given evidence-chain hash. */
export interface RunLookupResponse {
  success: boolean;
  found: boolean;
  session_id?: string;
  tool?: string;
  endpoint?: string;
  params?: Record<string, unknown>;
  stdout?: string;
  stderr?: string;
  return_code?: number;
  timestamp?: string;
  hash?: string;
  prev_hash?: string;
  error?: string;
}
