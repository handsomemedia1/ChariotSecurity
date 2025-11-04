import React, { useEffect, useState } from 'react'
import { securityService, ThreatAlert } from '../services/securityService'
import websocket from '../services/websocket'

const Dashboard: React.FC = () => {
  const [threats, setThreats] = useState<ThreatAlert[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadThreats()
    
    // Connect to WebSocket for real-time updates
    const userId = localStorage.getItem('userId')
    if (userId) {
      websocket.connect(userId)
      
      websocket.on('security_alert', (alert: ThreatAlert) => {
        setThreats(prev => [alert, ...prev])
      })
    }

    return () => {
      websocket.disconnect()
    }
  }, [])

  const loadThreats = async () => {
    try {
      const data = await securityService.getThreats()
      setThreats(data)
    } catch (error) {
      console.error('Failed to load threats:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">
            Security Dashboard
          </h1>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-500">Active Threats</div>
              <div className="text-2xl font-bold text-red-600">12</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-500">Blocked Today</div>
              <div className="text-2xl font-bold text-green-600">48</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-500">Risk Score</div>
              <div className="text-2xl font-bold text-yellow-600">0.34</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-500">Transactions</div>
              <div className="text-2xl font-bold text-blue-600">1,243</div>
            </div>
          </div>

          {/* Threats List */}
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold">Recent Threats</h2>
            </div>
            <div className="divide-y divide-gray-200">
              {loading ? (
                <div className="p-6 text-center text-gray-500">Loading...</div>
              ) : threats.length === 0 ? (
                <div className="p-6 text-center text-gray-500">No threats detected</div>
              ) : (
                threats.map(threat => (
                  <div key={threat.id} className="p-6 hover:bg-gray-50">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className={\px-2 py-1 text-xs rounded \\}>
                            {threat.severity.toUpperCase()}
                          </span>
                          <span className="font-medium">{threat.type}</span>
                        </div>
                        <p className="text-sm text-gray-600 mt-1">{threat.message}</p>
                      </div>
                      <div className="text-sm text-gray-500">
                        {new Date(threat.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
