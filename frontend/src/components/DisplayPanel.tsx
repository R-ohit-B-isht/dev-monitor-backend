import * as React from "react";
import { useState, useEffect } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Checkbox } from './ui/checkbox';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';
import { api } from '../services/api';
import { Loader2, Sun, Moon } from 'lucide-react';

interface DisplayPanelProps {
  engineerId?: string;
}

export function DisplayPanel({ engineerId = 'current' }: DisplayPanelProps) {
  const [display, setDisplay] = useState({
    theme: 'light',
    compactView: false,
    showAchievements: true,
    defaultView: 'board'
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
        setDisplay(settings.display);
      } catch (err) {
        setError('Failed to load display settings');
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
      await api.updateDisplay(engineerId, display);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError('Failed to save display settings');
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const handleToggle = (key: 'compactView' | 'showAchievements') => {
    setDisplay(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  return (
    <Card className="p-6">
      <h2 className="text-lg font-semibold mb-4">Display</h2>
      <p className="text-sm text-gray-500 mb-6">
        Customize theme and appearance settings.
      </p>

      {loading ? (
        <div className="flex items-center justify-center py-4">
          <Loader2 className="h-6 w-6 animate-spin text-gray-500" />
        </div>
      ) : (
        <div className="space-y-4">
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Theme</label>
              <Select
                value={display.theme}
                onValueChange={(value) => setDisplay(prev => ({ ...prev, theme: value }))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select theme" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="light">
                    <div className="flex items-center gap-2">
                      <Sun className="h-4 w-4" />
                      Light
                    </div>
                  </SelectItem>
                  <SelectItem value="dark">
                    <div className="flex items-center gap-2">
                      <Moon className="h-4 w-4" />
                      Dark
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Default View</label>
              <Select
                value={display.defaultView}
                onValueChange={(value) => setDisplay(prev => ({ ...prev, defaultView: value }))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select default view" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="board">Board View</SelectItem>
                  <SelectItem value="list">List View</SelectItem>
                  <SelectItem value="table">Table View</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="compactView"
                checked={display.compactView}
                onCheckedChange={() => handleToggle('compactView')}
              />
              <label htmlFor="compactView" className="text-sm font-medium">
                Compact View
              </label>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="showAchievements"
                checked={display.showAchievements}
                onCheckedChange={() => handleToggle('showAchievements')}
              />
              <label htmlFor="showAchievements" className="text-sm font-medium">
                Show Achievements
              </label>
            </div>
          </div>

          {error && (
            <p className="text-sm text-red-500 mt-2">{error}</p>
          )}

          {success && (
            <p className="text-sm text-green-500 mt-2">
              Display settings saved successfully
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
