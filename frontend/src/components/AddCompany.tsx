"use client";

import { SetStateAction, useState } from "react";

// material-ui
import {
  Button,
  Divider,
  CardContent,
  Modal,
  Stack,
  TextField,
} from "@mui/material";

import createCompany from "app/api/CreateCompany";

// project import
import MainCard from "components/MainCard";

// ==============================|| MODAL - BASIC ||============================== //

export default function BasicModal({
  onCompanyCreated,
}: {
  onCompanyCreated: any;
}) {
  const [open, setOpen] = useState(false);
  const [companyName, setCompanyName] = useState("");

  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  const handleInputChange = (event: {
    target: { value: SetStateAction<string> };
  }) => {
    setCompanyName(event.target.value);
  };

  const handleSubmit = async () => {
    const response = await createCompany({
      companyProps: { company_name: companyName },
    });
    if (response === "success") {
      handleClose();
      onCompanyCreated();
      setCompanyName("");
    }
  };

  return (
    <div>
      <Button variant="contained" onClick={handleOpen}>
        Add Company
      </Button>
      <Modal
        open={open}
        onClose={handleClose}
        aria-labelledby="modal-modal-title"
        aria-describedby="modal-modal-description"
      >
        <MainCard title="Add Company" modal darkTitle content={false}>
          <CardContent>
            <TextField
              id="company-name"
              label="Company Name"
              placeholder="Company Name"
              value={companyName}
              onChange={handleInputChange}
              sx={{ width: "300px" }}
            />{" "}
          </CardContent>
          <Divider />
          <Stack
            direction="row"
            spacing={1}
            justifyContent="flex-end"
            sx={{ px: 2.5, py: 2 }}
          >
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
