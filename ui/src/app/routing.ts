export type Page =
  | 'dashboard'
  | 'settings'
  | 'help'
  | 'logs'
  | 'run'
  | 'tasks'
  | 'tools'
  | 'plugins'
  | 'reports'
  | 'sessions'
  | 'session-detail'
  | 'loot'
  | 'verify'
  | 'workbench';

const VALID_PAGES = new Set<Page>([
  'dashboard',
  'settings',
  'help',
  'logs',
  'run',
  'tasks',
  'tools',
  'plugins',
  'reports',
  'sessions',
  'session-detail',
  'loot',
  'verify',
  'workbench',
]);

export function routeFromHash(): { page: Page; sessionId: string | null; toolName: string | null } {
  const hash = window.location.hash.replace(/^#\/?/, '');
  if (hash.startsWith('sessions/')) {
    const sessionId = hash.slice('sessions/'.length);
    return { page: 'session-detail', sessionId: sessionId || null, toolName: null };
  }
  if (hash.startsWith('run/')) {
    const toolName = decodeURIComponent(hash.slice('run/'.length));
    return { page: 'run', sessionId: null, toolName: toolName || null };
  }

  return {
    page: VALID_PAGES.has(hash as Page) ? (hash as Page) : 'dashboard',
    sessionId: null,
    toolName: null,
  };
}
