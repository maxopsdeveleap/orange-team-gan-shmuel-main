import React, { useState } from 'react';
import weightService, { ItemData } from '../api/WeightService';
import { X } from "lucide-react"; 

interface QuickSearchFormProps {
    onSuccess?: (data: any) => void;
  }
  
const QuickSearch: React.FC<QuickSearchFormProps> = ({ onSuccess }) => {

    const [id, setId] = useState('');

    // Filter states
    const [fromDate, setFromDate] = useState('');
    const [toDate, setToDate] = useState('');

    const [loading, setLoading] = useState(false);
    const [data, setData] = useState<ItemData>();
    const [error, setError] = useState('');


    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setData(undefined);
        
    
        try {
          // Form validation
          if (!id) {
            throw new Error('Please enter a valid id');
          }
    
          // Make API call
          const response = await weightService.getItem(id,fromDate,toDate);
          
          setData(response);

          if (onSuccess) {
            onSuccess(response);
          }
                    
        } catch (err: any) {

          setError(err instanceof Error ? err.message : 'An error occurred while searching');
          console.error('search submission error:', err);

        } finally {
          setLoading(false);
        }
      };


    return (

        <div>
            <h3>Search for item</h3>
      
            {error && error!=="Request failed with status code 404" && <div className="error-message">{error}</div>}

            <form onSubmit={handleSubmit}>

              <div className="form-group" style={{ position: "relative", display: "inline-block" }}>
                <input
                  id="itemId"
                  type="text"
                  value={id}
                  onChange={(e) => setId(e.target.value)}
                  placeholder="Item id"
                  style={{ paddingRight: id ? "30px" : "10px" }}
                />
                {id && (
                  <button
                    type="button"
                    onClick={() => setId('')}
                    style={{
                      position: "absolute",
                      right: "5px",
                      top: "50%",
                      transform: "translateY(-50%)",
                      border: "none",
                      background: "transparent",
                      cursor: "pointer",
                      color: "black"
                    }}
                  >
                    <X size={18} />
                  </button>
                )}
              </div>

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

              <button type="submit" disabled={loading}>
                    {loading ? 'Searching...' : 'Search'}
              </button>

            </form>

            {loading ? (
              <div className="loading">searching...</div>
            ) : data ? (
              <div className="records-table-wrapper">
                <table className="records-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Sessions</th>
                      <th>Tara (kg)</th>
                    </tr>
                  </thead>
                  <tbody>
                      <tr>
                        <td>{data.id}</td>
                        <td>{data.sessions.length}</td>
                        <td>{data.tara}</td>
                      </tr>
                  </tbody>
                </table>
              </div>
            ) : ""}

            {error==="Request failed with status code 404"? (
              <div className="no-records">No data found</div>
            ): ""}

        </div>
        
    )
}



export default QuickSearch;
