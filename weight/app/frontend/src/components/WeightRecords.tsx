// src/components/WeightRecords.tsx
import React, { useState, useEffect } from 'react';
import { format } from 'date-fns';
import weightService from '../api/WeightService';

interface WeightRecord {
  id: string;
  direction: 'in' | 'out' | 'none';
  bruto: number;
  neto: number | 'na';
  produce: string;
  containers: string[];
  session: number;
}

const WeightRecords: React.FC = () => {
  const [records, setRecords] = useState<WeightRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Filter states
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [directions, setDirections] = useState<string[]>(['in', 'out', 'none']);

  useEffect(() => {
    fetchRecords();
  }, []);

  const fetchRecords = async () => {
    setLoading(true);
    setError('');
    
    try {
      // Format dates for API if provided
      const fromParam = fromDate ? formatDateForApi(fromDate) : '';
      const toParam = toDate ? formatDateForApi(toDate) : '';
      
      // Build filter string
      const filterParam = directions.length > 0 && directions.length < 3 
        ? directions.join(',') 
        : '';
      
      const data = await weightService.getWeights(fromParam, toParam, filterParam);
      setRecords(data);
    } catch (err: any) {
      setError('Failed to fetch weight records');
      console.error('Error fetching records:', err);
    } finally {
      setLoading(false);
    }
  };

  // Helper to format date for API (yyyymmddhhmmss)
  const formatDateForApi = (dateStr: string): string => {
    const date = new Date(dateStr);
    return format(date, 'yyyyMMddHHmmss');
  };

  const handleDirectionToggle = (direction: string) => {
    setDirections(prev => 
      prev.includes(direction) 
        ? prev.filter(d => d !== direction)
        : [...prev, direction]
    );
  };

  const handleFilter = (e: React.FormEvent) => {
    e.preventDefault();
    fetchRecords();
  };

  return (
    <div className="weight-records-container">
      <h2>Weight Records</h2>
      
      <form onSubmit={handleFilter} className="filter-form">
        <div className="date-filters">
          <div className="form-group">
            <label htmlFor="fromDate">From:</label>
            <input
              id="fromDate"
              type="datetime-local"
              value={fromDate}
              onChange={(e) => setFromDate(e.target.value)}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="toDate">To:</label>
            <input
              id="toDate"
              type="datetime-local"
              value={toDate}
              onChange={(e) => setToDate(e.target.value)}
            />
          </div>
        </div>
        
        <div className="direction-filters">
          <div className="checkbox-group">
            <label>Directions:</label>
            <div className="checkboxes">
              <label>
                <input
                  type="checkbox"
                  checked={directions.includes('in')}
                  onChange={() => handleDirectionToggle('in')}
                />
                In
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={directions.includes('out')}
                  onChange={() => handleDirectionToggle('out')}
                />
                Out
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={directions.includes('none')}
                  onChange={() => handleDirectionToggle('none')}
                />
                None
              </label>
            </div>
          </div>
        </div>
        
        <button type="submit">Apply Filters</button>
      </form>
      
      {error && <div className="error-message">{error}</div>}
      
      {loading ? (
        <div className="loading">Loading records...</div>
      ) : records.length > 0 ? (
        <div className="records-table-wrapper">
          <table className="records-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Direction</th>
                <th>Bruto (kg)</th>
                <th>Neto (kg)</th>
                <th>Produce</th>
                <th>Containers</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {records.map(record => (
                <tr key={record.id}>
                  <td>{record.id}</td>
                  <td>{record.direction}</td>
                  <td>{record.bruto}</td>
                  <td>{record.neto === 'na' ? 'N/A' : record.neto}</td>
                  <td>{record.produce}</td>
                  <td>
                    {record.containers.length > 0 
                      ? record.containers.join(', ')
                      : 'None'}
                  </td>
                  <td>
                    <a href={`/Dashboard/session/${record.session}`}>View Details</a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="no-records">No records found</div>
      )}
    </div>
  );
};

export default WeightRecords;
