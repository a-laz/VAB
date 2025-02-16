import { useState, useEffect } from 'react'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

function Dashboard() {
  const [metrics, setMetrics] = useState<any>(null)

  useEffect(() => {
    fetch('/api/metrics')
      .then(res => res.json())
      .then(data => setMetrics(data))
  }, [])

  const fillerWordsData = {
    labels: metrics?.filler_words.map((d: any) => d.date),
    datasets: [{
      label: 'Filler Words',
      data: metrics?.filler_words.map((d: any) => d.count),
      borderColor: 'rgb(75, 192, 192)',
      tension: 0.1
    }]
  }

  const paceData = {
    labels: metrics?.pace.map((d: any) => d.date),
    datasets: [{
      label: 'Words per Minute',
      data: metrics?.pace.map((d: any) => d.value),
      borderColor: 'rgb(153, 102, 255)',
      tension: 0.1
    }]
  }

  const chartOptions = {
    responsive: true,
    scales: {
      x: {
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
        ticks: {
          color: '#9CA3AF',
        },
      },
      y: {
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
        ticks: {
          color: '#9CA3AF',
        },
      },
    },
    plugins: {
      legend: {
        labels: {
          color: '#9CA3AF',
        },
      },
    },
  }

  return (
    <div className="min-h-screen p-6 space-y-6">
      <div className="glass-panel p-8 max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-primary-400 to-primary-300 text-transparent bg-clip-text">
            Speaking Progress
          </h1>
          <button 
            onClick={() => window.location.href = '/speech'}
            className="btn-primary"
          >
            New Speech
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="chart-container">
            <h2 className="text-xl font-semibold mb-4 text-gray-300">Filler Words Trend</h2>
            {metrics && <Line data={fillerWordsData} options={chartOptions} />}
          </div>
          <div className="chart-container">
            <h2 className="text-xl font-semibold mb-4 text-gray-300">Speaking Pace Trend</h2>
            {metrics && <Line data={paceData} options={chartOptions} />}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard 