import ReactWordcloud from "react-wordcloud";
import { useContext } from "react";
import { GridTile } from "../layoutWrappers/TileWrapper";
import HeadlinesContext from "./headlines-state";
import WordsToggler from "./WordsToggler";
import styled from "styled-components";

//Options to be passed as props to the ReactWordcloud
const options = {
  fontSizes: [25, 60],
  rotationAngles: [0, 0],
  rotations: 0,
  padding: 10,
};



/* The word cloud component that renders the positive and negative polarity words or keyphrases for
the ticker currently selected as favorite */
const WordCloud = () => {
  const headlinesContext = useContext(HeadlinesContext);

  /* A function for getting the polarity words from the response received from the backend.
  Depending on the current itemsClass value(all,positive,negative) the words array is mapped to an
  array of objects that will be passed to the wordcloud component.*/
  const getWords = () => {
    return headlinesContext.words[headlinesContext.itemsClass].map(
      (item, index) => ({
        text: item.word,
        value: index * 10,
        headline: item.headline,
        url: item.url,
        sentiment: item.sentiment,
      })
    );
  };

  /* A fucntion for getting the polarity words from the response received from the backend.
  As for the polarity words, depending on the current itemsClass value the array is mapped to
  an array of objects that will be passed to the wordcloud component. The mapped array is sliced
  to contain 7 elements to avoid problems when being rendered in the word cloud. */
  const getPhrases = () => {
    return headlinesContext.itemsClass == "all" && headlinesContext.phrases
      ? headlinesContext.phrases
          .map((item, index) => ({
            text: item.phrase,
            value: index * 10,
            headline: item.headline,
            sentiment: item.sentiment,
          }))
          .slice(0, 7)
      : headlinesContext.phrases
          .filter((item) => item.sentiment == headlinesContext.itemsClass)
          .map((item, index) => ({
            text: item.phrase,
            value: index * 10,
            headline: item.headline,
            sentiment: item.sentiment,
          }))
          .slice(0, 7);
  };

  /*The callbacks that will be used by the word cloud component. Words/phrases color is conditionally
  set based on their sentiment and when the user hovers over then the source from where they came from is
  presented.*/
  const callbacks = {
    getWordColor: (word) =>
      word.sentiment === "Positiv" || word.sentiment === "positive"
        ? "#a3d9a3"
        : "#C25F5F",
    getWordTooltip: (word) => `Appears in: "${word.headline}"`,
  };

  return (
    <GridTile>
      {headlinesContext.words && headlinesContext.phrases ? (
          <div style={{minHeight:'500px'}}>
          <WordsToggler/>
        <ReactWordcloud
          words={
            headlinesContext.typeWords == "polarity" ? getWords() : getPhrases()
          }
          options={options}
          callbacks={callbacks}
          minSize={[675,500]}
        /></div>
      ) : (
        <div>Loading</div>
      )}
    </GridTile>
  );
};
export default WordCloud;
