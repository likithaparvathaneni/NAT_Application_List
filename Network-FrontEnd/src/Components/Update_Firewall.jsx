import React, { useState } from 'react';
import Modal from './Modal';
import axios from "axios";
import "../Css/button.css"
const Modal_hover = ({ message }) => (
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
const Update_Firewall = () => {
  const reload=()=>window.location.reload();
  const [showModal, setShowModal] = useState(false);
  const handleOpenModal = () => setShowModal(true);
  const handleCloseModal = () => setShowModal(false);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    Host: "",
    Username: "",
    Password:""
  });

  const [errors, setErrors] = useState({});
  const [submissionError, setSubmissionError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [Response,setResponse]=useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    const error = "";

    setFormData({ ...formData, [name]: value });
    setErrors({ ...errors, [name]: error });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmissionError("");
    setIsSubmitting(true);

    const formValid =
      Object.values(formData).every((field) => field.trim() !== "");

    if (formValid) {
      setLoading(true)
      try {
      
        await  axios({
          method: 'post',
          responseType: 'json',
          url: `http://127.0.0.1:8000/firewall_fetch/`,
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
    setLoading(false)
  };
  return (
    <div>
      <a onClick={handleOpenModal} className="glass-button" style={{
            position:"relative",
            alignItems: 'center',
            marginLeft:400,
justifyContent: 'center',
          }}>Update firewall</a>
      <Modal show={showModal} handleClose={reload}>

        <div className="upload-container">
      <h2>Firewall Updation</h2>
      <p>Please enter the required information:</p>
      <form onSubmit={handleSubmit}>
        {[
          { label: "Host", name: "Host", type:"text" },
          { label: "Username", name: "Username", ype:"text" },
          {label:"Password",name: "Password", type:"password"}
        ].map((field, idx) => (
          <div className="form-group row" key={idx}>
            <label className="col-sm-4 col-form-label form-label">
              {field.label}
            </label>
            <div className="col-sm-8">
              <input
                type={field.type}
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
          !Object.values(formData).every((field) => field.trim() !== "") ? "rgba(0, 123, 255, 0.3)" : "rgba(0, 123, 255, 0.5)",
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
      {loading && <Modal_hover message="Updating the database" />}
      {Response && Response.data ? (
 <div>
 {Response.data}
</div>
) : (
  <div> </div>
)}

    </div>
      </Modal>
    </div>
  );
};

export default Update_Firewall;
