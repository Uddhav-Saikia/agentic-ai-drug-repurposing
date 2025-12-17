'use client'

import { useQuery } from '@tanstack/react-query'
import { queryAPI, type Query } from '@/lib/api'
import { FileText, Clock, CheckCircle, XCircle, Loader2 } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import Link from 'next/link'

export function QueryList() {
  const { data: queries, isLoading, error } = useQuery({
    queryKey: ['queries'],
    queryFn: () => queryAPI.list({ limit: 50 }),
    refetchInterval: 5000, // Refetch every 5 seconds
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-danger-600">Failed to load queries</p>
      </div>
    )
  }

  if (!queries || queries.length === 0) {
    return (
      <div className="text-center py-12 bg-white rounded-lg shadow">
        <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          No queries yet
        </h3>
        <p className="text-gray-500">
          Start a new analysis to see your queries here
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {queries.map((query) => (
        <QueryCard key={query.id} query={query} />
      ))}
    </div>
  )
}

function QueryCard({ query }: { query: Query }) {
  const getStatusIcon = (status: Query['status']) => {
    switch (status) {
      case 'pending':
        return <Clock className="h-5 w-5 text-gray-500" />
      case 'processing':
        return <Loader2 className="h-5 w-5 text-primary-600 animate-spin" />
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-success-600" />
      case 'failed':
        return <XCircle className="h-5 w-5 text-danger-600" />
    }
  }

  const getStatusColor = (status: Query['status']) => {
    switch (status) {
      case 'pending':
        return 'bg-gray-100 text-gray-700'
      case 'processing':
        return 'bg-primary-100 text-primary-700'
      case 'completed':
        return 'bg-success-100 text-success-700'
      case 'failed':
        return 'bg-danger-100 text-danger-700'
    }
  }

  return (
    <Link href={`/query/${query.id}`}>
      <div className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6 border border-gray-200 cursor-pointer">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-2">
              {getStatusIcon(query.status)}
              <span
                className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(
                  query.status
                )}`}
              >
                {query.status.toUpperCase()}
              </span>
              {query.user_id && (
                <span className="text-xs text-gray-500">
                  User: {query.user_id}
                </span>
              )}
            </div>
            <p className="text-gray-900 font-medium mb-2 line-clamp-2">
              {query.query_text}
            </p>
            <div className="flex items-center space-x-4 text-sm text-gray-500">
              <span>ID: {query.id}</span>
              <span>
                Created {formatDistanceToNow(new Date(query.created_at))} ago
              </span>
            </div>
          </div>
          <div className="ml-4">
            <div className="text-right text-sm text-gray-500">
              Last updated
              <br />
              {formatDistanceToNow(new Date(query.updated_at))} ago
            </div>
          </div>
        </div>
      </div>
    </Link>
  )
}
