'use client'

import { useQuery } from '@tanstack/react-query'
import { useParams, useRouter } from 'next/navigation'
import { queryAPI, reportAPI } from '@/lib/api'
import { ArrowLeft, Loader2 } from 'lucide-react'
import Link from 'next/link'
import { ProgressTracker } from '@/components/query/ProgressTracker'
import { ReportView } from '@/components/report/ReportView'

export default function QueryDetailPage() {
  const params = useParams()
  const router = useRouter()
  const queryId = parseInt(params.id as string)

  // Fetch query status with real-time updates
  const {
    data: queryStatus,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['queryStatus', queryId],
    queryFn: () => queryAPI.getStatus(queryId),
    refetchInterval: (query) => {
      // Stop polling if completed or failed
      const status = query?.state?.data?.status
      if (status === 'completed' || status === 'failed') {
        return false
      }
      return 2000 // Poll every 2 seconds while processing
    },
  })

  // Fetch full result when completed
  const { data: analysisResult } = useQuery({
    queryKey: ['analysisResult', queryId],
    queryFn: () => queryAPI.getResult(queryId),
    enabled: queryStatus?.status === 'completed',
  })

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
        <Loader2 className="h-12 w-12 animate-spin text-primary-600" />
      </div>
    )
  }

  if (error || !queryStatus) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-danger-600 mb-4">Failed to load query</p>
          <Link
            href="/"
            className="text-primary-600 hover:text-primary-700 underline"
          >
            Back to home
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Back Button */}
        <Link
          href="/"
          className="inline-flex items-center space-x-2 text-primary-600 hover:text-primary-700 mb-6"
        >
          <ArrowLeft className="h-5 w-5" />
          <span>Back to Dashboard</span>
        </Link>

        {/* Query Info */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6 border border-gray-200">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Query #{queryId}
          </h1>
          <p className="text-gray-700 mb-4">{queryStatus.message}</p>
        </div>

        {/* Progress Tracker */}
        <ProgressTracker queryStatus={queryStatus} />

        {/* Report View (only when completed) */}
        {queryStatus.status === 'completed' && analysisResult?.report && (
          <div className="mt-6">
            <ReportView
              report={analysisResult.report}
              drugCandidates={analysisResult.drug_candidates}
            />
          </div>
        )}

        {/* Failed State */}
        {queryStatus.status === 'failed' && (
          <div className="mt-6 bg-danger-50 border-2 border-danger-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-danger-900 mb-2">
              Analysis Failed
            </h3>
            <p className="text-danger-700">
              The analysis encountered an error. Please try submitting a new
              query.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
