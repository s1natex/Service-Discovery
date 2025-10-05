import { useEffect, useState } from 'react'
import axios from 'axios'

function App() {
  const [services, setServices] = useState([])
  const [healthList, setHealthList] = useState([])
  const [now, setNow] = useState(Date.now())

  useEffect(() => {
    const fetchServices = async () => {
      try {
        const res = await axios.get('/api/services', { timeout: 1500 })
        const fetchedAt = Date.now()
        const normalized = res.data.map(item => {
          const baseTime = item.timestamp && item.timestamp !== 'N/A'
            ? new Date(item.timestamp).getTime()
            : null
          return { ...item, baseTimestamp: baseTime, fetchedAt }
        })
        setServices(normalized)
      } catch {}
    }

    const fetchHealthz = async () => {
      try {
        const res = await axios.get('/api/healthz', { timeout: 1500 })
        setHealthList(Array.isArray(res.data) ? res.data : [])
      } catch {
        setHealthList([])
      }
    }

    fetchServices()
    fetchHealthz()
    const fetchInterval = setInterval(() => { fetchServices(); fetchHealthz(); }, 3000)
    const clockInterval = setInterval(() => setNow(Date.now()), 100)

    return () => { clearInterval(fetchInterval); clearInterval(clockInterval) }
  }, [])

  const formatTimestamp = (base, fetched) => {
    if (!base || !fetched) return 'N/A'
    const offset = now - fetched
    const displayTime = new Date(base + offset)
    return displayTime.toISOString().replace('T', ' ').slice(0, -1)
  }

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Service Discovery Demo</h1>
      <h2>Testing-sync-4</h2>
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
                {(svc.status || 'unknown').toUpperCase()}
              </span>
            </div>
            <p><strong>Timestamp:</strong><br />{formatTimestamp(svc.baseTimestamp, svc.fetchedAt)}</p>
            <p><strong>Response Time:</strong> {svc.responseTime != null ? `${svc.responseTime} ms` : 'N/A'}</p>
            <p style={styles.host}>🖥️ {svc.host || 'N/A'}</p>
          </div>
        ))}
      </div>

      <div style={styles.healthz}>
        <h3 style={{ marginBottom: '0.5rem' }}>Cluster Health</h3>
        <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
          {healthList.map((h, i) => (
            <li key={i} style={{ margin: '0.25rem 0', color: h.status === 'healthy' ? '#28a745' : '#dc3545' }}>
              {`${h.name}: ${h.status}`}
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

const styles = {
  container: { textAlign: 'center', padding: '2rem' },
  title: { fontSize: '2.5rem', fontWeight: 600, marginBottom: '2rem', color: '#333' },
  grid: { display: 'flex', justifyContent: 'center', gap: '2rem', flexWrap: 'wrap' },
  card: { backgroundColor: '#fff', padding: '1.5rem', borderRadius: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.08)', width: '260px', textAlign: 'left' },
  cardHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  badge: { padding: '0.25rem 0.5rem', borderRadius: '6px', color: 'white', fontSize: '0.75rem', fontWeight: 'bold' },
  host: { marginTop: '1rem', color: '#777', fontSize: '0.9rem' },
  healthz: { marginTop: '2rem', paddingTop: '1rem', borderTop: '1px solid #e5e7eb', maxWidth: 640, marginLeft: 'auto', marginRight: 'auto', textAlign: 'left' },
}

export default App
