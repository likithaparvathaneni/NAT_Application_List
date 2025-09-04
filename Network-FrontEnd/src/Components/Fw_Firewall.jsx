import React, { useState } from "react";
import axios from "axios";
import { Link } from 'react-router-dom';
import Firewall from "./Firewall";


const Fwform = () => {
  const [formData, setFormData] = useState({
    sourceIP: "",
    destinationIP: "",
  });
  const handleClick = () => {
    window.location.href = `/fw?source_ip=${formData.sourceIP}&destination_ip=${formData.destinationIP}`;
    return (
      <Link to={`/fw?source_ip=${formData.sourceIP}&destination_ip=${formData.destinationIP}`}>
        <button>
          Go to Firewall
        </button>
      </Link>
    );
  };
  

  const [errors, setErrors] = useState({});
  const [submissionError, setSubmissionError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [Response,setResponse]=useState(null);

  const validateInput = (name, value) => {
    let error = "";

    if (name === "sourceIP" || name === "destinationIP") {
      const ipPattern =
        /^(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])){3}$/;
      const ipv4WithSubnetPattern =
        /^(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\/(3[0-2]|[12][0-9]|[0-9])$/;
      if (!ipPattern.test(value) && !ipv4WithSubnetPattern.test(value) && value !== "any") {
        error = "Invalid IP/subnet or FQDN.";
      }
      
      if(value==="0.0.0.0"){
        error="Network Ip is not accepted"
      }
      if(value==="any"){
        error="any not accepted"
      }
      if(value==="255.255.255.255"){
        error="Broadcast Ip is not accepted"
      }
    } 

    return error;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    const error = validateInput(name, value);

    setFormData({ ...formData, [name]: value });
    setErrors({ ...errors, [name]: error });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmissionError("");
    setIsSubmitting(true);

    const formValid =
      Object.values(errors).every((err) => !err) &&
      Object.values(formData).every((field) => field.trim() !== "");

    if (formValid) {
      try {
        await  axios({
          method: 'post',
          responseType: 'json',
          url: `http://127.0.0.1:8000/firewall_search/`,
          data: formData,
          headers:{

            "Content-Type": "multipart/form-data",
          }
        })
        .then((response) => {
          setResponse(response.data)
          console.log(response)
        })
        .catch((error) => {
          //error.data.error.message
          console.log(error)
        });
      } catch (error) {
        setSubmissionError("Failed to submit. Please try again.");
        console.error("Submission error:", error);
      } finally {
        setIsSubmitting(false);
      }
    } else {
      setSubmissionError("Please fix errors before submitting.");
      setIsSubmitting(false);
    }
  };


  return (
    <div className="upload-container">
      <button onClick={handleClick} className="glass-button">
    Go to Firewall
  </button>
      <h2>Firewall Finder</h2>
      <p>Please enter the required information:</p>
      <form onSubmit={handleSubmit}>
        {[
          { label: "Source IP", name: "sourceIP" },
          { label: "Destination IP", name: "destinationIP" },
        ].map((field, idx) => (
          <div className="form-group row" key={idx}>
            <label className="col-sm-4 col-form-label form-label">
              {field.label}
            </label>
            <div className="col-sm-8">
              <input
                type="text"
                name={field.name}
                value={formData[field.name]}
                onChange={handleChange}
                className="form-control"
              />
              {errors[field.name] && (
                <span className="error-message">{errors[field.name]}</span>
              )}
            </div>
          </div>
        ))}

        <button
          type="submit"
          className="btn btn-primary"
          disabled={
            isSubmitting ||
            !Object.values(errors).every((err) => !err) ||
            !Object.values(formData).every((field) => field.trim() !== "")
          }
          style={{marginTop: "20px",
          padding: "15px 30px",
          fontSize: "18px",
          backgroundColor:  isSubmitting ||
          !Object.values(errors).every((err) => !err) ||
          !Object.values(formData).every((field) => field.trim() !== "") ? "rgba(9, 45, 90, 0.3)" : "rgba(9, 114, 184, 0.9)",
          color: "white",
          border: "none",
          borderRadius: "8px",
          cursor:  isSubmitting ||
          !Object.values(errors).every((err) => !err) ||
          !Object.values(formData).every((field) => field.trim() !== "")? "not-allowed" : "pointer",
          transition: "all 0.3s ease",
          backdropFilter: "blur(5px)",
          display: "block",
          width: "200px",
          marginLeft: "auto",
          marginRight: "auto",
          textAlign: "center",}}
        >
          {isSubmitting ? "Submitting..." : "Submit"}
        </button>
        {submissionError && (
          <p className="error-message" style={{ color: "red" }}>
            {submissionError}
          </p>
        )}
      </form>
      {Response && Response.data ? (
  <div style={{ margin: 30 }}>
    {(Response.data[0]==="Not Found" || Response.data[0].length ===0) && (Response.data[3]==="Not Found" || Response.data[3].length===0)  ? (
      <div>No source firewall and destination firewall found</div>
    ) : (
      <>
        {JSON.stringify(Response.data[0]) === JSON.stringify(Response.data[3]) && Response.data[0]!=="Not Found"? (
          <div>
            <strong>Both source and destination are managed by the same firewall:</strong><br />
            <strong>Firewall Name:</strong> {Response.data[0].join(", ") || 'N/A'}<br />
            <strong> Source Zone:</strong> {Response.data[1] || 'N/A'} <br />
                  <strong> Destination Zone:</strong> {Response.data[2] || 'N/A'} <br />
                  <strong> Source Subnet:</strong> {Response.data[6] || 'N/A'} <br />
                  <strong> Destination Subnet:</strong> {Response.data[7] || 'N/A'}
          </div>
        ) : (
          <>
            <h2>Source Firewall</h2>
            <ul>
              {Response.data[0] === "Not Found" || Response.data[0].length === 0 ? (
                <div>No source firewall found</div>
              ) : (
                <li>
                  <strong>Source Firewall Names:</strong> {Response.data[0].join(", ") || 'N/A'} <br /> 
                  <strong> Source Zone:</strong> {Response.data[1] || 'N/A'} <br />
                  <strong> Destination Zone:</strong> {Response.data[2] || 'N/A'} <br /> 
                  <strong> Source Subnet:</strong> {Response.data[6] || 'N/A'}
                </li>
              )}
            </ul>
            <h2>Destination Firewall</h2>
            <ul>
              {Response.data[3]==="Not Found" || Response.data[3].length === 0 ?(
                <div>No destination firewall found</div>
              ) : (
                <li>
                  <strong>Destination Firewall Names:</strong> {Response.data[3].join(", ") || 'N/A'} <br /> 
                  <strong> Source Zone:</strong> {Response.data[4] || 'N/A'} <br /> 
                  <strong> Destination Zone:</strong> {Response.data[5] || 'N/A'} <br /> 
                  <strong> Destination Subnet:</strong> {Response.data[7] || 'N/A'}
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



    </div>
     
       
  );
};

export default Fwform;
