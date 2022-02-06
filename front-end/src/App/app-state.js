import { createContext, useState, useEffect } from "react";
import moment from "moment";

//create a context
const AppContext = createContext({
  page: "",
  pageSetter: (pageName) => {},
});

//A constant that limits the length of the favorites being rendered.
const MAX_LENGTH_FAVORITES = 5;

//A constsnt that determines the time units that will be displayed on the sentiment score chart.
const TIME_UNITS = 10;
//create the context Provider component wrapper that contains the context.Provider component
export const AppContextProvider = (props) => {
  // useState hook for tracking the page currently selected (Dashboard or Selection)
  const [appPage, setAppPage] = useState();
  // useState hook for tracking whether the user visits for the first time. Different content will be rendered based on that.
  const [firstVisit, setFirstVisit] = useState();
  // useState hook for tracking the all data received about the tickers that will be displayed in the grid tiles.
  const [tickerData, setTickerData] = useState();
  // useState hook for tracking the favorites the user has selected (but not yet confirmed).
  const [favorites, setFavorites] = useState([]);
  // useState hook for tracking the favorites the user has confirmed(after clicking the confirm button).
  const [confirmedFavorites, setConfirmedFavorites] = useState([]);
  // useState hook for tracking the tickers filtered while using the search input.
  const [filteredTickers, setFilteredTickers] = useState([]);
  // useState hook for tracking the sentiment score received by the backend.
  const [sentimentScore, setSentimentScore] = useState([]);
  // useState hook for tracking the current favorite the user has selected.
  const [currentFavorite, setCurrentFavorite] = useState();
  // useState hook for tracking the historical score data received by the backend.
  const [historicalScore, setHistoricalScore] = useState([]);
  // useState hook for tracking the historical score data that will be displayed on the chart.
  const [historicalChart, setHistoricalChart] = useState([]);
  // useState hook for tracking the count stats data received by the backend.
  const [countStats, setCountStats] = useState([]);
  // useState hook for tracking the headlines data received by the backend.
  const [headlines, setHeadlines] = useState([]);

  /*A function for checking localStorage to see whether the user is visiting for the first time.
    If so, he is redirected to the Selection page, otherwise to the Dashboard page. Additionally,
    all cached data in local storage is pulled and the states of the concerned variables are updated.*/
  const checkData = () => {
    let savedData = JSON.parse(localStorage.getItem("cachedData"));
    if (!savedData) {
      setFirstVisit(true);
      setAppPage("Selection");
    } else {
      //pulling data from the local storage using dictionary destructuring and setting the favorites based on that
      let { favorites, currentFavorite } = savedData;
      setFavorites(favorites);
      setCurrentFavorite(currentFavorite);

      setFirstVisit(false);
      setAppPage("Dashboard");
    }
  };

  /*useEffect that calls the checkData function. A use effect is needed as otherwise infinite rerenderings will
  be triggered. */
  useEffect(checkData, []);

  /*A function that will be used from other component using the context. The state of the current
  favorite is updated and the local storage variable is set to the value passed as a parameter*/
  const setCurrentFavoriteHandler = (ticker) => {
    setCurrentFavorite(ticker);
    setHistoricalChart(null);
    localStorage.setItem(
      "cachedData",
      JSON.stringify({
        ...JSON.parse(localStorage.getItem("cachedData")),
        currentFavorite: ticker,
      })
    );
  };

  /*Once a user clicks the ConfirmButton, a localstorage variable is set to indicate 
    that the user has already visited the page. Additionally, the favorites selected are stored
    so that they can be retrieved without the user loosing his picks when refreshing the page or
    switching between pages.*/
  const confirmFavorites = () => {
    setFirstVisit(false);
    const currentFavs = favorites;
    setConfirmedFavorites(currentFavs);
    setCurrentFavorite(currentFavs[0]);

    setAppPage("Dashboard");
    localStorage.setItem(
      "cachedData",
      JSON.stringify({
        favorites: currentFavs,
        currentFavorite: currentFavs[0],
      })
    );
  };

  /*a useEffect for getting the tickers to be rendered on the grid. UseEffect is used to avoid infinite re-rendering, cluttering network with
  infinite http requests. */
  useEffect(() => {
    fetch("http://127.0.0.1:5000/gettickers")
      .then((response) => response.json())
      .then((data) => setTickerData(data));
  }, []);

 

  /*The url and useEffect for fetching the historical data for the current favorite that will be graphed.
  The useEffect runs only when the value of the currentFavorite changes or when the page is reloaded.*/
  let historicalScoreUrl =
    "http://127.0.0.1:5000/gethistoricalscore?ticker=" +
    currentFavorite +
    "&period=" +
    TIME_UNITS;
  useEffect(() => {
    if (currentFavorite)
      fetch(historicalScoreUrl)
        .then((response) => response.json())
        .then((data) => setHistoricalScore(data));
  }, [currentFavorite]);

  /*The array of historical scores is mapped to an array, each element of which is an array of a date (obtained using
  moment) and the sentiment score at that moment. This structure is used to allow for charting the date at the
  x axis and the score at the y axis in the graph.*/
  let histChartData = [
    {
      name: currentFavorite,
      data: historicalScore.map((score, index) => [
        moment()
          .subtract({ days: TIME_UNITS - index })
          .add({ days: 1 })
          .valueOf(),
        score,
      ]),
    },
  ];

  
  /*After mapping the data to a format that works for highcharts, the state of the variable that will be passed to
  highcharts is set.*/
  useEffect(() => {
    setHistoricalChart(histChartData);
  }, [historicalScore]);

 // The url and useEffect for fetching the count stats data for the current favorite. 
  let url = "http://127.0.0.1:5000/getstats?ticker=" + currentFavorite;
  useEffect(() => {
    if (currentFavorite)
      fetch(url)
        .then((response) => response.json())
        .then((data) => setCountStats(data));
  }, [currentFavorite]);

   //A function that builds a url to fetch the sentiment scores of the tickers selected as favorites.
   const currentScoreUrl = () => {
    let url = "http://127.0.0.1:5000/getsentimentscore?ticker=";
    for (let i = 0; i < favorites.length; i++) {
      url = url.concat(favorites[i]);
      if (i !== favorites.length - 1) {
        url = url.concat(",");
      }
    }
    return url;
  };

  /* useEffect for fetching the sentiment scores of the tickers selected as favorites. */
  useEffect(() => {
    if (!firstVisit && currentFavorite) {
      fetch(currentScoreUrl())
        .then((response) => response.json())
        .then((data) => setSentimentScore(data));
    }
  }, [confirmedFavorites, appPage]);

  //A useEffect for retrieving the headlines, their urls and overall sentiment.
  let headlinesUrl =
    "http://127.0.0.1:5000/getheadlines?ticker=" + currentFavorite;
  useEffect(() => {
    if (currentFavorite)
      fetch(headlinesUrl)
        .then((response) => response.json())
        .then((data) => setHeadlines(data));
  }, [currentFavorite]);

  /*A function for adding a favorite and updating the favorite variable state. 
  The function is used to conditionally generate tiles with certain properties.*/
  const addFavorite = (tickerToAdd) => {
    //The spread operator is used to pull all values from the current favorites array
    let favoritesArr = [...favorites];
    if (favoritesArr.length < MAX_LENGTH_FAVORITES) {
      favoritesArr.push(tickerToAdd);
      setFavorites(favoritesArr);
    }
  };

  /*A function for removing a favorite from the favorites list. The filter function is used
  to generate the new array without the element that the user wants to remove.
  The function is used to conditionally generate tiles with certain properties.*/
  const removeFavorite = (tickerToRemove) => {
    let favoritesArr = [...favorites];
    setFavorites(favoritesArr.filter((ticker) => ticker !== tickerToRemove));
  };

  /*A function used to track whether a ticker is already added to favorites. It ensures that a user is not able
  to add a favorite multiple times. The function is used to conditionally generate tiles with certain properties.*/
  const isFavorite = (ticker) => {
    let favoritesArr = [...favorites];
    if (favorites.includes(ticker)) {
      return true;
    } else {
      return false;
    }
  };

  //Define the context variable with variables that will be passed to the Provider for tracking.
  const context = {
    page: appPage,
    firstVisit: firstVisit,
    tickerDataContext: tickerData,
    favoritesContext: favorites,
    filteredTickers: filteredTickers,
    sentimentScore: sentimentScore,
    confirmedFavorites: confirmedFavorites,
    currentFavorite: currentFavorite,
    historicalChart: historicalChart,
    countStats: countStats,
    headlines: headlines,
    setHeadlines: setHeadlines,
    setCountStats: setCountStats,
    setHistoricalChart: setHistoricalChart,
    setCurrentFavorite: setCurrentFavoriteHandler,
    setConfirmedFavorites: setConfirmedFavorites,
    setSentimentScore: setSentimentScore,
    setFilteredTickers: setFilteredTickers,
    addFavorite: addFavorite,
    removeFavorite: removeFavorite,
    isFavorite: isFavorite,
    favoritesSetter: setFavorites,
    tickerSetter: setTickerData,
    pageSetter: setAppPage,
    visitSetter: setFirstVisit,
    confirmFavorites: confirmFavorites,
  };

  return (
    <AppContext.Provider value={context}>{props.children}</AppContext.Provider>
  );
};
export default AppContext;
