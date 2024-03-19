import React from "react";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

import Header from "../header/Header";

import "./HomePage.css";

function HomePage(props) {
    const [buttonText, setButtonText] = useState("Login to explore");
    
    useEffect(() => {
        if (props.isAuthorized) {
            setButtonText("Create session");
        } else {
            setButtonText("Login to explore");
        }
    }, []);

    const navigate = useNavigate();

    const handleNavigate = () => {
        if (props.isAuthorized) {
            navigate("/create_session");
        } else {
            navigate("/login");
        }
    };

    return (
        <div style={{ height: "100vh" }} className="main-bg ">
            <Header />

            <div className="text-center cover-container" style={{ height: "90vh" }}>
                <main role="main" className="cover-text-container">
                    <h1>Movie Together</h1>
                    <p className="lead mb-3 pt-3 pb-2">
                        Even though the strictest days of social distancing are behind us, we’ve gotta admit:
                        We’re going to keep some of our pandemic habits alive. Case in point?
                        Watching movies and shows with our favorite people without leaving our couch.
                    </p>
                    <p className="lead mt-3">
                        <button onClick={handleNavigate} className="btn btn-lg btn-secondary">{buttonText}</button>
                    </p>
                </main>
            </div>
        </div>
    );
}

export default HomePage;