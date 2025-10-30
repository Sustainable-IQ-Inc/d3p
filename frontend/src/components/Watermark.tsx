import React from "react";

interface WatermarkProps {
  environmentName: string;
}

const Watermark: React.FC<WatermarkProps> = ({ environmentName }) => {
  if (environmentName !== "STAGING" && environmentName !== "LOCAL") {
    return null;
  }

  return (
    <div
      style={{
        position: "fixed",
        top: "80px",
        right: "10px",
        zIndex: 1000,
        color: "red",
        backgroundColor: "yellow",
      }}
    >
      {environmentName === "STAGING"
        ? "STAGING ENVIRONMENT"
        : "LOCAL ENVIRONMENT"}
    </div>
  );
};

export default Watermark;
