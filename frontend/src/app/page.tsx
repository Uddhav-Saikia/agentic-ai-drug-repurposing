'use client'

import { useState } from 'react'
import { Header } from '@/components/layout/Header'
import { QueryForm } from '@/components/query/QueryForm'
import { QueryList } from '@/components/query/QueryList'
import { SystemStatus } from '@/components/dashboard/SystemStatus'

export default function Home() {
  const [activeTab, setActiveTab] = useState<'new' | 'history' | 'status'>('new')

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <div className="flex space-x-4 mb-8 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('new')}
            className={`pb-4 px-4 font-semibold transition-colors ${
              activeTab === 'new'
                ? 'text-primary-600 border-b-2 border-primary-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            New Analysis
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`pb-4 px-4 font-semibold transition-colors ${
              activeTab === 'history'
                ? 'text-primary-600 border-b-2 border-primary-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Query History
          </button>
          <button
            onClick={() => setActiveTab('status')}
            className={`pb-4 px-4 font-semibold transition-colors ${
              activeTab === 'status'
                ? 'text-primary-600 border-b-2 border-primary-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            System Status
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'new' && (
          <div className="max-w-4xl mx-auto">
            <QueryForm />
          </div>
        )}
        
        {activeTab === 'history' && <QueryList />}
        
        {activeTab === 'status' && <SystemStatus />}
      </div>
    </main>
  )
}
