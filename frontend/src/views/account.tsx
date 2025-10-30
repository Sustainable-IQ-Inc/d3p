'use client';

import { useEffect, useState } from 'react';

// next
import { usePathname, useRouter } from 'next/navigation';

// material-ui
import { Box, Tab, Tabs } from '@mui/material';

// project import
import MainCard from 'components/MainCard';


import TabApiKeys from 'sections/TabApiKeys';

import { handlerActiveItem, useGetMenuMaster } from 'api/menu';

// assets
import { LockOutlined } from '@ant-design/icons';

// ==============================|| PROFILE - ACCOUNT ||============================== //
type Props = {
  tab: string;
};

const AccountProfile = ({ tab }: Props) => {
  const router = useRouter();
  const pathname = usePathname();
  const { menuMaster } = useGetMenuMaster();

  const [value, setValue] = useState(tab);

  const handleChange = (event: React.SyntheticEvent, newValue: string) => {
    setValue(newValue);
    router.replace(`/apps/profiles/account/${newValue}`);
  };

  
  useEffect(() => {
    if (menuMaster.openedItem !== 'account-profile') handlerActiveItem('account-profile');
    // eslint-disable-next-line
  }, [pathname]);

  return (
    <>

      <MainCard border={false} boxShadow>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', width: '100%' }}>
          <Tabs value={value} onChange={handleChange} variant="scrollable" scrollButtons="auto" aria-label="account profile tab">
            
            <Tab label="Manage API Keys" icon={<LockOutlined />} value="api-keys" iconPosition="start" />
          </Tabs>
        </Box>
        <Box sx={{ mt: 2.5 }}>

          {tab === 'api-keys' && <TabApiKeys />}
        </Box>
      </MainCard>
    </>
  );
};

export default AccountProfile;
