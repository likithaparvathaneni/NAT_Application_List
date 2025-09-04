import React, { useState, useEffect } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import "font-awesome/css/font-awesome.min.css";
import axios from "axios";
import { useNavigate, useLocation } from "react-router-dom";

const Modal = ({ message }) => (
  <div
    style={{
      position: "fixed",
      top: 0,
      left: 0,
      width: "100%",
      height: "100%",
      backgroundColor: "rgba(0, 0, 0, 0.5)",
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      zIndex: 1000,
    }}
  >
    <div
      style={{
        backgroundColor: "white",
        padding: "20px",
        borderRadius: "10px",
        textAlign: "center",
        boxShadow: "0 0 10px rgba(0, 0, 0, 0.25)",
      }}
    >
      <h3>{message}</h3>
      <div className="spinner" style={{ margin: "20px 0" }}>
        <i className="fa fa-spinner fa-spin" style={{ fontSize: "2em", color: "#007bff" }}></i>
      </div>
    </div>
  </div>
);

const ObjectChecker = ({ type = "address" }) => {
  const [address, setAddress] = useState("");
  const [objectName, setObjectName] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [errors, setErrors] = useState({});
  const [inputValidation, setInputValidation] = useState(null);
  const [checkingName, setCheckingName] = useState(false);
  const [nameExists, setNameExists] = useState(false);
  const [createForm, setCreateForm] = useState({
    type: "ip-netmask",
    description: "",
    value: "",
    deviceGroup: "shared"
  });
  const navigate = useNavigate();
  const location = useLocation();

  // Initialize form if coming from group creation with pre-filled data
  useEffect(() => {
    if (location.state?.fromGroupCreation && location.state?.prefilledObject) {
      setAddress(location.state.prefilledObject.value || "");
      setCreateForm(prev => ({
        ...prev,
        type: location.state.prefilledObject.type || "ip-netmask",
        value: location.state.prefilledObject.value || ""
      }));
      setShowCreateForm(true);
    }
  }, [location.state]);

  // Validate object name
  const validateObjectName = (name) => {
    if (!name) return "Object name is required.";
    if (name.length > 63) return "Name must be 63 characters or less";
    if (/[^a-zA-Z0-9\-_.]/.test(name)) return "Only letters, numbers, hyphens, underscores and periods allowed";
    if (/^[0-9]/.test(name)) return "Name cannot start with a number";
    return "";
  };

  // Check if object name exists in Panorama
  const checkObjectNameExists = async (name) => {
    if (!name) return false;
    
    setCheckingName(true);
    try {
      const response = await axios.post("http://127.0.0.1:8000/check_object_name/", { 
        objectName: name.trim(),
        objectType: type
      });
      return response.data.exists;
    } catch (error) {
      console.error("Error checking object name:", error);
      return false;
    } finally {
      setCheckingName(false);
    }
  };

  // Validate input based on type
  const validateInput = (value, type = null) => {
    if (!value) return "This field is required.";
    
    const ipNetmaskPattern = /^(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])){3}(\/(3[0-2]|[12][0-9]|[0-9]))?$/;
    const fqdnPattern = /^((?!-)[A-Za-z0-9-]{1,63}(?<!-)\.)+[A-Za-z]{2,6}$/;
    const wildcardPattern = /^(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])){3}(\/(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])){3})?$/;

    if (value === "any") return "";

    if (value.includes('-')) {
      const parts = value.split('-');
      if (parts.length !== 2) return "Invalid IP range format (e.g., 192.168.1.1-192.168.1.10)";
      
      if (!ipNetmaskPattern.test(parts[0])) return "Invalid IP range start";
      if (!ipNetmaskPattern.test(parts[1])) return "Invalid IP range end";
      
      return "";
    }

    const checkType = type || (showCreateForm ? createForm.type : null);
    if (checkType) {
      switch(checkType) {
        case "ip-netmask":
          if (!ipNetmaskPattern.test(value)) {
            return "Invalid IP/netmask format (e.g., 192.168.1.1 or 10.0.0.0/24)";
          }
          break;
        case "fqdn":
          if (!fqdnPattern.test(value)) {
            return "Invalid FQDN format (e.g., example.com)";
          }
          break;
        case "wildcard":
          if (!wildcardPattern.test(value)) {
            return "Invalid wildcard mask format (e.g., 192.168.1.0/255.255.255.0)";
          }
          break;
        case "ip-range":
          // Already handled above
          break;
        default:
          return "";
      }
    } else {
      if (!ipNetmaskPattern.test(value) && 
          !fqdnPattern.test(value) && 
          !wildcardPattern.test(value) && 
          value !== "any") {
        return "Invalid input. Must be IP/netmask, IP range, FQDN, or wildcard mask";
      }
    }
    
    return "";
  };

  // Real-time validation effect
  useEffect(() => {
    if (address) {
      const validationError = validateInput(address);
      setInputValidation(validationError);
    } else {
      setInputValidation(null);
    }
  }, [address]);

  // Check object name existence when it changes
  useEffect(() => {
    const timer = setTimeout(async () => {
      if (objectName) {
        const exists = await checkObjectNameExists(objectName);
        setNameExists(exists);
      } else {
        setNameExists(false);
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [objectName]);

  // Check if an address object exists in Panorama
  const handleCheckObject = async (e) => {
    e.preventDefault();
    const error = validateInput(address);
    if (error) {
      setErrors({ address: error });
      return;
    }

    setLoading(true);
    setErrors({});
    setShowCreateForm(false);
    
    try {
      const response = await axios.post("http://127.0.0.1:8000/check_object/", { 
        address: address.trim(),
        objectType: type
      });
      
      if (response.data.exists) {
        setResult({ 
          exists: true, 
          objects: response.data.objects || []
        });
      } else {
        setResult({ exists: false });
        const detectedType = detectAddressType(address);
        setCreateForm(prev => ({
          ...prev,
          type: detectedType,
          value: address
        }));
        setShowCreateForm(true);
      }
    } catch (error) {
      console.error("Panorama API error:", error);
      setErrors({ 
        general: error.response?.data?.message || "Failed to check address object." 
      });
    } finally {
      setLoading(false);
    }
  };

  // Detect address type for create form
  const detectAddressType = (value) => {
    if (value.includes('-')) return "ip-range";
    if (value.includes('/') && value.split('/')[1].includes('.')) return "wildcard";
    if (value.match(/[a-zA-Z]/)) return "fqdn";
    return "ip-netmask";
  };

  // Create a new address object in Panorama
  const handleCreateObject = async (e) => {
    e.preventDefault();
    
    const nameError = validateObjectName(objectName);
    const valueError = validateInput(address, createForm.type);
    
    const newErrors = {};
    if (nameError) newErrors.objectName = nameError;
    if (valueError) newErrors.address = valueError;
    if (nameExists) newErrors.objectName = "An object with this name already exists";
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post("http://127.0.0.1:8000/create_object/", { 
        objectName: objectName.trim(),
        type: createForm.type,
        value: address.trim(),
        description: createForm.description,
        deviceGroup: "shared",
        objectType: type
      });
      
      if (response.data.success) {
        setResult({ 
          exists: true, 
          objects: [{
            objectName: response.data.objectName,
            objectDetails: response.data.objectDetails || null
          }]
        });
        
        // Check if we came from group creation
        if (location.state?.fromGroupCreation) {
          navigate(location.state.previousPath, {
            state: { 
              newlyCreatedObject: response.data.objectName,
              fromObjectCreation: true,
              previousFormData: location.state.previousFormData // Pass back the group form data
            }
          });
        } else {
          setShowCreateForm(false);
          setErrors({});
        }
      } else {
        setErrors({
          general: response.data.message || "Failed to create address object. Please check permissions."
        });
      }
    } catch (error) {
      console.error("Panorama API error:", error);
      setErrors({ 
        general: error.response?.data?.message || 
                error.response?.data?.error || 
                "Failed to create address object. Please check Panorama connectivity and permissions." 
      });
    } finally {
      setLoading(false);
    }
  };

  // Handle create form field changes
  const handleCreateFormChange = (field, value) => {
    setCreateForm(prev => ({
      ...prev,
      [field]: value
    }));
    
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = {...prev};
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  return (
    <div style={{ 
      fontFamily: "Arial, sans-serif",
      backgroundColor: "#f4f4f9",
      padding: "20px",
      borderRadius: "10px",
      maxWidth: "800px",
      margin: "20px auto",
      boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)"
    }}>
      {/* Add back button if coming from group creation */}
      {location.state?.fromGroupCreation && (
        <button
          onClick={() => navigate(location.state.previousPath, {
            state: {
              previousFormData: location.state.previousFormData
            }
          })}
          className="btn btn-secondary mb-3"
          style={{ display: "flex", alignItems: "center", gap: "5px" }}
        >
          <i className="fa fa-arrow-left"></i> Back to Group Creation
        </button>
      )}
      
      <h2 style={{ textAlign: "center", color: "#007bff" }}>
        {type === "address" ? "Address Object Checker" : "Object Checker"}
      </h2>
      
      {/* Rest of the component remains the same */}
      {/* Address Check Form */}
      <form onSubmit={handleCheckObject}>
        <div style={{ marginBottom: "15px" }}>
          <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
            {type === "address" ? "IP Address/Subnet/FQDN/Range" : "Object Value"}
          </label>
          <input
            type="text"
            value={address}
            onChange={(e) => {
              setAddress(e.target.value);
              setErrors({ ...errors, address: "" });
            }}
            style={{ 
              width: "100%", 
              padding: "8px", 
              borderRadius: "4px", 
              border: errors.address || inputValidation ? "1px solid red" : "1px solid #ccc" 
            }}
            placeholder={type === "address" ? 
              "e.g., 192.168.1.1, 10.0.0.0/24, example.com, 192.168.1.1-192.168.1.10" : 
              "Enter object value"}
          />
          {inputValidation && (
            <div style={{ 
              color: inputValidation ? "red" : "green", 
              fontSize: "0.9em",
              marginTop: "5px"
            }}>
              {inputValidation || "✓ Valid format"}
            </div>
          )}
          {errors.address && !inputValidation && (
            <div style={{ color: "red", fontSize: "0.9em" }}>{errors.address}</div>
          )}
        </div>
        
        <button
          type="submit"
          className="btn btn-primary"
          style={{ width: "100%", padding: "10px", marginTop: "10px" }}
          disabled={loading || inputValidation}
        >
          {loading ? "Checking..." : "Check Object"}
        </button>
      </form>

      {/* Result Display */}
      {result && (
        <div style={{ 
          marginTop: "20px", 
          padding: "15px", 
          backgroundColor: result.exists ? "#d4edda" : "#fff3cd",
          borderRadius: "4px",
          border: `1px solid ${result.exists ? "#c3e6cb" : "#ffeeba"}`
        }}>
          {result.exists ? (
            <div>
              <strong>✅ Matching Objects Found:</strong>
              {result.objects.map((obj, index) => (
                <div key={index} style={{ 
                  marginTop: index > 0 ? "15px" : "10px",
                  paddingTop: index > 0 ? "15px" : "0",
                  borderTop: index > 0 ? "1px solid #c3e6cb" : "none"
                }}>
                  <p><strong>Name:</strong> {obj.objectName}</p>
                  {obj.objectDetails && (
                    <div style={{ marginTop: "5px" }}>
                      <p><strong>Type:</strong> {obj.objectDetails.type}</p>
                      <p><strong>Value:</strong> {obj.objectDetails.value}</p>
                      {obj.objectDetails.description && (
                        <p><strong>Description:</strong> {obj.objectDetails.description}</p>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div>
              <strong>❌ No matching object found.</strong>
            </div>
          )}
        </div>
      )}

      {/* Create Object Form (if not found) */}
      {showCreateForm && (
        <form onSubmit={handleCreateObject} style={{ marginTop: "20px" }}>
          <h3 style={{ marginBottom: "15px", color: "#007bff" }}>
            Create New {type === "address" ? "Address" : ""} Object
          </h3>
          
          <div style={{ marginBottom: "15px" }}>
            <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
              Object Name *
            </label>
            <input
              type="text"
              value={objectName}
              onChange={async (e) => {
                const newName = e.target.value.replace(/\s+/g, '_');
                setObjectName(newName);
                setErrors({ ...errors, objectName: "" });
              }}
              style={{ 
                width: "100%", 
                padding: "8px", 
                borderRadius: "4px", 
                border: errors.objectName || nameExists ? "1px solid red" : "1px solid #ccc" 
              }}
              placeholder="e.g., Server_Prod_Web (no spaces, only -_.)"
            />
            {checkingName && (
              <div style={{ color: "#007bff", fontSize: "0.9em" }}>Checking name availability...</div>
            )}
            {nameExists && (
              <div style={{ color: "red", fontSize: "0.9em" }}>An object with this name already exists</div>
            )}
            {errors.objectName && !nameExists && (
              <div style={{ color: "red", fontSize: "0.9em" }}>{errors.objectName}</div>
            )}
          </div>

          {type === "address" && (
            <div style={{ marginBottom: "15px" }}>
              <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
                Type *
              </label>
              <select
                value={createForm.type}
                onChange={(e) => handleCreateFormChange("type", e.target.value)}
                style={{ 
                  width: "100%", 
                  padding: "8px", 
                  borderRadius: "4px", 
                  border: "1px solid #ccc" 
                }}
              >
                <option value="ip-netmask">IP Netmask</option>
                <option value="ip-range">IP Range</option>
                <option value="fqdn">FQDN</option>
                <option value="wildcard">IP Wildcard Mask</option>
              </select>
            </div>
          )}

          <div style={{ marginBottom: "15px" }}>
            <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
              Value *
            </label>
            <input
              type="text"
              value={address}
              readOnly
              style={{ 
                width: "100%", 
                padding: "8px", 
                borderRadius: "4px", 
                border: "1px solid #ccc",
                backgroundColor: "#f5f5f5"
              }}
            />
          </div>

          <div style={{ marginBottom: "15px" }}>
            <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
              Description
            </label>
            <textarea
              value={createForm.description}
              onChange={(e) => handleCreateFormChange("description", e.target.value)}
              style={{ 
                width: "100%", 
                padding: "8px", 
                borderRadius: "4px", 
                border: "1px solid #ccc",
                minHeight: "60px"
              }}
              placeholder="Optional description for the object"
            />
          </div>

          <div style={{ marginBottom: "15px" }}>
            <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
              Device Group
            </label>
            <input
              type="text"
              value="shared"
              readOnly
              style={{ 
                width: "100%", 
                padding: "8px", 
                borderRadius: "4px", 
                border: "1px solid #ccc",
                backgroundColor: "#f5f5f5"
              }}
            />
          </div>
          
          <div style={{ display: "flex", gap: "10px" }}>
            <button
              type="button"
              className="btn btn-secondary"
              style={{ flex: 1, padding: "10px" }}
              onClick={() => setShowCreateForm(false)}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-success"
              style={{ flex: 1, padding: "10px" }}
              disabled={loading || nameExists}
            >
              {loading ? "Creating..." : "Create Object"}
            </button>
          </div>
        </form>
      )}

      {/* General Errors */}
      {errors.general && (
        <div style={{ 
          color: "red", 
          marginTop: "15px", 
          textAlign: "center",
          padding: "10px",
          backgroundColor: "#ffeeee",
          borderRadius: "4px"
        }}>
          <strong>Error:</strong> {errors.general}
          {errors.general.includes("connect") && (
            <div style={{ marginTop: "5px" }}>
              Please check Panorama connectivity and API key permissions
            </div>
          )}
        </div>
      )}

      {/* Loading Modal */}
      {loading && <Modal message="Processing request, please wait..." />}
    </div>
  );
};

export default ObjectChecker;