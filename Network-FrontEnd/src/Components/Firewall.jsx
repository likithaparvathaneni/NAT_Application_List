import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { useParams, useLocation } from "react-router-dom";
import Update_Firewall from "./Update_Firewall";
import SuggestionsInput from "./Suggestions";
import "../Css/button.css";
import is_ip_private from "private-ip";
import "../Css/Firewall.css";
import { isIP, isIPv4 } from 'is-ip';
import AddingRule from './AddingRule';

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

const FirewallDisplay = ({ data, memo, formData, allrules, onAddRule }) => {
  const [showMore, setShowMore] = useState({});
  const [popup, setPopup] = useState({ visible: false, content: "", x: 0, y: 0 });
  const [searchQuery, setSearchQuery] = useState("");
  const popupRef = useRef(null);

  const handleShowMore = (event, rowIndex, column) => {
    event.preventDefault();
    setShowMore((prevState) => ({
      ...prevState,
      [rowIndex]: {
        ...prevState[rowIndex],
        [column]: !prevState[rowIndex]?.[column],
      },
    }));
  };

  const handlePopup = (event, content) => {
    event.stopPropagation();
    const rect = event.target.getBoundingClientRect();
    setSearchQuery("");
    setPopup({
      visible: true,
      content: content.replace(/\n/g, "\n"),
      x: rect.left + window.scrollX,
      y: rect.bottom + window.scrollY,
    });
  };

  const handleClosePopup = () => {
    setPopup({ visible: false, content: "", x: 0, y: 0 });
  };

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (popupRef.current && !popupRef.current.contains(event.target)) {
        handleClosePopup();
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const filterContent = (content) => {
    const lines = content.split("\n");
    return lines.filter((line) => line.includes(searchQuery)).join("\n");
  };

  const getUniqueValues = (values) => {
    return [...new Set(values)];
  };

  const errors = data.filter((item) => typeof item[1] === "string");
  const rules = data.filter((item) => item.length > 0 && typeof item[1] !== "string");

  return (
    <div className="firewall-container">
      {rules.length > 0 ? (
        <div>
          {rules.map((item, index) => (
            <div key={index}>
              <h6>{item[0]}</h6>
              <h6>Rules Count {item[2]}</h6>
              <div style={{ maxHeight: "400px", overflowY: "auto" }}>
                <table style={{ tableLayout: "auto", width: "100%" }}>
                  <thead style={{ position: "sticky", top: 0, zIndex: 1 }}>
                    <tr>
                      <th style={{ position: "sticky", top: 0 }}>S.No</th>
                      <th style={{ position: "sticky", top: 0 }}>Rule Name</th>
                      <th style={{ position: "sticky", top: 0 }}>Source Zone</th>
                      <th style={{ position: "sticky", top: 0 }}>Source IP</th>
                      <th style={{ position: "sticky", top: 0 }}>Destination Zone</th>
                      <th style={{ position: "sticky", top: 0 }}>Destination IP</th>
                      <th style={{ position: "sticky", top: 0 }}>Service</th>
                      <th style={{ position: "sticky", top: 0 }}>Application</th>
                      <th style={{ position: "sticky", top: 0 }}>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {item[1].map((rule, ruleIndex) => (
                      <React.Fragment key={`${index}-${ruleIndex}`}>
                        <tr style={{ color: rule.action === "allow" ? "green" : "red" }}>
                          <td>
                            <strong>{ruleIndex + 1}</strong>
                          </td>
                          <td>
                            <strong>{rule.name}</strong>
                          </td>
                          <td>
                            {rule.fromdis.slice(0, 3).map((value, entryIndex) => (
                              <div key={entryIndex} style={{ marginBottom: "5px" }} title={JSON.stringify(memo?.[value])}>
                                {value}
                              </div>
                            ))}
                            {showMore[ruleIndex]?.fromdis &&
                              rule.fromdis.slice(3).map((value, entryIndex) => (
                                <div key={entryIndex + 3} style={{ marginBottom: "5px" }} title={JSON.stringify(memo?.[value])}>
                                  {value}
                                </div>
                              ))}
                            {rule.fromdis.length > 3 && (
                              <a href="#" onClick={(event) => handleShowMore(event, ruleIndex, "fromdis")}>
                                {showMore[ruleIndex]?.fromdis ? "Show Less" : "Show More"}
                              </a>
                            )}
                          </td>
                          <td style={rule?.["negate-source"] === "yes" ? { textDecoration: "line-through", textDecorationColor: "red" } : {}}>
                            {getUniqueValues(rule.sourcedis)
                              .slice(0, 3)
                              .map((value, entryIndex) => (
                                <div
                                  key={entryIndex}
                                  style={{ marginBottom: "5px", cursor: "pointer" }}
                                  onClick={(event) => memo?.[value] != null && handlePopup(event, JSON.stringify(memo?.[value], null, 2))}
                                  title={JSON.stringify(memo?.[value])}
                                >
                                  {value}
                                </div>
                              ))}
                            {showMore[ruleIndex]?.sourcedis &&
                              getUniqueValues(rule.sourcedis)
                                .slice(3)
                                .map((value, entryIndex) => (
                                  <div
                                    key={entryIndex + 3}
                                    style={{ marginBottom: "5px", cursor: "pointer" }}
                                    onClick={(event) => memo?.[value] != null && handlePopup(event, JSON.stringify(memo?.[value], null, 2))}
                                    title={JSON.stringify(memo?.[value])}
                                  >
                                    {value}
                                  </div>
                                ))}
                            {getUniqueValues(rule.sourcedis).length > 3 && (
                              <a href="#" onClick={(event) => handleShowMore(event, ruleIndex, "sourcedis")}>
                                {showMore[ruleIndex]?.sourcedis ? "Show Less" : "Show More"}
                              </a>
                            )}
                          </td>
                          <td>
                            {rule.todis.slice(0, 3).map((value, entryIndex) => (
                              <div key={entryIndex} style={{ marginBottom: "5px" }} div title={JSON.stringify(memo?.[value])}>
                                {value}
                              </div>
                            ))}
                            {showMore[ruleIndex]?.todis &&
                              rule.todis.slice(3).map((value, entryIndex) => (
                                <div key={entryIndex + 3} style={{ marginBottom: "5px" }} title={JSON.stringify(memo?.[value])}>
                                  {value}
                                </div>
                              ))}
                            {rule.todis.length > 3 && (
                              <a href="#" onClick={(event) => handleShowMore(event, ruleIndex, "todis")}>
                                {showMore[ruleIndex]?.todis ? "Show Less" : "Show More"}
                              </a>
                            )}
                          </td>
                          <td style={rule?.["negate-destination"] === "yes" ? { textDecoration: "line-through", textDecorationColor: "red" } : {}}>
                            {getUniqueValues(rule.destinationdis)
                              .slice(0, 3)
                              .map((value, entryIndex) => (
                                <div
                                  key={entryIndex}
                                  style={{ marginBottom: "5px", cursor: "pointer" }}
                                  onClick={(event) => memo?.[value] != null && handlePopup(event, JSON.stringify(memo?.[value], null, 2))}
                                  div title={JSON.stringify(memo?.[value])}
                                >
                                  {value}
                                </div>
                              ))}
                            {showMore[ruleIndex]?.destinationdis &&
                              getUniqueValues(rule.destinationdis)
                                .slice(3)
                                .map((value, entryIndex) => (
                                  <div
                                    key={entryIndex + 3}
                                    style={{ marginBottom: "5px", cursor: "pointer" }}
                                    onClick={(event) => memo?.[value] != null && handlePopup(event, JSON.stringify(memo?.[value], null, 2))}
                                    div title={JSON.stringify(memo?.[value])}
                                  >
                                    {value}
                                  </div>
                                ))}
                            {getUniqueValues(rule.destinationdis).length > 3 && (
                              <a href="#" onClick={(event) => handleShowMore(event, ruleIndex, "destinationdis")}>
                                {showMore[ruleIndex]?.destinationdis ? "Show Less" : "Show More"}
                              </a>
                            )}
                          </td>
                          <td>
                            {getUniqueValues(rule.servicedis)
                              .slice(0, 3)
                              .map((value, entryIndex) => (
                                <div
                                  key={entryIndex}
                                  style={{ marginBottom: "5px", cursor: "pointer" }}
                                  onClick={(event) => memo?.[value] != null && handlePopup(event, JSON.stringify(memo?.[value], null, 2))}
                                  div title={JSON.stringify(memo?.[value])}
                                >
                                  {value}
                                </div>
                              ))}
                            {showMore[ruleIndex]?.servicedis &&
                              getUniqueValues(rule.servicedis)
                                .slice(3)
                                .map((value, entryIndex) => (
                                  <div key={entryIndex + 3} style={{ marginBottom: "5px" }} title={JSON.stringify(memo?.[value])}>
                                    {value}
                                  </div>
                                ))}
                            {getUniqueValues(rule.servicedis).length > 3 && (
                              <a href="#" onClick={(event) => handleShowMore(event, ruleIndex, "servicedis")}>
                                {showMore[ruleIndex]?.servicedis ? "Show Less" : "Show More"}
                              </a>
                            )}
                          </td>
                          <td>
                            {getUniqueValues(rule.applicationdis)
                              .slice(0, 3)
                              .map((value, entryIndex) => (
                                <div key={entryIndex} style={{ marginBottom: "5px" }} title={JSON.stringify(memo?.[value])}>
                                  {value}
                                </div>
                              ))}
                            {showMore[ruleIndex]?.applicationdis &&
                              getUniqueValues(rule.applicationdis)
                                .slice(3)
                                .map((value, entryIndex) => (
                                  <div key={entryIndex + 3} style={{ marginBottom: "5px" }} title={JSON.stringify(memo?.[value])}>
                                    {value}
                                  </div>
                                ))}
                            {getUniqueValues(rule.applicationdis).length > 3 && (
                              <a href="#" onClick={(event) => handleShowMore(event, ruleIndex, "applicationdis")}>
                                {showMore[ruleIndex]?.applicationdis ? "Show Less" : "Show More"}
                              </a>
                            )}
                          </td>
                          <td>{rule.action}</td>
                        </tr>
                      </React.Fragment>
                    ))}
                  </tbody>
                </table>
              </div>
              <br />
            </div>
          ))}
          <button className="glass-button" onClick={onAddRule}>
            Go to Addition
          </button>
        </div>
      ) : (
        <div className="no-rules-found">
          <h3>No matching rules found</h3>
          <button 
            className="glass-button"
            onClick={() => onAddRule()}
          >
            Add New Rule
          </button>
        </div>
      )}
      {errors.length > 0 && errors[0].length > 1 && typeof errors[0] !== "string" ? (
        errors.map((err, index) => (
          <div key={index} className="errors">
            <h3>Firewall Name: {err[0]}</h3>
            <p>{err[1]}</p>
          </div>
        ))
      ) : (
        errors.length > 0 &&
        errors.length < 2 && (
          <div>
            No matching firewalls found
          </div>
        )
      )}
      {popup.visible && (
        <div
          ref={popupRef}
          className="popup"
          style={{
            position: "absolute",
            top: popup.y,
            left: popup.x,
            backgroundColor: "white",
            border: "1px solid black",
            padding: "10px",
            zIndex: 1000,
            boxShadow: "0 0 10px rgba(0, 0, 0, 0.25)",
            width: "250px",
            maxHeight: "150px",
            overflowY: "auto",
            whiteSpace: "pre-wrap",
            overflowX: "hidden",
          }}
        >
          <input
            type="text"
            placeholder="Search..."
            value={searchQuery}
            onChange={handleSearchChange}
            style={{ marginBottom: "10px", width: "100%" }}
          />
          <div>{filterContent(popup.content)}</div>
        </div>
      )}
    </div>
  );
};

const FirewallForm = () => {
  const query = new URLSearchParams(useLocation().search);
  const sourceIP = query.get("source_ip") || "";
  const destinationIP = query.get("destination_ip") || "";
  const [memo, setmemo] = useState({});
  const [allrules, setallrules] = useState([]);
  const [apps, setapps] = useState([]);
  const [showRuleCreator, setShowRuleCreator] = useState(false);
  const [firewallsForRuleCreation, setFirewallsForRuleCreation] = useState([]);

  const fetch_apps = async () => {
    try {
      const response = await axios.get(`http://127.0.0.1:8000/apps/`);
      setapps(response.data.data);
      console.log(response.data.data);
    } catch (error) {
      console.log(error);
    }
  };
  const [Firewall_response, SetFirewall_Response] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      if (sourceIP && destinationIP) {
        try {
          const response = await axios({
            method: "post",
            responseType: "json",
            url: `http://127.0.0.1:8000/firewall_search/`,
            data: { sourceIP, destinationIP },
            headers: {
              "Content-Type": "multipart/form-data",
            },
          });
          SetFirewall_Response(response.data);
          console.log(response);
        } catch (error) {
          console.error("Submission error:", error);
        }
      }
    };

    fetchData();
  }, [sourceIP, destinationIP]);

  const [formData, setFormData] = useState({
    sourceZone: "",
    sourceIP: sourceIP,
    destinationZone: "",
    destinationIP: destinationIP,
    protocol: "",
    destinationPort: "",
    application: "any",
    Action: "allow",
    firewallName: "",
  });

  const [errors, setErrors] = useState({});
  const [submissionError, setSubmissionError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [Response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const isPublicIP = (ip) => {
    try {
      return !is_ip_private(ip);
    } catch (e) {
      return false;
    }
  };
  const isAny = (ip) => {
    return ip=="any";
  };

  const validateInput = (name, value) => {
    let error = "";
    if (!value) {
      if (
        name === "sourceZone" ||
        name === "sourceIP" ||
        name === "destinationZone" ||
        name === "destinationIP" ||
        name === "protocol"
      ) {
        return "This field is required.";
      }
    }

    if (name === "sourceZone" || name === "destinationZone") {
      if (value.length > 255) {
        error = "The input should not exceed 255 characters.";
      }
    } else if (name === "sourceIP" || name === "destinationIP") {
      if (value.startsWith("0.")) {
        error = "IP cannot start with 0.";
      }
      const ipPattern =
        /^(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])){3}$/;
      const ipv4WithSubnetPattern =
        /^(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\/(3[0-2]|[12][0-9]|[0-9])$/;
      if (
        !ipPattern.test(value) &&
        !ipv4WithSubnetPattern.test(value) &&
        value !== "any"
      ) {
        error = "Invalid IP/subnet or FQDN.";
      }
    } else if (name === "protocol") {
      if (!["tcp", "udp", "icmp", "any"].includes(value.toLowerCase())) {
        error = "Invalid protocol (only udp, tcp, icmp are allowed).";
      }
    } else if (name === "destinationPort") {
      const ports = value.split(',').map(port => port.trim());
      for (let port of ports) {
        if (port.includes('-')) {
          const [start, end] = port.split('-').map(Number);
          if (!Number.isInteger(start) || !Number.isInteger(end) || start < 0 || end > 65535 || start > end) {
            error = "Range: 0-65535 and only numbers are allowed.";
            break;
          }
        } else {
          const portNumber = Number(port);
          if ((!Number.isInteger(portNumber) && port !== "app-default" && port !== "any") || portNumber < 0 || portNumber > 65535) {
            error = "Range: 0-65535 and only numbers are allowed.";
            break;
          }
        }
      }
    } else if (name === "Action") {
      if (!(value === "allow" || value === "deny" || value === "any")) {
        error = "Only allow or deny or any is allowed.";
      }
    }
    if (name == "destinationPort" && value == "") {
      if (formData["application"] === "") {
        error = "Both Application and Destination Port Cannot be empty"
      }
    }
    if (name == "application") {
      if (!apps.includes(value) ) {
        error = "Invalid Application "
      }
    }
    if (name == "application" && value == "") {
      if (formData["destinationPort"] === "") {
        error = "Both Application and Destination Port Cannot be empty"
      }
    }
    if (name === "sourceIP" || name === "destinationIP") {
      var error_f="";
      if ((((isPublicIP(name === "sourceIP" ? formData["destinationIP"] : value)) || isAny(name === "sourceIP" ? formData["destinationIP"] : value))) &&
      (isPublicIP(name === "destinationIP" ? formData["sourceIP"] : value) || isAny(name === "destinationIP" ? formData["sourceIP"] : value))) {
        if (
          ((isIP(name === "sourceIP" ? formData["destinationIP"] : value) || isAny(name === "sourceIP" ? formData["destinationIP"] : value)) &&
            (isIP(name === "destinationIP" ? formData["sourceIP"] : value)|| isAny(name === "destinationIP" ? formData["sourceIP"] : value))
        )) {
          error_f="Both src and dest cannot be public"
        }
      }
      else if (name === "destinationIP" && value === "any") {
        if (isPublicIP(formData["sourceIP"])) {
          error_f=("Both Source and destination cannot be public IPs/any. Please enter firewall name");
        }
        else if (formData["sourceIP"] === "any") {
          error_f=("Both Source and destination cannot be public IPs/any. Please enter firewall name");
        }
      }
      else if (name === "sourceIP" && value === "any") {
        if (isPublicIP(formData["destinationIP"])) {
          error_f=("Both Source and destination cannot be public IPs/any. Please enter firewall name");
        }
        else if (formData["destinationIP"] === "any") {
          error_f=("Both Source and destination cannot be public IPs/any. Please enter firewall name");
        }
      }
      else if (name === "destinationIP" && isIP(formData["destinationIP"]) && isPublicIP(formData["destinationIP"])) {
        if (formData["sourceIP"] === "any") {
          error_f=("Both Source and destination cannot be public IPs/any. Please enter firewall name");
        }
      }
      errors.firewallName=error_f;
    }

    return error;
  };

  const handleChange = async (name, value) => {
    const error = validateInput(name, value, formData);
    if (name == "application") {
      fetch_apps();
    }
    setErrors((prevErrors) => ({
      ...prevErrors,
      [name]: error,
    }));
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleChange_ip = async (name, value) => {
    const error = validateInput(name, value);
    setErrors((prevErrors) => ({
      ...prevErrors,
      [name]: error,
    }));

    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));

    if (name === "sourceIP" || name === "destinationIP") {
      try {
        const formData = new FormData();
        formData.append("data", value);

        const response = await axios({
          method: 'post',
          responseType: 'json',
          url: `http://127.0.0.1:8000/fqdn/`,
          data: formData,
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });

        const resolvedValue = response.data.data;

        setFormData((prevData) => ({
          ...prevData,
          [name]: resolvedValue,
        }));

        handleChange(name, resolvedValue);
      } catch (error) {
        setSubmissionError("Failed to resolve FQDN. Please try again.");
        console.error("FQDN resolution error:", error);
      }
    }
  };

const handleAddRule = () => {
  if (!Firewall_response?.data) {
    alert("No firewall data available");
    return;
  }

  // Extract firewall names from the response
  const firewalls = [];
  
  // Handle case where source and destination are the same firewall
  if (Array.isArray(Firewall_response.data[0]) && Firewall_response.data[0] !== "Not Found") {
    firewalls.push(...Firewall_response.data[0]);
  }
  // Handle destination firewalls
  if (Array.isArray(Firewall_response.data[3]) && Firewall_response.data[3] !== "Not Found") {
    firewalls.push(...Firewall_response.data[3]);
  }
  
  // Remove duplicates and empty values
  const uniqueFirewalls = [...new Set(firewalls.filter(fw => fw && fw !== "Not Found"))];
  
  if (uniqueFirewalls.length > 0) {
    setFirewallsForRuleCreation(uniqueFirewalls);
    setShowRuleCreator(true);
  } else {
    alert("No firewalls found in the response to add rules to");
  }
};

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmissionError("");
    setIsSubmitting(true);
    setLoading(true);
    const formValid =
      Object.values(errors).every((err) => !err);

    if (formValid) {
      try {
        const response = await axios({
          method: 'post',
          responseType: 'json',
          url: `http://127.0.0.1:8000/firewall/`,
          data: formData,
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });
        console.log(response)
        setResponse(response.data);
        setmemo(response.data.memo);
        setallrules(response.data.all_rules)
        console.log(memo)
        console.log(response);
      } catch (error) {
        error=(JSON.stringify(error));
        setSubmissionError("Failed to submit. Please try again.");
        console.error("Submission error:", error);
      } finally {
        setIsSubmitting(false);
        setLoading(false);
      }
    } else {
      setSubmissionError("Please fix errors before submitting.");
      setIsSubmitting(false);
      setLoading(false);
    }
  };

  const handleRuleCreated = () => {
    setShowRuleCreator(false);
    // Optionally refresh the rules list
    handleSubmit({ preventDefault: () => {} });
  };

  return (
    <div className="upload-container">
      <Update_Firewall />
      <h2>Rule Checking</h2>
      <p>Please enter the required information:</p>
      <form onSubmit={handleSubmit}>
        {[
          { label: "Source Zone", name: "sourceZone" },
          { label: "Source IP", name: "sourceIP" },
          { label: "Destination Zone", name: "destinationZone" },
          { label: "Destination IP", name: "destinationIP" },
          { label: "Firewall Name", name: "firewallName" },
          { label: "Protocol", name: "protocol" },
          { label: "Destination Port", name: "destinationPort" },
          { label: "Application", name: "application", value: "any" },
          { label: "Action", name: "Action", value: "allow" },
        ].map((field, idx) => (
          <div className="form-group row" key={idx}>
            <label className="col-sm-4 col-form-label form-label">
              {field.label}
              {["sourceZone", "sourceIP", "destinationZone", "destinationIP", "protocol"].includes(field.name) && (
                <span className="required">*</span>
              )}
            </label>

            <div className="col-sm-8">
              {field.name === "Action" ? (
                <select
                  name={field.name}
                  value={formData[field.name]}
                  onChange={(e) => handleChange(field.name, e.target.value)}
                  className="form-control"
                >
                  <option value="allow">allow</option>
                  <option value="deny">deny</option>
                  <option value="any">any</option>
                </select>
              ) : ["sourceZone", "destinationZone", "firewallName","application"].includes(field.name) ? (
                <SuggestionsInput
                  name={field.name}
                  value={formData[field.name]}
                  onChange={(value) => handleChange(field.name, value)}
                />
              ) : (
                <div className="input-group">
                  <input
                    type="text"
                    name={field.name}
                    value={formData[field.name] || ""}
                    onChange={(e) => handleChange(field.name, e.target.value)}
                    className="form-control"
                  />
                  {["sourceIP", "destinationIP"].includes(field.name) && (
                    <div className="input-group-append">
                      <button type="button" className="btn btn-primary" style={{ background: "linear-gradient(to right, #002f65, #60bfd4)" }} onClick={() => handleChange_ip(field.name, formData[field.name])}>
                        FQDN
                      </button>
                    </div>
                  )}
                </div>
              )}
              {errors[field.name] && (
                <span className="error-message">{errors[field.name]}</span>
              )}
            </div>
          </div>
        ))}

        <button
          type="submit"
          className="btn btn-primary"
          style={{
            position: "relative",
            alignItems: "center",
            marginLeft: 500,
            backgroundColor: "rgba(4, 104, 226, 0.7)",
            justifyContent: "center",
          }}
          disabled={
            isSubmitting ||
            !Object.values(errors).every((err) => !err) ||
            (formData["destinationPort"] === "" && formData["application"] === "") ||
            ["Action", "destinationIP", "sourceIP", "sourceZone", "destinationZone", "protocol"].some(
              (field) => formData[field] === ""
            )
          }
        >
          {isSubmitting ? "checking..." : "check"}
        </button>
        {submissionError && (
          <p className="error-message" style={{ color: "red" }}>
            {submissionError}
          </p>
        )}
      </form>

      {loading && <Modal message="Checking for the rule, please wait..." />}
      {!Response && Firewall_response && Firewall_response.data ? (
        <div style={{ margin: 30 }}>
          {Firewall_response.data[0] === "Not Found" && Firewall_response.data[3] === "Not Found" ? (
            <div>No source firewall and destination firewall found</div>
          ) : (
            <>
              {JSON.stringify(Firewall_response.data[0]) === JSON.stringify(Firewall_response.data[3]) && Firewall_response.data[0] !== "Not Found" ? (
                <div>
                  <strong>Both source and destination are managed by the same firewall:</strong><br />
                  <strong>Firewall Name:</strong> {Firewall_response.data[0].join(", ") || 'N/A'}
                  <strong> Source Zone:</strong> {Firewall_response.data[1] || 'N/A'},
                  <strong> Destination Zone:</strong> {Firewall_response.data[2] || 'N/A'},
                  <strong> Source Subnet:</strong> {Firewall_response.data[6] || 'N/A'}
                </div>
              ) : (
                <>
                  <h2>Source</h2>
                  <ul>
                    {Firewall_response.data[0] === "Not Found" ? (
                      <div>No source firewall found</div>
                    ) : (
                      <li>
                        <strong>Source Firewall Name:</strong> {Firewall_response.data[0].join(", ") || 'N/A'},
                        <strong> Source Zone:</strong> {Firewall_response.data[1] || 'N/A'},
                        <strong> Destination Zone:</strong> {Firewall_response.data[2] || 'N/A'},
                        <strong> Source Subnet:</strong> {Firewall_response.data[6] || 'N/A'}
                      </li>
                    )}
                  </ul>
                  <h2>Destination</h2>
                  <ul>
                    {Firewall_response.data[3] === "Not Found" ? (
                      <div>No destination firewall found</div>
                    ) : (
                      <li>
                        <strong>Destination Firewall Name:</strong> {Firewall_response.data[3].join(", ") || 'N/A'},
                        <strong> Source Zone:</strong> {Firewall_response.data[4] || 'N/A'},
                        <strong> Destination Zone:</strong> {Firewall_response.data[5] || 'N/A'},
                        <strong> Destination Subnet:</strong> {Firewall_response.data[7] || 'N/A'}
                      </li>
                    )}
                  </ul>
                </>
              )}
            </>
          )}
        </div>
      ) : (
        <div></div>
      )}

      {Response && Response.data ? (
        <FirewallDisplay 
          data={Response.data} 
          memo={memo} 
          allrules={allrules} 
          formData={formData}
          onAddRule={handleAddRule}
        /> 
      ) : (
        <div></div>
      )}

      {showRuleCreator && (
        <AddingRule
          firewalls={firewallsForRuleCreation}
          formData={formData}
          onClose={() => setShowRuleCreator(false)}
          onSuccess={handleRuleCreated}
        />
      )}
    </div>
  );
};

export default FirewallForm;