'use client'

import { useQuery } from '@tanstack/react-query'
import { agentAPI, healthAPI, type SystemStatus } from '@/lib/api'
import { Activity, Database, Server, CheckCircle, XCircle, AlertTriangle } from 'lucide-react'

export function SystemStatus() {
  const { data: systemStatus, isLoading, error } = useQuery<SystemStatus>({
    queryKey: ['systemStatus'],
    queryFn: () => agentAPI.getSystemStatus(),
    refetchInterval: 10000, // Refetch every 10 seconds
  })

  if (isLoading) {
    return <div className="text-center py-8">Loading system status...</div>
  }

  if (error || !systemStatus) {
    return <div className="text-center py-8 text-danger-600">Failed to load system status</div>
  }

  const getStatusIcon = (status: string) => {
    if (status === 'healthy') return <CheckCircle className="h-5 w-5 text-success-600" />
    if (status === 'degraded') return <AlertTriangle className="h-5 w-5 text-warning-600" />
    return <XCircle className="h-5 w-5 text-danger-600" />
  }

  const getStatusColor = (status: string) => {
    if (status === 'healthy') return 'bg-success-50 border-success-200 text-success-700'
    if (status === 'degraded') return 'bg-warning-50 border-warning-200 text-warning-700'
    return 'bg-danger-50 border-danger-200 text-danger-700'
  }

  return (
    <div className="space-y-6">
      {/* Overall Status */}
      <div className={`p-6 rounded-lg border-2 ${getStatusColor(systemStatus.status)}`}>
        <div className="flex items-center space-x-3">
          {getStatusIcon(systemStatus.status)}
          <div>
            <h3 className="text-lg font-semibold">System Status: {systemStatus.status.toUpperCase()}</h3>
            <p className="text-sm opacity-80">Last checked: {new Date(systemStatus.timestamp).toLocaleString()}</p>
          </div>
        </div>
      </div>

      {/* Infrastructure Status */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <div className="flex items-center space-x-3 mb-4">
            <Database className="h-6 w-6 text-primary-600" />
            <h4 className="font-semibold text-lg">Database</h4>
          </div>
          <div className="flex items-center space-x-2">
            {getStatusIcon(systemStatus.database)}
            <span className="capitalize">{systemStatus.database}</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <div className="flex items-center space-x-3 mb-4">
            <Server className="h-6 w-6 text-primary-600" />
            <h4 className="font-semibold text-lg">Redis Cache</h4>
          </div>
          <div className="flex items-center space-x-2">
            {getStatusIcon(systemStatus.redis)}
            <span className="capitalize">{systemStatus.redis}</span>
          </div>
        </div>
      </div>

      {/* Agent Status */}
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <div className="flex items-center space-x-3 mb-6">
          <Activity className="h-6 w-6 text-primary-600" />
          <h4 className="font-semibold text-lg">Agent Performance</h4>
        </div>

        <div className="space-y-4">
          {systemStatus.agents.map((agent) => (
            <div key={agent.agent_name} className="border-b border-gray-100 pb-4 last:border-0 last:pb-0">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-3">
                  {getStatusIcon(agent.status)}
                  <h5 className="font-semibold capitalize">{agent.agent_name} Agent</h5>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(agent.status)}`}>
                  {agent.status.toUpperCase()}
                </span>
              </div>

              <div className="grid grid-cols-3 gap-4 mt-3">
                <div>
                  <p className="text-xs text-gray-500">Executions</p>
                  <p className="text-lg font-semibold text-gray-900">{agent.executions}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Success Rate</p>
                  <p className="text-lg font-semibold text-gray-900">{agent.success_rate.toFixed(1)}%</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Avg Time</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {agent.average_execution_time ? `${agent.average_execution_time.toFixed(1)}s` : 'N/A'}
                  </p>
                </div>
              </div>

              {/* Progress Bar for Success Rate */}
              <div className="mt-3">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      agent.success_rate >= 95 ? 'bg-success-600' : agent.success_rate >= 80 ? 'bg-warning-600' : 'bg-danger-600'
                    }`}
                    style={{ width: `${agent.success_rate}%` }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
