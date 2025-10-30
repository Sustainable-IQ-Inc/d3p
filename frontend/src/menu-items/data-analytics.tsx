// This is example of menu item without group for horizontal layout. There will be no children.

// third-party

// assets
import { BarChartOutlined } from '@ant-design/icons';

// type
import { NavItemType } from 'types/menu';

// icons
const icons = {
  BarChartOutlined
};

// ==============================|| MENU ITEMS - SAMPLE PAGE ||============================== //

const reportUpload: NavItemType = {
  id: 'data-analytics',
  title: "Data Viewer",
  type: 'group',
  url: '/data-analytics',
  icon: icons.BarChartOutlined
};

export default reportUpload;
