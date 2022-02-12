import styled, {css} from "styled-components";
import { useContext } from "react";
import AppContext from "../App/app-state";
import TickerTile from "./TickerTile";
/*Wrapper element for the entire ticker grid. The grid is responsive and elements are displayed
properly on all screen sizes and devices. Auto-fill, fills rows with as many columns as it can hold. Minimum
colum width is set to 130px ensuring that elements will not get too small. 1fr ensures that the available
space is equally distributed between columns (they have the same size regardless of the screen size). */
export const TickerGridLayout=styled.div`
display:grid;
grid-template-columns:repeat(auto-fill,minmax(130px,1fr));
grid-gap:20px;
margin-top:30px;
`

//The TickerGrid component that holds all tiles in the settings page.
const TickerGrid=({favoritesSection})=>{
const appContext= useContext(AppContext);




/*A function that conditionally renders a list of TickerTile objects based on whether they are in the favorites section,
whether they are filtered elemenets, or if neither - renders all elements in the tickerDataContext variable*/
const getTickerObjects=(favoritesSection)=>{
    return favoritesSection ? appContext.favoritesContext.map(ticker=>
        <TickerTile key={ticker} tickerKey={ticker} favoritesSection={favoritesSection}/>) :appContext.filteredTickers ?
        Array.from(appContext.filteredTickers).map(ticker=><TickerTile key={ticker} tickerKey={ticker} favoritesSection={favoritesSection}/>):
        Object.keys(appContext.tickerDataContext).map(ticker=>
        <TickerTile key ={ticker} tickerKey={ticker} favoritesSection={favoritesSection}/>)
}

return(
<TickerGridLayout>{getTickerObjects(favoritesSection)}
</TickerGridLayout>
)
}
export default TickerGrid;