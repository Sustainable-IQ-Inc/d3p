// PROJECT IMPORTS
import DashboardLayout from 'layout/DashboardLayout';

import { DataReloadProvider } from "contexts/ProjectDataReload";

// ==============================|| DASHBOARD LAYOUT ||============================== //

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <DataReloadProvider>
      <DashboardLayout>{children}</DashboardLayout>
    </DataReloadProvider>
  );
}
