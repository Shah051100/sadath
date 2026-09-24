import { render, screen } from '@testing-library/react';
import App from './App';

test('renders the Kashmir Integrated Farm Hub deck', () => {
  render(<App />);
  expect(screen.getByRole('heading', { name: /KASHMIR\s+INTEGRATED\s+FARM HUB/i })).toBeInTheDocument();
  expect(screen.getByLabelText(/Slide 1 of 10/i)).toBeInTheDocument();
});
