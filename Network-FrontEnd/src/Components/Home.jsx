import React from 'react';
import { Link } from 'react-router-dom';
import "../Css/button.css";

const Home = () => {
  return (
    <div className="home-container">
      {/* Existing buttons */}
      <Link to="/Generatefiles" className="glass-button">
        Generate Files
      </Link>

      <Link to="/Compare" className="glass-button">
        Compare
      </Link>

      <Link to="/Fwform" className="glass-button">
        Firewall Finder
      </Link>

      <Link to="/fw" className="glass-button">
        Rule Checking
      </Link>
      
      {/* New button */}
      <Link to="/object-checker" className="glass-button">
        Object Checker
      </Link>
    </div>
  );
};

export default Home;