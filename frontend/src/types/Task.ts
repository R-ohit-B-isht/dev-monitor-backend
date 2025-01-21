export interface Task {
  _id: string;
  title: string;
  description?: string;
  status: 'To-Do' | 'In-Progress' | 'Done';
  integration: 'github' | 'jira' | 'linear';
  createdAt: string;
  updatedAt: string;
  devinSessionUrl?: string;
  sourceUrl?: string;
  sourceId?: string;
  issueKey?: string;
  priority?: 'high' | 'medium' | 'low';
}
