import { createClient } from "utils/supabase";

export async function getCompany(company_id: string) {
  console.log("=== GetCompany API Call ===");
  console.log("Input company_id:", company_id);
  
  const supabase = createClient();
  const { data: session } = await supabase.auth.getSession();

  let url = `${process.env.NEXT_PUBLIC_API_BASE_URL}/companies/${company_id}`;
  console.log("API URL:", url);

  try {
    const response = await fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session?.session?.access_token}`,
      },
    });

    console.log("Response status:", response.status);
    
    if (!response.ok) {
      console.error("Response not OK:", response.status, response.statusText);
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const jsonData = await response.json();
    console.log("Response JSON data:", jsonData);
    return jsonData;
  } catch (error) {
    console.error("An error occurred while fetching the data.", error);
    return error;
  }
}

