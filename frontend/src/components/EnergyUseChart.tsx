"use client";
import { useEffect, useState } from "react";

// material-ui
import { useTheme } from "@mui/material/styles";

// project imports
import useConfig from "hooks/useConfig";

// types
import { ThemeMode } from "types/config";

// third-party
import dynamic from "next/dynamic";
import { Props as ChartProps } from "react-apexcharts";
import { getProjectDetailsEndUsesChart } from "app/api/ProjectDetailsEndUsesChart";

// Dynamically import ReactApexChart to avoid SSR issues
const ReactApexChart = dynamic(() => import("react-apexcharts"), {
  ssr: false,
});

// ==============================|| ACQUISITION-CHANNELS CHART ||============================== //

interface EnergyUseChartProps {
  projectId: string;
  baseline_design: string;
}

const EnergyUseChart: React.FC<EnergyUseChartProps> = ({ projectId, baseline_design }) => {
  const theme = useTheme();
  const line = theme.palette.divider;
  const { primary, secondary } = theme.palette.text;
  
  

  const { mode } = useConfig();
  useEffect(() => {
    getProjectDetailsEndUsesChart(projectId, baseline_design)
      .then((response: any) => {
        const projectDetails = baseline_design === 'design' ? response.design.series : response.baseline.series;
        
        const categories = (baseline_design === 'design' ? response.design.categories : response.baseline.categories).map((category: string) => {
          const replaced = category.replace(/_/g, " ");
          return replaced.replace(/\w\S*/g, (w) =>
            w.replace(/^\w/, (c) => c.toUpperCase())
          );
        });

        // Calculate the sum for each category
        const sums = categories.map((_: any, index: any) =>
          projectDetails.reduce(
            (sum: any, series: any) => sum + (series.data[index] || 0),
            0
          )
        );

        // Filter out categories where the sum is 0
        const filteredCategories = categories.filter(
          (_: any, index: any) => sums[index] !== 0
        );

        // Filter out data for categories where the sum is 0
        const filteredProjectDetails = projectDetails.map((series: any) => ({
          ...series,
          data: series.data.filter((index: any) => sums[index] !== 0),
        }));

        // Filter out series where the sum of data is 0
        const nonZeroSeries = filteredProjectDetails.filter(
          (series: any) =>
            series.data.reduce((a: number, b: number) => a + b, 0) > 0
        );

        setSeries(projectDetails);

        // Update chart options
        setOptions((prevOptions) => ({
          ...prevOptions,
          xaxis: {
            ...prevOptions.xaxis,
            categories: filteredCategories,
          },
          legend: {
            ...prevOptions.legend,
            customLegendItems: nonZeroSeries.map((series: any) => series.name),
          },
        }));
      })
      .catch((error) => {
        console.error('ERROR: EnergyUseChart - API call failed:', error);
        console.error('ERROR: EnergyUseChart - Error details:', JSON.stringify(error, null, 2));
      });
  }, [projectId,baseline_design]);
  // chart options
  const barChartOptions = {
    chart: {
      type: "bar",
      height: 500,
      width: "100%",
      stacked: true,
      toolbar: {
        show: false,
      },
    },
    xaxis: {
      axisBorder: {
        show: false,
      },
      axisTicks: {
        show: false,
      },
      labels: {
        show: true, // show labels on the x-axis
      },
    },
    yaxis: {
      axisBorder: {
        show: false,
      },
      axisTicks: {
        show: false,
      },
      labels: {
        formatter: function (val: number) {
          return Math.floor(val).toString(); // convert to integer by flooring
        },
      },
      title: {
        text: "EUI (kBtu/SF)", // add a y-axis label
        rotate: -90,
        offsetX: 0,
        offsetY: 0,
        style: {
          color: undefined,
          fontSize: "12px",
          fontFamily: "Helvetica, Arial, sans-serif",
          fontWeight: 600,
          cssClass: "apexcharts-yaxis-title",
        },
      },
    },
    tooltip: {
      x: {
        show: false,
      },
    },
    legend: {
      show: true,
      position: "bottom",
      horizontalAlign: "left",
      offsetX: 10,
      markers: {
        width: 8,
        height: 8,
        radius: "50%",
      },
    },
    dataLabels: {
      enabled: false,
    },
    grid: {
      show: false,
    },
    stroke: {
      colors: ["transparent"],
      width: 1,
    },
  };

  const [options, setOptions] = useState<ChartProps>(barChartOptions);
  const [series, setSeries] = useState([]);
  /*const [series] = useState([
    {
      name: "Cooling",
      data: [21975.89, 0.0, 0.0],
    },
    {
      name: "DHW",
      data: [1711.9, 0.0, 0.16],
    },
    {
      name: "Exterior Lighting",
      data: [0.0, 0.0, 0.0],
    },
    {
      name: "Exterior Usage",
      data: [0.0, 0.0, 0.0],
    },
    {
      name: "Fans",
      data: [715.61, 0.0, 0.0],
    },
    {
      name: "Heat Recovery",
      data: [0.0, 0.0, 0.0],
    },
    {
      name: "Heat Rejection",
      data: [731.37, 0.0, 0.0],
    },
    {
      name: "Heating",
      data: [0.0, 4805.07, 0.0],
    },
    {
      name: "Humidification",
      data: [0.0, 0.0, 0.0],
    },
    {
      name: "Interior Lighting",
      data: [2072.08, 0.0, 0.0],
    },
    {
      name: "Other End Use",
      data: [40154.24, 1534.99, 0.0],
    },
    {
      name: "Plug Loads",
      data: [0.0, 0.0, 0.0],
    },
    {
      name: "Process Refrigeration",
      data: [0.0, 0.0, 0.0],
    },
    {
      name: "Pumps",
      data: [2053.15, 0.0, 0.0],
    },
  ]);*/
  useEffect(() => {
    setOptions((prevState) => ({
      ...prevState,
      colors: [
        "#4C78A8",
        "#F58518",
        "#E45756",
        "#72B7B2",
        "#54A24B",
        "#EECA3B",
        "#B279A2",
        "#FF9DA6",
        "#9D755D",
        "#BAB0AC",
      ],

      theme: {
        mode: mode === ThemeMode.DARK ? "dark" : "light",
        //palette: "palette1",
      },
      legend: {
        labels: {
          colors: "grey.500",
        },
      },
    }));
  }, [mode, primary, secondary, line, theme]);

  return (
    <ReactApexChart options={options} series={series} type="bar" height={350} />
  );
};

export default EnergyUseChart;
