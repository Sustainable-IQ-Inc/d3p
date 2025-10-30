// type
import { NavItemType } from "types/menu";

// ==============================|| MENU ITEMS - PAGES ||============================== //

const pages: NavItemType = {
  id: "settings",
  title: "Settings",
  type: "group",
  children: [
    {
      id: "settings",
      title: "Settings",
      type: "item",
      url: "/profiles/account/api-keys",
    },
  ],
};

export default pages;
