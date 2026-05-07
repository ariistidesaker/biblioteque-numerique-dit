import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Home from './pages/Home';
import Catalogue from './pages/Catalogue';
import Login from './pages/Login';
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import Confirmation from './pages/Confirmation';
import Profil from './pages/Profil';
import { Toaster } from 'react-hot-toast';
import './index.css';

function App() {
  return (
    <Router>
      <Toaster position="top-right" toastOptions={{ duration: 4000, style: { background: 'var(--surface)', color: 'var(--text)', border: '1px solid var(--border)' } }} />
      <div className="app-container" style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Navbar />
        <main className="main-content" style={{ flex: 1 }}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/catalogue" element={<Catalogue />} />
            <Route path="/login" element={<Login />} />
            <Route path="/inscription" element={<Register />} />
            <Route path="/mot-de-passe-oublie" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            <Route path="/confirmation" element={<Confirmation />} />
            <Route path="/profil" element={<Profil />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

export default App;
