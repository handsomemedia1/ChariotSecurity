import api from './api'

export interface ThreatAlert {
  id: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  type: string
  message: string
  timestamp: string
}

export interface TransactionAnalysis {
  transactionHash: string
  riskScore: number
  threats: string[]
  recommendation: string
}

export const securityService = {
  // Get recent threats
  getThreats: async (): Promise<ThreatAlert[]> => {
    const response = await api.get('/security/threats')
    return response.data
  },

  // Analyze transaction
  analyzeTransaction: async (transactionHash: string): Promise<TransactionAnalysis> => {
    const response = await api.post('/security/analyze', { transactionHash })
    return response.data
  },

  // Get security dashboard stats
  getDashboardStats: async () => {
    const response = await api.get('/security/stats')
    return response.data
  },
}
