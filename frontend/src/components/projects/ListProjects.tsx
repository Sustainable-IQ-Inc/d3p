import React, { useState, useEffect } from "react";
import CreatableSelect from "react-select/creatable";
import { getProjectList } from "./project"; // Import your API function
import CreateProject, { ProjectResponse } from "../../app/api/CreateProject"; //app/api/CreateProject';

// Define a type for the project list items
type ProjectListItem = {
  id: number;
  project_name: string;
};

// Define a type for the select option
type SelectOption = {
  value: string;
  label: string;
};

const createOption = (label: string, value: string) => ({
  label,
  value,
});

// Define the props type if your component takes props (optional)
interface MyCreatableComponentProps {
  companyId?: string;
  onProjectSelect?: (projectId: string) => void;
  value?: string;
}

const MyCreatableComponent: React.FC<MyCreatableComponentProps> = ({
  companyId,
  onProjectSelect,
  value: propValue,
}) => {
  const [options, setOptions] = useState<SelectOption[]>([]);
  const [value, setValue] = useState<SelectOption | null>();

  useEffect(() => {
    // If the value prop changes, update the value state
    if (!propValue) {
      setValue(null);
    }
  }, [propValue]);

  const fetchProjects = () => {
    console.log("Fetching projects for companyId:", companyId);
    getProjectList(companyId, true)
      .then((data: ProjectListItem[]) => {
        console.log("Received project data:", data);
        const transformedOptions = data.map((item) => ({
          value: item.id.toString(),
          label: item.project_name,
        }));
        setOptions(transformedOptions);
      })
      .catch((error: Error) => {
        console.error("Error fetching project list:", error);
      });
  };

  useEffect(() => {
    if (companyId) {
      fetchProjects();
    }
  }, [companyId]);

  const handleCreate = async (inputValue: string) => {
    // Handle new option creation
    const response: ProjectResponse = await CreateProject({
      companyId: companyId!,
      projectName: inputValue,
    });
    if (response.data.status === "success") {
      
      fetchProjects();
      if (onProjectSelect) {
        onProjectSelect(response.data.id);
      }
    } else {
      
    }

    const newOption = createOption(inputValue, response.data.id);
    setOptions((prev) => [...prev, newOption]);
    setValue(newOption);
  };

  return (
    <CreatableSelect
      id="project-selector"
      isClearable
      key={`project-selector-${value?.value}`}
      options={options}
      onChange={(newValue) => {
        setValue(newValue);
        if (onProjectSelect && newValue) {
          onProjectSelect(newValue.value);
        }
      }}
      onCreateOption={handleCreate}
      loadingMessage={() => "Loading Projects..."}
      placeholder="Select or create a project"
      value={value}
    />
  );
};

export default MyCreatableComponent;
