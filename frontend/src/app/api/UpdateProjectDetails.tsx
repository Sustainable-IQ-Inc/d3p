import axios from "axios";
import { createClient } from "utils/supabase";
import { ProjectUpdate } from "types/updates";

const submitUpload = async ({
  updateProps,
}: {
  updateProps: ProjectUpdate;
}): Promise<string> => {
  const supabase = createClient();
  const { data: session } = await supabase.auth.getSession();
  try {
    const response = await axios.post(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/update_upload/`,
      {
        ...updateProps,
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
    } else if (response.data === "custom_project_id_not_unique") {
      return "custom_project_id_not_unique";
    } else {
      return "failed";
    }
  } catch (error) {
    console.error("Error updating project:", error);
    return "failed";
  }
};

export default submitUpload;
