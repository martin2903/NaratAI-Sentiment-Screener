import { useContext } from "react";
import AppContext from "../App/app-state";

/*A wrapper component that assists in toggling between pages. If the current page in the app context
is different than the name prompt, no content is rendered. */

const Page = ({ name, children }) => {
  const appContext = useContext(AppContext);

  if (appContext.page == name) {
    return <div>{children}</div>;
  } else {
    return null;
  }
};
export default Page;
