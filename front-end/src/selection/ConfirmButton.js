import { useContext } from "react";
import styled from "styled-components";
import AppContext from "../App/app-state";


//The confirm button element.
const ConfirmButtonElement = styled.div`
  margin: 20px;
  color: #black;
  padding: 7px;
  font-size:1.5em;
  border: 2px solid grey;
  border-radius:10px;
  cursor:pointer;
  font-weight: bolder;
  &:hover {
    box-shadow: 0px 0px 4px 3px #17f580;
    border-radius:10px;
    text-shadow: 0px 0px 0.7px #002616;
  }
`;

//A container for centering the confirm button 
export const CenterContainer = styled.div`
  display: grid;
  justify-content: center;
`;

//The confirm button component. 
const ConfirmButton = () => {
  const appContext = useContext(AppContext);

  /*Upon clicking the ConfirmButtonElement the confirmFavorites function is triggered in the app context.
  Local storage is updated with the favorites selection of the user and the visit is recorded.*/
  const clickHandler = () => {
    appContext.confirmFavorites();
  };
  return (
    <CenterContainer>
      <ConfirmButtonElement onClick={clickHandler}>
        Confirm Favorites
      </ConfirmButtonElement>
    </CenterContainer>
  );
};
export default ConfirmButton;
