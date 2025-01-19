import * as React from "react";
import { useState, useEffect } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Checkbox } from './ui/checkbox';
import { api } from '../services/api';
import { Loader2 } from 'lucide-react';

interface NotificationsPanelProps {
  engineerId?: string;
}

export function NotificationsPanel({ engineerId = 'current' }: NotificationsPanelProps) {
  const [notifications, setNotifications] = useState({
    email: true,
    desktop: true,
    slack: false,
    scheduleAlerts: true,
    achievementAlerts: true
  });
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const fetchSettings = async () => {
      setLoading(true);
      setError(null);
      try {
        const settings = await api.getSettings(engineerId);
        setNotifications(settings.notifications);
      } catch (err) {
        setError('Failed to load notification settings');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchSettings();
  }, [engineerId]);

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    setSuccess(false);

    try {
      await api.updateNotifications(engineerId, notifications);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError('Failed to save notification settings');
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const handleToggle = (key: keyof typeof notifications) => {
    setNotifications(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  return (
    <Card className="p-6">
      <h2 className="text-lg font-semibold mb-4">Notifications</h2>
      <p className="text-sm text-gray-500 mb-6">
        Manage alert preferences and notification settings.
      </p>

      {loading ? (
        <div className="flex items-center justify-center py-4">
          <Loader2 className="h-6 w-6 animate-spin text-gray-500" />
        </div>
      ) : (
        <div className="space-y-4">
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="email"
                checked={notifications.email}
                onCheckedChange={() => handleToggle('email')}
              />
              <label htmlFor="email" className="text-sm font-medium">
                Email Notifications
              </label>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="desktop"
                checked={notifications.desktop}
                onCheckedChange={() => handleToggle('desktop')}
              />
              <label htmlFor="desktop" className="text-sm font-medium">
                Desktop Notifications
              </label>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="slack"
                checked={notifications.slack}
                onCheckedChange={() => handleToggle('slack')}
              />
              <label htmlFor="slack" className="text-sm font-medium">
                Slack Notifications
              </label>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="scheduleAlerts"
                checked={notifications.scheduleAlerts}
                onCheckedChange={() => handleToggle('scheduleAlerts')}
              />
              <label htmlFor="scheduleAlerts" className="text-sm font-medium">
                Schedule Limit Alerts
              </label>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="achievementAlerts"
                checked={notifications.achievementAlerts}
                onCheckedChange={() => handleToggle('achievementAlerts')}
              />
              <label htmlFor="achievementAlerts" className="text-sm font-medium">
                Achievement Notifications
              </label>
            </div>
          </div>

          {error && (
            <p className="text-sm text-red-500 mt-2">{error}</p>
          )}

          {success && (
            <p className="text-sm text-green-500 mt-2">
              Notification settings saved successfully
            </p>
          )}

          <Button
            onClick={handleSave}
            disabled={saving}
            className="w-full"
          >
            {saving ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              'Save Changes'
            )}
          </Button>
        </div>
      )}
    </Card>
  );
}
