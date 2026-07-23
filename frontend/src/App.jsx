import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Tools from "./pages/Tools";
import Jobs from "./pages/Jobs";
import Projects from "./pages/Projects";
import Contact from "./pages/Contact";
import RequestTool from "./pages/RequestTool";
import About from "./pages/About";
import Settings from "./pages/Settings";
import ProjectDetails from "./pages/ProjectDetails";
import JobDetails from "./pages/JobDetails";
import LeadGeneration from "./pages/LeadGeneration";


function App() {
  return (
    <BrowserRouter>
      <Routes>

        <Route element={<Layout />}>

          <Route path="/" element={<Dashboard />} />

          <Route path="/tools" element={<Tools />} />

          <Route path="/tools/lead-generation" element={<LeadGeneration />} />

          <Route path="/jobs" element={<Jobs />} />

          <Route path="/jobs/:jobId" element={<JobDetails />} />

          <Route path="/projects" element={<Projects />} />

          <Route path="/projects/:projectId" element={<ProjectDetails />} />

          <Route path="/contact" element={<Contact />} />

          <Route path="/request-tool" element={<RequestTool />} />

          <Route path="/about" element={<About />} />

          <Route path="/settings" element={<Settings />} />

        </Route>

      </Routes>
    </BrowserRouter>
  );
}

export default App;