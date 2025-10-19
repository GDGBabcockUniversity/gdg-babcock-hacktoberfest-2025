import { useState } from 'react';

function Home() {
  const [count, setCount] = useState(0);

  return (
    <div style={{ textAlign: 'center' }}>
      <h1>HacktoberFest Demo by Favour!</h1>
      <div className="card">
        <button onClick={() => setCount((c) => c + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/pages/Home/Home.jsx</code> and save to test HMR
        </p>
      </div>
    </div>
  );
}

export default Home;
