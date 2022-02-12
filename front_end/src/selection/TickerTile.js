import { useContext } from "react";
import AppContext from "../App/app-state";
import {
  SelectGridTile,
  DeleteGridTile,
  DisabledGridTile,
} from "../layoutWrappers/TileWrapper";
import TickerHeaderGrid from "./TickerHeaderGrid";
import TickerImage from "./TickerImage";
import styled from "styled-components";
import { LightenDarkenColor } from "lighten-darken-color";
//A component that ensures that tiles with certain properties are conditionally rendered(check TileWrapper for details)
const TickerTile = ({ tickerKey, favoritesSection }) => {
  const appContext = useContext(AppContext);

  /*A function that determines the scale of darkening the tile background color in the selection grid. n would be the 
number of news articles evaluated for the given ticker on the given day. The more the articles, the darker the color.*/
  const getColorScaling = (n) => {
    return n > 0 && n < 6
      ? -20 - n
      : n > 5 && n < 11
      ? -40 - n
      : n > 10 && n < 21
      ? -60 - n
      : n > 11 && n < 41
      ? -80 - n
      : -110;
  };
  /*The default tile type is set to a SelectGridTile. Styles are conditionally applied based on the amount of
    articles for that ticker on the given day*/
  let TileType = styled(SelectGridTile)`
    background-color: ${appContext.tickerDataContext[tickerKey].num_articles > 1
      ? LightenDarkenColor(
          "#d2ebd2",
          getColorScaling(appContext.tickerDataContext[tickerKey].num_articles)
        )
      : appContext.tickerDataContext[tickerKey].num_articles == 1
      ? "#d1edd1cf"
      : "#f4f3ef"};
  `;
  //The favorites section tile type is set to DeleteGridTile, ensuring properties that allow the user to remove it from favorites.
  if (favoritesSection) {
    TileType = styled(DeleteGridTile)`
      background-color: ${appContext.tickerDataContext[tickerKey].num_articles >
      1
        ? LightenDarkenColor(
            "#d2ebd2",
            getColorScaling(
              appContext.tickerDataContext[tickerKey].num_articles
            )
          )
        : appContext.tickerDataContext[tickerKey].num_articles == 1
        ? "#d1edd1cf"
        : "#f4f3ef"};
    `;
  }
  //If the tile has been added to favorites it is disabled in the rendered grid below the confirm button.
  else if (appContext.isFavorite(tickerKey)) {
    TileType = DisabledGridTile;
  }

  //Get the ticker ticker object based on the tickerKey passed in props.
  let ticker = appContext.tickerDataContext[tickerKey];

  /*A function for handling click events on tiles. If a tile is in the favorites section(based on the favoriteSection prop),
    it is removed from there upon clicking and the favorites context varaible is updated. The reverse is done 
    if the item is not in the favorites section. */
  const clickHandler = (
    tickerKey,
    favoritesSection,
    addFavorite,
    removeFavorite
  ) => {
    return favoritesSection
      ? () => {
          removeFavorite(tickerKey);
        }
      : () => {
          addFavorite(tickerKey);
        };
  };

  return (
    <TileType
      onClick={clickHandler(
        tickerKey,
        favoritesSection,
        appContext.addFavorite,
        appContext.removeFavorite
      )}
    >
      <TickerHeaderGrid
        favoritesSection={favoritesSection}
        tickerName={ticker.name}
        tickerSymbol={ticker.ticker}
      />
      <TickerImage ticker={ticker} />
    </TileType>
  );
};
export default TickerTile;
