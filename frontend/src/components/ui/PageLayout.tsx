import React from 'react';

interface PageLayoutProps {
  children: React.ReactNode;
  className?: string;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full';
}

export const PageLayout: React.FC<PageLayoutProps> = ({
  children,
  className = '',
  maxWidth = 'xl'
}) => {
  const maxWidthStyles = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-7xl',
    '2xl': 'max-w-2xl',
    full: 'max-w-full'
  };

  return (
    <div className={`min-h-screen bg-gray-50 ${className}`}>
      <div className={`mx-auto px-4 sm:px-6 lg:px-8 py-8 ${maxWidthStyles[maxWidth]}`}>
        {children}
      </div>
    </div>
  );
};

interface PageHeaderProps {
  children: React.ReactNode;
  className?: string;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  children,
  className = ''
}) => {
  return (
    <div className={`mb-8 ${className}`}>
      {children}
    </div>
  );
};

interface PageTitleProps {
  children: React.ReactNode;
  className?: string;
}

export const PageTitle: React.FC<PageTitleProps> = ({
  children,
  className = ''
}) => {
  return (
    <h1 className={`text-3xl font-bold text-gray-900 ${className}`}>
      {children}
    </h1>
  );
};

interface PageDescriptionProps {
  children: React.ReactNode;
  className?: string;
}

export const PageDescription: React.FC<PageDescriptionProps> = ({
  children,
  className = ''
}) => {
  return (
    <p className={`mt-2 text-gray-600 ${className}`}>
      {children}
    </p>
  );
};