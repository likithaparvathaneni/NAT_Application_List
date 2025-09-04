import React, { useState, useRef, useEffect, Fragment } from "react";
import axios from "axios";
import "../Css/Selection.css"

const SuggestionsInput = ({ name,value, onChange }) => {
  var url=`http://127.0.0.1:8000/zones/`;
  if(name==="firewallName"){
    url=`http://127.0.0.1:8000/Firewall_name/`
  }
  if(name=="application"){
    url=`http://127.0.0.1:8000/App/`
  }
  const [showDropdown, setShowDropdown] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const wrapperRef = useRef(null);

  const fetchSuggestions = async (query) => {
    try {
      const response = await axios.get(url);
      setSuggestions(response.data.data);
    } catch (error) {
      console.error("Error fetching suggestions:", error);
    }
  };

  const changeHandler = (e) => {
    const newValue = e.target.value;
    onChange(newValue);
    if (newValue) {
      fetchSuggestions(newValue);
      setShowDropdown(true);
    } else {
      setShowDropdown(false);
    }
    setSelectedIndex(-1); // Reset selected index on input change
  };

  const handleClickOutside = (e) => {
    if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
      setShowDropdown(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "ArrowDown") {
      setSelectedIndex((prevIndex) =>
        prevIndex < filteredSuggestions.length - 1 ? prevIndex + 1 : prevIndex
      );
    } else if (e.key === "ArrowUp") {
      setSelectedIndex((prevIndex) => (prevIndex > 0 ? prevIndex - 1 : prevIndex));
    } else if (e.key === "Enter" && selectedIndex >= 0) {
      onChange(filteredSuggestions[selectedIndex]);
      setShowDropdown(false);
    }
  };

  useEffect(() => {
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const handleSuggestionClick = (suggestion) => {
    onChange(suggestion);
    setShowDropdown(false);
  };

  const filteredSuggestions = suggestions.filter((suggestion) =>
    suggestion.toLowerCase().includes(value.toLowerCase())
  );

  return (
    <div className="input__wrapper" ref={wrapperRef}>
      <input
        type="text"
        onChange={changeHandler}
        onFocus={() => setShowDropdown(true)}
        onKeyDown={handleKeyDown}
        value={value}
        className="form-control"
      />
      {showDropdown && (
        <div className="suggestions__dropdown">
          {filteredSuggestions.length > 0 ? (
            <Fragment>
              {filteredSuggestions.map((suggestion, index) => (
                <div
                  key={"suggestion_" + index}
                  className={`suggestion__item ${index === selectedIndex ? "selected" : ""}`}
                  onClick={() => handleSuggestionClick(suggestion)}
                >
                  {suggestion}
                </div>
              ))}
            </Fragment>
          ) : (
            <div className="no__suggestions">No suggestions found</div>
          )}
        </div>
      )}
    </div>
  );
};

export default SuggestionsInput;
