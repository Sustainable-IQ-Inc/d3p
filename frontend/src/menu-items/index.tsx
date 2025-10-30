// project import
import projectUpload from "./project-upload";
import dashboard from "./dashboard";
import dataAnalytics from "./data-analytics";
import admin from "./admin";
import settings from "./settings";
// types
import { NavItemType } from "types/menu";

// ==============================|| MENU ITEMS ||============================== //

const menuItems: { items: NavItemType[] } = {
  items: [dashboard, projectUpload, dataAnalytics,settings, admin],
};

export default menuItems;
