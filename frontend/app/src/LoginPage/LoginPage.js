import Header from "../header/Header";
import { ToastContainer, toast } from "react-toastify";
import Cookies from "js-cookie";
import { useNavigate } from "react-router-dom";

import "react-toastify/dist/ReactToastify.css";

import "../App.css";
import "./LoginPage.css"

function LoginPage(props) {
    const navigate = useNavigate();

    const handleLogin = async (event) => {
        event.preventDefault();

        const username = document.getElementById("floatingInput").value;
        const password = document.getElementById("floatingPassword").value;

        if (!username || !password) {
            showErrorToast();
            return;
        }

        const response = await fetch("http://localhost:8080/api/v1/auth/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json;charset=utf-8"
            },
            body: JSON.stringify({
                "username": username,
                "password": password
            })
        });

        if (response.status !== 200) {
            showErrorToast();
            return;
        }

        const responseJson = await response.json();
        console.log(responseJson)

        Cookies.set("access_token", responseJson["access_token"]);
        Cookies.set("refresh_token", responseJson["refresh_token"]);

        // TODO: Return user_id from auth
        const userId = responseJson["user_id"]
        // const userId = '1234567890'; 

        props.setIsAuthorized(true);
        props.setUserId(userId);

        navigate(-1);
    };

    const showErrorToast = () => {
        toast.error("🦄 Please check your credentials", {
            position: "top-center",
            autoclose: 2000,
            hideprogressbar: true
        });
    }

    return (
        <div style={{ height: "100vh" }} className="main-bg">
            <Header />

            <div className="text-center form-container" style={{ height: "90vh" }}>
                <main className="form-signin form">
                    <form>
                        {/* <img class="mb-4" src="/docs/5.0/assets/brand/bootstrap-logo.svg" alt="" width="72" height="57" /> */}
                        <div className="mb-4"></div>
                        <h1 className="h3 mb-3 fw-normal">Please sign in</h1>

                        <div className="form-floating mb-2">
                            <input type="email" className="form-control" id="floatingInput" placeholder="Username" />
                            <label htmlFor="floatingInput">Username</label>
                        </div>
                        <div className="form-floating mb-3">
                            <input type="password" className="form-control" id="floatingPassword" placeholder="Password" />
                            <label htmlFor="floatingPassword">Password</label>
                        </div>

                        <button className="w-100 btn btn-lg buttons-bg text-light" type="submit" onClick={handleLogin}>Sign in</button>
                        <ToastContainer />

                        <p className="mt-5 mb-3 text-muted">© Ya29 2023–2024</p>
                    </form>
                </main>
            </div>
        </div>
    );
}

export default LoginPage;