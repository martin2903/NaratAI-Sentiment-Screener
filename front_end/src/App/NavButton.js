import styled, { css } from "styled-components";
import AppContext from "./app-state";
import { useContext } from "react";

//create the styled element. Different styles are applied based on the active prop.
const NavButtonElement = styled.div`
  cursor: pointer;
  ${(props) =>
    props.active &&
    css`
      text-shadow: 0px 0px 0px #002616;
      color: #1aa75d;
      font-size: 1.1em;
    `}
`;

//the NavButton component
const NavButton = ({ name }) => {
  //pull the AppContext that will be used for the onClick event.
  const appContext = useContext(AppContext);

  //A fucntion triggered by the onClick event. It sets the page to the name of the element clicked.
  const clickHandler = () => {
    appContext.pageSetter(name);
  };

  return (
    <NavButtonElement active={name === appContext.page} onClick={clickHandler}>
      {name}
    </NavButtonElement>
  );
};
export default NavButton;
