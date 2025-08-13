import { useEffect, useState } from 'react';
import { apiFetch } from '../api';
import NavBar from '../components/NavBar';

export default function Recommendations() {
  const [movieIds, setMovieIds] = useState([]);
  const [movies, setMovies] = useState([]);

  useEffect(() => {
    apiFetch('/movies/recommendations')
      .then((res) => res.json())
      .then((data) => setMovieIds(data.movie_ids || []));
  }, []);

  useEffect(() => {
    if (movieIds.length) {
      apiFetch('/movies/')
        .then((res) => res.json())
        .then((all) =>
          setMovies(all.filter((m) => movieIds.includes(m.movie_id)))
        );
    }
  }, [movieIds]);

  return (
    <div>
      <NavBar />
      <h2>Recommended</h2>
      <ul className="movie-grid">
        {movies.map((m) => (
          <li key={m.movie_id} className="movie-card">
            {m.poster_path && <img src={m.poster_path} alt={m.title} />}
            <h3>{m.title}</h3>
            <p>{m.overview}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
