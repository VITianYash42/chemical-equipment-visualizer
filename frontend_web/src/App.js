import React, { useState } from 'react';
import axios from 'axios';
import './App.css'; 
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

function App() {
  const [file, setFile] = useState(null);
  const [stats, setStats] = useState(null);
  const [chartData, setChartData] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError('');
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a CSV file first.');
      return;
    }
    
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      // 🔒 AUTHENTICATION (The Admin Password)
      const auth = {
        username: 'admin',
        password: 'admin123'
      };

      const response = await axios.post('http://127.0.0.1:8000/api/upload/', formData, {
        auth: auth
      });

      setStats(response.data.stats);
      setChartData({
        labels: response.data.chart_data.equipment_names,
        datasets: [
          {
            label: 'Flowrate (m³/h)',
            data: response.data.chart_data.flowrate,
            backgroundColor: '#3498db',
            borderRadius: 4,
          },
          {
            label: 'Pressure (bar)',
            data: response.data.chart_data.pressure,
            backgroundColor: '#e74c3c',
            borderRadius: 4,
          },
        ],
      });
    } catch (err) {
      console.error(err);
      setError('Upload Failed. Check your connection or admin password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard-container">
      {/* Header */}
      <header className="header">
        <h1>
          <span className="logo-emoji">⚗️</span> 
          Chemical Equipment Visualizer
        </h1>
        <div style={{color: "#7f8c8d"}}>FOSSEE 2026 Submission</div>
      </header>

      {/* Upload Section */}
      <div className="upload-card">
        <h2>Data Analysis Panel</h2>
        <p style={{marginBottom: '20px', color: '#666'}}>Upload your equipment CSV file to generate insights.</p>
        
        <div className="file-input-wrapper">
          <input type="file" onChange={handleFileChange} accept=".csv" />
        </div>
        
        <button className="btn-primary" onClick={handleUpload} disabled={loading}>
          {loading ? 'Analyzing...' : 'Analyze CSV Data'}
        </button>

        {error && <div className="error-msg">{error}</div>}
      </div>

      {/* Results Dashboard */}
      {stats && (
        <div className="results-section">
          
          {/* Key Metrics Cards */}
          <div className="stats-grid">
            <div className="stat-card" style={{borderLeftColor: '#2ecc71'}}>
              <h3>Total Equipment</h3>
              <p className="stat-value">{stats.total_count}</p>
            </div>
            <div className="stat-card" style={{borderLeftColor: '#3498db'}}>
              <h3>Avg Flowrate</h3>
              <p className="stat-value">{stats.avg_flowrate}</p>
            </div>
            <div className="stat-card" style={{borderLeftColor: '#e74c3c'}}>
              <h3>Avg Pressure</h3>
              <p className="stat-value">{stats.avg_pressure}</p>
            </div>
            <div className="stat-card" style={{borderLeftColor: '#f1c40f'}}>
              <h3>Avg Temperature</h3>
              <p className="stat-value">{stats.avg_temperature}</p>
            </div>
          </div>

          {/* Main Chart */}
          <div className="chart-container">
            <Bar 
              data={chartData} 
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: { position: 'top' },
                  title: { display: true, text: 'Equipment Performance Overview' },
                },
              }} 
            />
          </div>
        </div>
      )}

      {/* FOOTER */}
      <footer style={{ marginTop: '60px', textAlign: 'center', borderTop: '1px solid #e0e0e0', padding: '20px', color: '#95a5a6', fontSize: '12px' }}>
        <p>Copyright © 2026 Yash Singhal | yash.24bce10839@vitbhopal.ac.in</p>
      </footer>
    </div>
  );
}

export default App;