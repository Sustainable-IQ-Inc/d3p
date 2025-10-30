import { CardContent, Grid, Typography } from "@mui/material";
import MainCard from "components/MainCard";

const FeedsCard = ({
  avg_eui,
  conditioned_area,
  total_energy_annual,
  climate_zone,
}: {
  avg_eui: number;
  conditioned_area: number;
  total_energy_annual: number;
  climate_zone: string;
}) => (
  <MainCard title="Key Metrics" content={false}>
    <CardContent>
      <Grid container spacing={1}>
        <Grid item xs={4}>
          <Typography align="left" variant="body2">
            Metric
          </Typography>
        </Grid>
        <Grid item xs={4}>
          <Typography align="left" variant="body2">
            Baseline
          </Typography>
        </Grid>
        <Grid item xs={4}>
          <Typography align="left" variant="body2">
            Design
          </Typography>
        </Grid>

        <Grid item xs={4}>
          <Typography align="left" variant="body2">
            Average EEU
          </Typography>
        </Grid>

        <Grid item xs={4}>
          <Typography align="left" variant="caption" color="secondary">
            {avg_eui
              ? Number(avg_eui).toLocaleString("en-US", {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })
              : "-- "}
          </Typography>
        </Grid>
        <Grid item xs={4}>
          <Typography align="left" variant="caption" color="secondary">
            kbtu/sf
          </Typography>
        </Grid>

        <Grid item xs={4}>
          <Typography align="left" variant="body2">
            Conditioned Area
          </Typography>
        </Grid>

        <Grid item xs={4}>
          <Typography align="left" variant="caption" color="secondary">
            {conditioned_area
              ? Number(conditioned_area).toLocaleString("en-US", {
                  minimumFractionDigits: 0,
                  maximumFractionDigits: 0,
                })
              : "-- "}
          </Typography>
        </Grid>
        <Grid item xs={4}>
          <Typography align="left" variant="caption" color="secondary">
            sf
          </Typography>
        </Grid>

        <Grid item xs={4}>
          <Typography align="left" variant="body2">
            Total Annual Energy Usage
          </Typography>
        </Grid>
        <Grid item xs={4}>
          <Typography align="left" variant="caption" color="secondary">
            {total_energy_annual
              ? Number(total_energy_annual).toLocaleString("en-US", {
                  minimumFractionDigits: 0,
                  maximumFractionDigits: 0,
                })
              : "-- "}
          </Typography>
        </Grid>
        <Grid item xs={4}>
          <Typography align="left" variant="caption" color="secondary">
            MBTU
          </Typography>
        </Grid>

        <Grid item xs={4}>
          <Typography align="left" variant="body2">
            Climate Zone
          </Typography>
        </Grid>
        <Grid item xs={4}>
          <Typography align="left" variant="caption" color="secondary">
            {climate_zone ? climate_zone : "--"}
          </Typography>
        </Grid>
        <Grid item xs={4}>
          <Typography
            align="left"
            variant="caption"
            color="secondary"
          ></Typography>
        </Grid>
      </Grid>
    </CardContent>
  </MainCard>
);

export default FeedsCard;
