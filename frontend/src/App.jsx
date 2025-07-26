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
    <div style={{ textAlign: 'center' }}>
      <h1>Service Discovery Demo</h1>
      <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', marginTop: '2rem' }}>
        {services.map((svc, idx) => (
          <div key={idx} style={{ border: '1px solid #ccc', padding: '1rem', width: '200px' }}>
            <h3>{svc.service}</h3>
            <p>{svc.timestamp}</p>
            <small>{svc.host}</small>
          </div>
        ))}
      </div>
    </div>
  )
}

export default App
