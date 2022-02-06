import './App.css';
import AppLayout from './AppLayout';
import AppBar from './AppBar';
import { AppContextProvider } from './app-state';
import Selection from '../selection/Selection';
import Loading from '../layoutWrappers/Loading';
import Dashboard from '../dashboard/Dashboard';
import LoadingDash from '../layoutWrappers/LoadingDash';
function App() {
  return (
    <AppLayout>
      <AppContextProvider>
      <AppBar/>
      <Loading>
      <Selection/>
      <LoadingDash>
      <Dashboard/>
      </LoadingDash>
      </Loading>
      </AppContextProvider>
    </AppLayout>
  );
}

export default App;
