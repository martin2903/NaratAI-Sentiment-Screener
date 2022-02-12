import { useContext } from "react";
import styled from "styled-components";
import AppContext from "../App/app-state";

//An element that holds the welcome message displayed.
const WelcomeMessageElement = styled.p`
  font-size: 1.5em;
  font-weight: bolder;
`;

//A component that holds the welcome message displayed when a user first visits the page.
const WelcomeMessage = () => {
  const appContext = useContext(AppContext);

  /*use the appContext to pull the state and check whether the user is visiting for the first time,
    conditionally rendering the welcome message.*/
  if (appContext.firstVisit) {
    return (
      <div>
        <WelcomeMessageElement>
          Pick Your Tickers and Hit Confirm Favorites!
        </WelcomeMessageElement>
        <h2></h2>
      </div>
    );
  } else {
    return <div></div>;
  }
};
export default WelcomeMessage;
