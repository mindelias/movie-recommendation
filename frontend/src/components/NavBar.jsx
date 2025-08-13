import { Link, useNavigate } from 'react-router-dom';

export default function NavBar() {
  const navigate = useNavigate();
  const logout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };
  return (
    <nav className="navbar">
      <Link to="/movies">Movies</Link>
      <Link to="/top">Top</Link>
      <Link to="/recommendations">Recommended</Link>
      <button onClick={logout}>Logout</button>
    </nav>
  );
}
