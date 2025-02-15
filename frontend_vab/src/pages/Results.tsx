import { useLocation, useNavigate } from 'react-router-dom'

function Results() {
  const location = useLocation()
  const navigate = useNavigate()
  const { analysis } = location.state || {}

  if (!analysis) {
    return <div>No analysis available</div>
  }

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="glass-panel p-8">
          <h1 className="text-3xl font-bold mb-6 bg-gradient-to-r from-primary-400 to-primary-300 text-transparent bg-clip-text">
            Speech Analysis
          </h1>
          
          <div className="grid grid-cols-3 gap-6 mb-8">
            <div className="glass-panel p-4 text-center">
              <p className="text-gray-400 mb-2">Duration</p>
              <p className="text-2xl font-bold text-primary-400">
                {analysis.speech_details.duration} min
              </p>
            </div>
            <div className="glass-panel p-4 text-center">
              <p className="text-gray-400 mb-2">Words/Minute</p>
              <p className="text-2xl font-bold text-primary-400">
                {analysis.speech_details.words_per_minute}
              </p>
            </div>
            <div className="glass-panel p-4 text-center">
              <p className="text-gray-400 mb-2">Clarity</p>
              <p className="text-2xl font-bold text-primary-400">
                {analysis.speech_details.clarity_score * 100}%
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="glass-panel p-6">
              <h2 className="text-xl font-semibold mb-4 text-gray-300">Strengths</h2>
              <ul className="space-y-3">
                {analysis.evaluation.strengths.map((strength: string, index: number) => (
                  <li key={index} className="flex items-start">
                    <span className="text-primary-400 mr-2">✓</span>
                    <span className="text-gray-400">{strength}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="glass-panel p-6">
              <h2 className="text-xl font-semibold mb-4 text-gray-300">Areas for Improvement</h2>
              <ul className="space-y-3">
                {analysis.evaluation.improvements.map((improvement: string, index: number) => (
                  <li key={index} className="flex items-start">
                    <span className="text-primary-400 mr-2">•</span>
                    <span className="text-gray-400">{improvement}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="glass-panel p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4 text-gray-300">Recommendations</h2>
            <ul className="space-y-3">
              {analysis.evaluation.recommendations.map((rec: string, index: number) => (
                <li key={index} className="flex items-start">
                  <span className="text-primary-400 mr-2">→</span>
                  <span className="text-gray-400">{rec}</span>
                </li>
              ))}
            </ul>
          </div>

          <button
            onClick={() => navigate('/')}
            className="btn-primary"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  )
}

export default Results 