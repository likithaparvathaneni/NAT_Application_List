import React, { useState, useEffect } from "react";
import axios from "axios";
import "../Css/button.css";
import { useNavigate } from "react-router-dom";
import AddRulePreview from "./AddRulePreview";

const CreateObjectModal = ({ isOpen, onClose, onSuccess, ipValue }) => {
  const [objectName, setObjectName] = useState("");
  const [objectType, setObjectType] = useState("ip-netmask");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (ipValue && isOpen) {
      // Generate a suggested name based on the IP value
      const suggestedName = ipValue.replace(/[^a-zA-Z0-9]/g, '_').replace(/^_+|_+$/g, '');
      setObjectName(suggestedName);
    }
  }, [ipValue, isOpen]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await axios.post("http://127.0.0.1:8000/create_object/", {
        objectName,
        value: ipValue,
        type: objectType,
        description
      });

      if (response.data.success) {
        onSuccess(objectName);
        onClose();
      } else {
        setError(response.data.error || "Failed to create object");
      }
    } catch (err) {
      setError(err.response?.data?.error || "Failed to create object");
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content" style={{ maxWidth: "500px" }}>
        <h3>Create Address Object</h3>
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: "15px" }}>
            <label>IP Value: </label>
            <input
              type="text"
              value={ipValue}
              disabled
              style={{ padding: "8px", width: "100%" }}
            />
          </div>

          <div style={{ marginBottom: "15px" }}>
            <label>Object Name: *</label>
            <input
              type="text"
              value={objectName}
              onChange={(e) => setObjectName(e.target.value)}
              required
              style={{ padding: "8px", width: "100%" }}
              placeholder="Enter object name"
            />
          </div>

          <div style={{ marginBottom: "15px" }}>
            <label>Object Type: </label>
            <select
              value={objectType}
              onChange={(e) => setObjectType(e.target.value)}
              style={{ padding: "8px", width: "100%" }}
            >
              <option value="ip-netmask">IP Netmask</option>
              <option value="ip-range">IP Range</option>
              <option value="fqdn">FQDN</option>
            </select>
          </div>

          <div style={{ marginBottom: "15px" }}>
            <label>Description: </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              style={{ padding: "8px", width: "100%", minHeight: "60px" }}
              placeholder="Optional description"
            />
          </div>

          {error && <div style={{ color: "red", marginBottom: "15px" }}>{error}</div>}

          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <button
              type="button"
              onClick={onClose}
              className="glass-button"
              style={{ backgroundColor: "#6c757d" }}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="glass-button"
              disabled={loading || !objectName}
            >
              {loading ? "Creating..." : "Create Object"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const CreateServiceModal = ({ isOpen, onClose, onSuccess, serviceValue, serviceType }) => {
  const [objectName, setObjectName] = useState("");
  const [protocol, setProtocol] = useState("tcp");
  const [port, setPort] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [isGroup, setIsGroup] = useState(serviceType === "group");
  const [members, setMembers] = useState("");
  const [availableServices, setAvailableServices] = useState([]);

  useEffect(() => {
    if (serviceValue && isOpen) {
      // Parse service value for protocol and port
      if (serviceValue.includes('/')) {
        const [proto, portVal] = serviceValue.split('/');
        setProtocol(proto.toLowerCase());
        setPort(portVal);
        
        // Generate suggested name
        const suggestedName = `${proto.toUpperCase()}-${portVal}`.replace(/[^a-zA-Z0-9]/g, '_');
        setObjectName(suggestedName);
      } else {
        setObjectName(serviceValue.replace(/[^a-zA-Z0-9]/g, '_'));
      }
      
      // Fetch available services for group creation
      if (serviceType === "group") {
        fetchServiceObjects();
      }
    }
  }, [serviceValue, isOpen, serviceType]);

  const fetchServiceObjects = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:8000/list_service_objects/");
      setAvailableServices(response.data.objects || []);
    } catch (error) {
      console.error("Error fetching service objects:", error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      let response;
      if (isGroup) {
        // Create service group
        response = await axios.post("http://127.0.0.1:8000/create_service_group/", {
          name: objectName,
          members: members.split(',').map(m => m.trim()).filter(m => m),
          description
        });
      } else {
        // Create service object
        response = await axios.post("http://127.0.0.1:8000/create_service/", {
          objectName,
          protocol,
          port,
          description
        });
      }

      if (response.data.success) {
        onSuccess(objectName);
        onClose();
      } else {
        setError(response.data.error || `Failed to create service ${isGroup ? 'group' : 'object'}`);
      }
    } catch (err) {
      setError(err.response?.data?.error || `Failed to create service ${isGroup ? 'group' : 'object'}`);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content" style={{ maxWidth: "600px" }}>
        <h3>Create Service {isGroup ? 'Group' : 'Object'}</h3>
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: "15px" }}>
            <label>
              <input
                type="checkbox"
                checked={isGroup}
                onChange={(e) => setIsGroup(e.target.checked)}
                style={{ marginRight: "8px" }}
              />
              Create as Service Group
            </label>
          </div>

          {!isGroup && (
            <>
              <div style={{ marginBottom: "15px" }}>
                <label>Protocol: </label>
                <select
                  value={protocol}
                  onChange={(e) => setProtocol(e.target.value)}
                  style={{ padding: "8px", width: "100%" }}
                >
                  <option value="tcp">TCP</option>
                  <option value="udp">UDP</option>
                  <option value="icmp">ICMP</option>
                  <option value="sctp">SCTP</option>
                </select>
              </div>

              <div style={{ marginBottom: "15px" }}>
                <label>Port: </label>
                <input
                  type="text"
                  value={port}
                  onChange={(e) => setPort(e.target.value)}
                  required={!isGroup}
                  style={{ padding: "8px", width: "100%" }}
                  placeholder="e.g., 80, 443, 1000-2000"
                />
              </div>
            </>
          )}

          <div style={{ marginBottom: "15px" }}>
            <label>{isGroup ? 'Group' : 'Object'} Name: *</label>
            <input
              type="text"
              value={objectName}
              onChange={(e) => setObjectName(e.target.value)}
              required
              style={{ padding: "8px", width: "100%" }}
              placeholder={`Enter ${isGroup ? 'group' : 'object'} name`}
            />
          </div>

          {isGroup && (
            <div style={{ marginBottom: "15px" }}>
              <label>Members: *</label>
              <select
                multiple
                value={members.split(',').map(m => m.trim()).filter(m => m)}
                onChange={(e) => {
                  const selected = Array.from(e.target.selectedOptions, option => option.value);
                  setMembers(selected.join(','));
                }}
                style={{ padding: "8px", width: "100%", minHeight: "100px" }}
              >
                <option value="">-- Select Service Objects --</option>
                {availableServices.map((service, index) => (
                  <option key={index} value={service.name}>
                    {service.name} ({service.protocol}/{service.port})
                  </option>
                ))}
              </select>
              <div style={{ fontSize: "0.8em", color: "#666", marginTop: "5px" }}>
                Hold Ctrl/Cmd to select multiple members
              </div>
            </div>
          )}

          <div style={{ marginBottom: "15px" }}>
            <label>Description: </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              style={{ padding: "8px", width: "100%", minHeight: "60px" }}
              placeholder="Optional description"
            />
          </div>

          {error && <div style={{ color: "red", marginBottom: "15px" }}>{error}</div>}

          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <button
              type="button"
              onClick={onClose}
              className="glass-button"
              style={{ backgroundColor: "#6c757d" }}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="glass-button"
              disabled={loading || !objectName || (!isGroup && !port)}
            >
              {loading ? "Creating..." : `Create ${isGroup ? 'Group' : 'Object'}`}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const AddingRule = ({ firewalls, formData, onClose, onSuccess }) => {
  const navigate = useNavigate();
  const [selectedFirewall, setSelectedFirewall] = useState("");
  const [hierarchy, setHierarchy] = useState([]);
  const [selectedPath, setSelectedPath] = useState("");
  const [manualLocation, setManualLocation] = useState("");
  const [expandedNodes, setExpandedNodes] = useState(new Set());
  const [loading, setLoading] = useState(false);
  const [ruleType, setRuleType] = useState("post"); // Changed default to post
  const [availableZones, setAvailableZones] = useState([]);
  const [serviceObjects, setServiceObjects] = useState([]);
  const [showServiceDropdown, setShowServiceDropdown] = useState(true);
  const [serviceSearchTerm, setServiceSearchTerm] = useState('');
  const [securityProfiles, setSecurityProfiles] = useState({
    antivirus: [],
    antiSpyware: [],
    vulnerability: [],
    urlFiltering: [],
    fileBlocking: [],
    wildfire: [],
    dataFiltering: [],
    profileGroup: []
  });
  const [availableApplications, setAvailableApplications] = useState([]);
  const [showApplicationDropdown, setShowApplicationDropdown] = useState(true);
  const [applicationSearchTerm, setApplicationSearchTerm] = useState('');
  const [ruleDetails, setRuleDetails] = useState({
    name: "",
    description: "",
    action: formData.Action || "allow",
    disabled: false,
    logSetting: "",
    logStart: true,
    logEnd: true,
    negateSource: false,
    negateDestination: false,
    service: formData.destinationPort || "any",
    application: formData.application || "any",
    sourceZone: formData.sourceZone || "",
    destinationZone: formData.destinationZone || "",
    sourceIP: formData.sourceIP || "",
    destinationIP: formData.destinationIP || "",
    securityProfiles: {
      antivirus: "",
      antiSpyware: "",
      vulnerability: "",
      urlFiltering: "",
      fileBlocking: "",
      wildfire: "",
      dataFiltering: "",
      profileGroup: ""
    }
  });
  const [errors, setErrors] = useState({});
  const [validationErrors, setValidationErrors] = useState({});
  const [apiResponse, setApiResponse] = useState(null);
  const [showServiceCreationModal, setShowServiceCreationModal] = useState(false);
  const [serviceCreationType, setServiceCreationType] = useState("object");
  const [serviceCreationValue, setServiceCreationValue] = useState("");
  const [showObjectCreationModal, setShowObjectCreationModal] = useState(false);
  const [objectCreationField, setObjectCreationField] = useState("");
  const [objectCreationValue, setObjectCreationValue] = useState("");
  const [addressObjectNames, setAddressObjectNames] = useState({
    sourceIP: "",
    destinationIP: ""
  });
  const [showPreview, setShowPreview] = useState(false);

  // Debug: Log when component mounts
  useEffect(() => {
    console.log("AddingRule component mounted");
    fetchSecurityProfiles();
    fetchServiceObjects(); // Fetch service objects on mount
    fetchApplications(); // Fetch applications on mount
  }, []);

  useEffect(() => {
    if (selectedFirewall) {
      fetchHierarchy(selectedFirewall);
      updateZonesFromFormData();
    }
  }, [selectedFirewall, formData]);

  const fetchApplications = async () => {
    try {
      console.log("Fetching applications...");
      const response = await axios.get("http://127.0.0.1:8000/list_applications/");
      console.log("Applications response:", response.data);
      
      if (response.data.status === 'success') {
        setAvailableApplications(response.data.applications || []);
      } else {
        // Fallback to common applications
        const commonApps = [
          'any', 'web-browsing', 'ssl', 'dns', 'http', 'https', 'ftp', 'ssh',
          'smtp', 'pop3', 'imap', 'telnet', 'rdp', 'vnc', 'icmp'
        ];
        setAvailableApplications(commonApps);
      }
    } catch (error) {
      console.error("Error fetching applications:", error);
      // Fallback to basic applications
      const basicApps = ['any', 'web-browsing', 'ssl', 'dns', 'http', 'https', 'ftp', 'ssh'];
      setAvailableApplications(basicApps);
    }
  };

  const fetchServiceObjects = async () => {
    try {
      console.log("Fetching service objects...");
      const response = await axios.get("http://127.0.0.1:8000/list_service_objects/");
      console.log("Service objects response:", response.data);
      
      const objects = response.data.objects || [];
      const serviceOptions = objects.map(obj => ({
        name: obj.name,
        display: `${obj.name}${obj.protocol || obj.port ? ` (${obj.protocol || 'tcp'}/${obj.port || 'any'})` : ''}`
      }));
      
      // Add service groups from the objects' groups array
      objects.forEach(obj => {
        if (obj.groups && obj.groups.length > 0) {
          obj.groups.forEach(group => {
            if (!serviceOptions.some(opt => opt.name === group.name)) {
              serviceOptions.push({
                name: group.name,
                display: `${group.name} (service-group)`
              });
            }
          });
        }
      });
      
      setServiceObjects(serviceOptions);
    } catch (error) {
      console.error("Error fetching service objects:", error);
      setErrors({ service: `Error loading service objects: ${error.message}` });
    }
  };

  const fetchSecurityProfiles = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:8000/list_security_profiles/");
      setSecurityProfiles(response.data.profiles);
    } catch (error) {
      console.error("Error fetching security profiles:", error);
    }
  };

  const updateZonesFromFormData = () => {
    const zones = new Set();
    
    if (formData.sourceZone) {
      zones.add(formData.sourceZone);
    }
    
    if (formData.destinationZone) {
      zones.add(formData.destinationZone);
    }
    
    setAvailableZones(Array.from(zones));
  };

  const fetchHierarchy = async (firewallName) => {
    try {
      setLoading(true);
      setHierarchy([]);
      setSelectedPath("");
      setManualLocation("");
      setExpandedNodes(new Set());
      
      const response = await axios.get(
        `http://127.0.0.1:8000/firewall-hierarchy/`
      );
      
      const firewallData = response.data.data.find(fw => fw.hostname === firewallName);
      
      if (firewallData) {
        const hierarchyTree = buildTreeFromPath(firewallData.path);
        setHierarchy([hierarchyTree]);
        
        const pathParts = [];
        const newExpandedNodes = new Set();
        firewallData.path.forEach(part => {
          pathParts.push(part);
          newExpandedNodes.add(pathParts.join('/'));
        });
        setExpandedNodes(newExpandedNodes);
      } else {
        setHierarchy([]);
      }
      
      setLoading(false);
    } catch (error) {
      console.error("Error fetching hierarchy:", error);
      setLoading(false);
      setErrors({ hierarchy: `Error loading hierarchy: ${error.message}` });
    }
  };

  const buildTreeFromPath = (path) => {
    if (!path || path.length === 0) return null;
    
    let root = { name: path[0], children: [] };
    let current = root;
    
    for (let i = 1; i < path.length; i++) {
      const newNode = { name: path[i], children: [] };
      current.children.push(newNode);
      current = newNode;
    }
    
    return root;
  };

  const handleFirewallChange = (e) => {
    setSelectedFirewall(e.target.value);
    setSelectedPath("");
    setManualLocation("");
    setExpandedNodes(new Set());
  };

  const toggleNode = (nodePath) => {
    const newExpandedNodes = new Set(expandedNodes);
    if (newExpandedNodes.has(nodePath)) {
      newExpandedNodes.delete(nodePath);
    } else {
      newExpandedNodes.add(nodePath);
    }
    setExpandedNodes(newExpandedNodes);
  };

  const handlePathSelect = (path) => {
    setSelectedPath(path);
    setManualLocation(path);
  };

  const handleManualLocationChange = (e) => {
    const value = e.target.value;
    setManualLocation(value);
    if (value === "shared") {
      setSelectedPath("shared");
    } else if (value === selectedPath) {
      // No change needed
    } else {
      setSelectedPath("");
    }
  };

  const handleRuleDetailChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    if (name.startsWith('securityProfiles.')) {
      const profileType = name.split('.')[1];
      setRuleDetails(prev => ({
        ...prev,
        securityProfiles: {
          ...prev.securityProfiles,
          [profileType]: value
        }
      }));
    } else {
      setRuleDetails(prev => ({
        ...prev,
        [name]: type === "checkbox" ? checked : value
      }));
    }
    
    // Clear error when field changes
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = {...prev};
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const validateIP = (ip) => {
    if (ip.toLowerCase() === 'any') return true;
    
    // Check for CIDR notation
    if (ip.includes('/')) {
      const parts = ip.split('/');
      if (parts.length !== 2) return false;
      
      const ipPart = parts[0];
      const cidrPart = parseInt(parts[1], 10);
      
      // Validate CIDR part
      if (isNaN(cidrPart) || cidrPart < 0 || cidrPart > 32) return false;
      
      // Validate IP part
      const ipRegex = /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/;
      if (!ipRegex.test(ipPart)) return false;
      
      const octets = ipPart.split('.').map(Number);
      return octets.every(octet => octet >= 0 && octet <= 255);
    }
    
    // Check for IP range
    if (ip.includes('-')) {
      const parts = ip.split('-');
      if (parts.length !== 2) return false;
      
      const ip1 = parts[0];
      const ip2 = parts[1];
      
      const ipRegex = /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/;
      if (!ipRegex.test(ip1) || !ipRegex.test(ip2)) return false;
      
      const octets1 = ip1.split('.').map(Number);
      const octets2 = ip2.split('.').map(Number);
      
      return octets1.every(octet => octet >= 0 && octet <= 255) && 
             octets2.every(octet => octet >= 0 && octet <= 255);
    }
    
    // Check for single IP
    const ipRegex = /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/;
    if (!ipRegex.test(ip)) return false;
    
    const octets = ip.split('.').map(Number);
    return octets.every(octet => octet >= 0 && octet <= 255);
  };

  const checkAddressObject = async (ipValue) => {
    try {
      const response = await axios.post("http://127.0.0.1:8000/check_object/", {
        address: ipValue
      });
      
      if (response.data.exists && response.data.objects && response.data.objects.length > 0) {
        // Return the first object name found for this IP value
        return response.data.objects[0].objectName;
      }
      return null; // No object found
    } catch (error) {
      console.error("Error checking address object:", error);
      return null;
    }
  };

  const validateService = async (service) => {
    if (service === "any") return true;
    
    try {
        // First check by service name
        const nameCheckResponse = await axios.post("http://127.0.0.1:8000/check_service/", {
            serviceName: service
        });
        
        if (nameCheckResponse.data.exists) {
            return true;
        }
        
        // If service contains protocol/port format, check that too
        if (service.includes('/')) {
            const [protocol, port] = service.split('/');
            const portCheckResponse = await axios.post("http://127.0.0.1:8000/check_service/", {
                protocol: protocol,
                port: port
            });
            
            return portCheckResponse.data.exists;
        }
        
        return false;
    } catch (error) {
        console.error("Error validating service:", error);
        return false;
    }
};

  const validateForm = async () => {
    const newErrors = {};
    const newValidationErrors = {};
    const newObjectNames = { ...addressObjectNames };
    
    if (!selectedFirewall) {
      newErrors.firewall = "Please select a firewall";
    }
    
    const finalLocation = manualLocation.trim() || selectedPath;
    if (!finalLocation) {
      newErrors.location = "Please select or enter a location";
    }
    
    if (!ruleDetails.name) {
      newErrors.name = "Rule name is required";
    } else if (ruleDetails.name.length > 63) {
      newErrors.name = "Rule name must be 63 characters or less";
    } else if (!/^[a-zA-Z0-9\-_.]+$/.test(ruleDetails.name)) {
      newErrors.name = "Only letters, numbers, hyphens, underscores and periods allowed";
    } else if (/^[0-9]/.test(ruleDetails.name)) {
      newErrors.name = "Name cannot start with a number";
    }
    
    if (ruleDetails.description && ruleDetails.description.length > 1024) {
      newErrors.description = "Description too long (max 1024 chars)";
    }
    
    if (!ruleDetails.sourceZone) {
      newValidationErrors.sourceZone = "Source zone is required";
    } else if (!availableZones.includes(ruleDetails.sourceZone)) {
      newValidationErrors.sourceZone = "Invalid source zone";
    }
    
    if (!ruleDetails.destinationZone) {
      newValidationErrors.destinationZone = "Destination zone is required";
    } else if (!availableZones.includes(ruleDetails.destinationZone)) {
      newValidationErrors.destinationZone = "Invalid destination zone";
    }
    
    // Enhanced source IP validation with object checking
    if (!ruleDetails.sourceIP) {
      newValidationErrors.sourceIP = "Source IP is required";
    } else if (ruleDetails.sourceIP.toLowerCase() !== 'any' && !validateIP(ruleDetails.sourceIP)) {
      newValidationErrors.sourceIP = "Invalid IP address (valid formats: 1.1.1.1, 1.1.1.1/24, 1.1.1.1-1.1.1.10)";
    } else if (ruleDetails.sourceIP.toLowerCase() !== 'any') {
      const objectName = await checkAddressObject(ruleDetails.sourceIP);
      if (objectName) {
        newObjectNames.sourceIP = objectName;
      } else {
        newValidationErrors.sourceIP = `Address object for "${ruleDetails.sourceIP}" not found. Would you like to create it?`;
      }
    } else {
      newObjectNames.sourceIP = "any";
    }
    
    // Enhanced destination IP validation with object checking
    if (!ruleDetails.destinationIP) {
      newValidationErrors.destinationIP = "Destination IP is required";
    } else if (ruleDetails.destinationIP.toLowerCase() !== 'any' && !validateIP(ruleDetails.destinationIP)) {
      newValidationErrors.destinationIP = "Invalid IP address (valid formats: 1.1.1.1, 1.1.1.1/24, 1.1.1.1-1.1.1.10)";
    } else if (ruleDetails.destinationIP.toLowerCase() !== 'any') {
      const objectName = await checkAddressObject(ruleDetails.destinationIP);
      if (objectName) {
        newObjectNames.destinationIP = objectName;
      } else {
        newValidationErrors.destinationIP = `Address object for "${ruleDetails.destinationIP}" not found. Would you like to create it?`;
      }
    } else {
      newObjectNames.destinationIP = "any";
    }
    
    if (!ruleDetails.service) {
      newValidationErrors.service = "Service is required";
    } else if (ruleDetails.service !== "any") {
      const serviceExists = await validateService(ruleDetails.service);
      if (!serviceExists) {
        newValidationErrors.service = `Service "${ruleDetails.service}" not found. Would you like to create it?`;
      }
    }
    
    if (!ruleDetails.application) {
      newValidationErrors.application = "Application is required";
    }
    
    setErrors(newErrors);
    setValidationErrors(newValidationErrors);
    setAddressObjectNames(newObjectNames);
    
    return Object.keys(newErrors).length === 0 && Object.keys(newValidationErrors).length === 0;
  };

  const handleCreateObject = (field, value) => {
    setObjectCreationField(field);
    setObjectCreationValue(value);
    setShowObjectCreationModal(true);
  };

  const handleObjectCreated = (objectName) => {
    setShowObjectCreationModal(false);
    
    // Update the address object names with the newly created object
    setAddressObjectNames(prev => ({
      ...prev,
      [objectCreationField]: objectName
    }));
    
    // Clear the validation error for the field
    setValidationErrors(prev => {
      const newErrors = {...prev};
      delete newErrors[objectCreationField];
      return newErrors;
    });
  };

  const handleCreateService = (serviceValue, serviceType = "object") => {
    setServiceCreationValue(serviceValue);
    setServiceCreationType(serviceType);
    setShowServiceCreationModal(true);
  };

  const handleServiceCreated = (serviceName) => {
    setShowServiceCreationModal(false);
    setRuleDetails(prev => ({
      ...prev,
      service: serviceName
    }));
    setValidationErrors(prev => {
      const newErrors = {...prev};
      delete newErrors.service;
      return newErrors;
    });
    
    // Refresh service objects list
    fetchServiceObjects();
  };

  const prepareRuleData = () => {
    const finalLocation = manualLocation.trim() || selectedPath;
    
    // Use the address object names instead of raw IP values
    return {
      name: ruleDetails.name,
      description: ruleDetails.description,
      sourceZone: ruleDetails.sourceZone,
      sourceIP: ruleDetails.sourceIP.toLowerCase() === 'any' ? 'any' : addressObjectNames.sourceIP,
      destinationZone: ruleDetails.destinationZone,
      destinationIP: ruleDetails.destinationIP.toLowerCase() === 'any' ? 'any' : addressObjectNames.destinationIP,
      destinationPort: ruleDetails.service,
      application: ruleDetails.application,
      action: ruleDetails.action,
      location: finalLocation,
      rule_type: ruleType,
      disabled: ruleDetails.disabled,
      logSetting: ruleDetails.logSetting,
      logStart: ruleDetails.logStart,
      logEnd: ruleDetails.logEnd,
      negateSource: ruleDetails.negateSource,
      negateDestination: ruleDetails.negateDestination,
      securityProfiles: ruleDetails.securityProfiles
    };
  };

  const handlePreview = async () => {
    const isValid = await validateForm();
    if (!isValid) {
      return;
    }
    
    setShowPreview(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const isValid = await validateForm();
    if (!isValid) {
      return;
    }

    try {
      setLoading(true);
      const ruleData = prepareRuleData();

      console.log("Creating rule with data:", ruleData);

      const response = await axios.post("http://127.0.0.1:8000/create-rule/", ruleData);
      setApiResponse(response.data);
      
      if (response.data.success) {
        alert(`Rule created successfully at location: ${ruleData.location}`);
        onSuccess();
        onClose();
      } else {
        setErrors({ 
          submit: response.data.error || 
                 "Failed to create rule. " + 
                 (response.data.details ? `Details: ${response.data.details}` : '') 
        });
      }
    } catch (error) {
      console.error("Error creating rule:", error);
      let errorMessage = "Failed to create rule";
      if (error.response) {
        errorMessage += `: ${error.response.data.error || error.response.statusText}`;
        if (error.response.data.details) {
          errorMessage += ` (${error.response.data.details})`;
        }
      }
      setErrors({ submit: errorMessage });
    } finally {
      setLoading(false);
    }
  };

  const renderHierarchyNode = (node, path = "") => {
    if (!node) return null;
    
    const nodePath = path ? `${path}/${node.name}` : node.name;
    const isExpanded = expandedNodes.has(nodePath);
    const hasChildren = node.children && node.children.length > 0;
    
    return (
      <div key={nodePath} style={{ marginLeft: path ? "15px" : "0" }}>
        <div 
          style={{ 
            display: "flex",
            alignItems: "center",
            cursor: hasChildren ? "pointer" : "default",
            fontWeight: selectedPath === nodePath ? "bold" : "normal",
            color: selectedPath === nodePath ? "#007bff" : "inherit",
            backgroundColor: selectedPath === nodePath ? "#f0f8ff" : "transparent",
            padding: "4px 8px",
            borderRadius: "4px"
          }}
        >
          {hasChildren ? (
            <span 
              onClick={(e) => {
                e.stopPropagation();
                toggleNode(nodePath);
              }}
              style={{ marginRight: "5px", width: "20px" }}
            >
              {isExpanded ? "▼" : "▶"}
            </span>
          ) : (
            <span style={{ marginRight: "5px", width: "20px" }}>•</span>
          )}
          <span 
            onClick={() => handlePathSelect(nodePath)}
            style={{ padding: "2px 0", flex: 1 }}
          >
            {node.name}
          </span>
        </div>
        {isExpanded && hasChildren && (
          <div style={{ marginLeft: "15px" }}>
            {node.children.map(child => renderHierarchyNode(child, nodePath))}
          </div>
        )}
      </div>
    );
  };

  const renderSecurityProfileSection = () => (
    <div style={{ marginTop: "20px", borderTop: "1px solid #ddd", paddingTop: "15px" }}>
      <h4>Security Profiles</h4>
      
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "15px" }}>
        {Object.entries(securityProfiles).map(([profileType, profiles]) => (
          <div key={profileType}>
            <label>{profileType.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}: </label>
            <select
              name={`securityProfiles.${profileType}`}
              value={ruleDetails.securityProfiles[profileType]}
              onChange={handleRuleDetailChange}
              style={{ padding: "8px", width: "100%" }}
            >
              <option value="">None</option>
              {profiles.map((profile, index) => (
                <option key={index} value={profile.name}>
                  {profile.name}
                </option>
              ))}
            </select>
          </div>
        ))}
      </div>
    </div>
  );

  const renderIPField = (field, label) => (
    <div style={{ marginBottom: "15px" }}>
      <label>{label}: </label>
      <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
        <input
          type="text"
          name={field}
          value={ruleDetails[field]}
          onChange={handleRuleDetailChange}
          required
          style={{ flex: 1, padding: "8px" }}
          disabled={loading}
          placeholder="IP, CIDR, range, or 'any'"
        />
        {validationErrors[field] && validationErrors[field].includes("Would you like to create it?") && (
          <button
            type="button"
            className="btn btn-sm btn-primary"
            onClick={() => handleCreateObject(field, ruleDetails[field])}
            style={{ whiteSpace: 'nowrap' }}
          >
            Create Object
          </button>
        )}
      </div>
      {validationErrors[field] && (
        <div style={{ color: "red", fontSize: "0.8em", marginTop: "5px" }}>
          {validationErrors[field]}
        </div>
      )}
      {addressObjectNames[field] && addressObjectNames[field] !== ruleDetails[field] && (
        <div style={{ color: "green", fontSize: "0.8em", marginTop: "5px" }}>
          Will use address object: <strong>{addressObjectNames[field]}</strong>
        </div>
      )}
      
      {/* Negate checkbox placed below the IP field */}
      <div style={{ marginTop: "5px" }}>
        <label>
          <input
            type="checkbox"
            name={field === 'sourceIP' ? 'negateSource' : 'negateDestination'}
            checked={field === 'sourceIP' ? ruleDetails.negateSource : ruleDetails.negateDestination}
            onChange={handleRuleDetailChange}
            disabled={loading}
            style={{ marginRight: "5px" }}
          />
          Negate {field === 'sourceIP' ? 'Source' : 'Destination'}
        </label>
      </div>
    </div>
  );

  const renderServiceField = () => (
    <div style={{ marginBottom: "15px" }}>
      <label>Service: </label>
      {showServiceDropdown ? (
        <div>
          <div style={{ display: 'flex', gap: '10px', marginBottom: '5px' }}>
            <input
              type="text"
              placeholder="Search services..."
              value={serviceSearchTerm}
              onChange={(e) => setServiceSearchTerm(e.target.value)}
              style={{ flex: 1, padding: "8px" }}
            />
            <button
              type="button"
              className="btn btn-sm btn-outline-secondary"
              onClick={() => {
                setShowServiceDropdown(false);
                setRuleDetails(prev => ({ ...prev, service: '' }));
              }}
            >
              Enter Custom
            </button>
          </div>
          <select
            name="service"
            value={ruleDetails.service}
            onChange={(e) => {
              if (e.target.value === 'CREATE_NEW') {
                setShowServiceCreationModal(true);
                setServiceCreationType("object");
              } else {
                handleRuleDetailChange(e);
              }
            }}
            style={{ padding: "8px", width: "100%" }}
            disabled={loading}
          >
            <option value="">-- Select Service --</option>
            <option value="any">any</option>
            {serviceObjects
              .filter(obj => 
                obj.name.toLowerCase().includes(serviceSearchTerm.toLowerCase()) ||
                obj.display.toLowerCase().includes(serviceSearchTerm.toLowerCase())
              )
              .map((obj) => (
                <option key={obj.name} value={obj.name}>
                  {obj.display}
                </option>
              ))}
            <option value="CREATE_NEW" style={{ fontWeight: 'bold', color: '#007bff' }}>
              + Create New Service Object
            </option>
          </select>
        </div>
      ) : (
        <div style={{ display: 'flex', gap: '10px' }}>
          <input
            type="text"
            name="service"
            value={ruleDetails.service}
            onChange={handleRuleDetailChange}
            style={{ flex: 1, padding: "8px" }}
            placeholder="Enter service (e.g., tcp/80, udp/53, or object name)"
          />
          <button
            type="button"
            className="btn btn-sm btn-outline-secondary"
            onClick={() => setShowServiceDropdown(true)}
          >
            Browse Existing
          </button>
        </div>
      )}
      {validationErrors.service && (
        <div style={{ color: "red", fontSize: "0.8em" }}>
          {validationErrors.service}
          {validationErrors.service.includes("Would you like to create it?") && (
            <div style={{ marginTop: "5px" }}>
              <button 
                type="button" 
                className="btn btn-sm btn-primary"
                onClick={() => handleCreateService(ruleDetails.service, "object")}
              >
                Create Service Object
              </button>
              <button 
                type="button" 
                className="btn btn-sm btn-secondary ms-2"
                onClick={() => handleCreateService(ruleDetails.service, "group")}
              >
                Create Service Group
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );

  const renderApplicationField = () => (
    <div style={{ marginBottom: "15px" }}>
      <label>Application: </label>
      {showApplicationDropdown ? (
        <div>
          <div style={{ display: 'flex', gap: '10px', marginBottom: '5px' }}>
            <input
              type="text"
              placeholder="Search applications..."
              value={applicationSearchTerm}
              onChange={(e) => setApplicationSearchTerm(e.target.value)}
              style={{ flex: 1, padding: "8px" }}
            />
            <button
              type="button"
              className="btn btn-sm btn-outline-secondary"
              onClick={() => {
                setShowApplicationDropdown(false);
                setRuleDetails(prev => ({ ...prev, application: '' }));
              }}
            >
              Enter Custom
            </button>
          </div>
          <select
            name="application"
            value={ruleDetails.application}
            onChange={handleRuleDetailChange}
            style={{ padding: "8px", width: "100%" }}
            disabled={loading}
          >
            <option value="">-- Select Application --</option>
            <option value="any">any</option>
            {availableApplications
              .filter(app => 
                app.toLowerCase().includes(applicationSearchTerm.toLowerCase())
              )
              .map((app) => (
                <option key={app} value={app}>
                  {app}
                </option>
              ))}
          </select>
        </div>
      ) : (
        <div style={{ display: 'flex', gap: '10px' }}>
          <input
            type="text"
            name="application"
            value={ruleDetails.application}
            onChange={handleRuleDetailChange}
            style={{ flex: 1, padding: "8px" }}
            placeholder="Enter application name"
          />
          <button
            type="button"
            className="btn btn-sm btn-outline-secondary"
            onClick={() => setShowApplicationDropdown(true)}
          >
            Browse Existing
          </button>
        </div>
      )}
      {validationErrors.application && (
        <div style={{ color: "red", fontSize: "0.8em" }}>
          {validationErrors.application}
        </div>
      )}
    </div>
  );

  return (
    <div className="modal-overlay">
      <div className="modal-content" style={{ maxWidth: "1000px", width: "90%", maxHeight: "90vh", overflowY: "auto" }}>
        <h2>Create New Security Rule</h2>
        
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
          {/* Left Column - Firewall and Hierarchy */}
          <div>
            <div style={{ marginBottom: "20px" }}>
              <label>Select Firewall: </label>
              <select 
                value={selectedFirewall} 
                onChange={handleFirewallChange}
                style={{ padding: "8px", marginLeft: "10px", width: "100%" }}
                disabled={loading}
              >
                <option value="">-- Select Firewall --</option>
                {firewalls.map((fw, index) => (
                  <option key={index} value={fw}>{fw}</option>
                ))}
              </select>
              {errors.firewall && <div style={{ color: "red", fontSize: "0.8em" }}>{errors.firewall}</div>}
            </div>

            {selectedFirewall && (
              <>
                <div style={{ marginBottom: "20px" }}>
                  <h4>Firewall Hierarchy</h4>
                  {loading ? (
                    <p>Loading hierarchy...</p>
                  ) : hierarchy.length > 0 ? (
                    <div style={{ 
                      border: "1px solid #ddd", 
                      padding: "10px",
                      maxHeight: "300px",
                      overflowY: "auto",
                      backgroundColor: "#f9f9f9",
                      borderRadius: "4px"
                    }}>
                      {hierarchy.map((node, index) => renderHierarchyNode(node))}
                    </div>
                  ) : (
                    <p>No hierarchy data available for selected firewall</p>
                  )}
                </div>
                
                <div style={{ marginBottom: "20px" }}>
                  <label>Rule Location: </label>
                  <input
                    type="text"
                    value={manualLocation}
                    onChange={handleManualLocationChange}
                    placeholder="Enter 'shared' or select from hierarchy"
                    style={{ padding: "8px", width: "100%" }}
                  />
                  {errors.location && <div style={{ color: "red", fontSize: "0.8em" }}>{errors.location}</div>}
                  {selectedPath && !manualLocation && (
                    <p style={{ marginTop: "10px" }}>
                      Selected location: <strong>{selectedPath}</strong>
                    </p>
                  )}
                </div>
              </>
            )}
          </div>

          {/* Right Column - Rule Details */}
          <div>
            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: "15px" }}>
                <label>Rule Name: </label>
                <input
                  type="text"
                  name="name"
                  value={ruleDetails.name}
                  onChange={handleRuleDetailChange}
                  required
                  style={{ padding: "8px", width: "100%" }}
                  disabled={loading}
                />
                {errors.name && <div style={{ color: "red", fontSize: "0.8em" }}>{errors.name}</div>}
              </div>

              <div style={{ marginBottom: "15px" }}>
                <label>Description: </label>
                <textarea
                  name="description"
                  value={ruleDetails.description}
                  onChange={handleRuleDetailChange}
                  style={{ padding: "8px", width: "100%", minHeight: "80px" }}
                  disabled={loading}
                />
                {errors.description && <div style={{ color: "red", fontSize: "0.8em" }}>{errors.description}</div>}
              </div>

              <div style={{ marginBottom: "15px" }}>
                <label>Source Zone: </label>
                <select
                  name="sourceZone"
                  value={ruleDetails.sourceZone}
                  onChange={handleRuleDetailChange}
                  required
                  style={{ padding: "8px", width: "100%" }}
                  disabled={loading || !selectedFirewall}
                >
                  <option value="">-- Select Source Zone --</option>
                  {availableZones.map((zone, index) => (
                    <option key={index} value={zone}>{zone}</option>
                  ))}
                </select>
                {validationErrors.sourceZone && <div style={{ color: "red", fontSize: "0.8em" }}>{validationErrors.sourceZone}</div>}
              </div>

              <div style={{ marginBottom: "15px" }}>
                <label>Destination Zone: </label>
                <select
                  name="destinationZone"
                  value={ruleDetails.destinationZone}
                  onChange={handleRuleDetailChange}
                  required
                  style={{ padding: "8px", width: "100%" }}
                  disabled={loading || !selectedFirewall}
                >
                  <option value="">-- Select Destination Zone --</option>
                  {availableZones.map((zone, index) => (
                    <option key={index} value={zone}>{zone}</option>
                  ))}
                </select>
                {validationErrors.destinationZone && <div style={{ color: "red", fontSize: "0.8em" }}>{validationErrors.destinationZone}</div>}
              </div>

              {renderIPField('sourceIP', 'Source IP')}
              {renderIPField('destinationIP', 'Destination IP')}

              <div style={{ marginBottom: "15px" }}>
                <label>Action: </label>
                <select
                  name="action"
                  value={ruleDetails.action}
                  onChange={handleRuleDetailChange}
                  style={{ padding: "8px", width: "100%" }}
                  disabled={loading}
                >
                  <option value="allow">Allow</option>
                  <option value="deny">Deny</option>
                  <option value="drop">Drop</option>
                  <option value="reset-client">Reset Client</option>
                  <option value="reset-server">Reset Server</option>
                  <option value="reset-both">Reset Both</option>
                </select>
              </div>

              {renderServiceField()}
              {renderApplicationField()}

              <div style={{ marginBottom: "15px" }}>
                <label>Rule Type: </label>
                <select
                  name="ruleType"
                  value={ruleType}
                  onChange={(e) => setRuleType(e.target.value)}
                  style={{ padding: "8px", width: "100%" }}
                  disabled={loading}
                >
                  <option value="pre">Pre-Rule (before shared rules)</option>
                  <option value="post">Post-Rule (after shared rules)</option>
                </select>
              </div>

              <div style={{ marginBottom: "15px" }}>
                <label>
                  <input
                    type="checkbox"
                    name="disabled"
                    checked={ruleDetails.disabled}
                    onChange={handleRuleDetailChange}
                    disabled={loading}
                  />
                  Disabled
                </label>
              </div>

              <div style={{ marginBottom: "15px" }}>
                <label>
                  <input
                    type="checkbox"
                    name="logStart"
                    checked={ruleDetails.logStart}
                    onChange={handleRuleDetailChange}
                    disabled={loading}
                  />
                  Log at Session Start
                </label>
              </div>

              <div style={{ marginBottom: "15px" }}>
                <label>
                  <input
                    type="checkbox"
                    name="logEnd"
                    checked={ruleDetails.logEnd}
                    onChange={handleRuleDetailChange}
                    disabled={loading}
                  />
                  Log at Session End
                </label>
              </div>
            </form>
          </div>
        </div>

        {/* Security Profiles Section */}
        {renderSecurityProfileSection()}

        {errors.submit && (
          <div style={{ color: "red", margin: "10px 0", textAlign: "center" }}>
            {errors.submit}
          </div>
        )}

        {/* API Response Debugging Section */}
        {apiResponse && (
          <div style={{ 
            marginTop: "20px", 
            padding: "15px", 
            backgroundColor: "#f5f5f5", 
            border: "1px solid #ddd",
            borderRadius: "4px"
          }}>
            <h4>API Response</h4>
            <pre style={{ 
              whiteSpace: "pre-wrap", 
              wordWrap: "break-word",
              maxHeight: "200px",
              overflowY: "auto"
            }}>
              {JSON.stringify(apiResponse, null, 2)}
            </pre>
          </div>
        )}

        <div style={{ display: "flex", justifyContent: "space-between", marginTop: "20px" }}>
          <button 
            type="button" 
            onClick={onClose}
            className="glass-button"
            style={{ backgroundColor: "#dc3545" }}
            disabled={loading}
          >
            Cancel
          </button>
          <div style={{ display: "flex", gap: "10px" }}>
            <button 
              type="button" 
              className="glass-button"
              onClick={handlePreview}
              disabled={loading || !(manualLocation || selectedPath) || !selectedFirewall || !ruleDetails.name}
              style={{ backgroundColor: "#17a2b8" }}
            >
              Preview
            </button>
            <button 
              type="submit" 
              className="glass-button"
              onClick={handleSubmit}
              disabled={loading || !(manualLocation || selectedPath) || !selectedFirewall || !ruleDetails.name}
            >
              {loading ? "Creating..." : "Create Rule"}
            </button>
          </div>
        </div>
      </div>

      <CreateObjectModal
        isOpen={showObjectCreationModal}
        onClose={() => setShowObjectCreationModal(false)}
        onSuccess={handleObjectCreated}
        ipValue={objectCreationValue}
      />

      <CreateServiceModal
        isOpen={showServiceCreationModal}
        onClose={() => setShowServiceCreationModal(false)}
        onSuccess={handleServiceCreated}
        serviceValue={serviceCreationValue}
        serviceType={serviceCreationType}
      />

      <AddRulePreview
        isOpen={showPreview}
        onClose={() => setShowPreview(false)}
        ruleData={prepareRuleData()}
        onSubmit={handleSubmit}
      />
    </div>
  );
};

export default AddingRule;