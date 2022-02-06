import styled, { css } from "styled-components";
import { useContext } from "react";
import AppContext from "../App/app-state";

//A layout wrapper element that will contain the stats data for displayed in the spotlight.
const StatsLayout = styled.div`
  display: grid;
  text-align: center;
  grid-template-columns: 1fr 1fr 1fr;
  margin-top: 30px;
  grid-gap: 5px;
  font-size: 1em;
`;

/*A wrapper element for each statistic displayed. Styles are conditionally applied based on whether 
the element is related to the positive, negative, or neutral articles count. */
const StatStyleWrapper = styled.div`
  margin-top: 10px;
  font-size: 3em;
  margin-right: 10px;
  ${(props) =>
    props.negative
      ? css`
          color: red;
        `
      : props.positive
      ? css`
          color: green;
        `
      : css`
          color: grey;
        `}
`;

//A component containing the count statistics displayed in the spotlight for the current favorite.
const StatsContainer = () => {
  const appContext = useContext(AppContext);

  return (
    <StatsLayout>
      <div>
        <div style={{ fontWeight: "bolder" }}>Neutral</div>
        <StatStyleWrapper>{appContext.countStats.neutral}</StatStyleWrapper>
      </div>
      <div>
        <div>Negative</div>
        <StatStyleWrapper negative>
          {appContext.countStats.negative}
        </StatStyleWrapper>
      </div>
      <div>
        <div>Positive</div>
        <StatStyleWrapper positive>
          {appContext.countStats.positive}
        </StatStyleWrapper>
      </div>
    </StatsLayout>
  );
};
export default StatsContainer;
