import styled from "styled-components";

//A generic tile element that is used by various components or used as a base element for creating new tile elements.
export const GridTile = styled.div`
  box-shadow: 0px 0px 4px 2px #9ea4c6;
  font-weight: bolder;
  padding: 10px;
`;

//A tile that will be displayed in the section below the confirm button.
export const SelectGridTile = styled.div`
  box-shadow: 0px 0px 4px 2px #9ea4c6;
  font-weight: bolder;
  padding: 10px;
  background-color: lightgreen;
  
  &:hover {
    cursor: pointer;
    box-shadow: -1px -3px 3px 1px #9ea4c6;
  }
`;
//A tile that will be displayed in the favorites section after a user has placed it there.
export const DeleteGridTile = styled.div`
  cursor: pointer;
  font-weight: bolder;
  box-shadow: 0px 0px 4px 2px #9ea4c6;
  padding: 10px;
  &:hover {
    box-shadow: 7px -4px 4px 2px #c64a54;
  }
`;
//A tile that will be displayed in the bottom section after a user has alreay added it to favorites.
export const DisabledGridTile = styled.div`
  box-shadow: 0px 0px 4px 2px #9ea4c6;
  font-weight: bolder;
  padding: 10px;
  pointer-events: none;
  opacity: 0.5;
`;
