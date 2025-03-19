import React, { useState, useEffect } from 'react';
import weightService from '../api/WeightService';


  
const Unknown: React.FC = () => {

    const [loading, setLoading] = useState(true);
    const [unknown, setUnknown] = useState([]);

    useEffect(() => {
        const fetchDashboardData = async () => {

          setLoading(true);

          try {

            // Get count of unknown containers
            const unknownContainers = await weightService.getUnknownContainers();
            console.log(unknownContainers);
            setUnknown(unknownContainers);

          } catch (error) {
            console.error("Unknown data fetch error:", error);
          } 
          
          finally {
            setLoading(false);
          }
        };
    
        fetchDashboardData();

    }, []);


    return (
        <>
            {loading ? (
            <div className="loading">Loading records...</div>
        ) : unknown.length > 0 ? (
            <div className="records-table-wrapper">
            <table className="records-table">
                <thead>
                <tr>
                    <th>Unknown container</th>
                </tr>
                </thead>
                <tbody>
                {unknown.map(record => (
                    <td>{record}</td>
                ))}
                </tbody>
            </table>
            </div>
        ) : (
            <div className="no-records">No records found</div>
        )}
        </>

        
    )
}



export default Unknown;
