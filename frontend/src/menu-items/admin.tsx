// type
import { NavItemType } from "types/menu";

// ==============================|| MENU ITEMS - PAGES ||============================== //

const pages: NavItemType = {
  id: "admin",
  title: "Admin",
  type: "group",
  children: [
    {
      id: "companies",
      title: "Companies",
      type: "item",
      url: "/admin/companies",
    },
    {
      id: "failed-uploads",
      title: "Failed Uploads",
      type: "item",
      url: "/admin/failed-uploads",
    },
  ],
};

export default pages;
