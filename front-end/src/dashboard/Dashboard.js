import Page from "../layoutWrappers/Page";
import ScoreGrid from "./ScoreGrid";
import Spotlight from "./Spotlight";
import styled from "styled-components";
import SentScoreChart from "./SentScoreChart";
import Headlines from "./Headlines";
import WordCloud from "./WordCloud";
import { HeadlinesContextProvider } from "./headlines-state";
import WordsToggler from "./WordsToggler";
//A layout wrapper for containing the spotlight and the sentiment score chart.
const ChartLayout = styled.div`
  display: grid;
  margin-top: 30px;
  grid-gap: 15px;
  grid-template-columns: 1fr 3fr;
`;

//A layout wrapper for containing the headlines and word cloud.
const HeadlinesLayout = styled(ChartLayout)`
  grid-template-columns: 2fr 3fr;
  margin-top: 20px;
`;

//The Dashboard component is responsible for rendering all components in the Dashboard page.
const Dashboard = () => {
  

  return (
    //Pass in name as a prop to the Page component so that the correct content is rendered.
    <Page name="Dashboard">
      <ScoreGrid />
      <ChartLayout>
        <Spotlight />
        <SentScoreChart />
      </ChartLayout>

      <HeadlinesContextProvider>
        <HeadlinesLayout>
          <Headlines />
          <WordCloud />
        </HeadlinesLayout>
      </HeadlinesContextProvider>
    </Page>
  );
};
export default Dashboard;
