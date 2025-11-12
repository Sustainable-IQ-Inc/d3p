// assets
import { BookOutlined } from '@ant-design/icons';

// type
import { NavItemType } from 'types/menu';

// icons
const icons = {
  BookOutlined
};

// ==============================|| MENU ITEMS - DOCUMENTATION ||============================== //

const documentation: NavItemType = {
  id: 'documentation',
  title: 'Documentation',
  type: 'group',
  url: '/docs',
  icon: icons.BookOutlined,
};

export default documentation;

