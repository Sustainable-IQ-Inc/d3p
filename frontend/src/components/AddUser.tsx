'use client';

import { SetStateAction, useState, useEffect, useRef } from 'react';

// material-ui
import { Button, Divider, CardContent, Modal, Stack, TextField, FormHelperText } from '@mui/material';

import inviteUser  from 'app/api/InviteUser';

// project import
import MainCard from 'components/MainCard';

// ==============================|| MODAL - BASIC ||============================== //

interface BasicModalProps {
  onInviteUser: () => void;
  companyId: string;
}


export default function BasicModal({ onInviteUser, companyId }: BasicModalProps) {
  const [open, setOpen] = useState(false);
  const [emailAddress, setEmailAddress] = useState('');
  const [error, setError] = useState('');
  const handleOpen = () => setOpen(true);
  const handleClose = () => {
    setOpen(false);
    setEmailAddress(''); // Clear email address
    setError(''); // Clear error
  };

  const emailRef = useRef(emailAddress);

  useEffect(() => {
    emailRef.current = emailAddress;
  }, [emailAddress]);

  const handleInputChange = (event: { target: { value: SetStateAction<string>; }; }) => {
    setEmailAddress(event.target.value);
  };

  const handleSubmit = async () => {
    const response = await inviteUser({ inviteProps: { user_email: emailRef.current, company_id: companyId } });

    if (response === 'success') {
      handleClose();
      onInviteUser();
      setEmailAddress('');
      setError('');
    } else {
      setError(response);
    }
  };

  const handleKeyDown = (event: KeyboardEvent) => {
    if (event.key === 'Enter') {
      event.preventDefault(); // Prevent default form submission
      handleSubmit();
    }
  };

  // Add event listener when the modal opens and remove it when it closes
  useEffect(() => {
    if (open) {
      window.addEventListener('keydown', handleKeyDown);
    } else {
      window.removeEventListener('keydown', handleKeyDown);
    }

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [open]);

  return (
    <div>
      <Button variant="contained" onClick={handleOpen}>
        Invite User
      </Button>
      <Modal open={open} onClose={handleClose} aria-labelledby="modal-modal-title" aria-describedby="modal-modal-description">
        <MainCard title="Invite User" modal darkTitle content={false}>
          <CardContent>
            <TextField 
              id="email-address" 
              label="Email Address" 
              placeholder="Email Address" 
              value={emailAddress} 
              onChange={handleInputChange} 
              sx={{ width: '300px' }} 
              error={!!error} // Highlight the text field if there's an error
            />
            {error && <FormHelperText error>{error}</FormHelperText>} 
          </CardContent>
          <Divider />
          <Stack direction="row" spacing={1} justifyContent="flex-end" sx={{ px: 2.5, py: 2 }}>
            <Button color="error" size="small" onClick={handleClose}>
              Cancel
            </Button>
            <Button variant="contained" size="small" onClick={handleSubmit}>
              Submit
            </Button>
          </Stack>
        </MainCard>
      </Modal>
    </div>
  );
}