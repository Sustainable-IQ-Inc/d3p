import axios from "axios";
import { createClient } from "utils/supabase";

const updateGSF = async (projectId: string, gsfValue: string): Promise<string> => {
  const supabase = createClient();
  const { data: session } = await supabase.auth.getSession();
  
  try {
    const response = await axios.post(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/update_gsf/`,
      {
        project_id: projectId,
        use_type_total_area: gsfValue,
      },
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${session?.session?.access_token}`,
        },
      }
    );

    if (response.data === "success") {
      return "success";
    } else {
      return "failed";
    }
  } catch (error) {
    console.error("Error updating GSF:", error);
    return "failed";
  }
};

export default updateGSF;

