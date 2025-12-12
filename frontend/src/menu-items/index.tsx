// project import
import projectUpload from "./project-upload";
import dashboard from "./dashboard";
import dataAnalytics from "./data-analytics";
import admin from "./admin";
import settings from "./settings";
import pendingUploads from "./pending-uploads";
// types
import { NavItemType } from "types/menu";

// ==============================|| MENU ITEMS ||============================== //

const menuItems: { items: NavItemType[] } = {
  items: [dashboard, projectUpload, pendingUploads, dataAnalytics,settings, admin],
};

export default menuItems;
