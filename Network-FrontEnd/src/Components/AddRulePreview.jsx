import React from "react";

const AddRulePreview = ({ isOpen, onClose, ruleData, onSubmit }) => {
  if (!isOpen) return null;

  const formatValue = (value) => {
    if (value === null || value === undefined) return "N/A";
    if (typeof value === "boolean") return value ? "Yes" : "No";
    if (typeof value === "object") {
      if (Object.keys(value).length === 0) return "None";
      return JSON.stringify(value, null, 2);
    }
    if (value === "") return "Empty";
    return value;
  };

  const renderSecurityProfiles = (profiles) => {
    const activeProfiles = Object.entries(profiles)
      .filter(([_, value]) => value && value !== "")
      .map(([key, value]) => `${key}: ${value}`);

    return activeProfiles.length > 0 ? activeProfiles.join(", ") : "None";
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content" style={{ maxWidth: "800px", maxHeight: "90vh", overflowY: "auto" }}>
        <h2>Rule Preview</h2>
        <p style={{ color: "#666", marginBottom: "20px" }}>
          This is what will be sent to the backend for rule creation:
        </p>

        <div style={{ 
          backgroundColor: "#f8f9fa", 
          border: "1px solid #dee2e6", 
          borderRadius: "4px", 
          padding: "20px",
          marginBottom: "20px"
        }}>
          <h4 style={{ marginBottom: "15px", color: "#495057" }}>Rule Configuration</h4>
          
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "15px" }}>
            <div>
              <strong>Rule Name:</strong> {formatValue(ruleData.name)}
            </div>
            <div>
              <strong>Action:</strong> {formatValue(ruleData.action)}
            </div>
            
            <div>
              <strong>Source Zone:</strong> {formatValue(ruleData.sourceZone)}
            </div>
            <div>
              <strong>Destination Zone:</strong> {formatValue(ruleData.destinationZone)}
            </div>
            
            <div>
              <strong>Source IP/Object:</strong> {formatValue(ruleData.sourceIP)}
            </div>
            <div>
              <strong>Destination IP/Object:</strong> {formatValue(ruleData.destinationIP)}
            </div>
            
            <div>
              <strong>Service/Port:</strong> {formatValue(ruleData.destinationPort)}
            </div>
            <div>
              <strong>Application:</strong> {formatValue(ruleData.application)}
            </div>
            
            <div>
              <strong>Location:</strong> {formatValue(ruleData.location)}
            </div>
            <div>
              <strong>Rule Type:</strong> {formatValue(ruleData.rule_type)}
            </div>
            
            <div>
              <strong>Disabled:</strong> {formatValue(ruleData.disabled)}
            </div>
            <div>
              <strong>Log Start:</strong> {formatValue(ruleData.logStart)}
            </div>
            
            <div>
              <strong>Log End:</strong> {formatValue(ruleData.logEnd)}
            </div>
            <div>
              <strong>Negate Source:</strong> {formatValue(ruleData.negateSource)}
            </div>
            
            <div>
              <strong>Negate Destination:</strong> {formatValue(ruleData.negateDestination)}
            </div>
            <div>
              <strong>Security Profiles:</strong> {renderSecurityProfiles(ruleData.securityProfiles)}
            </div>
          </div>
          
          {ruleData.description && (
            <div style={{ marginTop: "15px" }}>
              <strong>Description:</strong>
              <div style={{ 
                backgroundColor: "white", 
                padding: "10px", 
                borderRadius: "4px", 
                marginTop: "5px",
                border: "1px solid #dee2e6"
              }}>
                {ruleData.description}
              </div>
            </div>
          )}
        </div>

        <div style={{ 
          backgroundColor: "#e9ecef", 
          border: "1px solid #ced4da", 
          borderRadius: "4px", 
          padding: "15px",
          marginBottom: "20px"
        }}>
          <h5 style={{ marginBottom: "10px", color: "#495057" }}>Raw JSON Data:</h5>
          <pre style={{ 
            backgroundColor: "white", 
            padding: "10px", 
            borderRadius: "4px",
            overflowX: "auto",
            fontSize: "12px",
            maxHeight: "200px",
            overflowY: "auto"
          }}>
            {JSON.stringify(ruleData, null, 2)}
          </pre>
        </div>

        <div style={{ display: "flex", justifyContent: "space-between", marginTop: "20px" }}>
          <button 
            type="button" 
            onClick={onClose}
            className="glass-button"
            style={{ backgroundColor: "#6c757d" }}
          >
            Back to Edit
          </button>
          <button 
            type="button" 
            className="glass-button"
            onClick={() => {
              onSubmit({ preventDefault: () => {} });
              onClose();
            }}
            style={{ backgroundColor: "#28a745" }}
          >
            Confirm and Create Rule
          </button>
        </div>
      </div>
    </div>
  );
};

export default AddRulePreview;