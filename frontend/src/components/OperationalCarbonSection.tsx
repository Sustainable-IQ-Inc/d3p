import React, { useState } from "react";
import MainCard from "components/MainCard";
import RoundIconCard from "components/cards/statistics/RoundIconCard";
import { Tooltip, IconButton, Modal, Box, Typography, Table, TableBody, 
  TableCell, TableContainer, TableHead, TableRow, Paper, SelectChangeEvent, 
  FormControl, Select, MenuItem } from "@mui/material";
import HelpOutlineIcon from "@mui/icons-material/HelpOutline";
import InfoIcon from "@mui/icons-material/Info";
import CloseIcon from '@mui/icons-material/Close';
import {
  EmissionsFactorsProps,
  OperationalCarbonDataCombinedProps,
  OperationalEnergyDataCombinedProps,
} from "types/operational-data";

interface OperationalCarbonDataWidgetProps {
  carbonData: OperationalCarbonDataCombinedProps;
  energyData: OperationalEnergyDataCombinedProps;
  emissionsFactors: EmissionsFactorsProps;
}

const OperationalCarbonDataWidget: React.FC<
  OperationalCarbonDataWidgetProps
> = ({ carbonData, energyData, emissionsFactors }) => {
  const [modalOpen, setModalOpen] = useState(false);

  const availableOptions = [
    { value: 'design', label: 'Design', available: energyData.design.status === 'success' },
    { value: 'baseline', label: 'Baseline', available: energyData.baseline.status === 'success' },
  ].filter(option => option.available);

  const [selectedOption, setSelectedOption] = useState<'design' | 'baseline'>(
    (availableOptions[0]?.value as 'design' | 'baseline') || 'design'
  );

  const handleOpenModal = () => setModalOpen(true);
  const handleCloseModal = () => setModalOpen(false);

  const handleOptionChange = (event: SelectChangeEvent<string>) => {
    setSelectedOption(event.target.value as 'design' | 'baseline');
  };

  

  const selectedCarbonData = carbonData[selectedOption];
  const selectedEnergyData = energyData[selectedOption];

  
  const modalStyle = {
    position: 'absolute' as 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: 600,
    bgcolor: 'background.paper',
    boxShadow: 24,
    p: 4,
    maxHeight: '90vh',
    overflow: 'auto',
    borderRadius: '8px',
  };


  return (
    <MainCard 
      title={
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
          <Typography variant="h6" style={{ fontWeight: 'bold' }}>Operational Carbon</Typography>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            {availableOptions.length > 1 ? (
              <FormControl variant="outlined" size="small" style={{ minWidth: 120, marginRight: '10px' }}>
                <Select
                  value={selectedOption}
                  onChange={handleOptionChange}
                >
                  {availableOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            ) : (
              <Typography variant="body2" style={{ marginRight: '10px' }}>
                {availableOptions[0]?.label || 'No options available'}
              </Typography>
            )}
            {energyData.baseline.status !== 'success' && (
              <Tooltip
                title="This project does not have a baseline file to compare to"
                style={{ marginRight: '6px' }}
              >
                <HelpOutlineIcon fontSize="small" />
              </Tooltip>
            )}
            <IconButton onClick={handleOpenModal} size="small">
              <InfoIcon />
            </IconButton>
          </div>
        </div>
      }
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          border: "0px solid #ccc",
          width: "100%",
          margin: "auto",
        }}
      >
        <div style={{ width: "66%", marginRight: "5%" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th></th>
                <th>Electricity</th>
                <th>Fossil Fuels</th>
                <th style={{ minWidth: "75px" }}></th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Building Energy</td>
                <td style={{ textAlign: "center" }}>
                  {Number(selectedCarbonData.building_electricity).toLocaleString(
                    "en-US",
                    {
                      minimumFractionDigits: 0,
                      maximumFractionDigits: 0,
                    }
                  )}
                </td>
                <td style={{ textAlign: "center" }}>
                  {Number(
                    Number(selectedCarbonData.building_natural_gas) +
                    Number(selectedCarbonData.district_heating_fossil_fuels) +
                    Number(selectedCarbonData.building_fuel_other)
                  ).toLocaleString("en-US", {
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 0,
                  })}
                </td>
                <td>MT CO2e</td>
              </tr>
              <tr>
                <td>On-site renewables</td>
                <td style={{ textAlign: "center" }}>
                  {Number(selectedCarbonData.avoided_emissions).toLocaleString(
                    "en-US",
                    {
                      minimumFractionDigits: 0,
                      maximumFractionDigits: 0,
                    }
                  )}
                </td>
                <td style={{ textAlign: "center" }}>0</td>
                <td>MT CO2e</td>
              </tr>
              <tr>
                <td>Off-site renewables</td>
                <td style={{ textAlign: "center" }}>0</td>
                <td style={{ textAlign: "center" }}>0</td>
                <td>MT CO2e</td>
              </tr>
              <tr>
                <td style={{ borderTop: "1px solid #ccc" }}>Net sub-total</td>
                <td
                  style={{ borderTop: "1px solid #ccc", textAlign: "center" }}
                >
                  {Number(
                    Number(selectedCarbonData.building_electricity) -
                    Number(selectedCarbonData.avoided_emissions)
                  ).toLocaleString("en-US", {
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 0,
                  })}
                </td>
                <td
                  style={{ borderTop: "1px solid #ccc", textAlign: "center" }}
                >
                  {Number(
                    Number(selectedCarbonData.building_natural_gas) +
                    Number(selectedCarbonData.district_heating_fossil_fuels) +
                    Number(selectedCarbonData.building_fuel_other)
                  ).toLocaleString("en-US", {
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 0,
                  })}
                </td>
                <td>MT CO2e</td>
              </tr>
              <tr></tr>
              <tr>
                <td style={{ borderTop: "1px solid #ccc" }}>
                  Net Operational Carbon Total
                </td>
                <td
                  colSpan={2}
                  style={{ borderTop: "1px solid #ccc" }}
                  align="center"
                >
                  {Number(selectedCarbonData.net_operational_carbon).toLocaleString(
                    "en-US",
                    {
                      minimumFractionDigits: 0,
                      maximumFractionDigits: 0,
                    }
                  )}
                </td>
                <td>MT CO2e</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div
          style={{
            width: "33%",
            textAlign: "center",
            marginTop: "20px",
            fontSize: "20px",
          }}
        >
          <div style={{ position: "relative" }}>
            <RoundIconCard
              primary={
                selectedOption === 'design' && !isNaN(Number(selectedCarbonData.pct_savings))
                  ? (Number(selectedCarbonData.pct_savings) * 100).toFixed(1) + "%"
                  : "--"
              }
              secondary="% Oper. Carbon Savings"
              color="primary.main"
              bgcolor="primary.lighter"
            />
            {selectedOption === 'design' && isNaN(Number(selectedCarbonData.pct_savings)) && (
              <Tooltip
                title="This project does not have a baseline file to compare to"
                style={{ position: "absolute", top: 5, right: 5 }}
              >
                <HelpOutlineIcon />
              </Tooltip>
            )}
          </div>
          <RoundIconCard
            primary={Number(selectedCarbonData.net_operational_carbon_intensity).toFixed(2)}
            secondary="kgCO2e/m2 Oper. Carbon Intensity"
            color="primary.main"
            bgcolor="primary.lighter"
          />
        </div>
      </div>

      <Modal
        open={modalOpen}
        onClose={handleCloseModal}
        aria-labelledby="modal-modal-title"
        aria-describedby="modal-modal-description"
      >
        <Box sx={modalStyle}>
          <IconButton
            aria-label="close"
            onClick={handleCloseModal}
            sx={{
              position: 'absolute',
              right: 8,
              top: 8,
              color: (theme) => theme.palette.grey[500],
            }}
          >
            <CloseIcon />
          </IconButton>
          <Typography 
            id="modal-modal-title" 
            variant="h6" 
            component="h2" 
            gutterBottom 
            sx={{ fontWeight: 'bold' }}
          >
            Calculation Formulas and Values
          </Typography>
          <TableContainer component={Paper}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Metric</TableCell>
                  <TableCell>Formula</TableCell>
                  <TableCell>Values</TableCell>
                  <TableCell>Result</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                <TableRow>
                  <TableCell>Building Energy (Electricity)</TableCell>
                  <TableCell>Electricity Usage (Mbtu) * Electricity Emissions Factor</TableCell>
                  <TableCell>{`${Number(selectedEnergyData.building_electricity).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} * ${Number(emissionsFactors.electricity).toLocaleString(undefined, {minimumFractionDigits: 1, maximumFractionDigits: 1})}`}</TableCell>
                  <TableCell>{Number(selectedCarbonData.building_electricity).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} MT CO2e</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Building Energy (Natural Gas)</TableCell>
                  <TableCell>Natural Gas Usage (Mbtu) * Natural Gas Emissions Factor</TableCell>
                  <TableCell>{`${Number(selectedEnergyData.building_natural_gas).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} * ${Number(emissionsFactors.natural_gas).toLocaleString(undefined, {minimumFractionDigits: 1, maximumFractionDigits: 1})}`}</TableCell>
                  <TableCell>{Number(selectedCarbonData.building_natural_gas).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} MT CO2e</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Building Energy (District Heating)</TableCell>
                  <TableCell>District Heating Usage (Mbtu) * District Heating Emissions Factor</TableCell>
                  <TableCell>{`${Number(selectedEnergyData.district_heating_fossil_fuels).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} * ${Number(emissionsFactors.district_heating_fossil_fuels).toLocaleString(undefined, {minimumFractionDigits: 1, maximumFractionDigits: 1})}`}</TableCell>
                  <TableCell>{Number(selectedCarbonData.district_heating_fossil_fuels).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} MT CO2e</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Building Energy (Other)</TableCell>
                  <TableCell>District Heating Usage (Mbtu) * District Heating Emissions Factor</TableCell>
                  <TableCell>{`${Number(selectedEnergyData.building_fuel_other).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} * ${Number(emissionsFactors.building_fuel_other).toLocaleString(undefined, {minimumFractionDigits: 1, maximumFractionDigits: 1})}`}</TableCell>
                  <TableCell>{Number(selectedCarbonData.building_fuel_other).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} MT CO2e</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>On-site renewables</TableCell>
                  <TableCell>Renewable Energy Generated (Mbtu) * Avoided Emissions Factor</TableCell>
                  <TableCell>{`${Number(selectedEnergyData.avoided_emissions).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} * ${Number(emissionsFactors.avoided_emissions).toLocaleString(undefined, {minimumFractionDigits: 1, maximumFractionDigits: 1})}`}</TableCell>
                  <TableCell>{Number(selectedEnergyData.avoided_emissions).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} MT CO2e</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Net Operational Carbon Total</TableCell>
                  <TableCell>Sum of all energy sources minus renewable offsets</TableCell>
                  <TableCell>{`${Number(selectedCarbonData.building_electricity).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} + ${Number(selectedCarbonData.building_natural_gas).toLocaleString(undefined, {minimumFractionDigits: 1, maximumFractionDigits: 1})} + ${Number(selectedCarbonData.district_heating_fossil_fuels).toLocaleString(undefined, {minimumFractionDigits: 1, maximumFractionDigits: 1})} + ${Number(selectedCarbonData.building_fuel_other).toLocaleString(undefined, {minimumFractionDigits: 1, maximumFractionDigits: 1})} - ${Number(selectedCarbonData.avoided_emissions).toLocaleString(undefined, {minimumFractionDigits: 1, maximumFractionDigits: 1})}`}</TableCell>    
                  <TableCell>{Number(selectedCarbonData.net_operational_carbon).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} MT CO2e</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Operational Carbon Intensity</TableCell>
                  <TableCell>Net Operational Carbon Total / Building Area (m²)</TableCell>
                  <TableCell>{`${Number(selectedCarbonData.net_operational_carbon).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} / ${(Number(selectedEnergyData.use_type_total_area) * 0.092903).toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 0})}`}</TableCell>
                  <TableCell>{Number(selectedCarbonData.net_operational_carbon_intensity).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} kgCO2e/m²</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      </Modal>
    </MainCard>
  );
};

export default OperationalCarbonDataWidget;