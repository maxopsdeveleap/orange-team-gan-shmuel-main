// src/components/Dashboard.tsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import weightService from '../api/WeightService';

const Dashboard: React.FC = () => {
  const [isHealthy, setIsHealthy] = useState(true);
  const [unknownCount, setUnknownCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      try {
        // Check system health
        await weightService.checkHealth();
        setIsHealthy(true);

        // Get count of unknown containers
        const unknownContainers = await weightService.getUnknownContainers();
        setUnknownCount(unknownContainers.length);
      } catch (error) {
        console.error("Dashboard data fetch error:", error);
        setIsHealthy(false);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  return (
    <div className="dashboard-container">
      <h1>Weight Management System</h1>
      
      {loading ? (
        <div className="loading">Loading dashboard...</div>
      ) : (
        <>
          <div className={`system-status ${isHealthy ? 'healthy' : 'unhealthy'}`}>
            System Status: {isHealthy ? 'Healthy' : 'Issue Detected'}
          </div>
          
          <div className="dashboard-stats">
            <div className="stat-card">
              <h3>Unknown Containers</h3>
              <div className="stat-value">{unknownCount}</div>
              <Link to="/unknown" className="stat-link">View List</Link>
            </div>
          </div>
          
          <div className="quick-actions">
            <h2>Quick Actions</h2>
            <div className="action-buttons">
              <Link to="/weight/new" className="action-button">
                Record New Weight
              </Link>
              <Link to="/weights" className="action-button">
                View Weight Records
              </Link>
              <Link to="/batch-upload" className="action-button">
                Batch Upload
              </Link>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Dashboard;
