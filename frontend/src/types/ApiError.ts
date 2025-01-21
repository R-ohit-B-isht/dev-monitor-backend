export interface ApiErrorResponse {
    error: string;
    data?: {
      error?: string;
    };
    response?: {
      data?: {
        error?: string;
      };
      status?: number;
      headers?: Record<string, string>;
    };
  }
