import { useContext, useEffect, useState } from "react";
import AppContext from "../App/app-state";
import TickerImage from "../selection/TickerImage";
import styled, { css } from "styled-components";
import { GridTile } from "../layoutWrappers/TileWrapper";
import StatsContainer from "./StatsContainer";

//A wrapper element for the ticker name
const TickerName = styled.h2`
  text-align: center;
  margin-bottom: 4px;
  margin-top: 5px;
  font-size: 2em;
`;

//A wrapper layout element for the price information
const PriceInfoLayout = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-gap: 70px;
  font-size: 1.2em;
  margin: 0 0 2px 1px;
  text-align: center;
`;

//A wrapper element for the % change info. Styles are conditionally applied based on whether the change is negative or positive.
const ChangeElementStyled = styled.div`
  color: green;
  
  ${(props) =>
    props.neg &&
    css`
      color: red;
    `}
`;

//A component that is responsible for rendering the correct price data (stock or crypto).
const ChangeElement = ({ data }) => {
  return data[1] < 0 ? (
    <ChangeElementStyled neg>{data[1]}% D</ChangeElementStyled>
  ) : (
    <ChangeElementStyled>{data[1]}% U</ChangeElementStyled>
  );
};

//A component for the spotlight where the current favorite and the data related to it is displayed.
const Spotlight = () => {
  const appContext = useContext(AppContext);
  const [stockPriceData, setStockPriceData] = useState([]);
  const [cryptoPrice, setCryptoPrice] = useState([]);

  //Fetch the historical price data for the current favorite from the Yahoo Finance API.
  useEffect(() => {
    let url =
      "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v3/get-historical-data?symbol=" +
      appContext.currentFavorite +
      "&region=US";
    if (
      appContext.tickerDataContext[appContext.currentFavorite].type === "stock"
    ) {
      fetch(url, {
        method: "GET",
        headers: {
          "x-rapidapi-host": "apidojo-yahoo-finance-v1.p.rapidapi.com",
          "x-rapidapi-key":
            "404c590b26msh0ab3a333bf13cb2p1244b9jsnf2917d19a548",
        },
      })
        .then((response) => response.json())
        .then((data) =>
          setStockPriceData([
            data["prices"][0]["close"].toFixed(2),
            (
              ((data["prices"][0]["close"] - data["prices"][1]["close"]) /
                data["prices"][1]["close"]) *
              100
            ).toFixed(3),
          ])
        )
        .catch((err) => {
          console.error(err);
        });
    }
  }, [appContext.currentFavorite]);

  // Fetch the historical price data from the CryptoCompare API.
  useEffect(() => {
    let url =
      "https://min-api.cryptocompare.com/data/v2/histoday?fsym=" +
      appContext.currentFavorite +
      "&tsym=USD&limit=2&api_key=f02f1d15d3fdd8a89fc025e7b072dc06235856ba7b1e6110e58e6eb17bb8edb6";
    if (
      appContext.tickerDataContext[appContext.currentFavorite]["type"] ===
      "crypto"
    ) {
      fetch(url)
        .then((response) => response.json())
        .then((data) =>
          setCryptoPrice([
            data.Data.Data[2].close.toFixed(2),
            ((data.Data.Data[2].close - data.Data.Data[0].close)/data.Data.Data[0].close*100).toFixed(3),
          ])
        );
    }
  }, [appContext.currentFavorite]);

  //Access the data for the currentFavorite ticker. The variable is needed when being passed a prop to TickerImage.
  let ticker = appContext.tickerDataContext[appContext.currentFavorite];

  return (
    <GridTile>
      <TickerName>
        {appContext.tickerDataContext[appContext.currentFavorite].name}
      </TickerName>
      <PriceInfoLayout>
        <div>Price</div>
        <div>% Change</div>
      </PriceInfoLayout>
      <PriceInfoLayout>
        {appContext.tickerDataContext[appContext.currentFavorite].type=='stock'?
        <div>{stockPriceData[0]}</div>:<div>${cryptoPrice[0]}</div>}
        <ChangeElement data={appContext.tickerDataContext[appContext.currentFavorite].type==='stock'?
        stockPriceData:cryptoPrice}>{stockPriceData[1]}%</ChangeElement>
      </PriceInfoLayout>
      <TickerImage
        style={{ height: "150px", display: "block", margin: "auto" }}
        ticker={ticker}
      />
      <div style={{ textAlign: "center", marginTop: "15px", fontSize: "2em" }}>
        Articles Evaluated
      </div>
      <StatsContainer />
    </GridTile>
  );
};
export default Spotlight;
