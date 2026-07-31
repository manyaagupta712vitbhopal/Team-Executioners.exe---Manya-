import { Routes, Route } from "react-router-dom";

import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import Organizer from "./pages/Organizer";
import Viewer from "./pages/Viewer";
import Mentor from "./pages/Mentor";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/organizer" element={<Organizer />} />
      <Route path="/viewer/:id" element={<Viewer />} />
      <Route path="/mentor" element={<Mentor />} />
    </Routes>
  );
}

export default App;