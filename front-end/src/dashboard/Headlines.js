import { useContext, createContext, useState } from "react";
import AppContext from "../App/app-state";
import styled,{css} from "styled-components";
import { GridTile } from "../layoutWrappers/TileWrapper";
import HeadlinesContext from "./headlines-state";
import WordsToggler from "./WordsToggler";

//A wrapper layout element that contains the elements for toggling between positive/negative or all options.
export const ToggleGrid = styled.div`
  display: grid;
  grid-template-columns:3fr 1fr;
  grid-gap:70px;
  text-align:center;
`;

export const ToggleGrid2 = styled.div`
  display: grid;
  align-items:right;
  justify-content:right;
  grid-template-columns: 0.5fr 0.5fr;
  width: 200px;
  text-align:center;
`;

//A toggle element. Styles are applied based on the isActive prop.
export const ToggleElement = styled.div`
  cursor: pointer;
  border-radius: 5px;
  ${props=>props.isActive && css`
  background-color #c8b9bd45;
  text-shadow: 0px 0px 0.7px #002616;
 transition:background-color 200ms linear;
`}
`;

//A component that contains the article headlines(as links) for the current favorite selected.
const Headlines = () => {

  
  const appContext = useContext(AppContext);
  const headlinesContext = useContext(HeadlinesContext);

  /*A function for generating the paragraphs containing anchor tags of the article headlines linked to their urls.
  When all is selected as the current class, both positive and negative articles are displayed, achieved by
  first filtering the array based on sentiment and then mapping each item to a paragraph. In cases where
  positive or negative is the class selected, the array items are just mapped to paragraphs. Each headline
  is a link to the article source and it is conditionally colored based on whether it is positive or negative.*/
  const generateItems = (itemSentClass) => {
    if (itemSentClass != "all") {
      return appContext.headlines
        .filter((item) => item.sentiment == itemSentClass)
        .map((item, index) => (
          <p key={index}>
            <a
              style={
                itemSentClass == "negative"
                  ? { color: "red", textDecoration: "none" }
                  : { color: "green", textDecoration: "none" }
              }
              href={item.url}
              target="_blank"
            >
              {item.headline}
            </a>
          </p>
        ));
    } else if (itemSentClass == "all") {
      return appContext.headlines.map((item, index) => (
        <p key={index}>
          <a
            style={
              item.sentiment == "negative"
                ? { color: "red", textDecoration: "none" }
                : item.sentiment=='positive'?{ color: "green", textDecoration: "none" }
                :{color:"grey", textDecoration:"none"}
            }
            href={item.url}
            target="_blank"
          >
            {item.headline}
          </a>
        </p>
      ));
    }
  };

  //Access the data for the currentFavorite ticker. The variable is needed when being passed a prop to TickerImage.

  return (
    
    <GridTile>
      <h3 style={{textAlign:'center',margin:'2px 0 3px 0',fontSize:'2em'}}>Headlines</h3>
      
      <ToggleGrid>
        <ToggleElement onClick={() => headlinesContext.setItemsClass("all")} isActive={headlinesContext.itemsClass==='all'}>
          See all
        </ToggleElement>
        
        <ToggleGrid2>
        <ToggleElement
          onClick={() => headlinesContext.setItemsClass("positive")} isActive={headlinesContext.itemsClass=='positive'}
        >
          positive
        </ToggleElement>
        <ToggleElement
          onClick={() => headlinesContext.setItemsClass("negative")} isActive={headlinesContext.itemsClass=='negative'}
        >
          negative
        </ToggleElement>
        </ToggleGrid2>
      </ToggleGrid>
      {generateItems(headlinesContext.itemsClass)}
    </GridTile>
  );
};
export default Headlines;
