import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login.jsx';
import Signup from './pages/Signup.jsx';
import Movies from './pages/Movies.jsx';
import TopMovies from './pages/TopMovies.jsx';
import Recommendations from './pages/Recommendations.jsx';

function PrivateRoute({ children }) {
  const token = localStorage.getItem('token');
  return token ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route
        path="/movies"
        element={
          <PrivateRoute>
            <Movies />
          </PrivateRoute>
        }
      />
      <Route
        path="/top"
        element={
          <PrivateRoute>
            <TopMovies />
          </PrivateRoute>
        }
      />
      <Route
        path="/recommendations"
        element={
          <PrivateRoute>
            <Recommendations />
          </PrivateRoute>
        }
      />
      <Route path="*" element={<Navigate to="/movies" replace />} />
    </Routes>
  );
}
