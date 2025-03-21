import React, { useState, useEffect } from 'react';
import weightService from '../api/WeightService';
import { useNavigate } from 'react-router-dom';


  
const Unknown: React.FC = () => {

    const navigate = useNavigate();

    const [loading, setLoading] = useState(true);
    const [unknown, setUnknown] = useState([]);

    useEffect(() => {
        const fetchDashboardData = async () => {

          setLoading(true);

          try {

            // Get count of unknown containers
            const unknownContainers = await weightService.getUnknownContainers();
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

    const handleNavigate = (container: string) => {
        navigate('/Dashboard/weight/new', { 
            state: {
                direction: 'none', 
                containers: container
            } 
        });
    };


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
                    <th></th>
                </tr>
                </thead>
                <tbody>
                {unknown.map((container, index) => (
                    <tr>
                        <td key={index}>{container}</td>
                        <td>
                            <button  onClick={()=>{ handleNavigate(container) }}>Add container</button>
                        </td>
                    </tr>
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
