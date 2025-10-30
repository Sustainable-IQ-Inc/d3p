"use client";
import React, { createContext, useContext, useState, useCallback, ReactNode } from "react";

interface DataReloadContextType {
  reloadData: () => void;
  reloadKey: number; // Add reloadKey to the context type
}

interface DataReloadProviderProps {
  children: ReactNode;
}

const DataReloadContext = createContext<DataReloadContextType | undefined>(undefined);

export const DataReloadProvider: React.FC<DataReloadProviderProps> = ({ children }) => {
  const [reloadKey, setReloadKey] = useState(0);

  const reloadData = useCallback(() => {
    
    setReloadKey((prevKey) => prevKey + 1);
  }, []);

  
  return (
    <DataReloadContext.Provider value={{ reloadData, reloadKey }}> {/* Pass reloadKey */}
      {children}
    </DataReloadContext.Provider>
  );
};

export const useDataReload = () => {
  const context = useContext(DataReloadContext);
  if (!context) {
    throw new Error("useDataReload must be used within a DataReloadProvider");
  }
  return context;
};