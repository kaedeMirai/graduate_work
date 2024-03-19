import React from "react";

import "./Header.css"

class Header extends React.Component {
    render() {
        return (
            <header className="d-flex flex-wrap align-items-center justify-content-center justify-content-md-between p-3 fw-bolder header-bg text-light">
                <div className="col-md-3 mb-2 mb-md-0 fs-5">Movie Together</div>

                {/* <div className="col-md-3 text-end">
                    <button type="button" className="btn buttons-bg text-light">Login</button>
                </div> */}
            </header>
        );
    }
}

export default Header;