import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import WeightForm from './components/WeightForm';
import WeightRecords from './components/WeightRecords';
import Dashboard from './components/Dashboard';
import weightService from './api/WeightService';
import './App.css';
import Unknown from './components/Unknown';
import BatchUpload from './components/BatchUpload';
import Session from './components/Session';
import DashboardLayout from './components/DashboardLayout';

function App() {
  const [isHealthy, setIsHealthy] = useState(true);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        await weightService.checkHealth();
        setIsHealthy(true);
      } catch (error) {
        setIsHealthy(false);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 60000); // Check every minute
    
    return () => clearInterval(interval);
  }, []);

  return (
    <Router>
      <div className="app-container">
        <header className="app-header">
          <div className="logo">
            <h1>Weight Management System</h1>
          </div>
          
          {!isHealthy && (
            <div className="health-alert">
              Backend service is currently unavailable
            </div>
          )}
          
          <nav className="main-nav">
            <ul>
              <li><Link to="/Dashboard">Dashboard</Link></li>
              <li><Link to="/Dashboard/weight/new">New Weight</Link></li>
              <li><Link to="/Dashboard/weights">Records</Link></li>
              <li><Link to="/Dashboard/unknown">Unknown Containers</Link></li>
              <li><Link to="/Dashboard/batch-upload">Batch Upload</Link></li>
            </ul>
          </nav>
        </header>
        
        <main className="app-content">
        <Routes>
        <Route path="/" element={<Navigate to="/Dashboard" replace />} />

        <Route path="/Dashboard" element={<DashboardLayout />}>
          <Route index element={<Dashboard />} /> {/* Default child route */}
          <Route path="weight/new" element={<WeightForm />} />
          <Route path="weights" element={<WeightRecords />} />
          <Route path="unknown" element={<Unknown />} />
          <Route path="batch-upload" element={<BatchUpload />} />
          <Route path="session/:id" element={<Session />} />
        </Route>
      </Routes>
        </main>
        
        <footer className="app-footer">
          <p>Weight Management System © 2025</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
