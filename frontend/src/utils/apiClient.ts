import { createClient } from "utils/supabase";
import https from 'https';

interface ApiOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  body?: any;
  queryParams?: Record<string, string>;
}

export async function apiRequest<T>(
  endpoint: string,
  options: ApiOptions = {}
): Promise<T> {
  const supabase = createClient();
  const { data: session } = await supabase.auth.getSession();
  
  const queryString = options.queryParams
    ? `?${new URLSearchParams(options.queryParams).toString()}`
    : '';
    
  const url = `${process.env.NEXT_PUBLIC_API_BASE_URL}${endpoint}${queryString}`;

  try {
    const response = await fetch(url, {
      method: options.method || 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${session?.session?.access_token}`,
      },
      ...(options.body && { body: JSON.stringify(options.body) }),
      agent: new https.Agent({
        rejectUnauthorized: true
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  } catch (error) {
    console.error(`API request failed for ${endpoint}:`, error);
    throw error;
  }
} 