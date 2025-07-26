import { useEffect, useState } from 'react'
import axios from 'axios'

function App() {
  const [services, setServices] = useState([])
  const [now, setNow] = useState(Date.now())

  useEffect(() => {
    const fetchServices = async () => {
      const serviceNames = ['service-a', 'service-b', 'service-c']
      const updated = []

      for (const name of serviceNames) {
        const start = performance.now()
        try {
          const res = await axios.get(`/api/service/${name}`)
          const end = performance.now()

          const baseTime = new Date(res.data.timestamp).getTime()

          updated.push({
            ...res.data,
            baseTimestamp: baseTime,
            fetchedAt: Date.now(),
            status: 'online',
            responseTime: Math.round(end - start)
          })
        } catch (err) {
          updated.push({
            service: name,
            timestamp: 'N/A',
            host: 'N/A',
            baseTimestamp: null,
            fetchedAt: null,
            status: 'offline',
            responseTime: null
          })
        }
      }

      setServices(updated)
    }

    fetchServices()
    const fetchInterval = setInterval(fetchServices, 3000)
    const clockInterval = setInterval(() => setNow(Date.now()), 100)

    return () => {
      clearInterval(fetchInterval)
      clearInterval(clockInterval)
    }
  }, [])

  const formatTimestamp = (base, fetched) => {
    if (!base || !fetched) return 'N/A'
    const offset = now - fetched
    const displayTime = new Date(base + offset)
    return displayTime.toISOString().replace('T', ' ').slice(0, -1) // trim trailing "Z"
  }

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Service Discovery Demo</h1>
      <div style={styles.grid}>
        {services.map((svc, idx) => (
          <div key={idx} style={styles.card}>
            <div style={styles.cardHeader}>
              <h2>{svc.service}</h2>
              <span
                style={{
                  ...styles.badge,
                  backgroundColor: svc.status === 'online' ? '#28a745' : '#dc3545'
                }}
              >
                {svc.status.toUpperCase()}
              </span>
            </div>
            <p><strong>Timestamp:</strong><br />{formatTimestamp(svc.baseTimestamp, svc.fetchedAt)}</p>
            <p><strong>Response Time:</strong> {svc.responseTime !== null ? `${svc.responseTime} ms` : 'N/A'}</p>
            <p style={styles.host}>🖥️ {svc.host}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

const styles = {
  container: {
    textAlign: 'center',
    padding: '2rem',
  },
  title: {
    fontSize: '2.5rem',
    fontWeight: '600',
    marginBottom: '2rem',
    color: '#333',
  },
  grid: {
    display: 'flex',
    justifyContent: 'center',
    gap: '2rem',
    flexWrap: 'wrap',
  },
  card: {
    backgroundColor: '#fff',
    padding: '1.5rem',
    borderRadius: '12px',
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)',
    width: '260px',
    textAlign: 'left',
    transition: 'transform 0.2s ease',
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  badge: {
    padding: '0.25rem 0.5rem',
    borderRadius: '6px',
    color: 'white',
    fontSize: '0.75rem',
    fontWeight: 'bold',
  },
  host: {
    marginTop: '1rem',
    color: '#777',
    fontSize: '0.9rem',
  },
}

export default App
