import React, { useState } from "react";
import MainCard from "components/MainCard";
import RoundIconCard from "components/cards/statistics/RoundIconCard";
import { Tooltip, SelectChangeEvent, FormControl,Select,MenuItem,Typography } from "@mui/material";
import HelpOutlineIcon from "@mui/icons-material/HelpOutline";
import {

  OperationalEnergyDataCombinedProps,
} from "types/operational-data";

interface OperationalEnergyTableProps {
  data: OperationalEnergyDataCombinedProps;
}

const OperationalEnergyTable: React.FC<OperationalEnergyTableProps> = ({
  data,
}) => {
  
  const availableOptions = [
    { value: 'design', label: 'Design', available: data.design.status === 'success' },
    { value: 'baseline', label: 'Baseline', available: data.baseline.status === 'success' },
  ].filter(option => option.available);

  const [selectedOption, setSelectedOption] = useState<'design' | 'baseline'>(
    (availableOptions[0]?.value as 'design' | 'baseline') || 'design'
  );

  const handleOptionChange = (event: SelectChangeEvent<string>) => {
    setSelectedOption(event.target.value as 'design' | 'baseline');
  };

  const selectedEnergyData = data[selectedOption];
  const hasDesign = data.design.status === "success";
  const hasBaseline = data.baseline.status === "success";
  const baselineNet = hasBaseline ? Number(data.baseline.building_net_energy_total) : 0;
  const designNet = hasDesign ? Number(data.design.building_net_energy_total) : 0;
  return (
    <MainCard 
      title={
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>Operational Energy</span>
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
        {(!hasBaseline || baselineNet === 0) && (
          <Tooltip
            title="This project does not have a baseline file to compare to"
            style={{ marginLeft: 4 }}
          >
            <HelpOutlineIcon fontSize="small" />
          </Tooltip>
        )}
      </div>}
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
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Building Energy</td>
                <td style={{ textAlign: "center" }}>
                  {Number(
                    Number(selectedEnergyData.building_electricity)
                  ).toLocaleString("en-US", {
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 1,
                  })}
                </td>
                <td style={{ textAlign: "center" }}>
                  {Number(
                    Number(selectedEnergyData.building_total_fossil_fuels) 
                    
                  ).toLocaleString("en-US", {
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 1,
                  })}
                </td>
                <td>MBtu/yr</td>
              </tr>
              <tr>
                <td>On-site renewables</td>
                <td style={{ textAlign: "center" }}>
                  {Number(
                    Number(selectedEnergyData.avoided_emissions) 
                  ).toLocaleString("en-US", {
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 1,
                  })}
                </td>
                <td style={{ textAlign: "center" }}>0</td>
                <td>MBtu/yr</td>
              </tr>
              <tr>
                <td>Off-site renewables</td>
                <td style={{ textAlign: "center" }}>0</td>
                <td style={{ textAlign: "center" }}>0</td>
                <td>MBtu/yr</td>
              </tr>
              <tr>
                <td style={{ borderTop: "1px solid #ccc" }}>Net sub-total</td>
                <td
                  style={{ borderTop: "1px solid #ccc", textAlign: "center" }}
                >
                  {Number(
                    Number(selectedEnergyData.building_net_electricity)
                  ).toLocaleString("en-US", {
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 1,
                  })}
                </td>
                <td
                  style={{ borderTop: "1px solid #ccc", textAlign: "center" }}
                >
                  {" "}
                  {Number(
                    Number(selectedEnergyData.building_total_fossil_fuels)
                  ).toLocaleString("en-US", {
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 1,
                  })}
                </td>
                <td>MBtu/yr</td>
              </tr>
              <tr></tr>
              <tr>
                <td style={{ borderTop: "1px solid #ccc" }}>
                  Net Operational Energy Total
                </td>
                <td
                  colSpan={2}
                  style={{ borderTop: "1px solid #ccc" }}
                  align="center"
                >
                  {Number(
                    Number(selectedEnergyData.building_net_energy_total)
                  ).toLocaleString("en-US", {
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 1,
                  })}
                </td>
                <td>MBtu/yr</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div
          style={{
            width: "30%",
            textAlign: "center",
            marginTop: "20px",
            fontSize: "20px",
          }}
        >
          <div style={{ position: "relative" }}>
            {(() => {
              const shouldShowSavings = hasDesign && hasBaseline && selectedOption !== "baseline" && baselineNet > 0;
              const primaryVal = shouldShowSavings
                ? (((baselineNet - designNet) / baselineNet) * 100).toFixed(1) + "%"
                : "--";
              return (
                <RoundIconCard
                  primary={primaryVal}
                  secondary="% Oper. Energy Savings"
                  color="primary.main"
                  bgcolor="primary.lighter"
                />
              );
            })()}
            {(!hasBaseline || baselineNet === 0) && (
              <Tooltip
                title="This project does not have a baseline file to compare to"
                style={{ position: "absolute", top: 5, right: 5 }}
              >
                <HelpOutlineIcon />
              </Tooltip>
            )}
          </div>
        </div>
      </div>
    </MainCard>
  );
};

export default OperationalEnergyTable;
