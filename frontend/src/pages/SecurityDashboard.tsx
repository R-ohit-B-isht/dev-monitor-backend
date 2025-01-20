import * as React from 'react';
import { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { AlertTriangle, AlertCircle, Shield, ShieldCheck, ShieldX } from 'lucide-react';
import { Breadcrumb } from '../components/Breadcrumb';
import { getSecurityAlerts, getSecurityStats, syncSecurityAlerts } from '../services/api';

interface SecurityAlert {
  _id: string;
  repository: string;
  alert_number: number;
  state: 'open' | 'fixed' | 'dismissed';
  severity: 'high' | 'medium' | 'low';
  description: string;
  location?: {
    path: string;
    start_line: number;
    end_line: number;
  };
  created_at: string;
  updated_at: string;
}

interface SecurityStats {
  total: number;
  open: number;
  fixed: number;
  dismissed: number;
  high_severity: number;
  medium_severity: number;
  low_severity: number;
}

const severityColors = {
  high: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
  medium: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
  low: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
};

const stateColors = {
  open: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
  fixed: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
  dismissed: 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300'
};

export function SecurityDashboard() {
  const [alerts, setAlerts] = useState<SecurityAlert[]>([]);
  const [stats, setStats] = useState<SecurityStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [syncing, setSyncing] = useState(false);

  const fetchData = async () => {
    try {
      const [alertsData, statsData] = await Promise.all([
        getSecurityAlerts({ repository }),
        getSecurityStats({ repository })
      ]);
      setAlerts(alertsData.alerts);
      setStats(statsData);
    } catch (err) {
      console.error('Failed to fetch security data:', err);
      setError('Failed to load security data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const [repository, setRepository] = useState<string>('');
  
  const handleSync = async () => {
    if (!repository) {
      setError('Please select a repository');
      return;
    }
    
    setSyncing(true);
    try {
      await syncSecurityAlerts(repository);
      await fetchData();
    } catch (err) {
      console.error('Failed to sync alerts:', err);
      setError('Failed to sync alerts');
    } finally {
      setSyncing(false);
    }
  };

  if (loading) {
    return <div>Loading security data...</div>;
  }

  return (
    <div className="p-4 sm:p-6">
      <Breadcrumb
        items={[
          { label: 'Dashboard', href: '/' },
          { label: 'Security' }
        ]}
      />

      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
        <h1 className="text-xl sm:text-2xl font-bold">Security Dashboard</h1>
        <div className="flex items-center gap-4">
          <input
            type="text"
            placeholder="Enter repository (owner/repo)"
            value={repository}
            onChange={(e) => setRepository(e.target.value)}
            className="px-3 py-2 border rounded-md text-sm"
          />
          <Button
            onClick={handleSync}
            disabled={syncing || !repository}
          >
            {syncing ? 'Syncing...' : 'Sync Alerts'}
          </Button>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 border border-red-200 rounded-lg bg-red-50 text-red-800">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4" />
            {error}
          </div>
        </div>
      )}

      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">
                Total Alerts
              </CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">
                Open Alerts
              </CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{stats.open}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">
                Fixed Alerts
              </CardTitle>
              <ShieldCheck className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{stats.fixed}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">
                Dismissed Alerts
              </CardTitle>
              <ShieldX className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-600">{stats.dismissed}</div>
            </CardContent>
          </Card>
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Security Alerts</CardTitle>
          <CardDescription>
            Code scanning alerts and security advisories
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {alerts.map((alert) => (
              <div
                key={alert._id}
                className="p-4 border rounded-lg space-y-2"
              >
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <h3 className="font-medium">
                        {alert.repository} #{alert.alert_number}
                      </h3>
                      <Badge
                        variant="secondary"
                        className={severityColors[alert.severity]}
                      >
                        {alert.severity}
                      </Badge>
                      <Badge
                        variant="secondary"
                        className={stateColors[alert.state]}
                      >
                        {alert.state}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {alert.description}
                    </p>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {new Date(alert.created_at).toLocaleDateString()}
                  </div>
                </div>
                {alert.location && (
                  <div className="text-sm text-muted-foreground">
                    {alert.location.path}:{alert.location.start_line}-{alert.location.end_line}
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
