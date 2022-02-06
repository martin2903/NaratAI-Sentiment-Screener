//A component that hold the image corresponding to the given ticker in each tile.
const TickerImage = ({ ticker, style }) => {
  return (
    <img
      alt={ticker.ticker}
      style={style || { height: "50px" }}
      src={ticker.image_url}
    />
  );
};
export default TickerImage;
