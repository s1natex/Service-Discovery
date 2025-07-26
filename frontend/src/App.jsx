import { useEffect, useState } from 'react'
import axios from 'axios'

function App() {
  const [services, setServices] = useState([])

  useEffect(() => {
    const fetchServices = () => {
      axios.get('/api/services')
        .then(res => setServices(res.data))
        .catch(err => console.error(err))
    }

    fetchServices()
    const interval = setInterval(fetchServices, 3000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Service Discovery Demo</h1>
      <div style={styles.grid}>
        {services.map((svc, idx) => (
          <div key={idx} style={styles.card}>
            <h2>{svc.service}</h2>
            <p><strong>Timestamp:</strong><br />{svc.timestamp}</p>
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
    width: '220px',
    textAlign: 'left',
    transition: 'transform 0.2s ease',
  },
  host: {
    marginTop: '1rem',
    color: '#777',
    fontSize: '0.9rem',
  },
}

export default App
