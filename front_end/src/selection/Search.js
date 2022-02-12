import styled from "styled-components";
import { useEffect, useContext, useState } from "react";
import AppContext from "../App/app-state";
import fuzzy from "fuzzy";

//A contained element for the search grid that includes the Search ticker text and the input field
const SearchGrid = styled.div`
  display: grid;
  grid-template-columns: 200px 1fr;
  place-self: center-left;
`;

//The input field styled element
const SearchInput = styled.input`
  background-color: #e7dfdfdb;
  font-size: 0.95em;
  color: #748d8b;
  padding-left: 10px;
  height: 30px;
  border: 1px solid #f7f7f7db;
  border-radius: 10px;
  place-self: center left;
  &:focus {
    outline: none;
  }
  ::placeholder,
  ::-webkit-input-placeholder {
    font-size: 0.9em;
    padding: 1px;
    font-style: italic;
  }
`;

//The component that holds the search field
const Search = () => {
  //Pull the app context and instantiate useStates for the variables that will be needed
  const appContext = useContext(AppContext);
  const [tickerEntered, setTickerEntered] = useState("");
  

/*A helper function for the getFilteredResult function used when rendering the filtered results while a user types.
It checks whether filterValue is a value that is either a ticker symbol or a ticker name in the ticker data response
fetched in app-state.*/
  const checker = (filterValue) => {
    let keys = Object.keys(appContext.tickerDataContext);
    for (let i = 0; i < keys.length; i++) {
      let obj = appContext.tickerDataContext[keys[i]];
      if (obj.ticker === filterValue || obj.name === filterValue) {
        return obj.ticker;
      }
    }
    return null;
  };

  /*A function that retrieves the ticker symbols of the ticker symbols or names from searchArray that match with 
  values in the ticker data response fetched in app-state.*/ 
  const getFilteredResults = (searchArray) => {
    let results = new Set();
    for (let i = 0; i < searchArray.length; i++) {
      if (checker(searchArray[i]) !== null) {
        results.add(checker(searchArray[i]));
      }
    }
    return results;
  };

  /*A useEffect used to render user input in time intervals. The function it takes as argument will only execute
  if the tickerEntered dependency changes its value. In the function, a fuzzy search algorithm is applied to an array 
  of both the ticker symbols and full names so that the user can search based on both. The results obtained
  from fuzzy search are used to set the state of the filteredResults variable which is tracked in the app-state context,
  allowing the rendering of results live.*/
  useEffect(() => {
    /*setTimeout takes as arguments the function that will be executed and the time interval and returns an Id.
The id is being retrieved in identifier as it allows for the timer to be reset in clearTimeout.*/
    const identifier = setTimeout(() => {
        //Get the array of all ticker symbols and full names to be used by fuzzy search.
      let tickerSymbols = Object.keys(appContext.tickerDataContext);
      let fullNames = tickerSymbols.map(
        (symbol) => appContext.tickerDataContext[symbol].name
      );
      let allSearchValues = tickerSymbols.concat(fullNames);
      let fuzzySearchResult = fuzzy
        .filter(tickerEntered, allSearchValues, {})
        .map((result) => result.string);
        //Get the array of matching ticker symbols and set the filteredResult state.
      let filteredResults = getFilteredResults(fuzzySearchResult);
      appContext.setFilteredTickers(filteredResults);
    }, 500);
    return () => {
      clearTimeout(identifier);
    };
  }, [tickerEntered]);


  /*The chenageHandler for the change event of the input field. It sets the tickerEntered state to the value entered
  and in terms triggers re-rendering and executiong of the function in the useEffect above.*/
  const tickerChangeHandler = (event) => {
    setTickerEntered(event.target.value);
  };



  return (
    <SearchGrid>
      <h2>Search Heat Map</h2>
      <SearchInput
        onChange={tickerChangeHandler}
        placeholder="Start typing.."
      />
    </SearchGrid>
  );
};
export default Search;
