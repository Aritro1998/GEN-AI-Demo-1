import { Route, Routes } from "react-router-dom";
import Main from "./Layout/Main/MainLayout";
import LoginPage from "./pages/Auth/Login/LoginPage";
import HomePage from "./pages/Home/HomePage";

import "./App.css";
import MainLayout from "./Layout/Main/MainLayout";
import ChatPage from "./pages/Chat/ChatScreen";
import ManageUser from "./pages/mange-user/manage-user";
import FarmerDashboard from "./pages/Farmer/FarmerDashboard";
import DiagnosePage from "./pages/Farmer/Diagnose/DiagnoseForm";
import DiagnosisResultPage from "./pages/Farmer/Diagnose/DiagnosisResultPage";
import DiagnosisHistoryPage from "./pages/Farmer/Diagnose/DiagnosisHistory";
import useUserStore from "./store/useUserStore";
import DiagnosisDetailsPage from "./pages/Farmer/Diagnose/DiagnoseDetails";

const App = () => {
  const {user} = useUserStore();
  console.log(user)
  return (
    <div className="bg-background">
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route element={<MainLayout />}>
          <Route path="/" element={user ? <HomePage />:<LoginPage />} />
          <Route path="/home" element={<HomePage />} />
          <Route path="/manage-user" element={<ManageUser />} />
          <Route path="/diagnose" element={<DiagnosePage />} />
          <Route path="/result/:id" element={<DiagnosisResultPage />} />
          <Route path="/diagnose/:id" element={<DiagnosisDetailsPage />} />

          <Route path="/history" element={<DiagnosisHistoryPage />} />



          <Route path="/chat" element={<ChatPage />} />
          <Route path="/farmer" element={<FarmerDashboard />} />


        </Route>
      </Routes>
    </div>
  );
};

export default App;
