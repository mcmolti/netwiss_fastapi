# NetWiss FastAPI - Frontend

This is the frontend application for the NetWiss proposal generation system, built with [Next.js](https://nextjs.org) and TypeScript. The application provides an intelligent interface for generating funding proposals (Förderanträge) using AI assistance.

## Features

- **Interactive Proposal Generator**: Create funding proposals step-by-step with guided input
- **AI-Powered Content Generation**: Generate proposal sections using integrated LLM services
- **Modern UI Components**: Built with Radix UI components and Tailwind CSS
- **Real-time Preview**: See generated content as you work through the proposal
- **Responsive Design**: Optimized for desktop and mobile devices

## Tech Stack

- **Framework**: Next.js 15.4.6 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4.0
- **UI Components**: shadcn/ui / Radix UI primitives
- **Icons**: Lucide React
- **Development**: Turbopack for fast development builds

## Getting Started

First, install the dependencies:

```bash
npm install
```

Then, run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the application.

The application will automatically connect to the FastAPI backend running on `http://localhost:8000` for proposal generation services.


