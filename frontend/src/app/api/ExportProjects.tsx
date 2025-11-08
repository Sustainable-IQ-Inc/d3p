import { createClient } from "utils/supabase";

export async function exportProjectsCSV(
  projectId?: string,
  companyId?: string,
  measurementSystem?: string,
  searchTerm?: string
) {
  const supabase = createClient();
  const { data: session } = await supabase.auth.getSession();

  const url = `${process.env.NEXT_PUBLIC_API_BASE_URL}/export_projects_csv/`;
  
  // Build request body for POST (to avoid URL length limits with many project IDs)
  const body: any = {};
  
  if (projectId) {
    body.project_id = projectId;
  }

  if (companyId) {
    body.company_id = companyId;
  }

  if (measurementSystem) {
    body.measurement_system = measurementSystem;
  }

  // If search term is provided, send it to filter on the backend
  if (searchTerm && searchTerm.trim()) {
    body.search_term = searchTerm.trim();
  }

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session?.session?.access_token}`,
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      // Try to get error message from response body
      let errorMessage = `HTTP error! status: ${response.status}`;
      try {
        const errorData = await response.text();
        if (errorData) {
          errorMessage += ` - ${errorData}`;
        }
      } catch (e) {
        // Ignore if we can't parse error
      }
      console.error("Export API error:", errorMessage);
      throw new Error(errorMessage);
    }

    // Get filename from Content-Disposition header or use default
    const contentDisposition = response.headers.get("Content-Disposition");
    let filename = "d3p-export.csv";
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="(.+)"/);
      if (filenameMatch) {
        filename = filenameMatch[1];
      }
    }

    // Convert response to blob and trigger download
    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = downloadUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);

    return { status: "success" };
  } catch (error) {
    console.error("An error occurred while exporting the data.", error);
    throw error;
  }
}

