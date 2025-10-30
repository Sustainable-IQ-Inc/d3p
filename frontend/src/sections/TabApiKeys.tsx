'use client';



// project import
import MainCard from 'components/MainCard';
import { TextField, Box, Button } from '@mui/material';
import { Field, Form, Formik } from 'formik';
import { useEffect, useState } from 'react';
import useUser  from 'hooks/useUser';
import { fetchKeyStatus, updateKeys } from 'app/api/apiKeyService';

// ==============================|| TAB - PASSWORD CHANGE ||============================== //

type KeyFieldProps = {
  name: string;
  label: string;
  isEditing: boolean;
  isKeySet: boolean;
  isKeyTyped: boolean;
  setIsEditing: React.Dispatch<React.SetStateAction<boolean>>;
  setIsKeySet: React.Dispatch<React.SetStateAction<boolean>>;
  setIsKeyTyped: React.Dispatch<React.SetStateAction<boolean>>;
  handleChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  handleSubmit: (event: React.FormEvent<HTMLFormElement>) => void;
  userId: string;
};

const KeyField: React.FC<KeyFieldProps> = ({
  name,
  label,
  isEditing,
  isKeySet,
  setIsEditing,
  setIsKeySet,
  setIsKeyTyped,
  handleChange,
  handleSubmit,
  userId
}) => (
  <Field name={name}>
    {({ field, form }: { field: any; form: any }) => (
      <Box mb={2}>
        <TextField
          {...field}
          id={name}
          label={label}
          value={isEditing ? form.values[name] : isKeySet ? '••••••••' : ''}
          variant="outlined"
          disabled={!isEditing}
          onChange={(e) => {
            form.setFieldValue(name, e.target.value);
            setIsKeyTyped(true);
          }}
          InputProps={{
            style: { width: '250px' }
          }}
        />
        {isEditing ? (
          <>
            <Button
              variant="contained"
              onClick={async (e) => {
                e.preventDefault();
                const keyValue = form.values[name];
                const payload = name === 'user_key' 
                  ? { userKey: keyValue }
                  : { firmKey: keyValue };
                await updateKeys(userId, payload);
                form.setFieldValue(name, '');
                setIsKeySet(true);
                setIsEditing(false);
                setIsKeyTyped(false);
              }}
              style={{ marginLeft: '10px', marginRight: '8px' }}
              disabled={!form.values[name]}
            >
              Save Changes
            </Button>
            <Button variant="outlined" onClick={() => {
              setIsEditing(false);
              setIsKeyTyped(false);
            }}>Cancel</Button>
          </>
        ) : (
          <Button
            variant="contained"
            onClick={() => setIsEditing(true)}
            style={{ marginLeft: '16px' }}
          >
            {isKeySet ? 'Update' : 'Add'} {label}
          </Button>
        )}
      </Box>
    )}
  </Field>
);

const TabPassword = () => {
  const [initialValues] = useState({ user_key: '', firm_key: '' });
  const [isUserKeySet, setIsUserKeySet] = useState(false);
  const [isFirmKeySet, setIsFirmKeySet] = useState(false);
  const { user } = useUser();
  // Assume you have a way to get the current user's ID
  const userId = user.id; // Replace with actual user ID retrieval logic
  const [isUserKeyEditing, setIsUserKeyEditing] = useState(false);
  const [isFirmKeyEditing, setIsFirmKeyEditing] = useState(false);
  const [isUserKeyTyped, setIsUserKeyTyped] = useState(false);
  const [isFirmKeyTyped, setIsFirmKeyTyped] = useState(false);

  useEffect(() => {
    const getKeyStatus = async () => {
      if (!userId) {
        return; // Wait until userId is available
      }
      try {
        const { user_key, firm_key } = await fetchKeyStatus(userId);
        console.log("user_id  ", userId);

        setIsUserKeySet(user_key);
        console.log("user_key", user_key);
        setIsFirmKeySet(firm_key);
        console.log("firm_key", firm_key);
      } catch (error) {
        console.error('Error fetching key status:', error);
      }
    };

    getKeyStatus();
  }, [userId]); // Add userId as a dependency

  return (
    <MainCard title="Manage DDX API Keys">
      <Formik
        initialValues={initialValues}
        enableReinitialize
        onSubmit={() => {}}  // Empty handler since we handle submission in KeyField
      >
        {({ values, handleChange, handleSubmit }) => (
          <Form onSubmit={handleSubmit}>
            <Box mb={3}>
              <KeyField
                name="user_key"
                label="User Key"
                isEditing={isUserKeyEditing}
                isKeySet={isUserKeySet}
                isKeyTyped={isUserKeyTyped}
                setIsEditing={setIsUserKeyEditing}
                setIsKeySet={setIsUserKeySet}
                setIsKeyTyped={setIsUserKeyTyped}
                handleChange={handleChange}
                handleSubmit={handleSubmit}
                userId={userId}
              />
            </Box>
            <Box mb={3}>
              <KeyField
                name="firm_key"
                label="Firm Key"
                isEditing={isFirmKeyEditing}
                isKeySet={isFirmKeySet}
                isKeyTyped={isFirmKeyTyped}
                setIsEditing={setIsFirmKeyEditing}
                setIsKeySet={setIsFirmKeySet}
                setIsKeyTyped={setIsFirmKeyTyped}
                handleChange={handleChange}
                handleSubmit={handleSubmit}
                userId={userId}
              />
            </Box>
          </Form>
        )}
      </Formik>
    </MainCard>
  );
};

export default TabPassword;
