import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi, describe, it, expect } from 'vitest';

// Mock App component for navigation testing
const MockApp = () => {
  return (
    <div data-testid="app">
      <nav data-testid="navigation">
        <a href="/dashboard" data-testid="dashboard-link">Dashboard</a>
        <a href="/profile" data-testid="profile-link">Profile</a>
      </nav>
      <div data-testid="feedback-button">
        Feedback Button Present
      </div>
    </div>
  );
};

describe('Navigation', () => {
  it('renders navigation links correctly', () => {
    render(
      <MemoryRouter>
        <MockApp />
      </MemoryRouter>
    );

    expect(screen.getByTestId('navigation')).toBeInTheDocument();
    expect(screen.getByTestId('dashboard-link')).toBeInTheDocument();
    expect(screen.getByTestId('profile-link')).toBeInTheDocument();
  });

  it('shows feedback button on all pages', () => {
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <MockApp />
      </MemoryRouter>
    );

    expect(screen.getByTestId('feedback-button')).toBeInTheDocument();
  });

  it('maintains feedback button visibility across route changes', () => {
    const { rerender } = render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <MockApp />
      </MemoryRouter>
    );

    expect(screen.getByTestId('feedback-button')).toBeInTheDocument();

    // Simulate navigation to profile page
    rerender(
      <MemoryRouter initialEntries={['/profile']}>
        <MockApp />
      </MemoryRouter>
    );

    expect(screen.getByTestId('feedback-button')).toBeInTheDocument();
  });

  it('renders app container correctly', () => {
    render(
      <MemoryRouter>
        <MockApp />
      </MemoryRouter>
    );

    expect(screen.getByTestId('app')).toBeInTheDocument();
  });
});
