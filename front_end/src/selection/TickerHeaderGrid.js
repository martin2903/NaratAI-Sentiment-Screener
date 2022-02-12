import styled from "styled-components";
import { DeleteGridTile } from "../layoutWrappers/TileWrapper";

//Layout wrapper for the grid element. It splits each tile in the grid into two columns for the ticker name/image and symbol.
export const HeaderGridLayout = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  margin-top: 5px;
`;

//A wrapper for the ticker symbol that aligns it to the right in the grid element.
export const TickerSymbol = styled.div`
  justify-self: right;
`;

//A delete icon that will only appear and replace the ticker symbol if the element is a DeleteGridTile .
export const DeleteIcon = styled.div`
  justify-self: right;
  display: none;
  ${DeleteGridTile}:hover & {
    display: block;
    color: red;
    font-weight: bolder;
  }
`;

/*A component that holds the proprties of each tile in the grid. Depending on whether the tile is
in the upper grid(favorites) or bottom grid the Delete Icon is displayed allowing the user to remove a favorite.*/

const TickerHeaderGrid = ({ tickerName, tickerSymbol, favoritesSection }) => {
  return (
    <HeaderGridLayout>
      <div>{tickerName}</div>
      {favoritesSection ? (
        <DeleteIcon>X</DeleteIcon>
      ) : (
        <TickerSymbol>{tickerSymbol}</TickerSymbol>
      )}
    </HeaderGridLayout>
  );
};

export default TickerHeaderGrid;
