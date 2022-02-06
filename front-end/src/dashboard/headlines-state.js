import { useState, createContext, useContext, useEffect } from "react";
import AppContext from "../App/app-state";

/* A context provider component that will allow for sharing variable states between the Headlines, WordCloud and
WordsToggler components.*/
const HeadlinesContext = createContext();
export const HeadlinesContextProvider = (props) => {
  /* useState hook for tracking the value of the itemsClass const. It is responsible for allowing the user to 
  switch between seeing positive or negative headlines/words/keyphrases or seeing both mixed.*/
  const [itemsClass, setItemsClass] = useState("all");
  /* useState hook for tracking the value of the typeWords const. It is responsible for allowing the user
  to selectively toggle polarity words or keyphrases in the word cloud. */
  const [typeWords, setTypeWords] = useState("polarity");
  // useState hook for tracking the value of the keyphrases received as a response from the backend.
  const [phrases, setPhrases] = useState();
  // useState hook for tracking the value of the polarity words received as a response from the backend
  const [words, setWords] = useState();

  const appContext = useContext(AppContext);

  /* a useEffect that fetches the polarity words from the backend. The fetch function is reexecuted
  only when the value of the currentFavorite has changed. */
  let wordsUrl =
    "http://127.0.0.1:5000/getpolaritywords?ticker=" + appContext.currentFavorite;
  useEffect(() => {
    fetch(wordsUrl)
      .then((response) => response.json())
      .then((data) => setWords(data));
  }, [appContext.currentFavorite]);


  /* a useEffect that fetches the keyphrases from the backend. The fetch function is reexecuted
  only when the value of the currentFavorite has changed. */
  let phrasesUrl =
    "http://127.0.0.1:5000/getkeyphrases?ticker=" + appContext.currentFavorite;
  useEffect(() => {
    fetch(phrasesUrl)
      .then((response) => response.json())
      .then((data) => setPhrases(data));
  }, [appContext.currentFavorite]);

  //The context constants that will be tracked.
  const context = {
    itemsClass: itemsClass,
    setItemsClass: setItemsClass,
    words: words,
    setWords: setWords,
    typeWords: typeWords,
    setTypeWords: setTypeWords,
    phrases: phrases,
    setPhrases: setPhrases,
  };

  return (
    <HeadlinesContext.Provider value={context}>
      {props.children}
    </HeadlinesContext.Provider>
  );
};
export default HeadlinesContext;
