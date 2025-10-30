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

const DocumentCard = ({
  total_energy,
  use_type_total_area,
  climate_zone,
  file_name,
  showCloseIcon = false,
  onClose,
}: {
  total_energy: number | undefined;
  use_type_total_area: number | undefined;
  climate_zone: string | undefined;
  file_name: string | undefined;
  showCloseIcon?: boolean;
  onClose?: () => void;
}) => {
  const energyPerArea =
    use_type_total_area && total_energy
      ? (total_energy * 1000) / use_type_total_area
      : 0;
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

  const formattedTotalEnergy = total_energy
    ? total_energy.toLocaleString(undefined, {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      })
    : "";

  return (
    <Container>
      {showCloseIcon && ( // Add this block
        <IconButton
          style={{
            position: "absolute",
            top: 0,
            right: 0,
          }}
          onClick={onClose}
        >
          <CloseIcon />
        </IconButton>
      )}
      <Grid container>
        <Grid item xs={12} component={Item}>
          <Icon>
            <FaFilePdf size={24} />
          </Icon>
          <Typography variant="h5" style={{ fontWeight: "bold" }}>
            {file_name}
          </Typography>
        </Grid>
        <Grid item xs={6} sm={6} component={Item}>
          <Icon>
            <FaPlug size={24} />
          </Icon>
          <Typography variant="h6">{formattedEnergyPerArea} kBtu/SF</Typography>
        </Grid>
        <Grid item xs={6} sm={6} component={Item}>
          <Icon>
            <FaCloud size={24} />
          </Icon>
          <Typography variant="h6">{climate_zone}</Typography>
        </Grid>
        <Grid item xs={6} sm={6} component={Item}>
          <Icon>
            <FaPlug size={24} />
          </Icon>
          <Typography variant="h6">{formattedTotalEnergy} MBTU</Typography>
        </Grid>
        <Grid item xs={6} sm={6} component={Item}>
          <Icon>
            <FaBuilding size={24} />
          </Icon>
          <Typography variant="h6">{formattedUseTypeTotalArea} sf</Typography>
        </Grid>
      </Grid>
    </Container>
  );
};

export default DocumentCard;
