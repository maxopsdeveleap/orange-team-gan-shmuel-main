import axios from 'axios';

// Set base URL for API - change this to your Flask backend URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types for our API
export interface WeightData {
  direction: 'in' | 'out' | 'none';
  truck: string;
  containers?: string;
  weight: number;
  unit?: 'kg' | 'lbs';
  force: boolean;
  produce?: string;
}

export interface WeightResponse {
  id: string;
  truck: string;
  bruto: number;
  truckTara?: number;
  neto?: number | 'na';
}


export interface BatchWeightData {
  file: string;
}

export interface BatchWeightResponse {
  count: number;
  message: string
}

export interface SessionData {
  id: string;
  truck: string;
  bruto: number;
  truckTara?: number;
  neto?: number | 'na';
}

export interface ItemData {
  id: string;
  tara: number | 'na';
  sessions: string[];
}

// Weight API functions
export const weightService = {


  // Record a new weight
  createWeight: async (data: WeightData): Promise<WeightResponse> => {
    const response = await api.post('/weight', data);
    return response.data;
  },

  uploadBatchWeight: async (data: BatchWeightData): Promise<BatchWeightResponse> => {
    const response = await api.post('/batch-weight', data);
    return response.data;
  },

  // Get weight records with optional filters
  getWeights: async (
    from?: string,
    to?: string,
    filter?: string
  ) => {
    const params = new URLSearchParams();
    if (from) params.append('from', from);
    if (to) params.append('to', to);
    if (filter) params.append('filter', filter);
    
    const response = await api.get(`/weight?${params.toString()}`);
    return response.data;
  },

  // Upload batch weight file
  // uploadBatchWeight: async (file: File) => {
  //   const formData = new FormData();
  //   formData.append('file', file);
    
  //   const response = await api.post('/batch-weight', formData, {
  //     headers: {
  //       'Content-Type': 'multipart/form-data',
  //     },
  //   });
    
  //   return response.data;
  // },

  // Get unknown containers
  getUnknownContainers: async () => {
    const response = await api.get('/unknown');
    return response.data;
  },

  // Get item details
  getItem: async (
    id: string,
    from?: string,
    to?: string
  ): Promise<ItemData> => {
    const params = new URLSearchParams();
    if (from) params.append('from', from);
    if (to) params.append('to', to);
    
    const response = await api.get(`/item/${id}?${params.toString()}`);
    return response.data;
  },

  // Get session details
  getSession: async (id: string): Promise<SessionData> => {
    const response = await api.get(`/session/${id}`);
    return response.data;
  },

  // Check system health
  checkHealth: async () => {
    const response = await api.get('/health');
    return response.data;
  }
};

export default weightService;
