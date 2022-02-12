import { useContext } from "react";
import AppContext from "../App/app-state";


//A wrapper component that will generate a loading message while the data being fetched from the API.
const Loading=(props)=>{
const appContext = useContext(AppContext);

/*If there is no data in the tickerDataContext, a Loading message is displayed. Otherwise load the content 
around between the wrapper (props.children)*/
if(!appContext.tickerDataContext){
    return(
        <div>Loading Tickers</div>
    )
}else if(!appContext.sentimentScore){
    return(
        <div>Loading Scores</div>
    )
}else{
    return(
        props.children
    )
}
}
export default Loading;