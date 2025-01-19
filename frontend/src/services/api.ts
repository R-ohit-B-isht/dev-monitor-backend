import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';

export interface MonitoringMetrics {
  focusTimeSeconds: number;
  focusTimePercentage: number;
  totalActivities: number;
  focusActivities: number;
  focusActivityRatio: number;
  productivityScore: number;
  newBadges: string[];
}

export interface Achievement {
  badge: string;
  earnedAt: string;
  metadata: {
    sessionId: string;
    productivityScore: number;
    focusTime: number;
    totalActivities: number;
  };
}

export interface MeetingTimeMetrics {
  totalMeetingTime: number;
  meetingCount: number;
  idleTime: number;
}

export interface Relationship {
  _id: string;
  sourceTaskId: string;
  targetTaskId: string;
  type: 'blocks' | 'relates-to';
  createdAt: string;
  updatedAt: string;
}

export const api = {
  // Monitoring endpoints
  getMonitoringMetrics: async (): Promise<MonitoringMetrics> => {
    const response = await axios.get(`${API_BASE_URL}/monitoring/focus-metrics/current`);
    return response.data;
  },

  getAchievements: async (): Promise<{ achievements: Achievement[] }> => {
    const response = await axios.get(`${API_BASE_URL}/monitoring/achievements/current`);
    return response.data;
  },

  getMeetingTime: async (engineerId: string): Promise<MeetingTimeMetrics> => {
    const response = await axios.get(`${API_BASE_URL}/monitoring/meeting-time/${engineerId}`);
    return response.data;
  },

  discardIdleTime: async (sessionId: string): Promise<void> => {
    await axios.post(`${API_BASE_URL}/monitoring/discard-idle`, { sessionId });
  },

  generateReport: async (params: {
    startDate?: string;
    endDate?: string;
    type: 'daily' | 'weekly' | 'monthly';
    format: 'json' | 'csv';
    engineerId: string;
    includeAchievements: boolean;
    includeMeetings: boolean;
  }): Promise<any> => {
    const response = await axios.get(`${API_BASE_URL}/monitoring/report`, { params });
    return response.data;
  },

  getReportSummary: async () => {
    const response = await axios.get(`${API_BASE_URL}/monitoring/report/summary`);
    return response.data;
  }
};
