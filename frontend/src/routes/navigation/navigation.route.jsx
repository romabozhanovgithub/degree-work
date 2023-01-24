import { Fragment } from "react";
import { Outlet, Link } from "react-router-dom";


const Navigation = () => {
    return (
        <Fragment>
            <div>
                <Link to="/">Logo</Link>
                <div className="nav-link-container">
                    <Link to="/">Home</Link>
                    <Link to="/about">About</Link>
                    <Link to="/sign-in">Sign In</Link>
                </div>
            </div>
            <Outlet />
        </Fragment>
    );
};

export default Navigation;
