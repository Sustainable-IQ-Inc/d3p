import { createClient } from "utils/supabase";

export async function getEnumList(
  enum_name: string,
  additional_filter_fields?: { [key: string]: any }
) {
  const supabase = createClient();
  const { data: session } = await supabase.auth.getSession();

  let url = `${process.env.NEXT_PUBLIC_API_BASE_URL}/enums/${enum_name}/`;

  // Convert additional_filter_fields to a query string and append it to the URL
  if (additional_filter_fields) {
    const queryString = new URLSearchParams(
      additional_filter_fields
    ).toString();
    url += `?${queryString}`;
  }

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
