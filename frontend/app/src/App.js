import React from "react";
import { useState } from "react";
import { Routes, Route } from "react-router-dom";

import HomePage from "./HomePage/HomePage";
import LoginPage from "./LoginPage/LoginPage";
import CreateSessionPage from "./CreateSessionPage/CreateSessionPage";
import SessionPage from "./SessionPage/SessionPage";

import "./App.css";

function App() {
    const [isAuthorized, setIsAuthorized] = useState(false);
    const [userId, setUserId] = useState("")

    return (
        <Routes>
            <Route path="/" element={<HomePage isAuthorized={isAuthorized} />}></Route>
            <Route path="/login" element={<LoginPage setIsAuthorized={setIsAuthorized} setUserId={setUserId} />}></Route>
            <Route path="/create_session" element={<CreateSessionPage isAuthorized={isAuthorized} />}></Route>
            <Route path="/join_session" element={<SessionPage userId={userId} />}></Route>
        </Routes>
    );
}

export default App;