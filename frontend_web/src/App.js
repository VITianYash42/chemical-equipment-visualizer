import React, { useState } from 'react';
import axios from 'axios';
import './App.css';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

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
      // 🔒 AUTHENTICATION
      const auth = { username: 'admin', password: 'admin123' };

      const response = await axios.post('http://127.0.0.1:8000/api/upload/', formData, { auth: auth });

      setStats(response.data.stats);
      setChartData({
        labels: response.data.chart_data.equipment_names,
        datasets: [
          { label: 'Flowrate', data: response.data.chart_data.flowrate, backgroundColor: '#3498db' },
          { label: 'Pressure', data: response.data.chart_data.pressure, backgroundColor: '#e74c3c' },
        ],
      });
    } catch (err) {
      console.error(err);
      setError('Upload Failed. Check connection or login.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard-container">
      <header className="header">
        <h1>⚗️ Chemical Equipment Visualizer</h1>
      </header>

      <div className="upload-card">
        <h2>Data Analysis Panel</h2>
        <input type="file" onChange={handleFileChange} />
        <button className="btn-primary" onClick={handleUpload} disabled={loading}>
          {loading ? 'Analyzing...' : 'Analyze CSV'}
        </button>
        {error && <div className="error-msg">{error}</div>}
      </div>

      {stats && (
        <div className="results-section">
          <div className="stats-grid">
            <div className="stat-card"><h3>Total</h3><p>{stats.total_count}</p></div>
            <div className="stat-card"><h3>Avg Flow</h3><p>{stats.avg_flowrate}</p></div>
            <div className="stat-card"><h3>Avg Pressure</h3><p>{stats.avg_pressure}</p></div>
          </div>
          <div className="chart-container">
             <Bar data={chartData} options={{ responsive: true, maintainAspectRatio: false }} />
          </div>
        </div>
      )}

      {/* YOUR FOOTER */}
      <footer style={{ marginTop: '50px', textAlign: 'center', color: '#888', fontSize: '12px', borderTop: '1px solid #ddd', padding: '20px' }}>
        <p>Copyright © 2026 Yash Singhal | yash.24bce10839@vitbhopal.ac.in</p>
      </footer>
    </div>
  );
}

export default App;