import React, { useState, useEffect } from 'react';
import axios from 'axios';
import "../Css/RuleCreator.css";

const RuleCreator = ({ firewalls, formData, onClose, onSuccess }) => {
  const [hierarchy, setHierarchy] = useState(null);
  const [selectedPath, setSelectedPath] = useState('');
  const [expandedNodes, setExpandedNodes] = useState(new Set());
  const [ruleDetails, setRuleDetails] = useState({
    name: '',
    description: '',
    position: 'top'
  });
  const [loading, setLoading] = useState(false);
  const [selectedFirewall, setSelectedFirewall] = useState('');
  const [filteredHierarchy, setFilteredHierarchy] = useState({});

  useEffect(() => {
    const fetchHierarchy = async () => {
      try {
        setLoading(true);
        const response = await axios.get('http://127.0.0.1:8000/get_rule_hierarchy/');
        setHierarchy(response.data);
      } catch (error) {
        console.error("Error fetching hierarchy:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchHierarchy();
  }, []);

  // Filter hierarchy based on selected firewall
  useEffect(() => {
    if (hierarchy && selectedFirewall) {
      const filtered = {};
      
      // Check device groups for the selected firewall
      for (const [groupName, groupDetails] of Object.entries(hierarchy)) {
        // Check if the group contains the selected firewall
        const hasFirewall = groupDetails.firewalls?.some(fw => fw.name === selectedFirewall);
        
        if (hasFirewall) {
          // Only include the firewall that matches the selection
          filtered[groupName] = {
            ...groupDetails,
            firewalls: groupDetails.firewalls.filter(fw => fw.name === selectedFirewall)
          };
        }
      }
      
      setFilteredHierarchy(filtered);
    } else if (hierarchy) {
      // If no firewall selected but hierarchy loaded, show all with only the passed firewalls
      const filtered = {};
      for (const [groupName, groupDetails] of Object.entries(hierarchy)) {
        filtered[groupName] = {
          ...groupDetails,
          firewalls: groupDetails.firewalls.filter(fw => firewalls.includes(fw.name))
        };
      }
      setFilteredHierarchy(filtered);
    }
  }, [selectedFirewall, hierarchy, firewalls]);

  const handleCreateRule = async () => {
    try {
      setLoading(true);
      
      const rulePayload = {
        name: ruleDetails.name,
        sourceZone: formData.sourceZone,
        sourceIP: formData.sourceIP,
        destinationZone: formData.destinationZone,
        destinationIP: formData.destinationIP,
        destinationPort: formData.destinationPort === "any" ? "any" : formData.destinationPort,
        application: formData.application === "any" ? "any" : formData.application,
        action: formData.Action,
        location: selectedPath,
        description: ruleDetails.description
      };

      const response = await axios.post('http://127.0.0.1:8000/create_security_rule/', rulePayload);
      
      if (response.data.success) {
        onSuccess();
        onClose();
      } else {
        console.error("Error creating rule:", response.data.error);
      }
    } catch (error) {
      console.error("Error creating rule:", error);
    } finally {
      setLoading(false);
    }
  };

  const toggleExpand = (path) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
    }
    setExpandedNodes(newExpanded);
  };

  const renderHierarchy = (items, level = 0) => {
    return Object.entries(items).map(([name, details]) => {
      const isExpanded = expandedNodes.has(details.path);
      const hasChildren = details.firewalls && details.firewalls.length > 0;
      
      return (
        <div key={details.path} className={`hierarchy-item level-${level}`}>
          <div 
            className="hierarchy-header"
            onClick={() => toggleExpand(details.path)}
          >
            {hasChildren && (
              <span className="expand-icon">
                {isExpanded ? '▼' : '►'}
              </span>
            )}
            <span 
              className={`location-name ${selectedPath === details.path ? 'active' : ''}`}
              onClick={(e) => {
                e.stopPropagation();
                setSelectedPath(details.path);
              }}
            >
              {name} ({details.type})
            </span>
          </div>
          
          {isExpanded && hasChildren && (
            <div className="children-container">
              {details.firewalls.map(fw => (
                <div 
                  key={fw.path} 
                  className={`hierarchy-item level-${level + 1}`}
                >
                  <span 
                    className={`location-name ${selectedPath === fw.path ? 'active' : ''}`}
                    onClick={() => setSelectedPath(fw.path)}
                  >
                    {fw.name} (firewall)
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      );
    });
  };

  return (
    <div className="rule-creator-modal">
      <div className="modal-header">
        <h3>Add New Rule</h3>
        <button className="close-button" onClick={onClose}>×</button>
      </div>
      
      <div className="modal-content">
        <div className="firewall-selection">
          <h4>Select Firewall:</h4>
          <select 
            value={selectedFirewall} 
            onChange={(e) => setSelectedFirewall(e.target.value)}
            className="firewall-select"
          >
            <option value="">All Firewalls</option>
            {firewalls.map(fw => (
              <option key={fw} value={fw}>{fw}</option>
            ))}
          </select>
        </div>

        <div className="hierarchy-view">
          <h4>Select Location:</h4>
          {loading && !hierarchy ? (
            <div className="loading-spinner">Loading hierarchy...</div>
          ) : (
            <div className="hierarchy-tree">
              {filteredHierarchy && Object.keys(filteredHierarchy).length > 0 ? (
                renderHierarchy(filteredHierarchy)
              ) : (
                <div className="no-results">
                  {selectedFirewall ? 
                    `No locations found for ${selectedFirewall}` : 
                    'Select a firewall to see locations'}
                </div>
              )}
            </div>
          )}
        </div>

        {selectedPath && (
          <div className="rule-form-container">
            <div className="rule-form">
              <div className="form-group">
                <label>Rule Name:</label>
                <input 
                  type="text" 
                  value={ruleDetails.name}
                  onChange={(e) => setRuleDetails({...ruleDetails, name: e.target.value})}
                  placeholder="Enter rule name"
                  required
                />
              </div>
              <div className="form-group">
                <label>Description:</label>
                <textarea 
                  value={ruleDetails.description}
                  onChange={(e) => setRuleDetails({...ruleDetails, description: e.target.value})}
                  placeholder="Enter description (optional)"
                  rows="3"
                />
              </div>
              <div className="form-group">
                <label>Position:</label>
                <select
                  value={ruleDetails.position}
                  onChange={(e) => setRuleDetails({...ruleDetails, position: e.target.value})}
                >
                  <option value="top">Top</option>
                  <option value="bottom">Bottom</option>
                </select>
              </div>
              
              <div className="rule-preview">
                <h5>Rule Preview:</h5>
                <div className="preview-grid">
                  <div className="preview-row">
                    <span className="preview-label">From:</span>
                    <span className="preview-value">{formData.sourceZone}</span>
                  </div>
                  <div className="preview-row">
                    <span className="preview-label">To:</span>
                    <span className="preview-value">{formData.destinationZone}</span>
                  </div>
                  <div className="preview-row">
                    <span className="preview-label">Source:</span>
                    <span className="preview-value">{formData.sourceIP}</span>
                  </div>
                  <div className="preview-row">
                    <span className="preview-label">Destination:</span>
                    <span className="preview-value">{formData.destinationIP}</span>
                  </div>
                  <div className="preview-row">
                    <span className="preview-label">Service:</span>
                    <span className="preview-value">{formData.destinationPort}</span>
                  </div>
                  <div className="preview-row">
                    <span className="preview-label">Application:</span>
                    <span className="preview-value">{formData.application}</span>
                  </div>
                  <div className="preview-row">
                    <span className="preview-label">Action:</span>
                    <span className="preview-value">{formData.Action}</span>
                  </div>
                </div>
              </div>
              
              <button 
                className="create-button"
                onClick={handleCreateRule}
                disabled={!ruleDetails.name || loading}
              >
                {loading ? 'Creating...' : 'Create Rule'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RuleCreator;