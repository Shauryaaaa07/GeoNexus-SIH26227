import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { ReactLenis } from "lenis/react";

import "./index.css";
import App from "./App.jsx";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <ReactLenis root options={{ autoRaf: true }}>
      <App />
    </ReactLenis>
  </StrictMode>
);