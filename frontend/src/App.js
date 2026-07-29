import { useState } from "react";
import "./App.css";

async function api(url, body) {
  const response = await fetch(url, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.message ||
      data.detail ||
      data.error ||
      "Request failed"
    );
  }

  return data;
}

function App() {
  const [tab, setTab] = useState("Login");

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [loginForm, setLoginForm] = useState({
    email: "",
    password: "",
  });

  const [registerForm, setRegisterForm] = useState({
    first_name: "",
    last_name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  async function login() {
    setError("");
    setSuccess("");

    if (!loginForm.email) {
      setError("Please enter your email.");
      return;
    }

    if (!loginForm.email.includes("@")) {
      setError("Please enter a valid email.");
      return;
    }

    if (!loginForm.password) {
      setError("Please enter your password.");
      return;
    }

    try {
      const data = await api(
        "http://localhost:8000/api/v1/auth/login",
        loginForm
      );

      setSuccess("Logged in successfully!");
      console.log(data);
    } catch (err) {
      setError(err.message || "Could not connect to the server.");
    }
  }

  async function register() {
    setError("");
    setSuccess("");

    if (!registerForm.first_name) {
      setError("Please enter your first name.");
      return;
    }

    if (!registerForm.last_name) {
      setError("Please enter your last name.");
      return;
    }

    if (!registerForm.email) {
      setError("Please enter your email.");
      return;
    }

    if (!registerForm.email.includes("@")) {
      setError("Please enter a valid email.");
      return;
    }

    if (!registerForm.password) {
      setError("Please enter your password.");
      return;
    }

    if (registerForm.password !== registerForm.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    try {
      const data = await api("http://localhost:8000/api/v1/auth/register", registerForm);

      setSuccess("Account created successfully!");
      console.log(data);
    } catch (err) {
      setError(err.message || "Could not connect to the server.");
    }
  }

  return (
    <div className="TestArray">
      <h1>Test Array</h1>

      <div className="tab">
        <button
          className={tab === "Login" ? "tablinks active" : "tablinks"}
          onClick={() => {
            setTab("Login");
            setError("");
            setSuccess("");
          }}
        >
          Login
        </button>

        <button
          className={tab === "Register" ? "tablinks active" : "tablinks"}
          onClick={() => {
            setTab("Register");
            setError("");
            setSuccess("");
          }}
        >
          Register
        </button>
      </div>

      

      {tab === "Login" && (
        <div className="tabcontent">
          <input
            type="email"
            placeholder="Email"
            value={loginForm.email}
            onChange={(e) =>
              setLoginForm({
                ...loginForm,
                email: e.target.value,
              })
            }
          />

          <input
            type="password"
            placeholder="Password"
            value={loginForm.password}
            onChange={(e) =>
              setLoginForm({
                ...loginForm,
                password: e.target.value,
              })
            }
          />

          <button onClick={login}>Login</button>
        </div>
      )}

      {tab === "Register" && (
        <div className="tabcontent">
          <input
            placeholder="First name"
            value={registerForm.first_name}
            onChange={(e) =>
              setRegisterForm({
                ...registerForm,
                first_name: e.target.value,
              })
            }
          />

          <input
            placeholder="Last name"
            value={registerForm.last_name}
            onChange={(e) =>
              setRegisterForm({
                ...registerForm,
                last_name: e.target.value,
              })
            }
          />

          <input
            type="email"
            placeholder="Email"
            value={registerForm.email}
            onChange={(e) =>
              setRegisterForm({
                ...registerForm,
                email: e.target.value,
              })
            }
          />

          <input
            type="password"
            placeholder="Password"
            value={registerForm.password}
            onChange={(e) =>
              setRegisterForm({
                ...registerForm,
                password: e.target.value,
              })
            }
          />

          <input
            type="password"
            placeholder="Confirm password"
            value={registerForm.confirmPassword}
            onChange={(e) =>
              setRegisterForm({
                ...registerForm,
                confirmPassword: e.target.value,
              })
            }
          />

          <button onClick={register}>Register</button>
        </div>
      )}
      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}
    </div>
  );
}

export default App;