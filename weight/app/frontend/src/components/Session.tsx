import React, { useState, useEffect } from 'react';
import weightService, { SessionData } from '../api/WeightService';
import { useParams } from "react-router-dom";


  
const Session: React.FC = () => {

    const { id } = useParams<string>();

    const [loading, setLoading] = useState(true);
    const [session, setSession] = useState<SessionData>();

    useEffect(() => {
        const fetchDashboardData = async () => {

          setLoading(true);

          try {

            // Get count of unknown containers
            const session = await weightService.getSession(id || "");
            setSession(session);

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
            <div className="loading">Loading session...</div>
        ) : session ? (
            <div className="records-table-wrapper">
            <table className="records-table">
                <thead>
                <tr>
                    <th>id</th>
                    <th>truck</th>
                    <th>bruto</th>
                    <th>truckTara</th>
                    <th>neto</th>
                    <th>produce</th>
                </tr>
                </thead>
                <tbody>            
                    <tr>
                        <td>{session.id}</td>
                        <td>{session.truck}</td>
                        <td>{session.bruto}</td>
                        <td>{session.truckTara}</td>
                        <td>{session.neto}</td>
                        <td>{session.produce}</td>
                    </tr>
                </tbody>
            </table>
            </div>
        ) : (
            <div className="no-records">No session found</div>
        )}
        </>

        
    )
}



export default Session;
