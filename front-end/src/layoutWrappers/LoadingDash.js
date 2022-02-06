import { useContext } from "react";
import AppContext from "../App/app-state";


//A wrapper component that will generate a loading message while the is data being fetched from the backend.
const LoadingDash=(props)=>{
const appContext = useContext(AppContext);

if(appContext.page==='Dashboard'&&!appContext.currentFavorite||Object.keys(appContext.sentimentScore)[0]===''){
    return(<div style={{fontSize:'2em'}}>Please confirm your favorites</div>)
}
else{
    return(
        props.children
    )
}
}
export default LoadingDash