'use client'

import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { queryAPI } from '@/lib/api'
import { Send, Sparkles, AlertCircle } from 'lucide-react'
import { useRouter } from 'next/navigation'

const EXAMPLE_QUERIES = [
  'Find drug repurposing opportunities for Alzheimer\'s disease',
  'Analyze potential of metformin for type 2 diabetes treatment',
  'What drugs could be repurposed for COVID-19 treatment?',
  'Explore aspirin repurposing for cardiovascular disease prevention',
]

export function QueryForm() {
  const [queryText, setQueryText] = useState('')
  const [userId, setUserId] = useState('demo_user')
  const router = useRouter()
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: (data: { query_text: string; user_id: string }) =>
      queryAPI.create(data.query_text, data.user_id),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['queries'] })
      // Navigate to query details page
      router.push(`/query/${data.id}`)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (queryText.trim().length < 10) {
      return
    }
    mutation.mutate({ query_text: queryText, user_id: userId })
  }

  const handleExampleClick = (example: string) => {
    setQueryText(example)
  }

  return (
    <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
      <div className="flex items-center space-x-3 mb-6">
        <div className="bg-gradient-to-br from-primary-500 to-purple-600 p-2 rounded-lg">
          <Sparkles className="h-6 w-6 text-white" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            Start New Analysis
          </h2>
          <p className="text-sm text-gray-500">
            Describe your drug repurposing research question
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* User ID Input */}
        <div>
          <label
            htmlFor="userId"
            className="block text-sm font-medium text-gray-900 mb-2"
          >
            User ID (optional)
          </label>
          <input
            type="text"
            id="userId"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all text-gray-900 bg-white"
            placeholder="Enter your user ID"
          />
        </div>

        {/* Query Text Area */}
        <div>
          <label
            htmlFor="queryText"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Research Question *
          </label>
          <textarea
            id="queryText"
            value={queryText}
            onChange={(e) => setQueryText(e.target.value)}
            rows={4}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all resize-none text-gray-900 bg-white"
            placeholder="e.g., Find drug repurposing opportunities for Alzheimer's disease..."
            required
            minLength={10}
          />
          <p className="mt-2 text-sm text-gray-500">
            {queryText.length}/2000 characters (minimum 10)
          </p>
        </div>

        {/* Example Queries */}
        <div>
          <p className="text-sm font-medium text-gray-700 mb-3">
            Example queries:
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {EXAMPLE_QUERIES.map((example, index) => (
              <button
                key={index}
                type="button"
                onClick={() => handleExampleClick(example)}
                className="text-left text-sm p-3 bg-gray-50 hover:bg-primary-50 rounded-lg transition-colors border border-gray-200 hover:border-primary-300 text-gray-900"
              >
                {example}
              </button>
            ))}
          </div>
        </div>

        {/* Error Message */}
        {mutation.isError && (
          <div className="flex items-start space-x-2 p-4 bg-danger-50 rounded-lg border border-danger-200">
            <AlertCircle className="h-5 w-5 text-danger-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-danger-800">
                Failed to submit query
              </p>
              <p className="text-sm text-danger-600 mt-1">
                {mutation.error instanceof Error
                  ? mutation.error.message
                  : 'Please try again or check your connection'}
              </p>
            </div>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={mutation.isPending || queryText.trim().length < 10}
          className="w-full bg-gradient-to-r from-primary-600 to-purple-600 text-white py-4 px-6 rounded-lg font-semibold hover:from-primary-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center space-x-2 shadow-lg hover:shadow-xl"
        >
          {mutation.isPending ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent" />
              <span>Submitting...</span>
            </>
          ) : (
            <>
              <Send className="h-5 w-5" />
              <span>Start Analysis</span>
            </>
          )}
        </button>
      </form>

      {/* Info Box */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <p className="text-sm text-blue-800">
          <strong>How it works:</strong> Our AI agents will analyze clinical
          trials, patent landscapes, market intelligence, and scientific
          literature to identify drug repurposing opportunities. Analysis
          typically takes 30-60 seconds.
        </p>
      </div>
    </div>
  )
}
