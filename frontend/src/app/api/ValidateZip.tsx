import axios from "axios";
import { createClient } from "utils/supabase";
interface ValidateZipProps {
  zip_code: string;
  project_id: string;
}

export interface ZipResponse {
  data: {
    status: string;
  };
}

const validateZip = async ({
  zip_code,
  project_id,
}: ValidateZipProps): Promise<ZipResponse> => {
  const supabase = createClient();
  const { data: session } = await supabase.auth.getSession();

  try {
    const response: ZipResponse = await axios.post(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/update_climate_zone_by_zip/`,
      {
        zip_code: zip_code,
        project_id: project_id,
      },
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${session?.session?.access_token}`,
        },
      }
    );


    if (response.data.status === "success") {
      //return a dict with the status and the id of the project

      return {
        data: {
          status: response.data.status,
        },
      };
    } else {
      return Promise.reject("failed");
    }
  } catch (error) {
    console.error("Error creating project:", error);
    return Promise.reject("failed");
  }
};

export default validateZip;
