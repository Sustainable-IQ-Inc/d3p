import { createClient } from "utils/supabase";

export async function getProjectList(
  companyId?: string,
  basic_info?: boolean,
  measurementSystem?: string,
  projectId?: string
) {
  const supabase = createClient();
  const { data: session } = await supabase.auth.getSession();

  let url = `${process.env.NEXT_PUBLIC_API_BASE_URL}/projects/`;
  let params = new URLSearchParams();

  if (companyId) {
    params.append("company_id", companyId);
  }

  if (basic_info !== undefined) {
    params.append("basic_info", String(basic_info));
  }

  if (measurementSystem !== undefined) {
    params.append("measurement_system", String(measurementSystem));
  }

  if (projectId !== undefined) {
    params.append("project_id", String(projectId));
  }

  if (params.toString()) {
    url += "?" + params.toString();
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
