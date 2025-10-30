import { createClient } from 'utils/supabase';

export const FetchDDXPreviewData = async (project_id: string) => {
  const supabase = createClient();
  const { data: session } = await supabase.auth.getSession();

  let url = `${process.env.NEXT_PUBLIC_API_BASE_URL}/ddx_data/?project_id=${project_id}`;

  try {
    const response = await fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session?.session?.access_token}`,
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    
    // Extract clean_data from the response if it exists
    if (result.status === 'success' && result.clean_data) {
      return result.clean_data;
    }
    
    // If there's an error or different format, return the full result
    return result;
  } catch (error) {
    console.error("An error occurred while fetching the data.", error);
    return error;
    // You can decide how to handle the error here
  }
};


