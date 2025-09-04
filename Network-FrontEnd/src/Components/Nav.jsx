import React, { useState } from "react";
import "../Css/nav.css";
import { Link } from "react-router-dom";

const Navbar = () => {
  const [showObjectDropdown, setShowObjectDropdown] = useState(false);

  return (
    <header className="header">
      <Link to="/" className="logo">
        <img src="Images/Providence-logo.jpg" alt="Logo" className="logo-img" />
        <span className="logo-text"> Providence India </span>
      </Link>
      <nav className="navbar">
        <Link to="/Generatefiles">Generate Files</Link>
        <Link to="/Compare">Compare</Link>
        <Link to="/Fwform">Firewall Finder</Link>
        <Link to="/fw">Rule-Checking</Link>
        
        {/* Object Checker Dropdown */}
        <div 
          className="dropdown-container"
          onMouseEnter={() => setShowObjectDropdown(true)}
          onMouseLeave={() => setShowObjectDropdown(false)}
        >
          <Link 
            to="#" 
            className="dropdown-trigger"
            onClick={(e) => {
              e.preventDefault();
              setShowObjectDropdown(!showObjectDropdown);
            }}
          >
            Object Checker
          </Link>
          {showObjectDropdown && (
            <div className="dropdown-menu">
              <Link to="/object-checker/address" onClick={() => setShowObjectDropdown(false)}>
                Address Object
              </Link>
              <Link to="/object-checker/service" onClick={() => setShowObjectDropdown(false)}>
                Service Object
              </Link>
              <Link to="/object-checker/address-group" onClick={() => setShowObjectDropdown(false)}>
                Address Group
              </Link>
              <Link to="/object-checker/service-group" onClick={() => setShowObjectDropdown(false)}>
                Service Group
              </Link>
            </div>
          )}
        </div>
      </nav>
    </header>
  );
};

export default Navbar;