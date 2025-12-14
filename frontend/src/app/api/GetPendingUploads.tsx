import { createClient } from "utils/supabase";

export async function getPendingUploads() {
  const supabase = createClient();
  const { data: session } = await supabase.auth.getSession();

  const url = `${process.env.NEXT_PUBLIC_API_BASE_URL}/pending-uploads/`;

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
    console.error("An error occurred while fetching pending uploads.", error);
    return [];
  }
}


