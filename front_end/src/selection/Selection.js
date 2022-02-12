import Page from "../layoutWrappers/Page";
import ConfirmButton from "./ConfirmButton"
import TickerGrid from "./TickerGrid";
import WelcomeMessage from "./WelcomeMessage"
import Search from "./Search";

//The Selection component is responsible for rendering all components in the Selection page.
const Selection = ()=>{
    
    return(
        //pass in name as a prop to the Page component so that the correct content is displayed
        <Page name='Selection'>
        <WelcomeMessage/>
        <TickerGrid favoritesSection/>
        <ConfirmButton/>
       
        <Search/>
        <TickerGrid/>
        </Page>
    )
}
export default Selection;