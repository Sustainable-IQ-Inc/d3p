// material-ui
import { Grid, Stack, Typography, IconButton, Tooltip } from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';

// project imports
import MainCard from 'components/MainCard';
import { GenericCardProps } from 'types/root';

// ==============================|| REPORT CARD ||============================== //

interface ReportCardProps extends GenericCardProps {
  showInfoIcon?: boolean;
  infoTooltip?: string;
}

const ReportCard = ({ primary, secondary, iconPrimary, color, showInfoIcon, infoTooltip }: ReportCardProps) => {
  const IconPrimary = iconPrimary!;
  const primaryIcon = iconPrimary ? <IconPrimary fontSize="large" /> : null;

  return (
    <MainCard>
      <Grid container justifyContent="space-between" alignItems="center">
        <Grid item>
          <Stack spacing={1}>
            <Typography variant="h4">{primary}</Typography>
            <Stack direction="row" alignItems="center" spacing={1}>
              <Typography variant="body1" color="secondary">
                {secondary}
              </Typography>
              {showInfoIcon && infoTooltip && (
                <Tooltip title={infoTooltip} placement="top">
                  <IconButton size="small" sx={{ p: 0.5 }}>
                    <InfoIcon fontSize="small" color="action" />
                  </IconButton>
                </Tooltip>
              )}
            </Stack>
          </Stack>
        </Grid>
        <Grid item>
          <Typography variant="h2" style={{ color }}>
            {primaryIcon}
          </Typography>
        </Grid>
      </Grid>
    </MainCard>
  );
};

export default ReportCard;
