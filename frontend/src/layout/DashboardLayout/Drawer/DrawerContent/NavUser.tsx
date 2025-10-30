import { useState, MouseEvent } from "react";

// next
import Link from "next/link";
//import { useSession, signOut } from 'next-auth/react';

// material-ui
import { styled, useTheme, Theme } from "@mui/material/styles";
import {
  Box,
  IconButton,
  IconButtonProps,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Menu,
  MenuItem,
} from "@mui/material";

// project import
import Avatar from "components/@extended/Avatar";
import useUser from "hooks/useUser";
import { useGetMenuMaster } from "api/menu";

// assets
import { RightOutlined } from "@ant-design/icons";

interface ExpandMoreProps extends IconButtonProps {
  theme: Theme;
  expand: boolean;
  drawerOpen: boolean;
}

const ExpandMore = styled(IconButton, {
  shouldForwardProp: (prop) =>
    prop !== "theme" && prop !== "expand" && prop !== "drawerOpen",
})(({ theme, expand, drawerOpen }: ExpandMoreProps) => ({
  transform: !expand ? "rotate(0deg)" : "rotate(-90deg)",
  marginLeft: "auto",
  color: theme.palette.secondary.dark,
  transition: theme.transitions.create("transform", {
    duration: theme.transitions.duration.shortest,
  }),
  ...(!drawerOpen && {
    opacity: 0,
    width: 50,
    height: 50,
  }),
}));

// ==============================|| LIST - USER ||============================== //

const NavUser = () => {
  const theme = useTheme();

  const { menuMaster } = useGetMenuMaster();
  const drawerOpen = menuMaster.isDashboardDrawerOpened;

  const { user } = useUser();
  //const { data: session } = useSession();
  //const provider = session?.provider;

  const handleLogout = () => {
    return null;
  };

  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

  const handleClick = (event: MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };

  return (
    <Box
      sx={{
        p: 1.25,
        px: !drawerOpen ? 1.25 : 3,
        borderTop: `2px solid ${theme.palette.divider}`,
      }}
    >
      <List disablePadding>
        <ListItem
          disablePadding
          secondaryAction={
            <ExpandMore
              theme={theme}
              expand={open}
              drawerOpen={drawerOpen}
              id="basic-button"
              aria-controls={open ? "basic-menu" : undefined}
              aria-haspopup="true"
              aria-expanded={open ? "true" : undefined}
              onClick={handleClick}
              aria-label="show more"
            >
              <RightOutlined style={{ fontSize: "0.625rem" }} />
            </ExpandMore>
          }
          sx={{
            "& .MuiListItemSecondaryAction-root": {
              right: !drawerOpen ? -20 : -16,
            },
          }}
        >
          <ListItemAvatar>
            {user && (
              <Avatar
                alt="Avatar"
                src={user.avatar}
                sx={{ ...(drawerOpen && { width: 46, height: 46 }) }}
              />
            )}
          </ListItemAvatar>
          {user && (
            <ListItemText primary={user.name} secondary="UI/UX Designer" />
          )}
        </ListItem>
      </List>
      <Menu
        id="basic-menu"
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        MenuListProps={{
          "aria-labelledby": "basic-button",
        }}
        anchorOrigin={{
          vertical: "top",
          horizontal: "right",
        }}
        transformOrigin={{
          vertical: "bottom",
          horizontal: "right",
        }}
      >
        <MenuItem onClick={handleLogout}>Logout</MenuItem>
        <MenuItem component={Link} href="#" onClick={handleClose}>
          Profile
        </MenuItem>
        <MenuItem component={Link} href="#" onClick={handleClose}>
          My account
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default NavUser;
