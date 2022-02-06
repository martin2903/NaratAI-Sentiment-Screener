import styled from "styled-components";
import NavButton from "./NavButton";

/*A const that will be used for the navbar that implements css grid. Four grid columns are generated
with the second one set to auto to fill in the space between the first column(that hold
  the logo) and the other two(Dashboard and Selection)*/
const GridBar = styled.div`
  display: grid;
  margin-botton: 40px;
  font-weight: bolder;
  grid-template-columns: 200px auto 100px 100px;
`;

const Logo = styled.div`
  font-size: 2em;
  text-shadow: 0px 0px 0.7px #002616;
`;

//AppBar component
const AppBar = () => {
  return (
    <GridBar>
      <Logo>NaratAI</Logo>
      <div />
      <NavButton name="Dashboard" />
      <NavButton name="Selection" />
    </GridBar>
  );
};
export default AppBar;
