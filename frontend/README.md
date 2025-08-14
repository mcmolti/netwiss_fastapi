# NetWiss FastAPI - Frontend

A modern, responsive web application for AI-powered proposal generation, built with Next.js 15, TypeScript, and Tailwind CSS. The application provides an intuitive interface for creating funding proposals (Förderanträge) with integrated file upload and AI assistance.

## Features

### Core Functionality
- **Interactive Proposal Generator**: Step-by-step proposal creation with guided input
- **Multi-LLM Support**: Choose between OpenAI and Anthropic models for optimal results
- **Template Management**: Dynamic templates with configurable sections
- **Real-time Generation**: Live content generation with progress indicators
- **Attachment Processing**: PDF upload and URL integration with AI-powered summarization

### User Experience
- **Modern UI Components**: Built with shadcn/ui and Radix UI primitives
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Dark/Light Mode**: Automatic theme detection and manual toggle
- **Error Handling**: Comprehensive error states with user-friendly messages
- **Loading States**: Visual feedback during content generation and file processing

### Technical Features
- **File Upload**: Drag-and-drop PDF upload with progress tracking
- **URL Processing**: Web content extraction and integration
- **State Management**: Efficient React state management with hooks
- **API Integration**: Seamless communication with FastAPI backend
- **Type Safety**: Full TypeScript implementation with strict type checking

## Tech Stack

### Framework & Runtime
- **Next.js 15.4.6**: React framework with App Router and server components
- **React 19.1.0**: Modern React with concurrent features
- **TypeScript**: Full type safety and enhanced developer experience

### UI & Styling
- **Tailwind CSS 4.0**: Utility-first CSS framework with modern features
- **shadcn/ui**: High-quality, accessible component library
- **Radix UI**: Unstyled, accessible UI primitives
- **Lucide React**: Modern icon library with consistent design
- **class-variance-authority (CVA)**: Type-safe variant APIs

### Development Tools
- **Turbopack**: Ultra-fast bundler for development (Next.js 15 default)
- **ESLint**: Code linting with Next.js specific rules
- **PostCSS**: CSS processing and optimization

### API Integration
- **Fetch API**: Native browser API for HTTP requests
- **TypeScript Interfaces**: Strongly typed API contracts
- **Error Boundaries**: Graceful error handling and recovery

## Project Structure

```
frontend/
├── src/
│   ├── app/                     # Next.js App Router
│   │   ├── favicon.ico
│   │   ├── globals.css          # Global styles and Tailwind imports
│   │   ├── layout.tsx           # Root layout component
│   │   └── page.tsx             # Main application page (410 lines)
│   ├── components/              # React components
│   │   ├── FileAttachment.tsx   # File upload and attachment handling
│   │   ├── attachments/         # Attachment-related components
│   │   ├── proposal/            # Proposal-specific components
│   │   └── ui/                  # Reusable UI components
│   │       ├── button.tsx       # Button component variants
│   │       ├── card.tsx         # Card layout components
│   │       ├── dropdown-menu.tsx # Dropdown menu implementation
│   │       ├── input.tsx        # Form input components
│   │       ├── select.tsx       # Select dropdown components
│   │       └── textarea.tsx     # Textarea form components
│   └── lib/                     # Utility libraries
│       ├── api.ts               # API client and type definitions
│       └── utils.ts             # Utility functions and helpers
├── public/                      # Static assets
│   ├── file.svg                 # File-related icons
│   ├── globe.svg               # Web/URL icons
│   ├── next.svg                # Next.js branding
│   ├── vercel.svg              # Vercel deployment assets
│   └── window.svg              # UI element icons
├── components.json              # shadcn/ui configuration
├── eslint.config.mjs           # ESLint configuration
├── next-env.d.ts               # Next.js TypeScript declarations
├── next.config.ts              # Next.js configuration
├── package.json                # Dependencies and scripts
├── postcss.config.mjs          # PostCSS configuration
├── tsconfig.json               # TypeScript configuration
└── README.md                   # This file
```

## Getting Started

### Prerequisites

- **Node.js 20+**: Required for Next.js 15
- **npm/yarn/pnpm**: Package manager of choice
- **Backend Service**: NetWiss FastAPI backend running on `http://localhost:8000`

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   # or
   yarn install
   # or
   pnpm install
   ```

2. **Configure environment (optional):**
   ```bash
   # Create .env.local for custom API endpoints
   echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
   ```

### Development

Run the development server with Turbopack:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

### Building for Production

```bash
# Build the application
npm run build

# Start the production server
npm run start
```

### Linting

```bash
# Run ESLint
npm run lint
```

## Key Features

### Proposal Generation Workflow

1. **Template Selection**: Choose from available proposal templates
2. **Model Selection**: Select AI model (OpenAI GPT or Anthropic Claude)
3. **Section Configuration**: Fill in user input for each proposal section
4. **Attachment Processing**: 
   - Upload PDF files for context
   - Add relevant URLs for additional information
5. **AI Generation**: Generate content with AI assistance
6. **Review & Export**: Review generated content and export results

### File Upload System

- **Drag & Drop**: Intuitive file upload interface
- **PDF Support**: Automatic text extraction from PDF documents
- **Progress Tracking**: Real-time upload and processing status
- **Error Handling**: Clear error messages and retry options
- **File Management**: Remove and re-upload files as needed

### URL Processing

- **Web Content Extraction**: Automatic content extraction from web URLs
- **Content Validation**: URL accessibility and content verification
- **Processing Status**: Visual feedback during content extraction
- **Error Recovery**: Graceful handling of inaccessible URLs

### AI Model Integration

- **Multiple Providers**: Support for OpenAI and Anthropic models
- **Dynamic Selection**: Choose optimal model per request
- **Cost Optimization**: Balance between performance and cost
- **Rate Limiting**: Handled gracefully with user feedback

The application automatically connects to the FastAPI backend for all AI processing and template management.

## API Integration

The frontend communicates with the FastAPI backend through a well-defined API:

### Core Endpoints Used
- `GET /api/v1/templates` - Fetch available proposal templates
- `GET /api/v1/models` - Get available AI models
- `POST /api/v1/generate-sections` - Generate proposal content
- `POST /api/v1/attachments/upload` - Upload PDF files
- `POST /api/v1/attachments/url` - Process web URLs

### Type Safety
All API interactions are fully typed with TypeScript interfaces defined in `src/lib/api.ts`, ensuring compile-time safety and excellent developer experience.

## Component Architecture

### Core Components

- **`page.tsx`**: Main application orchestrating the entire proposal generation workflow
- **`FileAttachment.tsx`**: Comprehensive file upload and management component
- **`ui/`**: Reusable UI components built with Radix UI and styled with Tailwind CSS

### State Management

The application uses React's built-in state management with hooks:
- `useState` for component-level state
- `useEffect` for side effects and API calls
- Custom hooks for complex state logic

### Styling Strategy

- **Tailwind CSS**: Utility-first approach for rapid development
- **Component Variants**: CVA for type-safe component styling
- **Design System**: Consistent spacing, colors, and typography
- **Responsive Design**: Mobile-first approach with breakpoint utilities

## Development Guidelines

### Code Organization
- Components are organized by feature and reusability
- Utilities and helpers are centralized in `src/lib/`
- Types and interfaces are co-located with their usage

### Best Practices
- Full TypeScript coverage with strict mode enabled
- Component composition over inheritance
- Accessible design with proper ARIA labels and keyboard navigation
- Performance optimization with React best practices

### Adding New Features

1. **New Components**: Add to appropriate directory in `src/components/`
2. **API Integration**: Extend `src/lib/api.ts` with new endpoints and types
3. **Styling**: Use existing design tokens and component patterns
4. **State Management**: Follow existing patterns with hooks and context


