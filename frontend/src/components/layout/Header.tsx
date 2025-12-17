import { Brain, Activity } from 'lucide-react'

export function Header() {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-gradient-to-br from-primary-500 to-purple-600 p-3 rounded-lg">
              <Brain className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Drug Repurposing AI
              </h1>
              <p className="text-sm text-gray-500">
                Agentic Intelligence Platform
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2 px-4 py-2 bg-success-50 rounded-lg">
            <Activity className="h-5 w-5 text-success-600 animate-pulse" />
            <span className="text-sm font-medium text-success-700">
              System Online
            </span>
          </div>
        </div>
      </div>
    </header>
  )
}
