import api from './api'

export interface LoginCredentials {
  email: string
  password: string
}

export interface AuthResponse {
  token: string
  user: {
    id: string
    email: string
    name: string
  }
}

export const authService = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response = await api.post('/auth/login', credentials)
    return response.data
  },

  logout: () => {
    localStorage.removeItem('authToken')
    window.location.href = '/login'
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me')
    return response.data
  },
}
