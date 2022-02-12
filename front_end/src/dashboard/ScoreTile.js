import styled, { css } from "styled-components";
import AppContext from "../App/app-state";
import { HeaderGridLayout } from "../selection/TickerHeaderGrid";
import { useContext } from "react";

/* A wrapper element for the score tiles. Styles are applied conditionally based on whether an element is
selected as favorite */
const ScoreTileStyled = styled.div`
  box-shadow: 0px 0px 4px 2px #9ea4c6;
  font-weight: bolder;
  &:hover {
    box-shadow: -1px -3px 3px 1px #9ea4c6;
  }
  padding: 10px;
  cursor: pointer;
  ${(props) =>
    props.currentFavorite &&
    css`
      box-shadow: 0px 0px 4px 3px #17f580;
    `}
`;

/*A wrapper element for the score in each tile. Styles are conditionally applied based on whether the score is
positive or negative. */
const ScoreWrapper = styled.div`
  justify-self: right;
  font-size: 3em;
  color: green;
  ${(props) =>
    props.neg &&
    css`
      color: red;
    `}
`;
/*A wrapper component for each score tile that is responsible for putting the layout together and displaying the ticker data.
The component receives the ticker and score as props from ScoreTile. */
const ScoreTileWrapper = ({ ticker, score }) => {
  const appContext = useContext(AppContext);

  return (
    <ScoreTileStyled
      onClick={() => appContext.setCurrentFavorite(ticker)}
      currentFavorite={appContext.currentFavorite === ticker}
    >
      <HeaderGridLayout>
        <div>{ticker}</div>
        <ScoreWrapper neg={score < 0}>{score}</ScoreWrapper>
      </HeaderGridLayout>
    </ScoreTileStyled>
  );
};

/*The score tile component that receives the score and ticker as props in the Score Grid component and passes them
to the ScoreTileWrapper component */
const ScoreTile = ({ score, ticker }) => {
  return <ScoreTileWrapper score={score} ticker={ticker}></ScoreTileWrapper>;
};
export default ScoreTile;
