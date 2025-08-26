import React, {useState, useEffect} from 'react';

function App(){
  const [upi, setUpi] = useState('');
  const [tx, setTx] = useState(null);
  const [status, setStatus] = useState(null);

  async function genUPI(){
    const r = await fetch('/api/generate_upi', {method:'POST'});
    const j = await r.json();
    setUpi(j.upi);
  }

  async function sendCollect(){
    const r = await fetch('/api/collect', {
      method:'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({to_upi: upi, amount: 10.0})
    });
    const j = await r.json();
    setTx(j.tx_id);
    setStatus(j.status);
  }

  useEffect(()=>{
    let t;
    if(tx){
      t = setInterval(async ()=>{
        const r = await fetch(`/api/status/${tx}`);
        const j = await r.json();
        setStatus(j.status);
      }, 1500);
    }
    return ()=> clearInterval(t);
  }, [tx]);

  return (
    <div style={{padding:20}}>
      <h2>Mini UPI Gateway (sim)</h2>
      <button onClick={genUPI}>Generate UPI</button>
      {upi && <div><b>UPI:</b> {upi} <button onClick={sendCollect}>Request Collect ₹10</button></div>}
      {tx && <div><b>Tx ID</b>: {tx} <br/><b>Status</b>: {status}</div>}
    </div>
  );
}

export default App;
