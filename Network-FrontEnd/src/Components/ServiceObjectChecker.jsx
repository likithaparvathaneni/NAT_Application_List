import React, { useState, useEffect } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import "font-awesome/css/font-awesome.min.css";
import axios from "axios";
import { useLocation, useNavigate } from "react-router-dom";

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

const ServiceObjectChecker = () => {
  const [protocol, setProtocol] = useState("tcp");
  const [port, setPort] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [errors, setErrors] = useState({});
  const [portValidation, setPortValidation] = useState(null);
  const [checkingName, setCheckingName] = useState(false);
  const [nameExists, setNameExists] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  
  const [createForm, setCreateForm] = useState({
    name: "",
    protocol: "tcp",
    port: "",
    description: "",
    tags: "",
    deviceGroup: "shared"
  });

  // Initialize state based on navigation
  useEffect(() => {
    if (location.state?.fromGroupCreation) {
      setProtocol(location.state.prefilledObject?.protocol || "tcp");
      setPort(location.state.prefilledObject?.port || "");
      setCreateForm(prev => ({
        ...prev,
        protocol: location.state.prefilledObject?.protocol || "tcp",
        port: location.state.prefilledObject?.port || ""
      }));
    }
  }, [location.state]);

  // Validate port input
  const validatePort = (portValue) => {
    if (!portValue) return "Port is required";
    
    if (portValue.includes(',')) {
      const ports = portValue.split(',').map(p => p.trim());
      for (const p of ports) {
        if (isNaN(p) || p < 1 || p > 65535) {
          return "All ports must be between 1-65535";
        }
      }
      return "";
    }
    
    if (portValue.includes('-')) {
      const [start, end] = portValue.split('-').map(Number);
      if (isNaN(start) || isNaN(end) || start > end || start < 1 || end > 65535) {
        return "Invalid port range (1-65535)";
      }
      return "";
    }
    
    if (isNaN(portValue) || portValue < 1 || portValue > 65535) {
      return "Port must be between 1-65535";
    }
    
    return "";
  };

  // Real-time validation effect for port
  useEffect(() => {
    if (port) {
      const validationError = validatePort(port);
      setPortValidation(validationError);
    } else {
      setPortValidation(null);
    }
  }, [port]);

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
        objectType: "service"
      });
      return response.data.exists;
    } catch (error) {
      console.error("Error checking object name:", error);
      return false;
    } finally {
      setCheckingName(false);
    }
  };

  // Check if a service object exists in Panorama
  const handleCheckService = async (e) => {
    if (e && e.preventDefault) e.preventDefault();
    
    const portError = validatePort(port);
    if (portError) {
      setErrors({ port: portError });
      return;
    }

    setLoading(true);
    setErrors({});
    setShowCreateForm(false);
    
    try {
      const response = await axios.post("http://127.0.0.1:8000/check_service/", { 
        protocol,
        port: port.trim()
      });
      
      if (response.data.exists) {
        setResult({ 
          exists: true, 
          objects: response.data.objects || []
        });
      } else {
        setResult({ exists: false });
        setCreateForm(prev => ({
          ...prev,
          protocol,
          port
        }));
        setShowCreateForm(true);
      }
    } catch (error) {
      console.error("Panorama API error:", error);
      setErrors({ 
        general: error.response?.data?.message || "Failed to check service object." 
      });
    } finally {
      setLoading(false);
    }
  };

  // Create a new service object in Panorama
  const handleCreateObject = async (e) => {
    e.preventDefault();
    
    const nameError = validateObjectName(createForm.name);
    const portError = validatePort(createForm.port);
    
    const newErrors = {};
    if (nameError) newErrors.name = nameError;
    if (portError) newErrors.port = portError;
    if (nameExists) newErrors.name = "An object with this name already exists";
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post("http://127.0.0.1:8000/create_service/", { 
        objectName: createForm.name.trim(),
        protocol: createForm.protocol,
        port: createForm.port.trim(),
        description: createForm.description,
        tags: createForm.tags.split(',').map(tag => tag.trim()).filter(tag => tag),
        deviceGroup: "shared"
      });
      
      if (response.data.success) {
        // If coming from service group creation, return with all preserved state
        if (location.state?.fromGroupCreation) {
          navigate(location.state.previousPath, {
            state: { 
              newlyCreatedObject: response.data.objectName,
              fromObjectCreation: true,
              previousFormData: location.state.previousFormData
            }
          });
          return;
        }
        
        // Regular flow if not coming from service group
        setResult({ 
          exists: true, 
          objects: [{
            objectName: response.data.objectName,
            objectDetails: response.data.objectDetails || null
          }]
        });
        setShowCreateForm(false);
        setErrors({});
      } else {
        setErrors({
          general: response.data.message || "Failed to create service object. Please check permissions."
        });
      }
    } catch (error) {
      console.error("Panorama API error:", error);
      setErrors({ 
        general: error.response?.data?.message || 
                error.response?.data?.error || 
                "Failed to create service object. Please check Panorama connectivity and permissions." 
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

  // Check object name existence when it changes
  useEffect(() => {
    const timer = setTimeout(async () => {
      if (createForm.name) {
        const exists = await checkObjectNameExists(createForm.name);
        setNameExists(exists);
      } else {
        setNameExists(false);
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [createForm.name]);

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
        Service Object Checker
      </h2>
      
      {/* Service Check Form */}
      <form onSubmit={handleCheckService}>
        <div style={{ marginBottom: "15px" }}>
          <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
            Protocol *
          </label>
          <select
            value={protocol}
            onChange={(e) => setProtocol(e.target.value)}
            style={{ 
              width: "100%", 
              padding: "8px", 
              borderRadius: "4px", 
              border: "1px solid #ccc" 
            }}
          >
            <option value="tcp">TCP</option>
            <option value="udp">UDP</option>
          </select>
        </div>
        
        <div style={{ marginBottom: "15px" }}>
          <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
            Port (single, range, or comma-separated) *
          </label>
          <input
            type="text"
            value={port}
            onChange={(e) => {
              setPort(e.target.value);
              setErrors({ ...errors, port: "" });
            }}
            style={{ 
              width: "100%", 
              padding: "8px", 
              borderRadius: "4px", 
              border: errors.port || portValidation ? "1px solid red" : "1px solid #ccc" 
            }}
            placeholder="e.g., 80, 1000-2000, 443,8080"
          />
          {portValidation && (
            <div style={{ 
              color: portValidation ? "red" : "green", 
              fontSize: "0.9em",
              marginTop: "5px"
            }}>
              {portValidation || "✓ Valid format"}
            </div>
          )}
          {errors.port && !portValidation && (
            <div style={{ color: "red", fontSize: "0.9em" }}>{errors.port}</div>
          )}
        </div>
        
        <button
          type="submit"
          className="btn btn-primary"
          style={{ width: "100%", padding: "10px", marginTop: "10px" }}
          disabled={loading || portValidation}
        >
          {loading ? "Checking..." : "Check Service"}
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
              <strong>✅ Matching Service Objects Found:</strong>
              {result.objects.map((obj, index) => (
                <div key={index} style={{ 
                  marginTop: index > 0 ? "15px" : "10px",
                  paddingTop: index > 0 ? "15px" : "0",
                  borderTop: index > 0 ? "1px solid #c3e6cb" : "none"
                }}>
                  <p><strong>Name:</strong> {obj.objectName}</p>
                  <div style={{ marginTop: "5px" }}>
                    <p><strong>Protocol:</strong> {obj.protocol || obj.objectDetails?.protocol}</p>
                    <p><strong>Port:</strong> {obj.port || obj.objectDetails?.port}</p>
                    {obj.description && (
                      <p><strong>Description:</strong> {obj.description}</p>
                    )}
                    {obj.objectDetails?.description && (
                      <p><strong>Description:</strong> {obj.objectDetails.description}</p>
                    )}
                    {obj.tags && obj.tags.length > 0 && (
                      <p><strong>Tags:</strong> {obj.tags.join(', ')}</p>
                    )}
                    {obj.objectDetails?.tags && obj.objectDetails.tags.length > 0 && (
                      <p><strong>Tags:</strong> {obj.objectDetails.tags.join(', ')}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div>
              <strong>❌ No matching service object found.</strong>
            </div>
          )}
        </div>
      )}

      {/* Create Object Form (if not found) */}
      {showCreateForm && (
        <form onSubmit={handleCreateObject} style={{ marginTop: "20px" }}>
          <h3 style={{ marginBottom: "15px", color: "#007bff" }}>
            Create New Service Object
          </h3>
          
          <div style={{ marginBottom: "15px" }}>
            <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
              Object Name *
            </label>
            <input
              type="text"
              value={createForm.name}
              onChange={(e) => {
                const newName = e.target.value.replace(/\s+/g, '_');
                handleCreateFormChange("name", newName);
              }}
              style={{ 
                width: "100%", 
                padding: "8px", 
                borderRadius: "4px", 
                border: errors.name || nameExists ? "1px solid red" : "1px solid #ccc" 
              }}
              placeholder="e.g., Web_Service (no spaces, only -_.)"
            />
            {checkingName && (
              <div style={{ color: "#007bff", fontSize: "0.9em" }}>Checking name availability...</div>
            )}
            {nameExists && (
              <div style={{ color: "red", fontSize: "0.9em" }}>An object with this name already exists</div>
            )}
            {errors.name && !nameExists && (
              <div style={{ color: "red", fontSize: "0.9em" }}>{errors.name}</div>
            )}
          </div>

          <div style={{ marginBottom: "15px" }}>
            <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
              Protocol *
            </label>
            <select
              value={createForm.protocol}
              onChange={(e) => handleCreateFormChange("protocol", e.target.value)}
              style={{ 
                width: "100%", 
                padding: "8px", 
                borderRadius: "4px", 
                border: "1px solid #ccc" 
              }}
            >
              <option value="tcp">TCP</option>
              <option value="udp">UDP</option>
            </select>
          </div>

          <div style={{ marginBottom: "15px" }}>
            <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
              Port *
            </label>
            <input
              type="text"
              value={createForm.port}
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
              placeholder="Optional description for the service object"
            />
          </div>

          <div style={{ marginBottom: "15px" }}>
            <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
              Tags (comma separated)
            </label>
            <input
              type="text"
              value={createForm.tags}
              onChange={(e) => handleCreateFormChange("tags", e.target.value)}
              style={{ 
                width: "100%", 
                padding: "8px", 
                borderRadius: "4px", 
                border: "1px solid #ccc"
              }}
              placeholder="e.g., web,production,external"
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
              onClick={() => {
                if (location.state?.fromGroupCreation) {
                  navigate(location.state.previousPath, {
                    state: {
                      previousFormData: location.state.previousFormData
                    }
                  });
                } else {
                  setShowCreateForm(false);
                }
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-success"
              style={{ flex: 1, padding: "10px" }}
              disabled={loading || nameExists}
            >
              {loading ? "Creating..." : "Create Service Object"}
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

export default ServiceObjectChecker;