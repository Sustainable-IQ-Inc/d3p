import axios from "axios";
import { createClient } from "utils/supabase";
interface CreateProjectProps {
  companyId: string;
  projectName: string;
}

export interface ProjectResponse {
  data: {
    status: string;
    id: string;
  };
}

const createProject = async ({
  companyId,
  projectName,
}: CreateProjectProps): Promise<ProjectResponse> => {
  const supabase = createClient();
  const { data: session } = await supabase.auth.getSession();
  try {
    const response: ProjectResponse = await axios.post(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/create_project/`,
      {
        company_id: companyId,
        project_name: projectName,
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
          id: response.data.id,
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

export default createProject;
