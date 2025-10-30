// This is example of menu item without group for horizontal layout. There will be no children.



// assets
import { DashboardOutlined } from '@ant-design/icons';

// type
import { NavItemType } from 'types/menu';

// icons
const icons = {
  DashboardOutlined
};

// ==============================|| MENU ITEMS - SAMPLE PAGE ||============================== //

const dashboard: NavItemType = {
  id: 'projects',
  title: 'Projects',
  type: 'group',
  url: '/dashboard/default',
  icon: icons.DashboardOutlined,
};

export default dashboard;
