import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://10.11.200.99:8000/api/v1';
const PIPELINE_URL = process.env.NEXT_PUBLIC_PIPELINE_URL || 'http://10.11.200.99:8001';

export const api = axios.create({
  baseURL: API_URL,
});

export interface Model {
  name: string;
  provider: string;
  active: boolean;
}

export interface OCRResponse {
  text: string;
  format: string;
  metadata: any;
  bounding_boxes?: any[];
}

export const fetchModels = async (): Promise<Model[]> => {
  const response = await api.get('/models');
  return response.data;
};

export const setActiveModel = async (name: string): Promise<void> => {
  await api.post('/models/active', { name });
};

export const processImage = async (file: File, modelName?: string, prompt?: string, template?: string): Promise<OCRResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  if (modelName) formData.append('model_name', modelName);
  if (prompt) formData.append('prompt', prompt);
  if (template) formData.append('template', template);

  const response = await api.post('/ocr/process', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export interface PipelineJobResponse {
  job_id: string;
  status: string;
}

export const submitPipelineJob = async (file: File, schema?: string): Promise<PipelineJobResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  if (schema) formData.append('schema', schema);

  // Use the port 8001 directly for the backend pipeline
  // const pipelineUrl = 'http://localhost:8001';
  const response = await axios.post(`${PIPELINE_URL}/v1/ocr/schema`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

export const getPipelineResult = async (jobId: string) => {
  // const pipelineUrl = 'http://localhost:8001';
  const response = await axios.get(`${PIPELINE_URL}/v1/ocr/results/${jobId}`);
  return response.data;
};

export const fetchBenchmarks = async () => {
  const response = await api.get('/benchmark');
  return response.data;
};
