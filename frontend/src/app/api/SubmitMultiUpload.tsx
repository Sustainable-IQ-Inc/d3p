import axios from "axios";
import { List } from "lodash";
import { createClient } from "utils/supabase";

interface MultiSubmitUploadProps {
  design_files: List<string>;
  baseline_files: List<string>;
}

const submitMultiUpload = async ({
  uploadProps,
}: {
  uploadProps: MultiSubmitUploadProps;
}): Promise<any> => {
  const supabase = createClient();
  const { data: session } = await supabase.auth.getSession();
  try {
    const response = await axios.post(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/submit_multi_upload/`,
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

    return response.data;
  } catch (error) {
    
    console.error("An error occurred while fetching the data.", error);
    return error;
    // You can decide how to handle the error here
  }
};
export default submitMultiUpload;
