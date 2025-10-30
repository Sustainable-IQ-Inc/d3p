import { useRef, useState, ReactNode, SyntheticEvent } from "react";

// next
import { useRouter } from "next/navigation";
import styled from "styled-components";
//import { useSession, signOut } from 'next-auth/react';

//supabase
import useSupabase from "hooks/useSupabase";

// material-ui
import { useTheme } from "@mui/material/styles";
import {
  Box,
  ButtonBase,
  CardContent,
  ClickAwayListener,
  Grid,
  Paper,
  Popper,
  Stack,
  Tab,
  Tabs,
  Tooltip,
  Typography,
} from "@mui/material";

// project import
import ProfileTab from "./ProfileTab";
import MainCard from "components/MainCard";
import Transitions from "components/@extended/Transitions";
import IconButton from "components/@extended/IconButton";
import useUser from "hooks/useUser";

// types
import { ThemeMode } from "types/config";

// assets
import {
  LogoutOutlined,
  SettingOutlined,
} from "@ant-design/icons";
import { AppRouterInstance } from "next/dist/shared/lib/app-router-context.shared-runtime";

// types
interface TabPanelProps {
  children?: ReactNode;
  dir?: string;
  index: number;
  value: number;
}

// tab panel wrapper
function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`profile-tabpanel-${index}`}
      aria-labelledby={`profile-tab-${index}`}
      {...other}
    >
      {value === index && children}
    </div>
  );
}

const AvatarInitials = styled.div`
  background-color: green;
  color: white;
  width: 30px;
  height: 30px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 50%;
  font-size: 14px;
  font-weight: bold;
`;

function a11yProps(index: number) {
  return {
    id: `profile-tab-${index}`,
    "aria-controls": `profile-tabpanel-${index}`,
  };
}

// ==============================|| HEADER CONTENT - PROFILE ||============================== //

const Profile = () => {
  const theme = useTheme();
  const { user } = useUser();
  //const { data: session } = useSession();
  //const provider = session?.provider;
  const router = useRouter();
  const supabase = useSupabase();

  const logout = async (router: AppRouterInstance, supabase: any) => {
    // Perform the logout process here
    const { error } = await supabase.auth.signOut();
    if (error) {
      console.error("Error logging out:", error);
    } else {
      // Add a delay before redirecting to the login page
      localStorage.removeItem("supabase.auth.token");
      router.push("/login");
    }
  };

  const handleLogout = () => {
    logout(router, supabase);
  };

  const anchorRef = useRef<any>(null);
  const [open, setOpen] = useState(false);
  const handleToggle = () => {
    setOpen((prevOpen) => !prevOpen);
  };

  const handleClose = (event: MouseEvent | TouchEvent) => {
    if (anchorRef.current && anchorRef.current.contains(event.target)) {
      return;
    }
    setOpen(false);
  };

  const [value, setValue] = useState(0);

  const handleChange = (event: SyntheticEvent, newValue: number) => {
    setValue(newValue);
  };

  const iconBackColorOpen =
    theme.palette.mode === ThemeMode.DARK ? "background.default" : "grey.100";
  const initials = user.name
    .split(" ")
    .slice(0, 2)
    .map((namePart) => namePart[0])
    .join("")
    .toUpperCase();

  return (
    <Box sx={{ flexShrink: 0, ml: 0.75 }}>
      <ButtonBase
        sx={{
          p: 0.25,
          bgcolor: open ? iconBackColorOpen : "transparent",
          borderRadius: 1,
          "&:hover": {
            bgcolor:
              theme.palette.mode === ThemeMode.DARK
                ? "secondary.light"
                : "secondary.lighter",
          },
          "&:focus-visible": {
            outline: `2px solid ${theme.palette.secondary.dark}`,
            outlineOffset: 2,
          },
        }}
        aria-label="open profile"
        ref={anchorRef}
        aria-controls={open ? "profile-grow" : undefined}
        aria-haspopup="true"
        onClick={handleToggle}
      >
        {user && (
          <Stack
            direction="row"
            spacing={1.25}
            alignItems="center"
            sx={{ p: 0.5 }}
          >
            <AvatarInitials>{initials}</AvatarInitials>
          </Stack>
        )}
      </ButtonBase>
      <Popper
        placement="bottom-end"
        open={open}
        anchorEl={anchorRef.current}
        role={undefined}
        transition
        disablePortal
        popperOptions={{
          modifiers: [
            {
              name: "offset",
              options: {
                offset: [0, 9],
              },
            },
          ],
        }}
      >
        {({ TransitionProps }) => (
          <Transitions type="fade" in={open} {...TransitionProps}>
            <Paper
              sx={{
                boxShadow: theme.customShadows.z1,
                width: 290,
                minWidth: 320,
                maxWidth: 500,
                [theme.breakpoints.down("md")]: {
                  maxWidth: 250,
                },
              }}
            >
              <ClickAwayListener onClickAway={handleClose}>
                <MainCard elevation={0} border={false} content={false}>
                  <CardContent sx={{ px: 2.5, pt: 3 }}>
                    <Grid
                      container
                      justifyContent="space-between"
                      alignItems="center"
                    >
                      <Grid item>
                        {user && (
                          <Stack
                            direction="row"
                            spacing={1.25}
                            alignItems="center"
                          >
                            <AvatarInitials>{initials}</AvatarInitials>
                            <Stack>
                              <Typography variant="h6">{user.name}</Typography>
                              <Typography variant="body2" color="textSecondary">
                                {user.company}
                              </Typography>
                            </Stack>
                          </Stack>
                        )}
                      </Grid>
                      <Grid item>
                        <Tooltip title="Logout">
                          <IconButton
                            size="large"
                            sx={{ color: "text.primary" }}
                            onClick={handleLogout}
                          >
                            <LogoutOutlined />
                          </IconButton>
                        </Tooltip>
                      </Grid>
                    </Grid>
                  </CardContent>
                  {open && (
                    <>
                      <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
                        <Tabs
                          variant="fullWidth"
                          value={value}
                          onChange={handleChange}
                          aria-label="profile tabs"
                        >
                          <Tab
                            sx={{
                              display: "flex",
                              flexDirection: "row",
                              justifyContent: "center",
                              alignItems: "center",
                              textTransform: "capitalize",
                            }}
                            icon={
                              <SettingOutlined
                                style={{ marginBottom: 0, marginRight: "10px" }}
                              />
                            }
                            label="Settings"
                            {...a11yProps(0)}
                          />
                          
                        </Tabs>
                      </Box>
                      <TabPanel value={value} index={0} dir={theme.direction}>
                        <ProfileTab handleLogout={handleLogout} />
                      </TabPanel>

                    </>
                  )}
                </MainCard>
              </ClickAwayListener>
            </Paper>
          </Transitions>
        )}
      </Popper>
    </Box>
  );
};

export default Profile;
