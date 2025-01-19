import * as React from "react";
import { useState, useEffect } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { api } from '../services/api';
import { Loader2, Github, Trello, LineChart } from 'lucide-react';

interface IntegrationsPanelProps {
  engineerId?: string;
}

export function IntegrationsPanel({ engineerId = 'current' }: IntegrationsPanelProps) {
  const [integrations, setIntegrations] = useState({
    github: '',
    jira: '',
    linear: ''
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
        setIntegrations({
          github: settings.integrations.github || '',
          jira: settings.integrations.jira || '',
          linear: settings.integrations.linear || ''
        });
      } catch (err) {
        setError('Failed to load integration settings');
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
      await api.updateIntegrations(engineerId, integrations);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError('Failed to save integration settings');
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (key: keyof typeof integrations, value: string) => {
    setIntegrations(prev => ({
      ...prev,
      [key]: value
    }));
  };

  return (
    <Card className="p-6">
      <h2 className="text-lg font-semibold mb-4">Integrations</h2>
      <p className="text-sm text-gray-500 mb-6">
        Configure GitHub, Jira, and Linear integrations.
      </p>

      {loading ? (
        <div className="flex items-center justify-center py-4">
          <Loader2 className="h-6 w-6 animate-spin text-gray-500" />
        </div>
      ) : (
        <div className="space-y-4">
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium flex items-center gap-2">
                <Github className="h-4 w-4" />
                GitHub Token
              </label>
              <Input
                type="password"
                value={integrations.github}
                onChange={(e) => handleChange('github', e.target.value)}
                placeholder="Enter GitHub personal access token"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium flex items-center gap-2">
                <Trello className="h-4 w-4" />
                Jira Token
              </label>
              <Input
                type="password"
                value={integrations.jira}
                onChange={(e) => handleChange('jira', e.target.value)}
                placeholder="Enter Jira API token"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium flex items-center gap-2">
                <LineChart className="h-4 w-4" />
                Linear Token
              </label>
              <Input
                type="password"
                value={integrations.linear}
                onChange={(e) => handleChange('linear', e.target.value)}
                placeholder="Enter Linear API key"
              />
            </div>
          </div>

          {error && (
            <p className="text-sm text-red-500 mt-2">{error}</p>
          )}

          {success && (
            <p className="text-sm text-green-500 mt-2">
              Integration settings saved successfully
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
