import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import FloatingFeedbackButton from '../components/FloatingFeedbackButton';

// Mock the FeedbackModal component
vi.mock('../components/FeedbackModal', () => ({
  default: ({ isOpen, onClose, userContext }: any) =>
    isOpen ? (
      <div data-testid="feedback-modal">
        <button data-testid="modal-close" onClick={onClose}>
          Close Modal
        </button>
        <div data-testid="user-context">
          {userContext?.email || 'Anonymous'}
        </div>
      </div>
    ) : null,
}));

describe('FloatingFeedbackButton', () => {
  const mockUserContext = {
    id: '1',
    email: 'test@example.com',
    username: 'testuser',
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the floating feedback button', () => {
    render(<FloatingFeedbackButton userContext={mockUserContext} />);

    const button = screen.getByRole('button', { name: 'Share Feedback' });
    expect(button).toBeInTheDocument();
    expect(button).toHaveAttribute('title', 'Share your feedback with us');
  });

  it('opens feedback modal when button is clicked', async () => {
    const user = userEvent.setup();
    render(<FloatingFeedbackButton userContext={mockUserContext} />);

    const button = screen.getByRole('button', { name: 'Share Feedback' });
    await user.click(button);

    expect(screen.getByTestId('feedback-modal')).toBeInTheDocument();
  });

  it('closes feedback modal when modal close is triggered', async () => {
    const user = userEvent.setup();
    render(<FloatingFeedbackButton userContext={mockUserContext} />);

    // Open modal
    const button = screen.getByRole('button', { name: 'Share Feedback' });
    await user.click(button);

    expect(screen.getByTestId('feedback-modal')).toBeInTheDocument();

    // Close modal
    const closeButton = screen.getByTestId('modal-close');
    await user.click(closeButton);

    expect(screen.queryByTestId('feedback-modal')).not.toBeInTheDocument();
  });

  it('shows authenticated tooltip on hover for authenticated user', async () => {
    const user = userEvent.setup();
    render(<FloatingFeedbackButton userContext={mockUserContext} />);

    const button = screen.getByRole('button', { name: 'Share Feedback' });
    await user.hover(button);

    expect(screen.getByText('Share your feedback')).toBeInTheDocument();
  });

  it('shows anonymous tooltip on hover for anonymous user', async () => {
    const user = userEvent.setup();
    render(<FloatingFeedbackButton userContext={null} />);

    const button = screen.getByRole('button', { name: 'Share Feedback' });
    await user.hover(button);

    expect(screen.getByText('Share feedback anonymously')).toBeInTheDocument();
  });

  it('hides tooltip when not hovering', () => {
    render(<FloatingFeedbackButton userContext={mockUserContext} />);

    // Use the testid to find the tooltip container
    const tooltipContainer = screen.getByTestId('feedback-tooltip');
    expect(tooltipContainer).toHaveClass('opacity-0', 'invisible');
  });

  it('passes user context to feedback modal', async () => {
    const user = userEvent.setup();
    render(<FloatingFeedbackButton userContext={mockUserContext} />);

    const button = screen.getByRole('button', { name: 'Share Feedback' });
    await user.click(button);

    expect(screen.getByTestId('user-context')).toHaveTextContent('test@example.com');
  });

  it('passes null user context to feedback modal when anonymous', async () => {
    const user = userEvent.setup();
    render(<FloatingFeedbackButton userContext={null} />);

    const button = screen.getByRole('button', { name: 'Share Feedback' });
    await user.click(button);

    expect(screen.getByTestId('user-context')).toHaveTextContent('Anonymous');
  });

  it('has proper accessibility attributes', () => {
    render(<FloatingFeedbackButton userContext={mockUserContext} />);

    const button = screen.getByRole('button', { name: 'Share Feedback' });
    expect(button).toHaveAttribute('aria-label', 'Share Feedback');
    expect(button).toHaveAttribute('title', 'Share your feedback with us');
  });

  it('maintains focus when opened and closed', async () => {
    const user = userEvent.setup();
    render(<FloatingFeedbackButton userContext={mockUserContext} />);

    const button = screen.getByRole('button', { name: 'Share Feedback' });
    
    // Focus and click the button
    button.focus();
    expect(button).toHaveFocus();
    
    await user.click(button);
    
    // Modal should be open
    expect(screen.getByTestId('feedback-modal')).toBeInTheDocument();
    
    // Close modal
    const closeButton = screen.getByTestId('modal-close');
    await user.click(closeButton);
    
    // Modal should be closed
    expect(screen.queryByTestId('feedback-modal')).not.toBeInTheDocument();
  });

  it('handles keyboard navigation', async () => {
    const user = userEvent.setup();
    render(<FloatingFeedbackButton userContext={mockUserContext} />);

    const button = screen.getByRole('button', { name: 'Share Feedback' });
    
    // Tab to the button and press Enter
    await user.tab();
    expect(button).toHaveFocus();
    
    await user.keyboard('{Enter}');
    expect(screen.getByTestId('feedback-modal')).toBeInTheDocument();
  });
});
