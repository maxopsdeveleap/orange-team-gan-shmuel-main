import React, { useState } from 'react';
import weightService from '../api/WeightService';

interface BatchUploadFormProps {
    onSuccess?: (data: any) => void;
  }
  
const BatchUpload: React.FC<BatchUploadFormProps> = ({ onSuccess }) => {

    const [fileName, setFileName] = useState('');
    const [loading, setLoading] = useState(false);
    const [successMessage, setSuccessMessage] = useState('');
    const [error, setError] = useState('');


    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        
    
        try {
          // Form validation
          if (!fileName) {
            throw new Error('Please enter a valid file name');
          }
    
          // Prepare data for API
          let formData = {
            file: fileName
          };
    
    
          // Make API call
          const response = await weightService.uploadBatchWeight(formData);
          
          setSuccessMessage(response.message);

          if (onSuccess) {
            onSuccess(response);
          }
          
            setFileName('');
          
        } catch (err: any) {
          setError(err instanceof Error ? err.message : 'An error occurred while recording weight');
          console.error('Weight submission error:', err);
        } finally {
          setLoading(false);
        }
      };


    return (

        <div>
            <h2>Upload Batch Weight</h2>
      
            {error && <div className="error-message">{error}</div>}
            {successMessage && <div className="success-message">{successMessage}</div>}

            <form onSubmit={handleSubmit}>

                <div className="form-group">
                    <label htmlFor="fileName">File Name:</label>
                    <input
                        id="fileName"
                        type="text"
                        value={fileName}
                        onChange={(e) => setFileName(e.target.value)}
                        placeholder="File name"
                    />
                </div>

                <button type="submit" disabled={loading}>
                    {loading ? 'Submitting...' : 'Upload'}
                </button>

            </form>

        </div>
        
    )
}



export default BatchUpload;
