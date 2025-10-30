import React from "react";
import { Box, Typography, Grid, Paper, IconButton } from "@mui/material";
import { styled } from "@mui/system";
import { FaPlug, FaFilePdf, FaCloud, FaBuilding } from "react-icons/fa";
import CloseIcon from "@mui/icons-material/Close";

const Container = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  border: "1px solid #ccc",
  borderRadius: "8px",
  display: "flex",
  alignItems: "center",
  position: "relative",
}));

const Icon = styled("div")(({ theme }) => ({
  marginRight: theme.spacing(1),
}));

const Item = styled(Box)(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  marginRight: theme.spacing(2),
}));

const DocumentCardHorizontal = ({
  total_energy,
  use_type_total_area,
  climate_zone,
  file_name,
  showCloseIcon = false,
}: {
  total_energy: number;
  use_type_total_area: number;
  climate_zone: string;
  file_name: string;
  showCloseIcon?: boolean;
}) => {
  const energyPerArea = (total_energy * 1000) / use_type_total_area;
  const formattedEnergyPerArea = energyPerArea
    ? energyPerArea.toLocaleString(undefined, {
        minimumFractionDigits: 1,
        maximumFractionDigits: 1,
      })
    : "";

  const formattedUseTypeTotalArea = use_type_total_area
    ? use_type_total_area.toLocaleString(undefined, {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      })
    : "";

  return (
    <Container>
      {showCloseIcon && (
        <IconButton
          style={{
            position: "absolute",
            top: 0,
            right: 0,
          }}
          onClick={() => {
            // Handle close icon click event here
          }}
        >
          <CloseIcon />
        </IconButton>
      )}
      <Grid container component="div">
        <Grid item xs={6} sm={4} component={Item}>
          <Icon>
            <FaFilePdf size={24} />
          </Icon>
          <Typography variant="h6" style={{ fontWeight: "bold" }}>
            {file_name}
          </Typography>
        </Grid>
        <Grid item xs={6} sm={3} component={Item}>
          <Icon>
            <FaPlug size={24} />
          </Icon>
          <Typography variant="h6">{formattedEnergyPerArea} kBtu/SF</Typography>
        </Grid>
        <Grid item xs={6} sm={2} component={Item}>
          <Icon>
            <FaCloud size={24} />
          </Icon>
          <Typography variant="h6">{climate_zone}</Typography>
        </Grid>
        <Grid item xs={6} sm={2} component={Item}>
          <Icon>
            <FaBuilding size={24} />
          </Icon>
          <Typography variant="h6">{formattedUseTypeTotalArea} sfss</Typography>
        </Grid>
      </Grid>
    </Container>
  );
};

export default DocumentCardHorizontal;
