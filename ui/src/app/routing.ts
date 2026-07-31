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

export function buildWorkbenchHash(operationId: string | null, recipeJson: string | null): string {
  const path = operationId ? `/workbench/${encodeURIComponent(operationId)}` : '/workbench';
  if (!recipeJson) return path;
  const params = new URLSearchParams();
  params.set('recipe', recipeJson);
  return `${path}?${params.toString()}`;
}

export function routeFromHash(): {
  page: Page;
  sessionId: string | null;
  toolName: string | null;
  workbenchOperationId: string | null;
  workbenchRecipe: string | null;
} {
  const hash = window.location.hash.replace(/^#\/?/, '');
  if (hash.startsWith('sessions/')) {
    const sessionId = hash.slice('sessions/'.length);
    return {
      page: 'session-detail',
      sessionId: sessionId || null,
      toolName: null,
      workbenchOperationId: null,
      workbenchRecipe: null,
    };
  }
  if (hash.startsWith('run/')) {
    const toolName = decodeURIComponent(hash.slice('run/'.length));
    return {
      page: 'run',
      sessionId: null,
      toolName: toolName || null,
      workbenchOperationId: null,
      workbenchRecipe: null,
    };
  }
  if (hash === 'workbench' || hash.startsWith('workbench/') || hash.startsWith('workbench?')) {
    const [pathPart, queryPart] = hash.slice('workbench'.length).split('?');
    const operationId = pathPart.startsWith('/') ? decodeURIComponent(pathPart.slice(1)) : '';
    const recipe = new URLSearchParams(queryPart ?? '').get('recipe');
    return {
      page: 'workbench',
      sessionId: null,
      toolName: null,
      workbenchOperationId: operationId || null,
      workbenchRecipe: recipe,
    };
  }

  return {
    page: VALID_PAGES.has(hash as Page) ? (hash as Page) : 'dashboard',
    sessionId: null,
    toolName: null,
    workbenchOperationId: null,
    workbenchRecipe: null,
  };
}
