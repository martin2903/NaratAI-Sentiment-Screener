import { useContext } from "react";
import styled from "styled-components";
import { ToggleElement, ToggleGrid } from "./Headlines";
import HeadlinesContext from "./headlines-state";

//A container for the elements that will allow toggling between polarity words and keyphrases
export const WordsTogglerGrid = styled.div`
  display: grid;
  align-items:right;
  justify-content:right;
  width: 300px;
  margin-bottom:10px;
  text-align:center;
  grid-template-columns: 2fr 0.5fr;
  grid-gap: 50px;
  font-weight:bolder;
  text-align:center;
`;


/*A component that allows the user to choose the content generated in the word cloud. The user can choose
to either see the polarity words or the keyphrases from the articles listed in the Headlines component.*/
const WordsToggler = () => {
  const headlinesContext = useContext(HeadlinesContext);


  return (
    <WordsTogglerGrid>
      <ToggleElement onClick={()=>headlinesContext.setTypeWords('polarity')} isActive={
        headlinesContext.typeWords==='polarity'
      }>polarity words</ToggleElement>
      <ToggleElement onClick={()=>headlinesContext.setTypeWords('keyphrases')} isActive={
        headlinesContext.typeWords==='keyphrases'
      }>keyphrases</ToggleElement>
    </WordsTogglerGrid>
  );
};
export default WordsToggler;
