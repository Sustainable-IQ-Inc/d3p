import React, { useEffect, useState } from 'react';
import { getProjectChangeHistory } from 'app/api/ProjectChangeHistory';

// Define the type for the change history data
interface ChangeHistoryData {
  field_name: string;
  previous_value: string;
  new_value: string;
  updated_at: string;
  updated_by: string;
  
}

const ChangeHistory: React.FC<{ project_id: string }> = ({ project_id }) => {
  const [data, setData] = useState<ChangeHistoryData[]>([]); // Change to an array
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = () => {
      getProjectChangeHistory(project_id)
        .then((response: string) => {
          try {
            const result = JSON.parse(response); // Parse the JSON string
            
            
            
            if (Array.isArray(result)) {
              if (result.length === 0) {
                setError("There have not been any changes for this project");
              } else {
                setData(result); // Directly set the data
              }
            } else {
              setData([]); // Fallback to an empty array if not
              setError("Unexpected data format");
            }
          } catch (parseError) {
            setError("Failed to parse response");
          }
        })
        .catch((error) => {
          if (error instanceof Error) {
            setError(error.message);
          } else {
            setError(String(error));
          }
        })
        .finally(() => {
          setLoading(false);
        });
    };

    fetchData();
  }, [project_id]); // Add project_id as a dependency

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;
  if (data.length === 0) return null; // Check for empty array

  return (
    <div>
      {data.map((item, index) => (
        <div key={index} style={{ border: '1px solid #ccc', padding: '10px', borderRadius: '5px', marginBottom: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <div style={{ backgroundColor: '#4CAF50', borderRadius: '50%', width: '30px', height: '30px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', marginRight: '10px' }}>
              {item.updated_by.charAt(0).toUpperCase()}
            </div>
            <div>
              <strong>{item.updated_by}</strong>
              <div>{new Date(item.updated_at).toLocaleString()}</div>
            </div>
          </div>
          <div style={{ marginTop: '10px' }}>
            <strong>Field:</strong> {item.field_name}
          </div>
          <div>
            <strong>Value:</strong> <s>{item.previous_value}</s> &rarr; <span style={{ color: '#007BFF' }}>{item.new_value}</span>
          </div>
        </div>
      ))}
    </div>
  );
};

export default ChangeHistory;
