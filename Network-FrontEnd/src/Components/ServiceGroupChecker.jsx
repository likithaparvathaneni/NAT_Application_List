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

const ServiceGroupChecker = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [errors, setErrors] = useState({});
  const [serviceItems, setServiceItems] = useState([]);
  const [selectedItems, setSelectedItems] = useState([]);
  const [showBrowser, setShowBrowser] = useState(false);
  const [browserSearchTerm, setBrowserSearchTerm] = useState("");
  const [createForm, setCreateForm] = useState({
    name: "",
    deviceGroup: "shared",
    tags: ""
  });
  const [checkingName, setCheckingName] = useState(false);
  const [nameExists, setNameExists] = useState(false);
  const [successMessage, setSuccessMessage] = useState(null);
  const [expandedGroups, setExpandedGroups] = useState({});
  const navigate = useNavigate();
  const location = useLocation();

  // Initialize form state from location if coming back from service object creation
  useEffect(() => {
    if (location.state?.previousFormData) {
      setCreateForm(location.state.previousFormData.createForm || {
        name: "",
        deviceGroup: "shared",
        tags: ""
      });
      setSelectedItems(location.state.previousFormData.selectedItems || []);
      setShowCreateForm(true);
      setShowBrowser(true);
    }

    if (location.state?.fromObjectCreation && location.state?.newlyCreatedObject) {
      if (!selectedItems.includes(location.state.newlyCreatedObject)) {
        setSelectedItems(prev => [...prev, location.state.newlyCreatedObject]);
      }
    }
  }, [location.state]);

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
      const response = await axios.post("http://127.0.0.1:8000/check_service_group_name/", { 
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
    setShowBrowser(false);
    
    try {
      const response = await axios.post("http://127.0.0.1:8000/search_service_group/", { 
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

  const loadServiceItems = async () => {
    setLoading(true);
    try {
      const [objectsRes, groupsRes] = await Promise.all([
        axios.get("http://127.0.0.1:8000/list_service_objects/"),
        axios.get("http://127.0.0.1:8000/list_service_groups/")
      ]);

      const objects = objectsRes.data.objects || [];
      const groups = groupsRes.data.groups || [];

      const serviceObjectMap = {};
      objects.forEach(obj => {
        serviceObjectMap[obj.name] = {
          protocol: obj.protocol || 'any',
          port: obj.port || 'any'
        };
      });

      const combinedItems = [
        ...objects.map(obj => ({
          ...obj,
          type: 'object',
          displayText: `${obj.name} (${obj.protocol || 'any'}/${obj.port || 'any'})`,
          protocol: obj.protocol || 'any',
          port: obj.port || 'any'
        })),
        ...groups.map(group => ({
          ...group,
          type: 'group',
          displayText: `${group.name} (Group)`,
          memberDetails: group.members.map(member => {
            const obj = serviceObjectMap[member];
            return obj 
              ? `${member} (${obj.protocol}/${obj.port})` 
              : member;
          })
        }))
      ];

      setServiceItems(combinedItems);
    } catch (error) {
      console.error("Error loading service items:", error);
      setErrors({ 
        general: error.response?.data?.message || "Failed to load service items." 
      });
    } finally {
      setLoading(false);
    }
  };

  const toggleItemSelection = (itemName) => {
    setSelectedItems(prev => 
      prev.includes(itemName) 
        ? prev.filter(name => name !== itemName)
        : [...prev, itemName]
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
  
  if (selectedItems.length === 0) {
    setErrors({ members: "Please select at least one service object or group" });
    return;
  }

  if (nameExists) {
    setErrors({ name: "A service group with this name already exists" });
    return;
  }

  setLoading(true);
  try {
    const response = await axios.post("http://127.0.0.1:8000/create_service_group/", {
      name: createForm.name.trim(),
      members: selectedItems,
      deviceGroup: createForm.deviceGroup,
      tags: createForm.tags
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    });

    if (response.data.success) {
      setSuccessMessage(`Service group "${response.data.group_name}" created successfully!`);
      // Show the newly created group in results
      setResults({
        groups: [{
          name: response.data.group_name,
          details: {
            members: selectedItems,
            tags: createForm.tags ? createForm.tags.split(',').map(tag => tag.trim()) : [],
            location: 'shared'
          }
        }]
      });
      
      // Reset form and close it
      setCreateForm({
        name: "",
        deviceGroup: "shared",
        tags: ""
      });
      setSelectedItems([]);
      setErrors({});
      setShowCreateForm(false);
      setShowBrowser(false);
      
      // Clear success message after 5 seconds
      setTimeout(() => setSuccessMessage(null), 5000);
    } else {
      setErrors({
        general: response.data.error || "Failed to create service group."
      });
    }
  } catch (error) {
    console.error("Creation error:", error);
    setErrors({ 
      general: error.response?.data?.error || 
             "Failed to create service group. Please check Panorama connectivity." 
    });
  } finally {
    setLoading(false);
  }
};

  const handleCreateNewObject = () => {
    navigate("/object-checker/service", { 
      state: { 
        fromGroupCreation: true,
        previousPath: location.pathname,
        previousFormData: {
          createForm,
          selectedItems
        }
      }
    });
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
    if (showBrowser) {
      loadServiceItems();
    }
  }, [showBrowser]);

  useEffect(() => {
    if (!searchTerm.trim() && results) {
      setResults(null);
    }
  }, [searchTerm]);

  const filteredItems = serviceItems.filter(item => 
    item.displayText.toLowerCase().includes(browserSearchTerm.toLowerCase())
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
        Service Group Checker
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
            Search Service Groups or Objects
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
            placeholder="Enter group name or service (e.g., tcp/80) to search"
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
          + Create New Service Group
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
              <strong>✅ Matching Service Groups Found:</strong>
              {results.groups.map((group, index) => (
                <div key={index} style={{ 
                  marginTop: index > 0 ? "15px" : "10px",
                  paddingTop: index > 0 ? "15px" : "0",
                  borderTop: index > 0 ? "1px solid #c3e6cb" : "none"
                }}>
                  <p><strong>Name:</strong> {group.name}</p>
                  {group.details && (
                    <div style={{ marginTop: "5px" }}>
                      {group.details.members?.length > 0 && (
                        <div>
                          <p><strong>Members ({group.details.members.length}):</strong></p>
                          <ul style={{ marginLeft: "20px" }}>
                            {group.details.members.map((member, i) => {
                              const item = serviceItems.find(item => item.name === member);
                              return (
                                <li key={i}>
                                  {member}
                                  {item?.type === 'group' && 
                                    ` (Group with ${item.members?.length || 0} members)`}
                                  {item?.type === 'object' && 
                                    ` (${item.protocol || 'any'}/${item.port || 'any'})`}
                                </li>
                              );
                            })}
                          </ul>
                        </div>
                      )}
                      {group.details.tags && group.details.tags.length > 0 && (
                        <p><strong>Tags:</strong> {group.details.tags.join(', ')}</p>
                      )}
                      <p><strong>Location:</strong> {group.details.location || 'shared'}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : results.objects?.length > 0 ? (
            <div>
              <strong>🔍 Matching Service Objects Found:</strong>
              {results.objects.map((obj, index) => (
                <div key={index} style={{ 
                  marginTop: index > 0 ? "15px" : "10px",
                  paddingTop: index > 0 ? "15px" : "0",
                  borderTop: index > 0 ? "1px solid #c3e6cb" : "none"
                }}>
                  <p><strong>Name:</strong> {obj.name}</p>
                  <p><strong>Protocol:</strong> {obj.protocol || 'any'}</p>
                  <p><strong>Port:</strong> {obj.port || 'any'}</p>
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
                    <p style={{ color: "#666", fontStyle: "italic" }}>Not a member of any service groups</p>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div>
              <strong>❌ No matching service groups or objects found.</strong>
            </div>
          )}
        </div>
      )}

      {showCreateForm && (
        <form onSubmit={handleCreateGroup} style={{ marginTop: "20px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "15px" }}>
            <h3 style={{ margin: 0, color: "#007bff" }}>
              Create New Service Group
            </h3>
            <button
              type="button"
              className="btn btn-sm btn-outline-secondary"
              onClick={() => {
                setShowCreateForm(false);
                setSelectedItems([]);
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
              placeholder="e.g., GRP_Web_Services (no spaces, only -_.)"
            />
            {checkingName && (
              <div style={{ color: "#007bff", fontSize: "0.9em" }}>Checking name availability...</div>
            )}
            {nameExists && (
              <div style={{ color: "red", fontSize: "0.9em" }}>A service group with this name already exists</div>
            )}
            {errors.name && !nameExists && (
              <div style={{ color: "red", fontSize: "0.9em" }}>{errors.name}</div>
            )}
          </div>

          <div style={{ marginBottom: "15px" }}>
            <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
              Tags (comma separated)
            </label>
            <input
              type="text"
              value={createForm.tags}
              onChange={(e) => setCreateForm(prev => ({ ...prev, tags: e.target.value }))}
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

          <div style={{ marginBottom: "15px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <label style={{ fontWeight: "bold" }}>Members *</label>
              <button
                type="button"
                className="btn btn-sm btn-outline-primary"
                onClick={() => {
                  setShowBrowser(!showBrowser);
                  setSuccessMessage(null);
                }}
              >
                {showBrowser ? "Hide Browser" : "Browse Services"}
              </button>
            </div>
            
            {selectedItems.length > 0 && (
              <div style={{ 
                margin: "10px 0", 
                padding: "10px", 
                backgroundColor: "#f0f8ff",
                borderRadius: "4px"
              }}>
                <strong>Selected Items ({selectedItems.length}):</strong>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "5px", marginTop: "5px" }}>
                  {selectedItems.map(item => {
                    const serviceItem = serviceItems.find(si => si.name === item);
                    return (
                      <span 
                        key={item}
                        style={{
                          backgroundColor: "#e1f0ff",
                          padding: "3px 8px",
                          borderRadius: "4px",
                          display: "flex",
                          alignItems: "center"
                        }}
                      >
                        {item}
                        {serviceItem?.type === 'group' && 
                          ` (${serviceItem.members?.length || 0} members)`}
                        {serviceItem?.type === 'object' && 
                          ` (${serviceItem.protocol || 'any'}/${serviceItem.port || 'any'})`}
                        <button
                          onClick={() => toggleItemSelection(item)}
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
                    );
                  })}
                </div>
              </div>
            )}
            
            {errors.members && (
              <div style={{ color: "red", fontSize: "0.9em" }}>{errors.members}</div>
            )}
          </div>

          {showBrowser && (
            <div style={{ 
              marginBottom: "15px",
              maxHeight: "400px",
              overflowY: "auto",
              border: "1px solid #ddd",
              borderRadius: "4px",
              padding: "10px"
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "10px" }}>
                <h4 style={{ margin: 0 }}>Service Objects & Groups</h4>
                <button
                  type="button"
                  className="btn btn-sm btn-outline-success"
                  onClick={handleCreateNewObject}
                >
                  + Create New Service Object
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
                  placeholder="Search service objects or groups..."
                />
              </div>
              
              {loading ? (
                <div style={{ textAlign: "center", padding: "20px" }}>
                  <i className="fa fa-spinner fa-spin" style={{ fontSize: "2em", color: "#007bff" }}></i>
                </div>
              ) : (
                filteredItems.length > 0 ? (
                  <table className="table table-sm table-hover">
                    <thead>
                      <tr>
                        <th>Select</th>
                        <th>Name</th>
                        <th>Type</th>
                        <th>Details</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredItems.map(item => (
                        <tr key={item.name}>
                          <td>
                            <input
                              type="checkbox"
                              checked={selectedItems.includes(item.name)}
                              onChange={() => toggleItemSelection(item.name)}
                            />
                          </td>
                          <td>{item.name}</td>
                          <td>
                            <span className={`badge ${item.type === 'object' ? 'bg-primary' : 'bg-success'}`}>
                              {item.type === 'object' ? 'Object' : 'Group'}
                            </span>
                          </td>
                          <td>
                            {item.type === 'object' ? (
                              `${item.protocol || 'any'}/${item.port || 'any'}`
                            ) : (
                              <div>
                                {item.members?.length || 0} members
                                {expandedGroups[item.name] ? (
                                  <ul style={{ margin: 0, paddingLeft: "20px" }}>
                                    {item.memberDetails?.map((member, i) => (
                                      <li key={i}>{member}</li>
                                    ))}
                                  </ul>
                                ) : (
                                  <ul style={{ margin: 0, paddingLeft: "20px" }}>
                                    {item.memberDetails?.slice(0, 3).map((member, i) => (
                                      <li key={i}>{member}</li>
                                    ))}
                                    {item.memberDetails?.length > 3 && (
                                      <li>
                                        <button
                                          onClick={() => toggleGroupExpansion(item.name)}
                                          style={{
                                            background: "none",
                                            border: "none",
                                            color: "#007bff",
                                            padding: 0,
                                            cursor: "pointer"
                                          }}
                                        >
                                          +{item.memberDetails.length - 3} more
                                        </button>
                                      </li>
                                    )}
                                  </ul>
                                )}
                              </div>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <div style={{ textAlign: "center", padding: "20px", color: "#666" }}>
                    No service items found
                  </div>
                )
              )}
            </div>
          )}

          <div style={{ display: "flex", gap: "10px" }}>
            <button
              type="button"
              className="btn btn-secondary"
              style={{ flex: 1, padding: "10px" }}
              onClick={() => {
                setSelectedItems([]);
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

export default ServiceGroupChecker;