import React, { useState } from 'react';
import weightService from '../api/WeightService';
import { AxiosError } from 'axios';
import { useLocation } from "react-router-dom";

interface WeightFormProps {
  onSuccess?: (data: any) => void;
}

interface LocationState {
  direction?: 'in' | 'out' | 'none';
  containers?: string;
}

const WeightForm: React.FC<WeightFormProps> = ({ onSuccess }) => {

  const location = useLocation();
  const state = location.state as LocationState || {}; 


  const [direction, setDirection] = useState<'in' | 'out' | 'none'>(state.direction || 'in');
  const [truck, setTruck] = useState('');
  const [containers, setContainers] = useState(state.containers || '');
  const [weight, setWeight] = useState('');
  const [unit, setUnit] = useState<'kg' | 'lbs'>('kg');
  const [force, setForce] = useState(false);
  const [produce, setProduce] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccessMessage('');

    try {
      // Form validation
      if (!weight || isNaN(Number(weight))) {
        throw new Error('Please enter a valid weight');
      }

      // Prepare data for API
      let formData = {

        ...(direction !== "out" && {
          containers,
          produce: produce || 'na',
        }),

        ...(direction !== "none" && {
          force,
          truck: truck || 'na',
        }),

        direction,
        weight: parseInt(weight, 10),
        unit,
        
      };


      // Make API call
      const response = await weightService.createWeight(formData);
      
      setSuccessMessage(`Weight recorded successfully! ID: ${response.id}`);
      if (onSuccess) {
        onSuccess(response);
      }
      
      // Reset form if needed
      if (direction === 'out' || direction === 'none') {
        setTruck('');
        setContainers('');
        setWeight('');
        setProduce('');
      }
      
    } 

    catch (err: any) {

      if (err instanceof AxiosError){
        setError(err.response?.data.error || err.message);
      } 

      else if(err instanceof Error){
        setError(err.message);
      } 
      
      else {
        setError('An error occurred while recording weight');
      }

      console.error('Weight submission error:', err);
    }

    finally {
      setLoading(false);
    }
  };

  return (
    <div className="weight-form-container">
      <h2>Record New Weight</h2>
      
      {error && <div className="error-message">{error}</div>}
      {successMessage && <div className="success-message">{successMessage}</div>}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="direction">Direction:</label>
          <select 
            id="direction"
            value={direction}
            onChange={(e) => setDirection(e.target.value as 'in' | 'out' | 'none')}
            required
          >
            <option value="in">In</option>
            <option value="out">Out</option>
            <option value="none">None</option>
          </select>
        </div>

        {direction !== 'none' && (
          <div className="form-group">
            <label htmlFor="truck">Truck License:</label>
            <input
              id="truck"
              type="text"
              value={truck}
              onChange={(e) => setTruck(e.target.value)}
              placeholder="License number or 'na'"
            />
          </div>
        )}
        
        {direction !== 'out' && (
          <div className="form-group">
            <label htmlFor="containers">Containers:</label>
            <input
              id="containers"
              type="text"
              value={containers}
              onChange={(e) => setContainers(e.target.value)}
              placeholder="Container IDs (comma-separated)"
            />
          </div>
        )}

        

        <div className="form-group">
          <label htmlFor="weight">Weight:</label>
          <input
            id="weight"
            type="number"
            value={weight}
            onChange={(e) => setWeight(e.target.value)}
            placeholder="Enter weight"
            required
          />
        </div>

        
        <div className="form-group">
          <label htmlFor="unit">Unit:</label>
          <select
            id="unit"
            value={unit}
            onChange={(e) => setUnit(e.target.value as 'kg' | 'lbs')}
          >
            <option value="kg">kg</option>
            <option value="lbs">lbs</option>
          </select>
        </div>

        {direction === 'in' && (
            <div className="form-group">
              <label htmlFor="produce">Produce:</label>
              <input
                id="produce"
                type="text"
                value={produce}
                onChange={(e) => setProduce(e.target.value)}
                placeholder="e.g., orange, tomato, or 'na'"
              />
            </div>
        )}

        
        {direction !== 'none' && (
          <div className="form-group checkbox">
            <input
              id="force"
              type="checkbox"
              checked={force}
              onChange={(e) => setForce(e.target.checked)}
            />
            <label htmlFor="force">Force (Overwrite previous weighing if exists)</label>
          </div>
        )}

        <button type="submit" disabled={loading}>
          {loading ? 'Submitting...' : 'Record Weight'}
        </button>
      </form>
    </div>
  );
};

export default WeightForm;
