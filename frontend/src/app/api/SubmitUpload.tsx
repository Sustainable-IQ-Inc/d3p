import axios from "axios";
import { createClient } from "utils/supabase";
import { SubmitUploadProps } from "types/file-submission";

const submitUpload = async ({
  uploadProps,
}: {
  uploadProps: SubmitUploadProps;
}): Promise<string> => {
  const supabase = createClient();
  const { data: session } = await supabase.auth.getSession();
  try {
    console.log("Submitting project with data:", uploadProps);
    const response = await axios.post(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/submit_project/`,
      {
        ...uploadProps,
      },
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${session?.session?.access_token}`,
        },
      }
    );

    console.log("Submit response:", response.data);
    if (response.data === "success") {
      return "success";
    } else if (response.data && typeof response.data === 'object' && response.data.error) {
      console.error("Submit error:", response.data.error);
      throw new Error(response.data.error);
    } else {
      console.error("Submit returned non-success:", response.data);
      return "failed";
    }
  } catch (error: any) {
    console.error("Error creating project:", error);
    if (error.response) {
      console.error("Error response data:", error.response.data);
      console.error("Error response status:", error.response.status);
    }
    return "failed";
  }
};

export default submitUpload;
