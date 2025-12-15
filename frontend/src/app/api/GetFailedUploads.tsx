import { createClient } from "utils/supabase";

export async function getFailedUploads() {
  const supabase = createClient();
  const { data: session } = await supabase.auth.getSession();

  const url = `${process.env.NEXT_PUBLIC_API_BASE_URL}/admin/failed-uploads/`;

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
    console.error("An error occurred while fetching failed uploads.", error);
    return [];
  }
}

export async function downloadFailedFile(uploadId: number) {
  const supabase = createClient();
  const { data: session } = await supabase.auth.getSession();

  const url = `${process.env.NEXT_PUBLIC_API_BASE_URL}/admin/failed-uploads/${uploadId}/download`;

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
    console.error("An error occurred while getting download URL.", error);
    throw error;
  }
}

export async function updateFailedUploadFileUrl(uploadId: number, fileUrl: string, fileName?: string) {
  const supabase = createClient();
  const { data: session } = await supabase.auth.getSession();

  let url = `${process.env.NEXT_PUBLIC_API_BASE_URL}/admin/failed-uploads/${uploadId}/file-url`;
  const params = new URLSearchParams();
  params.append("file_url", fileUrl);
  if (fileName) {
    params.append("file_name", fileName);
  }
  if (params.toString()) {
    url += "?" + params.toString();
  }

  try {
    const response = await fetch(url, {
      method: "PATCH",
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
    console.error("An error occurred while updating file URL.", error);
    throw error;
  }
}

export async function rerunFailedUpload(uploadId: number, baselineDesign?: string) {
  const supabase = createClient();
  const { data: session } = await supabase.auth.getSession();

  let url = `${process.env.NEXT_PUBLIC_API_BASE_URL}/admin/failed-uploads/${uploadId}/rerun`;
  const params = new URLSearchParams();
  if (baselineDesign) {
    params.append("baseline_design", baselineDesign);
  }
  if (params.toString()) {
    url += "?" + params.toString();
  }

  try {
    const response = await fetch(url, {
      method: "POST",
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
    console.error("An error occurred while rerunning upload.", error);
    throw error;
  }
}


