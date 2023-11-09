import './App.css';
import React, {useState, useEffect} from 'react';

function App() {

  const [data, setData] = useState([]);
  const[selectedServer, setSelectedServer] = useState("server1");

  const servers = {
    server1: { label: "server 1"},
    server2: { label: "server 2"},
  };


  useEffect(() => {
    console.log("Fetching data for server: ", selectedServer)
    fetch(`/get_tablespace_storage?server=${selectedServer}`)
      .then((response) => response.json())
      .then((data) => setData(data));
      console.log("Data of ", selectedServer, "has been set")
  }, [selectedServer]);

  const handleAddStorage = async (tablespaceName) => {
    try {
      const response = await fetch(`/add_storage/${tablespaceName}?server=${selectedServer}`, {
        method: 'POST'
      });
      const result = await response.json();

      if(result.success) {

        fetch(`/get_tablespace_storage?server=${selectedServer}`)
          .then((response) =>response.json())
          .then((data) => setData(data));
      }else {
        console.error("Failed to add storage", result.message);
      }
    } catch (error) {
      console.error("Error", error)
    }
  }



  //const [serverStatus, setServerStatus] = useState([]);

  //useEffect(() => {
    //fetch(`/get_server_status?server=${selectedServer}`)
    //.then((response) => response.json())
    //.then((data) => setServerStatus(data));
  //}, [selectedServer]);


  const [windowsServices, setWindowsServices] = useState([]);
  


  useEffect(() => {
    const fetchWindowsServices = async () => {
      try {
        const response = await fetch(`/get_windows_services?server=${selectedServer}`);
        
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        
        if (!Array.isArray(data.services)) {
          console.log(data.services)
          console.log(typeof(data.services))
          throw new Error('Data format is incorrect')
          
        }
        
        setWindowsServices(data.services);
      } catch (error) {
        console.error('Error fetching windows services:', error);
        // Optionally set some state here to indicate an error occurred
        // setErrorState(error.message);
        setWindowsServices([]);
      }
    };
  
    fetchWindowsServices();
  }, [selectedServer]);
  
  


  return (
    <div className="App">
      <h1>Capacidad de Base de Datos</h1>
      <select
        value={selectedServer}
        onChange={(e) => setSelectedServer(e.target.value)}
        style={{width: '200px', height: '30px', color: 'black', backgroundColor: 'white'}}
        >
          <option value="server1">Server 1</option>
          <option value="server2">Server 2</option>
        </select>
      <table>
        <thead>
          <tr>
            <th>Tablespace</th>
            <th>Tamaño (MB)</th>
            <th>MBs Utilizados</th>
            <th>MBs Libres</th>
            <th>Pct. Utilizado</th>
            <th>Estatus</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <tr key={index}>
              <td>{row.TablespaceName}</td>
              <td>{row.SizeMB}</td>
              <td>{row.UsedMB}</td>
              <td>{row.FreeMB}</td>
              <td>{row.PctUsed}%
              <div className={`bar ${row.PctUsed < 60 ? "bar-green" : row.PctUsed < 90 ? "bar-yellow" : "bar-red"}`} 
              style={{width: `${row.PctUsed}%`}}></div>
              </td>
              <td>{row.Status}</td>
              <td><button 
              disabled={row.PctUsed < 75}
              onClick={() => handleAddStorage(row.TablespaceName)}>Agregar espacio</button></td>
              
              
            </tr>
          ))}
        </tbody>
      </table>

      <h2>Servicios en linea para {servers[selectedServer].label}</h2>
      <ul>
  {windowsServices && windowsServices.map((service, index) => (
    <li key={index}>
      {Object.entries(service).map(([key, value], idx) => (
        <div key={idx}>
          {key}: {value}
        </div>
      ))}
    </li>
  ))}
</ul>


    </div>
  );
}

export default App;
