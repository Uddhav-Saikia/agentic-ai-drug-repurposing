'use client'

import { QueryStatus } from '@/lib/api'
import { CheckCircle, Clock, Loader2, XCircle, Activity } from 'lucide-react'

interface ProgressTrackerProps {
  queryStatus: QueryStatus
}

export function ProgressTracker({ queryStatus }: ProgressTrackerProps) {
  const { progress } = queryStatus

  const getAgentIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-6 w-6 text-success-600" />
      case 'running':
        return <Loader2 className="h-6 w-6 text-primary-600 animate-spin" />
      case 'failed':
        return <XCircle className="h-6 w-6 text-danger-600" />
      default:
        return <Clock className="h-6 w-6 text-gray-400" />
    }
  }

  const getAgentColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'border-success-300 bg-success-50'
      case 'running':
        return 'border-primary-300 bg-primary-50 animate-pulse-slow'
      case 'failed':
        return 'border-danger-300 bg-danger-50'
      default:
        return 'border-gray-300 bg-gray-50'
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <div className="flex items-center space-x-3 mb-6">
        <Activity className="h-6 w-6 text-primary-600" />
        <h2 className="text-xl font-semibold text-gray-900">
          Analysis Progress
        </h2>
      </div>

      {/* Overall Progress Bar */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">
            Overall Progress
          </span>
          <span className="text-sm font-semibold text-primary-600">
            {progress.percentage.toFixed(0)}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            className="bg-gradient-to-r from-primary-500 to-purple-600 h-3 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${progress.percentage}%` }}
          />
        </div>
        <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
          <span>{progress.completed} completed</span>
          <span>{progress.running} running</span>
          <span>{progress.failed} failed</span>
          <span>{progress.total} total</span>
        </div>
      </div>

      {/* Agent Tasks */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {progress.tasks.map((task) => (
          <div
            key={task.agent_type}
            className={`border-2 rounded-lg p-4 transition-all ${getAgentColor(
              task.status
            )}`}
          >
            <div className="flex items-center space-x-3 mb-2">
              {getAgentIcon(task.status)}
              <h3 className="font-semibold capitalize text-gray-900">
                {task.agent_type} Agent
              </h3>
            </div>
            <div className="space-y-1 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Status:</span>
                <span className="font-medium capitalize text-gray-900">
                  {task.status}
                </span>
              </div>
              {task.started_at && (
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Started:</span>
                  <span className="text-gray-900">
                    {new Date(task.started_at).toLocaleTimeString()}
                  </span>
                </div>
              )}
              {task.completed_at && (
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Completed:</span>
                  <span className="text-gray-900">
                    {new Date(task.completed_at).toLocaleTimeString()}
                  </span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Status Message */}
      {queryStatus.message && (
        <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <p className="text-sm text-blue-800">{queryStatus.message}</p>
        </div>
      )}
    </div>
  )
}
