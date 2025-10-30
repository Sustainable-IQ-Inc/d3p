import { createClient } from 'utils/supabase';
import axios from 'axios';

export const authenticateDDX = async (userId: string) => {
  const supabase = createClient();
  const { data: session } = await supabase.auth.getSession();
  
  const url = `${process.env.NEXT_PUBLIC_API_BASE_URL}/ddx_keys/authenticate/${userId}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${session?.session?.access_token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
};

export const fetchKeyStatus = async (userId: string) => {
  const supabase = createClient();
  const { data: session } = await supabase.auth.getSession();
  try {
    const response = await axios.get(`${process.env.NEXT_PUBLIC_API_BASE_URL}/ddx_keys/status/${userId}`, {
      headers: {
        'Authorization': `Bearer ${session?.session?.access_token}`
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching key status:', error);
    throw error;
  }
};

interface KeyUpdate {
  userKey?: string;
  firmKey?: string;
}

export const updateKeys = async (userId: string, keys: KeyUpdate) => {
  const supabase = createClient();
  const { data: session } = await supabase.auth.getSession();

  try {
    const response = await axios.post(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/ddx_keys/update/${userId}`, 
      keys,
      {
        headers: {
          'Authorization': `Bearer ${session?.session?.access_token}`,
          'Content-Type': 'application/json'
        },
        httpsAgent: new (require('https').Agent)({
          rejectUnauthorized: true // Enforce SSL certificate validation
        })
      }
    );
    return response.data;
  } catch (error) {
    console.error('Error updating keys:', error);
    throw error;
  }
};

export const getDDXIntegrationStatus = async (projectId: string) => {
  const supabase = createClient();
  const { data: session } = await supabase.auth.getSession();
  
  const url = `${process.env.NEXT_PUBLIC_API_BASE_URL}/ddx_integration_status/${projectId}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${session?.session?.access_token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
};

export const getDDXIntegrationStatusBatch = async (projectIds: string[]) => {
  const supabase = createClient();
  const { data: session } = await supabase.auth.getSession();
  
  const url = `${process.env.NEXT_PUBLIC_API_BASE_URL}/ddx_integration_status_batch/`;
  
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${session?.session?.access_token}`,
    },
    body: JSON.stringify({ project_ids: projectIds }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
};