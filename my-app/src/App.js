import {createClient, StartCharge} from './socket'
let client = createClient
function App() {

  return (
    <div >
      <button onClick={() =>StartCharge(client, "CP_1")}></button>
    </div>
  );
}

export default App;
