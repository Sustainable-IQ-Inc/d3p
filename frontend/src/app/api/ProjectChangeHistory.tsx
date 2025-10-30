import { createClient } from "utils/supabase";

export async function getProjectChangeHistory(
  projectId: string
) {
  const supabase = createClient();
  const { data: session } = await supabase.auth.getSession();

  let url = `${process.env.NEXT_PUBLIC_API_BASE_URL}/project_change_history/?project_id=${projectId}`;




  

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
    return response.json();
  } catch (error) {
    
    console.error("An error occurred while fetching the data.", error);
    return error;
    // You can decide how to handle the error here
  }
}
