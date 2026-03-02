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

// Registering chart components to avoid "canvas" errors
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

function App() {
  // State for the uploaded file and the API response data
  const [selectedFile, setSelectedFile] = useState(null);
  const [analysisReport, setAnalysisReport] = useState(null); // Renamed from 'stats' for clarity
  const [visualizationData, setVisualizationData] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleFileSelection = (e) => {
    setSelectedFile(e.target.files[0]);
    setErrorMessage(''); // Clear errors when user picks a new file
  };

  const handleAnalysis = async () => {
    if (!selectedFile) {
      setErrorMessage('Please select a CSV file first.');
      return;
    }
    
    setIsLoading(true);

    // CRITICAL: We must use FormData here.
    // Standard JSON ({ file: ... }) does not work for binary file uploads.
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      // Hardcoded credentials for the screening task. 
      // TODO: In production, move these to a .env file or use JWT tokens.
      const authHeaders = {
        username: 'admin',
        password: 'admin123'
      };

      // Sending POST request to Django Backend
      const response = await axios.post('http://127.0.0.1:8000/api/upload/', formData, {
        auth: authHeaders
      });

      // Update UI with the data calculated by Pandas on the backend
      setAnalysisReport(response.data.stats);
      
      setVisualizationData({
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
      setErrorMessage('Upload Failed. Check backend connection or credentials.');
    } finally {
      setIsLoading(false);
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
      </header>

      {/* Upload Section */}
      <div className="upload-card">
        <h2>Data Analysis Panel</h2>
        <p style={{marginBottom: '20px', color: '#666'}}>Upload your equipment CSV file to generate insights.</p>
        
        <div className="file-input-wrapper">
          <input type="file" onChange={handleFileSelection} accept=".csv" />
        </div>
        
        <button className="btn-primary" onClick={handleAnalysis} disabled={isLoading}>
          {isLoading ? 'Processing...' : 'Analyze CSV Data'}
        </button>

        {errorMessage && <div className="error-msg">{errorMessage}</div>}
      </div>

      {/* Results Dashboard (Only shows if analysisReport exists) */}
      {analysisReport && (
        <div className="results-section">
          
          {/* Key Metrics Cards */}
          <div className="stats-grid">
            <div className="stat-card" style={{borderLeftColor: '#2ecc71'}}>
              <h3>Total Equipment</h3>
              <p className="stat-value">{analysisReport.total_count}</p>
            </div>
            <div className="stat-card" style={{borderLeftColor: '#3498db'}}>
              <h3>Avg Flowrate</h3>
              <p className="stat-value">{analysisReport.avg_flowrate}</p>
            </div>
            <div className="stat-card" style={{borderLeftColor: '#e74c3c'}}>
              <h3>Avg Pressure</h3>
              <p className="stat-value">{analysisReport.avg_pressure}</p>
            </div>
            <div className="stat-card" style={{borderLeftColor: '#f1c40f'}}>
              <h3>Avg Temperature</h3>
              <p className="stat-value">{analysisReport.avg_temperature}</p>
            </div>
          </div>

          {/* Main Chart */}
          <div className="chart-container">
            <Bar 
              data={visualizationData} 
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