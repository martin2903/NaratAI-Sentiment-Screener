import { useContext } from "react";
import AppContext from "../App/app-state";
import styled from "styled-components";
import ScoreTile from "./ScoreTile";

//A layout wrapper element that will contain the tiles with sentiment scores for the confirmed favorites.
const ScoreGridLayout = styled.div`
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  grid-gap: 15px;
  margin-top: 50px;
`;

//A component containing the score tiles for the tickers currently selected as favorites.
const ScoreGrid = () => {
  const appContext = useContext(AppContext);

  return (
    <ScoreGridLayout  >
      {Object.keys(appContext.sentimentScore).map((ticker) => (
        <ScoreTile key={ticker} score={appContext.sentimentScore[ticker]} ticker={ticker}>
          {appContext.sentimentScore[ticker]}
        </ScoreTile>
      ))}
    </ScoreGridLayout>
  );
};
export default ScoreGrid;
