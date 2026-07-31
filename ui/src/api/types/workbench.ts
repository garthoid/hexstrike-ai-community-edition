export interface WorkbenchParamSpec {
  name: string;
  label: string;
  type: 'text' | 'textarea' | 'number' | 'select';
  required: boolean;
  default: string | number;
  help_text: string;
  choices?: string[];
  hidden?: boolean;
}

export interface WorkbenchOperation {
  id: string;
  category: string;
  name: string;
  description: string;
  params: WorkbenchParamSpec[];
}

export interface WorkbenchOperationsResponse {
  success: boolean;
  categories: string[];
  operations: WorkbenchOperation[];
}

export interface WorkbenchRunResponse {
  success: boolean;
  output?: string;
  note?: string;
  error?: string;
}

export interface WorkbenchRecipeStepInput {
  operation_id: string;
  params: Record<string, unknown>;
}

export interface WorkbenchRecipeStepResult {
  operation_id: string;
  name?: string;
  output?: string;
  error?: string;
}

export interface WorkbenchRunRecipeResponse {
  success: boolean;
  output?: string;
  steps?: WorkbenchRecipeStepResult[];
  error?: string;
}

export interface WorkbenchSavedRecipe {
  recipe_id: string;
  name: string;
  steps: WorkbenchRecipeStepInput[];
  created_at: string;
  updated_at: string;
}

export interface WorkbenchRecipesResponse {
  success: boolean;
  recipes: WorkbenchSavedRecipe[];
  error?: string;
}

export interface WorkbenchRecipeMutationResponse {
  success: boolean;
  recipe?: WorkbenchSavedRecipe;
  error?: string;
}

export interface WorkbenchRecipeDeleteResponse {
  success: boolean;
  error?: string;
}
