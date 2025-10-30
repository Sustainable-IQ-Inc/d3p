// This is example of menu item without group for horizontal layout. There will be no children.

// third-party

// assets
import { ChromeOutlined } from "@ant-design/icons";

// type
import { NavItemType } from "types/menu";

// icons
const icons = {
  ChromeOutlined,
};

// ==============================|| MENU ITEMS - SAMPLE PAGE ||============================== //

const projectUpload: NavItemType = {
  id: "project-upload",
  title: "Project Upload",
  type: "group",
  url: "/project-upload",
  icon: icons.ChromeOutlined,
};

export default projectUpload;
