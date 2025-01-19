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

export interface ScheduleLimits {
  engineerId: string;
  dailyHourLimit: number;
  weeklyHourLimit: number;
  alertThreshold: number;
}

export interface NotificationSettings {
  email: boolean;
  desktop: boolean;
  slack: boolean;
  scheduleAlerts: boolean;
  achievementAlerts: boolean;
}

export interface IntegrationSettings {
  github: string | null;
  jira: string | null;
  linear: string | null;
}

export interface DisplaySettings {
  theme: 'light' | 'dark';
  compactView: boolean;
  showAchievements: boolean;
  defaultView: 'board' | 'list' | 'table';
}

export interface Settings {
  engineerId: string;
  notifications: NotificationSettings;
  integrations: IntegrationSettings;
  display: DisplaySettings;
  createdAt: string;
  updatedAt: string;
}

export const api = {
  // Schedule endpoints
  getScheduleLimits: async (engineerId: string): Promise<ScheduleLimits> => {
    try {
      const response = await axios.get(`${API_BASE_URL}/settings/${engineerId}/schedule`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch schedule limits:', error);
      throw error;
    }
  },

  setScheduleLimits: async (data: {
    engineerId: string;
    dailyHourLimit: number;
    weeklyHourLimit: number;
    alertThreshold?: number;
  }): Promise<void> => {
    try {
      await axios.patch(`${API_BASE_URL}/settings/${data.engineerId}/schedule`, {
        dailyHourLimit: data.dailyHourLimit,
        weeklyHourLimit: data.weeklyHourLimit,
        alertThreshold: data.alertThreshold || 80
      });
      
      // Re-fetch to ensure data is persisted
      const response = await axios.get(`${API_BASE_URL}/settings/${data.engineerId}/schedule`);
      console.log('Schedule limits verification response:', response.data);
      
      if (response.data.dailyHourLimit !== data.dailyHourLimit || 
          response.data.weeklyHourLimit !== data.weeklyHourLimit) {
        throw new Error('Schedule limits not persisted correctly');
      }
    } catch (error) {
      console.error('Failed to set schedule limits:', error);
      throw error;
    }
  },

  // Settings endpoints
  getSettings: async (engineerId: string): Promise<Settings> => {
    try {
      const response = await axios.get(`${API_BASE_URL}/settings/${engineerId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch settings:', error);
      throw error;
    }
  },

  updateNotifications: async (engineerId: string, notifications: NotificationSettings): Promise<void> => {
    try {
      await axios.patch(`${API_BASE_URL}/settings/${engineerId}/notifications`, notifications);
    } catch (error) {
      console.error('Failed to update notification settings:', error);
      throw error;
    }
  },

  updateIntegrations: async (engineerId: string, integrations: IntegrationSettings): Promise<void> => {
    try {
      await axios.patch(`${API_BASE_URL}/settings/${engineerId}/integrations`, integrations);
    } catch (error) {
      console.error('Failed to update integration settings:', error);
      throw error;
    }
  },

  updateDisplay: async (engineerId: string, display: DisplaySettings): Promise<void> => {
    try {
      await axios.patch(`${API_BASE_URL}/settings/${engineerId}/display`, display);
    } catch (error) {
      console.error('Failed to update display settings:', error);
      throw error;
    }
  },

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
