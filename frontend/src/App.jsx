import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import ProtectedRoute from "./auth/ProtectedRoute";
import Dashboard from "./pages/Dashboard"; import Tools from "./pages/Tools"; import Jobs from "./pages/Jobs";
import Projects from "./pages/Projects"; import Contact from "./pages/Contact"; import RequestTool from "./pages/RequestTool";
import About from "./pages/About"; import Settings from "./pages/Settings"; import ProjectDetails from "./pages/ProjectDetails";
import JobDetails from "./pages/JobDetails"; import LeadGeneration from "./pages/LeadGeneration";
import Login from "./pages/Login"; import Register from "./pages/Register";
import ProjectJobs from "./pages/ProjectJobs"; import AdminDashboard from "./pages/AdminDashboard";
import SpreadsheetEnrichment from "./pages/SpreadsheetEnrichment";

export default function App() {
  return <BrowserRouter><Routes>
    <Route path="/login" element={<Login/>}/><Route path="/register" element={<Register/>}/>
    <Route element={<ProtectedRoute/>}><Route element={<Layout/>}>
      <Route path="/" element={<Dashboard/>}/><Route path="/tools" element={<Tools/>}/>
      <Route path="/tools/lead-generation" element={<LeadGeneration/>}/>
      <Route path="/tools/spreadsheet-enrichment" element={<SpreadsheetEnrichment/>}/>
      <Route path="/jobs" element={<Jobs/>}/><Route path="/jobs/:jobId" element={<JobDetails/>}/>
      <Route path="/projects" element={<Projects/>}/><Route path="/projects/:projectId" element={<ProjectDetails/>}/>
      <Route path="/projects/:projectId/jobs" element={<ProjectJobs/>}/>
      <Route path="/projects/:projectId/jobs/:jobId" element={<JobDetails/>}/>
      <Route path="/contact" element={<Contact/>}/><Route path="/request-tool" element={<RequestTool/>}/>
      <Route path="/about" element={<About/>}/><Route path="/settings" element={<Settings/>}/>
      <Route element={<ProtectedRoute admin/>}><Route path="/admin" element={<AdminDashboard/>}/></Route>
    </Route></Route>
  </Routes></BrowserRouter>;
}
