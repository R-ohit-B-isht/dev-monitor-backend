import * as React from "react";
import { useState, useEffect } from 'react';
import { Card } from './ui/card';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { api } from '../services/api';
import { Loader2 } from 'lucide-react';

interface ScheduleLimitsProps {
  engineerId?: string;
}

export function ScheduleLimits({ engineerId = 'current' }: ScheduleLimitsProps) {
  const [dailyHourLimit, setDailyHourLimit] = useState<number>(8);
  const [weeklyHourLimit, setWeeklyHourLimit] = useState<number>(40);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const fetchLimits = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await api.getScheduleLimits(engineerId);
        console.log('Schedule limits response:', response);
        if (response && typeof response.dailyHourLimit === 'number' && typeof response.weeklyHourLimit === 'number') {
          setDailyHourLimit(response.dailyHourLimit);
          setWeeklyHourLimit(response.weeklyHourLimit);
        } else {
          console.error('Invalid schedule limits response:', response);
          throw new Error('Invalid schedule limits response');
        }
      } catch (err) {
        setError('Failed to load schedule limits');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchLimits();
  }, [engineerId]);

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    setSuccess(false);

    try {
      await api.setScheduleLimits({
        engineerId,
        dailyHourLimit,
        weeklyHourLimit,
        alertThreshold: 80
      });
      
      // Re-fetch to ensure data is persisted
      const response = await api.getScheduleLimits(engineerId);
      setDailyHourLimit(response.dailyHourLimit);
      setWeeklyHourLimit(response.weeklyHourLimit);
      
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError('Failed to save schedule limits');
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const handleDailyChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value);
    if (!isNaN(value) && value >= 1 && value <= 24) {
      setDailyHourLimit(value);
    }
  };

  const handleWeeklyChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value);
    if (!isNaN(value) && value >= 1 && value <= 168) {
      setWeeklyHourLimit(value);
    }
  };

  return (
    <Card className="p-6">
      <h2 className="text-lg font-semibold mb-4">Schedule Limits</h2>
      <p className="text-sm text-gray-500 mb-6">
        Configure daily and weekly work hour limits.
      </p>

      {loading ? (
        <div className="flex items-center justify-center py-4">
          <Loader2 className="h-6 w-6 animate-spin text-gray-500" />
        </div>
      ) : (
        <div className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Daily Hour Limit</label>
            <Input
              type="number"
              min="1"
              max="24"
              value={dailyHourLimit}
              onChange={handleDailyChange}
              className="w-full"
            />
            <p className="text-xs text-gray-500">Maximum hours per day (1-24)</p>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Weekly Hour Limit</label>
            <Input
              type="number"
              min="1"
              max="168"
              value={weeklyHourLimit}
              onChange={handleWeeklyChange}
              className="w-full"
            />
            <p className="text-xs text-gray-500">Maximum hours per week (1-168)</p>
          </div>

          {error && (
            <p className="text-sm text-red-500 mt-2">{error}</p>
          )}

          {success && (
            <p className="text-sm text-green-500 mt-2">
              Schedule limits saved successfully
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
