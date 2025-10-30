// material-ui
import { Grid, Stack, Typography } from "@mui/material";

// project imports
import MainCard from "components/MainCard";
import { GenericCardProps } from "types/root";

// ============================|| ROUND ICON CARD ||============================ //

interface Props {
  primary: string;
  secondary: string;
  content?: string;
  iconPrimary?: GenericCardProps["iconPrimary"];
  color: string;
  bgcolor: string;
}

const RoundIconCard = ({
  primary,
  secondary,
  content,
  iconPrimary,
  color,
  bgcolor,
}: Props) => {
  return (
    <MainCard>
      <Grid
        item
        container
        alignItems="center"
        spacing={0}
        justifyContent="center"
      >
        <Stack spacing={1}>
          <Typography variant="h4" color="inherit">
            {primary}
          </Typography>
          <Typography variant="h6">{secondary}</Typography>
        </Stack>
      </Grid>
    </MainCard>
  );
};

export default RoundIconCard;
