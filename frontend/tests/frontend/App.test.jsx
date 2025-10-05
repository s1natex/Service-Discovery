import { render, screen } from '@testing-library/react'
import React from 'react'
vi.mock('axios', () => ({
  default: { get: vi.fn() }
}))
import axios from 'axios'

async function loadApp() {
  const mod = await import('../../src/App.jsx')
  return mod.default
}

afterEach(() => {
  vi.clearAllMocks()
})

test('renders services and health list when API calls succeed', async () => {
  axios.get.mockImplementation((url) => {
    if (url === '/api/services') {
      return Promise.resolve({
        data: [{
          service: 'service-a',
          status: 'online',
          timestamp: '2024-01-01 00:00:00.000',
          host: 'h1',
          responseTime: 123
        }]
      })
    }
    if (url === '/api/healthz') {
      return Promise.resolve({ data: [{ name: 'service-a', status: 'healthy' }] })
    }
    throw new Error(`Unexpected URL: ${url}`)
  })

  const App = await loadApp()
  render(<App />)

  expect(await screen.findByText(/Service Discovery Demo/i)).toBeInTheDocument()
  expect(await screen.findByRole('heading', { level: 2, name: /service-a/i })).toBeInTheDocument()
  expect(await screen.findByText('ONLINE')).toBeInTheDocument()
  expect(await screen.findByText(/123 ms/)).toBeInTheDocument()
  expect(await screen.findByText('service-a: healthy')).toBeInTheDocument()
})

test('shows empty lists when APIs fail', async () => {
  axios.get.mockImplementation((url) => {
    if (url === '/api/services') return Promise.reject(new Error('down'))
    if (url === '/api/healthz') return Promise.reject(new Error('down'))
    throw new Error(`Unexpected URL: ${url}`)
  })

  const App = await loadApp()
  render(<App />)

  expect(await screen.findByText(/Service Discovery Demo/i)).toBeInTheDocument()
  expect(screen.queryByText(/Timestamp:/i)).not.toBeInTheDocument()
  expect(screen.queryAllByRole('listitem').length).toBe(0)
  expect(axios.get).toHaveBeenCalled()
})
