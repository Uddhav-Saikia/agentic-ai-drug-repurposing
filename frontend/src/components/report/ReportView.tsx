'use client'

import { Report, DrugCandidate } from '@/lib/api'
import { FileText, TrendingUp, AlertTriangle, Lightbulb, ArrowRight, Pill } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts'

interface ReportViewProps {
  report: Report
  drugCandidates: DrugCandidate[]
}

export function ReportView({ report, drugCandidates }: ReportViewProps) {
  // Prepare data for confidence chart
  const confidenceData = [
    {
      name: 'Clinical',
      score: report.sections?.clinical?.evidence_score || 0,
    },
    {
      name: 'Patent',
      score: 10 - (report.sections?.patent?.risk_score || 10), // Invert risk to score
    },
    {
      name: 'Market',
      score: report.sections?.market?.attractiveness_score || 0,
    },
    {
      name: 'Research',
      score: report.sections?.web?.momentum_score || 0,
    },
  ]

  // Radar chart data
  const radarData = confidenceData

  return (
    <div className="space-y-6">
      {/* Report Header */}
      <div className="bg-gradient-to-r from-primary-600 to-purple-600 rounded-lg shadow-lg p-8 text-white">
        <div className="flex items-center space-x-3 mb-4">
          <FileText className="h-8 w-8" />
          <h1 className="text-3xl font-bold">{report.title}</h1>
        </div>
        {report.overall_confidence !== undefined && (
          <div className="flex items-center space-x-4 mt-4">
            <div className="bg-white/20 rounded-lg px-6 py-3">
              <p className="text-sm opacity-90">Overall Confidence</p>
              <p className="text-3xl font-bold">{report.overall_confidence.toFixed(1)}/10</p>
            </div>
            {report.condition && (
              <div className="bg-white/20 rounded-lg px-6 py-3">
                <p className="text-sm opacity-90">Condition</p>
                <p className="text-xl font-semibold">{report.condition}</p>
              </div>
            )}
            {report.drug_name && (
              <div className="bg-white/20 rounded-lg px-6 py-3">
                <p className="text-sm opacity-90">Drug</p>
                <p className="text-xl font-semibold">{report.drug_name}</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Executive Summary */}
      {report.executive_summary && (
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
            <FileText className="h-6 w-6 text-primary-600" />
            <span>Executive Summary</span>
          </h2>
          <p className="text-gray-700 leading-relaxed whitespace-pre-line">
            {report.executive_summary}
          </p>
        </div>
      )}

      {/* Drug Candidates */}
      {drugCandidates && drugCandidates.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
            <Pill className="h-6 w-6 text-primary-600" />
            <span>Drug Candidates ({drugCandidates.length})</span>
          </h2>
          <div className="space-y-4">
            {drugCandidates.map((candidate) => (
              <div
                key={candidate.id}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {candidate.drug_name}
                  </h3>
                  <div className="bg-primary-100 text-primary-700 px-3 py-1 rounded-full text-sm font-semibold">
                    {candidate.confidence_score.toFixed(1)}/10
                  </div>
                </div>
                <p className="text-gray-600 mb-3">{candidate.indication}</p>
                {candidate.clinical_data && (
                  <div className="text-sm text-gray-700">
                    <strong>Clinical:</strong> {JSON.stringify(candidate.clinical_data).slice(0, 100)}...
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Confidence Scores Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
            <TrendingUp className="h-6 w-6 text-primary-600" />
            <span>Confidence Scores</span>
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={confidenceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis domain={[0, 10]} />
              <Tooltip />
              <Bar dataKey="score" fill="#0ea5e9" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
            <TrendingUp className="h-6 w-6 text-primary-600" />
            <span>Multi-Dimensional Analysis</span>
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={radarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="name" />
              <PolarRadiusAxis domain={[0, 10]} />
              <Radar name="Score" dataKey="score" stroke="#0ea5e9" fill="#0ea5e9" fillOpacity={0.6} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Key Findings */}
      {report.key_findings && report.key_findings.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
            <Lightbulb className="h-6 w-6 text-primary-600" />
            <span>Key Findings</span>
          </h2>
          <ul className="space-y-3">
            {report.key_findings.map((finding, index) => (
              <li key={index} className="flex items-start space-x-3">
                <ArrowRight className="h-5 w-5 text-primary-600 flex-shrink-0 mt-0.5" />
                <span className="text-gray-700">{finding}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Risk Assessment */}
      {report.risk_assessment && Object.keys(report.risk_assessment).length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
            <AlertTriangle className="h-6 w-6 text-warning-600" />
            <span>Risk Assessment</span>
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(report.risk_assessment).map(([key, value]) => (
              <div key={key} className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600 capitalize mb-1">{key.replace(/_/g, ' ')}</p>
                <p className="text-lg font-semibold text-gray-900">{value as string}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {report.recommendations && Object.keys(report.recommendations).length > 0 && (
        <div className="bg-success-50 rounded-lg shadow-md p-6 border-2 border-success-200">
          <h2 className="text-xl font-bold text-success-900 mb-4">Recommendations</h2>
          <div className="space-y-3">
            {Object.entries(report.recommendations).map(([key, value]) => (
              <div key={key}>
                <p className="text-sm font-semibold text-success-800 capitalize mb-1">
                  {key.replace(/_/g, ' ')}
                </p>
                <p className="text-success-700">{value as string}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Next Steps */}
      {report.next_steps && report.next_steps.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Next Steps</h2>
          <ol className="space-y-2">
            {report.next_steps.map((step, index) => (
              <li key={index} className="flex items-start space-x-3">
                <span className="flex-shrink-0 w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-semibold">
                  {index + 1}
                </span>
                <span className="text-gray-700">{step}</span>
              </li>
            ))}
          </ol>
        </div>
      )}

      {/* Data Sources */}
      {report.data_sources && report.data_sources.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">Data Sources</h3>
          <p className="text-sm text-gray-600">{report.data_sources.join(', ')}</p>
        </div>
      )}
    </div>
  )
}
