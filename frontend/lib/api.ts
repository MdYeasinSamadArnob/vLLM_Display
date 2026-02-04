import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

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

export const fetchBenchmarks = async () => {
  const response = await api.get('/benchmark');
  return response.data;
};
