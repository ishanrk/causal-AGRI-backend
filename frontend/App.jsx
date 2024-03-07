import { useState } from 'react'  
import styles from './styles'
import Title from './components/Title.jsx'
import Navbar from './components/Navbar.jsx'
import Graph from './components/visaulize.jsx'
import Technologies from './components/Technology.jsx'
import DATA from './components/data.jsx'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

function App() {

  return(

    <Router>
       <div className='bg primary bg-black w-full overflow-hidden'>
      <div className={`${styles.paddingX} ${styles.flexCenter} flex flex-row`}>
      <h1 className="font-poppins font-semibold text-[20px] text-sky-300  ">
               Powered by CAUSALML
            </h1>
        <div className={`${styles.boxWidth}`}>
        
          <Navbar/>
        </div>
      </div>
    <Routes>
    <Route exact path="/" element={<Title />} />
    <Route exact path="/home" element={<Title />} />
    <Route exact path ="/tech" element = {<Technologies/>}/>
    <Route exact path ="/visualize" element = {<Graph/>}/>
    <Route exact path ="/data" element = {<DATA/>}/>
      </Routes>
    </div>
    
    </Router>
   
    
  )

}

export default App