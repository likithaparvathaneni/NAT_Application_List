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

const AddressGroupChecker = ({ type = "address-group" }) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [errors, setErrors] = useState({});
  const [addressObjects, setAddressObjects] = useState([]);
  const [addressGroups, setAddressGroups] = useState([]);
  const [selectedObjects, setSelectedObjects] = useState([]);
  const [selectedGroups, setSelectedGroups] = useState([]);
  const [showObjectBrowser, setShowObjectBrowser] = useState(false);
  const [browserType, setBrowserType] = useState("objects");
  const [browserSearchTerm, setBrowserSearchTerm] = useState("");
  const [createForm, setCreateForm] = useState({
    name: "",
    description: "",
    deviceGroup: "shared",
    type: "static"
  });
  const [checkingName, setCheckingName] = useState(false);
  const [nameExists, setNameExists] = useState(false);
  const [expandedGroups, setExpandedGroups] = useState({});
  const [successMessage, setSuccessMessage] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (location.state?.previousFormData) {
      setCreateForm(location.state.previousFormData.createForm || {
        name: "",
        description: "",
        deviceGroup: "shared",
        type: "static"
      });
      setSelectedObjects(location.state.previousFormData.selectedObjects || []);
      setSelectedGroups(location.state.previousFormData.selectedGroups || []);
      setShowCreateForm(true);
      setShowObjectBrowser(true);
    }

    if (location.state?.fromObjectCreation && location.state?.newlyCreatedObject) {
      if (!selectedObjects.includes(location.state.newlyCreatedObject)) {
        setSelectedObjects(prev => [...prev, location.state.newlyCreatedObject]);
      }
    }
  }, [location.state]);

  useEffect(() => {
    // Clear results when search term is cleared
    if (!searchTerm.trim() && results) {
      setResults(null);
    }
  }, [searchTerm]);

  const validateGroupName = (name) => {
    if (!name) return "Group name is required.";
    if (name.length > 63) return "Name must be 63 characters or less";
    if (/[^a-zA-Z0-9\-_.]/.test(name)) return "Only letters, numbers, hyphens, underscores and periods allowed";
    if (/^[0-9]/.test(name)) return "Name cannot start with a number";
    return "";
  };

  const checkGroupNameExists = async (name) => {
    if (!name) return false;
    
    setCheckingName(true);
    try {
      const response = await axios.post("http://127.0.0.1:8000/check_address_group_name/", { 
        groupName: name.trim()
      });
      return response.data.exists;
    } catch (error) {
      console.error("Error checking group name:", error);
      return false;
    } finally {
      setCheckingName(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchTerm.trim()) return;

    setLoading(true);
    setErrors({});
    setShowCreateForm(false);
    setShowObjectBrowser(false);
    
    try {
      const response = await axios.post("http://127.0.0.1:8000/search_address_group/", { 
        searchTerm: searchTerm.trim()
      });
      
      setResults(response.data);
    } catch (error) {
      console.error("Search error:", error);
      setErrors({ 
        general: error.response?.data?.message || "Failed to search. Please try again." 
      });
    } finally {
      setLoading(false);
    }
  };

  const loadAddressObjects = async () => {
    setLoading(true);
    try {
      const response = await axios.get("http://127.0.0.1:8000/list_address_objects/");
      setAddressObjects(response.data.objects || []);
    } catch (error) {
      console.error("Error loading address objects:", error);
      setErrors({ 
        general: error.response?.data?.message || "Failed to load address objects." 
      });
    } finally {
      setLoading(false);
    }
  };

  const loadAddressGroups = async () => {
    setLoading(true);
    try {
      const response = await axios.get("http://127.0.0.1:8000/list_address_groups/");
      setAddressGroups(response.data.groups || []);
    } catch (error) {
      console.error("Error loading address groups:", error);
      setErrors({ 
        general: error.response?.data?.message || "Failed to load address groups." 
      });
    } finally {
      setLoading(false);
    }
  };

  const toggleObjectSelection = (objectName) => {
    setSelectedObjects(prev => 
      prev.includes(objectName) 
        ? prev.filter(name => name !== objectName)
        : [...prev, objectName]
    );
  };

  const toggleGroupSelection = (groupName) => {
    setSelectedGroups(prev => 
      prev.includes(groupName) 
        ? prev.filter(name => name !== groupName)
        : [...prev, groupName]
    );
  };

  const toggleGroupExpansion = (groupName) => {
    setExpandedGroups(prev => ({
      ...prev,
      [groupName]: !prev[groupName]
    }));
  };

  const handleCreateGroup = async (e) => {
    e.preventDefault();
    
    const nameError = validateGroupName(createForm.name);
    if (nameError) {
      setErrors({ name: nameError });
      return;
    }
    
    if (selectedObjects.length === 0 && selectedGroups.length === 0) {
      setErrors({ members: "Please select at least one address object or group" });
      return;
    }

    if (nameExists) {
      setErrors({ name: "An address group with this name already exists" });
      return;
    }

    setLoading(true);
    try {
      const members = [...selectedObjects, ...selectedGroups];

      const response = await axios.post("http://127.0.0.1:8000/create_address_group/", {
        name: createForm.name.trim(),
        description: createForm.description,
        deviceGroup: createForm.deviceGroup,
        type: createForm.type,
        members: members
      });

      if (response.data.success) {
        setSuccessMessage(`Address group "${response.data.group_name}" created successfully!`);
        setResults({
          groups: [{
            name: response.data.group_name,
            details: {
              description: createForm.description,
              members: members,
              type: createForm.type,
              location: 'shared'
            }
          }]
        });
        
        setCreateForm({
          name: "",
          description: "",
          deviceGroup: "shared",
          type: "static"
        });
        setSelectedObjects([]);
        setSelectedGroups([]);
        setErrors({});
        setShowCreateForm(false);
        setShowObjectBrowser(false);
        
        setTimeout(() => setSuccessMessage(null), 5000);
      } else {
        setErrors({
          general: response.data.message || "Failed to create address group."
        });
      }
    } catch (error) {
      console.error("Creation error:", error);
      setErrors({ 
        general: error.response?.data?.message || 
               "Failed to create address group. Please check Panorama connectivity." 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateNewObject = () => {
    navigate("/object-checker/address", {
      state: { 
        fromGroupCreation: true, 
        previousPath: location.pathname,
        previousFormData: {
          createForm,
          selectedObjects,
          selectedGroups
        },
        prefilledObject: {
          value: browserSearchTerm,
          type: detectAddressType(browserSearchTerm)
        }
      }
    });
  };

  const detectAddressType = (value) => {
    if (!value) return "ip-netmask";
    if (value.includes('-')) return "ip-range";
    if (value.includes('/') && value.split('/')[1].includes('.')) return "wildcard";
    if (value.match(/[a-zA-Z]/)) return "fqdn";
    return "ip-netmask";
  };

  useEffect(() => {
    const timer = setTimeout(async () => {
      if (createForm.name) {
        const exists = await checkGroupNameExists(createForm.name);
        setNameExists(exists);
      } else {
        setNameExists(false);
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [createForm.name]);

  useEffect(() => {
    if (showObjectBrowser) {
      if (browserType === "objects") {
        loadAddressObjects();
      } else {
        loadAddressGroups();
      }
    }
  }, [showObjectBrowser, browserType]);

  const filteredObjects = addressObjects.filter(obj => 
    obj.name.toLowerCase().includes(browserSearchTerm.toLowerCase()) ||
    obj.value.toLowerCase().includes(browserSearchTerm.toLowerCase())
  );

  const filteredGroups = addressGroups.filter(group => 
    group.name.toLowerCase().includes(browserSearchTerm.toLowerCase())
  );

  return (
    <div style={{ 
      fontFamily: "Arial, sans-serif",
      backgroundColor: "#f4f4f9",
      padding: "20px",
      borderRadius: "10px",
      maxWidth: "1000px",
      margin: "20px auto",
      boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)"
    }}>
      <h2 style={{ textAlign: "center", color: "#007bff" }}>
        Address Group Checker
      </h2>
      
      {successMessage && (
        <div style={{ 
          color: "green", 
          marginBottom: "15px", 
          textAlign: "center",
          padding: "10px",
          backgroundColor: "#eeffee",
          borderRadius: "4px"
        }}>
          <strong>Success:</strong> {successMessage}
        </div>
      )}
      
      <form onSubmit={handleSearch}>
        <div style={{ marginBottom: "15px" }}>
          <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
            Search Address Groups or Objects
          </label>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ 
              width: "100%", 
              padding: "8px", 
              borderRadius: "4px", 
              border: "1px solid #ccc" 
            }}
            placeholder="Enter group name or address object to search"
          />
        </div>
        
        <button
          type="submit"
          className="btn btn-primary"
          style={{ width: "100%", padding: "10px", marginTop: "10px" }}
          disabled={loading || !searchTerm.trim()}
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {/* Always show the Create New Address Group button */}
      <div style={{ marginTop: "20px", textAlign: "center" }}>
        <button
          className="btn btn-success"
          style={{ padding: "10px 20px" }}
          onClick={() => {
            setShowCreateForm(true);
            setErrors({});
            setSuccessMessage(null);
            setResults(null);
            setSearchTerm("");
          }}
          disabled={showCreateForm}
        >
          + Create New Address Group
        </button>
      </div>

      {results && (
        <div style={{ 
          marginTop: "20px", 
          padding: "15px", 
          backgroundColor: results.groups?.length || results.objects?.length ? "#d4edda" : "#fff3cd",
          borderRadius: "4px",
          border: `1px solid ${results.groups?.length || results.objects?.length ? "#c3e6cb" : "#ffeeba"}`
        }}>
          {results.groups?.length > 0 ? (
            <div>
              <strong>✅ Matching Address Groups Found:</strong>
              {results.groups.map((group, index) => (
                <div key={index} style={{ 
                  marginTop: index > 0 ? "15px" : "10px",
                  paddingTop: index > 0 ? "15px" : "0",
                  borderTop: index > 0 ? "1px solid #c3e6cb" : "none"
                }}>
                  <p><strong>Name:</strong> {group.name}</p>
                  {group.details && (
                    <div style={{ marginTop: "5px" }}>
                      <p><strong>Type:</strong> {group.details.type}</p>
                      {group.details.members?.length > 0 && (
                        <div>
                          <p><strong>Members:</strong></p>
                          <ul style={{ marginLeft: "20px" }}>
                            {group.details.members.map((member, i) => (
                              <li key={i}>{member}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {group.details.description && (
                        <p><strong>Description:</strong> {group.details.description}</p>
                      )}
                      <p><strong>Location:</strong> {group.details.location}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : results.objects?.length > 0 ? (
            <div>
              <strong>🔍 Matching Address Objects Found:</strong>
              {results.objects.map((obj, index) => (
                <div key={index} style={{ 
                  marginTop: index > 0 ? "15px" : "10px",
                  paddingTop: index > 0 ? "15px" : "0",
                  borderTop: index > 0 ? "1px solid #c3e6cb" : "none"
                }}>
                  <p><strong>Name:</strong> {obj.name}</p>
                  <p><strong>Type:</strong> {obj.type}</p>
                  <p><strong>Value:</strong> {obj.value}</p>
                  {obj.description && (
                    <p><strong>Description:</strong> {obj.description}</p>
                  )}
                  <p><strong>Location:</strong> {obj.location}</p>
                  {obj.groups?.length > 0 ? (
                    <div style={{ marginTop: "5px" }}>
                      <strong>Member of Groups:</strong>
                      <ul style={{ marginLeft: "20px" }}>
                        {obj.groups.map((group, i) => (
                          <li key={i}>{group.name} ({group.location})</li>
                        ))}
                      </ul>
                    </div>
                  ) : (
                    <p style={{ color: "#666", fontStyle: "italic" }}>Not a member of any address groups</p>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div>
              <strong>❌ No matching address groups or objects found.</strong>
            </div>
          )}
        </div>
      )}

      {showCreateForm && (
        <form onSubmit={handleCreateGroup} style={{ marginTop: "20px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "15px" }}>
            <h3 style={{ margin: 0, color: "#007bff" }}>
              Create New Address Group
            </h3>
            <button
              type="button"
              className="btn btn-sm btn-outline-secondary"
              onClick={() => {
                setShowCreateForm(false);
                setSelectedObjects([]);
                setSelectedGroups([]);
                setErrors({});
                setSuccessMessage(null);
              }}
            >
              Cancel
            </button>
          </div>
          
          <div style={{ marginBottom: "15px" }}>
            <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
              Group Name *
            </label>
            <input
              type="text"
              value={createForm.name}
              onChange={(e) => {
                const newName = e.target.value.replace(/\s+/g, '_');
                setCreateForm(prev => ({ ...prev, name: newName }));
                setErrors({ ...errors, name: "" });
              }}
              style={{ 
                width: "100%", 
                padding: "8px", 
                borderRadius: "4px", 
                border: errors.name || nameExists ? "1px solid red" : "1px solid #ccc" 
              }}
              placeholder="e.g., GRP_Web_Servers (no spaces, only -_.)"
            />
            {checkingName && (
              <div style={{ color: "#007bff", fontSize: "0.9em" }}>Checking name availability...</div>
            )}
            {nameExists && (
              <div style={{ color: "red", fontSize: "0.9em" }}>An address group with this name already exists</div>
            )}
            {errors.name && !nameExists && (
              <div style={{ color: "red", fontSize: "0.9em" }}>{errors.name}</div>
            )}
          </div>

          <div style={{ marginBottom: "15px" }}>
            <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
              Description
            </label>
            <textarea
              value={createForm.description}
              onChange={(e) => setCreateForm(prev => ({ ...prev, description: e.target.value }))}
              style={{ 
                width: "100%", 
                padding: "8px", 
                borderRadius: "4px", 
                border: "1px solid #ccc",
                minHeight: "60px"
              }}
              placeholder="Optional description for the group"
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

          <div style={{ marginBottom: "15px" }}>
            <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
              Type
            </label>
            <input
              type="text"
              value="static"
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
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <label style={{ fontWeight: "bold" }}>Members *</label>
              <button
                type="button"
                className="btn btn-sm btn-outline-primary"
                onClick={() => {
                  setShowObjectBrowser(!showObjectBrowser);
                  if (!showObjectBrowser) {
                    setBrowserType("objects");
                  }
                }}
              >
                {showObjectBrowser ? "Hide Browser" : "Browse Address Objects/Groups"}
              </button>
            </div>
            
            {(selectedObjects.length > 0 || selectedGroups.length > 0) && (
              <div style={{ 
                margin: "10px 0", 
                padding: "10px", 
                backgroundColor: "#f0f8ff",
                borderRadius: "4px"
              }}>
                <strong>Selected Members:</strong>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "5px", marginTop: "5px" }}>
                  {selectedObjects.map(obj => (
                    <span 
                      key={obj}
                      style={{
                        backgroundColor: "#e1f0ff",
                        padding: "3px 8px",
                        borderRadius: "4px",
                        display: "flex",
                        alignItems: "center"
                      }}
                    >
                      {obj}
                      <button
                        onClick={() => toggleObjectSelection(obj)}
                        style={{
                          background: "none",
                          border: "none",
                          color: "#ff6b6b",
                          marginLeft: "5px",
                          cursor: "pointer"
                        }}
                      >
                        ×
                      </button>
                    </span>
                  ))}
                  {selectedGroups.map(group => (
                    <span 
                      key={group}
                      style={{
                        backgroundColor: "#e1f0ff",
                        padding: "3px 8px",
                        borderRadius: "4px",
                        display: "flex",
                        alignItems: "center"
                      }}
                    >
                      {group} (Group)
                      <button
                        onClick={() => toggleGroupSelection(group)}
                        style={{
                          background: "none",
                          border: "none",
                          color: "#ff6b6b",
                          marginLeft: "5px",
                          cursor: "pointer"
                        }}
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            {errors.members && (
              <div style={{ color: "red", fontSize: "0.9em" }}>{errors.members}</div>
            )}
          </div>

          {showObjectBrowser && (
            <div style={{ 
              marginBottom: "15px",
              maxHeight: "400px",
              overflowY: "auto",
              border: "1px solid #ddd",
              borderRadius: "4px",
              padding: "10px"
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "10px" }}>
                <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
                  <h4 style={{ margin: 0 }}>
                    {browserType === "objects" ? "Address Objects" : "Address Groups"}
                  </h4>
                  <div className="btn-group btn-group-sm">
                    <button
                      type="button"
                      className={`btn ${browserType === "objects" ? "btn-primary" : "btn-outline-primary"}`}
                      onClick={() => setBrowserType("objects")}
                    >
                      Objects
                    </button>
                    <button
                      type="button"
                      className={`btn ${browserType === "groups" ? "btn-primary" : "btn-outline-primary"}`}
                      onClick={() => setBrowserType("groups")}
                    >
                      Groups
                    </button>
                  </div>
                </div>
                <button
                  type="button"
                  className="btn btn-sm btn-outline-success"
                  onClick={handleCreateNewObject}
                >
                  + Create New Address Object
                </button>
              </div>

              <div style={{ marginBottom: "10px" }}>
                <input
                  type="text"
                  value={browserSearchTerm}
                  onChange={(e) => setBrowserSearchTerm(e.target.value)}
                  style={{ 
                    width: "100%", 
                    padding: "6px 10px", 
                    borderRadius: "4px", 
                    border: "1px solid #ccc" 
                  }}
                  placeholder={`Search ${browserType === "objects" ? "address objects" : "address groups"}...`}
                />
              </div>
              
              {loading ? (
                <div style={{ textAlign: "center", padding: "20px" }}>
                  <i className="fa fa-spinner fa-spin" style={{ fontSize: "2em", color: "#007bff" }}></i>
                </div>
              ) : (
                <>
                  {browserType === "objects" ? (
                    filteredObjects.length > 0 ? (
                      <table className="table table-sm table-hover">
                        <thead>
                          <tr>
                            <th>Select</th>
                            <th>Name</th>
                            <th>Type</th>
                            <th>Value</th>
                          </tr>
                        </thead>
                        <tbody>
                          {filteredObjects.map(obj => (
                            <tr key={obj.name}>
                              <td>
                                <input
                                  type="checkbox"
                                  checked={selectedObjects.includes(obj.name)}
                                  onChange={() => toggleObjectSelection(obj.name)}
                                />
                              </td>
                              <td>{obj.name}</td>
                              <td>{obj.type}</td>
                              <td>{obj.value}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    ) : (
                      <div style={{ textAlign: "center", padding: "20px", color: "#666" }}>
                        No address objects found
                      </div>
                    )
                  ) : (
                    filteredGroups.length > 0 ? (
                      <table className="table table-sm table-hover">
                        <thead>
                          <tr>
                            <th>Select</th>
                            <th>Name</th>
                            <th>Type</th>
                            <th>Members</th>
                          </tr>
                        </thead>
                        <tbody>
                          {filteredGroups.map(group => (
                            <tr key={group.name}>
                              <td>
                                <input
                                  type="checkbox"
                                  checked={selectedGroups.includes(group.name)}
                                  onChange={() => toggleGroupSelection(group.name)}
                                />
                              </td>
                              <td>{group.name}</td>
                              <td>{group.type}</td>
                              <td>
                                {group.members?.length > 0 ? (
                                  <div>
                                    {expandedGroups[group.name] ? (
                                      <ul style={{ margin: 0, paddingLeft: "20px" }}>
                                        {group.members.map((member, i) => (
                                          <li key={i}>{member}</li>
                                        ))}
                                      </ul>
                                    ) : (
                                      <ul style={{ margin: 0, paddingLeft: "20px" }}>
                                        {group.members.slice(0, 3).map((member, i) => (
                                          <li key={i}>{member}</li>
                                        ))}
                                        {group.members.length > 3 && (
                                          <li>
                                            <button
                                              onClick={() => toggleGroupExpansion(group.name)}
                                              style={{
                                                background: "none",
                                                border: "none",
                                                color: "#007bff",
                                                padding: 0,
                                                cursor: "pointer"
                                              }}
                                            >
                                              +{group.members.length - 3} more
                                            </button>
                                          </li>
                                        )}
                                      </ul>
                                    )}
                                  </div>
                                ) : (
                                  <span style={{ color: "#666", fontStyle: "italic" }}>No members</span>
                                )}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    ) : (
                      <div style={{ textAlign: "center", padding: "20px", color: "#666" }}>
                        No address groups found
                      </div>
                    )
                  )}
                </>
              )}
            </div>
          )}

          <div style={{ display: "flex", gap: "10px" }}>
            <button
              type="button"
              className="btn btn-secondary"
              style={{ flex: 1, padding: "10px" }}
              onClick={() => {
                setSelectedObjects([]);
                setSelectedGroups([]);
                setErrors({});
              }}
            >
              Clear Selections
            </button>
            <button
              type="submit"
              className="btn btn-success"
              style={{ flex: 1, padding: "10px" }}
              disabled={loading || nameExists}
            >
              {loading ? "Creating..." : "Create Group"}
            </button>
          </div>
        </form>
      )}

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
        </div>
      )}

      {loading && <Modal message="Processing request, please wait..." />}
    </div>
  );
};

export default AddressGroupChecker;