import HighChart from "./HighChart";
import { GridTile } from "../layoutWrappers/TileWrapper";
import styled from "styled-components";

//A wrapper element for the chart used to set the background color.
const ChartWrapper = styled(HighChart)`
  .highcharts-background {
    fill: #f4f3ef;
  }
`;

//A wrapper component for the high chart.
const SentScoreChart = () => {
  return (
    <GridTile>
      <ChartWrapper />
    </GridTile>
  );
};
export default SentScoreChart;
